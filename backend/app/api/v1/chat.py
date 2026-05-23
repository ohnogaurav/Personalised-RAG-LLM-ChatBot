from typing import List
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db, async_session_maker
from app.core.dependencies import get_current_user, get_current_user_websocket
from app.models.sql import User, ChatSession, Message, MemoryItem
from app.models.pydantic_schemas import (
    ChatSessionResponse,
    ChatSessionCreate,
    ChatSessionDetailResponse,
    MessageResponse
)
from app.services.llm import llm_service
from app.services.vector_db import vector_db_service
from app.services.memory_agent import memory_agent

router = APIRouter(prefix="/chats", tags=["chats"])

@router.post("", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_in: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    session = ChatSession(user_id=current_user.id, title=session_in.title)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

@router.get("", response_model=List[ChatSessionResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
    )
    return result.scalars().all()

@router.get("/{session_id}", response_model=ChatSessionDetailResponse)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .options(selectinload(ChatSession.messages))
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    await db.delete(session)
    await db.commit()
    return

# --- WebSocket Streaming Chat Server ---

@router.websocket("/ws/{session_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str = None
):
    await websocket.accept()
    
    # WebSocket authentication
    async with async_session_maker() as db:
        user = await get_current_user_websocket(db, token)
        if not user:
            await websocket.send_json({"type": "error", "content": "Authentication failed"})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Check if chat session belongs to authenticated user
        result = await db.execute(
            select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user.id)
        )
        session = result.scalars().first()
        if not session:
            await websocket.send_json({"type": "error", "content": "Chat session not found"})
            await websocket.close()
            return
            
    try:
        while True:
            # Wait for message from user
            data = await websocket.receive_json()
            user_text = data.get("content", "").strip()
            
            if not user_text:
                continue
                
            # Create a separate DB session for processing this conversation turn
            async with async_session_maker() as db:
                # 1. Save user message to database
                user_msg = Message(session_id=session_id, role="user", content=user_text)
                db.add(user_msg)
                
                # Fetch recent conversation history (short-term memory)
                history_result = await db.execute(
                    select(Message)
                    .where(Message.session_id == session_id)
                    .order_by(Message.created_at.desc())
                    .limit(15)
                )
                recent_messages = list(reversed(history_result.scalars().all()))
                
                # 2. Vector search user's long-term memory
                memories = []
                query_vector = await llm_service.get_embedding(user_text)
                if any(v != 0.0 for v in query_vector):
                    memories = await vector_db_service.search_memories(user_id=user.id, query_vector=query_vector, limit=5)
                
                # Fallback to recent active memories from SQL if vector search is empty or embedding failed
                if not memories:
                    db_memories = await db.execute(
                        select(MemoryItem)
                        .where(MemoryItem.user_id == user.id, MemoryItem.is_active == True)
                        .order_by(MemoryItem.updated_at.desc())
                        .limit(5)
                    )
                    memories = [{"fact": m.fact} for m in db_memories.scalars().all()]
                
                # Format long-term memories into context
                memory_context_str = ""
                if memories:
                    memory_context_str = "You remember these facts about the user:\n"
                    for m in memories:
                        memory_context_str += f"- {m['fact']}\n"
                
                # 3. Construct prompt
                system_instruction = f"""
You are Aethera, a highly advanced Personal AI Assistant.
You have a persistent, long-term memory of the user.

{memory_context_str}

Respond to the user naturally and directly. If the user tells you new information (like their name, preferences, or goals), acknowledge it.
Keep your responses conversational, insightful, and helpful.
"""
                # Compile recent dialog history
                dialogue_contents = []
                for msg in recent_messages:
                    dialogue_contents.append(f"{msg.role.capitalize()}: {msg.content}")
                # Append the new message
                dialogue_contents.append(f"User: {user_text}")
                chat_prompt = "\n".join(dialogue_contents)

                # Send typing indicator
                await websocket.send_json({"type": "status", "content": "thinking"})
                
                # 4. Stream response from Groq
                assistant_response = ""
                async for chunk in llm_service.stream_chat_response(
                    prompt=chat_prompt,
                    system_instruction=system_instruction
                ):
                    assistant_response += chunk
                    await websocket.send_json({"type": "content", "content": chunk})
                
                # 5. Save assistant response to DB
                assistant_msg = Message(session_id=session_id, role="assistant", content=assistant_response)
                db.add(assistant_msg)
                
                # Update session timestamp
                result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
                active_session = result.scalars().first()
                if active_session:
                    active_session.updated_at = active_session.updated_at # triggers updated_at refresh
                
                await db.commit()
                
                # 6. Trigger memory extraction in the background
                # Run this asynchronously without holding up the socket connection
                background_tasks = BackgroundTasks()
                background_tasks.add_task(
                    memory_agent.process_conversation_turn,
                    user_id=user.id,
                    user_message=user_text,
                    assistant_response=assistant_response,
                    db=db
                )
                
                # Notify frontend we are done
                await websocket.send_json({"type": "done"})
                
                # Run the background tasks manually (since this is WebSockets and background tasks aren't natively run by FastAPI)
                await background_tasks()
                
    except WebSocketDisconnect:
        print(f"WebSocket client disconnected for session {session_id}")
    except Exception as e:
        print(f"WebSocket Error: {e}")
        try:
            await websocket.send_json({"type": "error", "content": str(e)})
        except:
            pass

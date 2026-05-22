from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.sql import MemoryItem
from app.services.gemini import gemini_service
from app.services.vector_db import vector_db_service

class MemoryAgent:
    @staticmethod
    async def process_conversation_turn(
        user_id: str,
        user_message: str,
        assistant_response: str,
        db: AsyncSession
    ):
        """
        Asynchronously parses conversation turn, extracts new user facts,
        resolves contradictions/updates, and saves them to SQLite and Qdrant.
        """
        # 1. Fetch active memories for this user
        result = await db.execute(
            select(MemoryItem)
            .where(MemoryItem.user_id == user_id, MemoryItem.is_active == True)
        )
        active_memories = result.scalars().all()
        
        # Format active memories for prompt context
        existing_memories_text = ""
        memory_map = {}
        for m in active_memories:
            existing_memories_text += f"- [{m.id}] ({m.category}): {m.fact}\n"
            # Map fact to its memory item to help resolve contradictions
            memory_map[m.fact.lower().strip()] = m
            
        # 2. Extract facts via Gemini Service structured output
        extracted_facts = await gemini_service.extract_memories(
            user_query=user_message,
            assistant_response=assistant_response,
            existing_memories_text=existing_memories_text
        )
        
        if not extracted_facts:
            return
            
        for new_fact in extracted_facts:
            # Skip if confidence is low
            if new_fact.confidence < 0.6:
                continue
                
            # 3. Handle conflict resolution
            if new_fact.is_contradiction and new_fact.contradicted_memory_text:
                # Find the contradicted memory
                contradicted_text = new_fact.contradicted_memory_text.lower().strip()
                matched_item = None
                
                # Check for exact or substring matches in our active memories
                for stored_text, item in memory_map.items():
                    if contradicted_text in stored_text or stored_text in contradicted_text:
                        matched_item = item
                        break
                        
                if matched_item:
                    # Deactivate contradicted memory in SQL
                    matched_item.is_active = False
                    db.add(matched_item)
                    # Delete from Qdrant vector database
                    await vector_db_service.delete_memory(matched_item.id)
                    print(f"🔄 Conflict resolved: Deactivated old memory '{matched_item.fact}' for new fact '{new_fact.fact}'")
            
            # 4. Save new fact to relational DB
            new_item = MemoryItem(
                user_id=user_id,
                category=new_fact.category,
                fact=new_fact.fact,
                confidence=new_fact.confidence,
                is_active=True
            )
            db.add(new_item)
            await db.flush()  # Flushes to DB to generate the UUID primary key (new_item.id)
            
            # 5. Compute embedding vector for the new fact
            embedding = await gemini_service.get_embedding(new_fact.fact)
            
            # 6. Insert new memory vector into Qdrant
            await vector_db_service.upsert_memory(
                memory_id=new_item.id,
                user_id=user_id,
                fact=new_fact.fact,
                category=new_fact.category,
                vector=embedding
            )
            print(f"🧠 Learned new fact: ({new_fact.category}) -> '{new_fact.fact}'")
            
        await db.commit()

memory_agent = MemoryAgent()

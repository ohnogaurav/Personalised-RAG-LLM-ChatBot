from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.sql import User, MemoryItem
from app.models.pydantic_schemas import MemoryResponse, MemoryUpdate
from app.services.vector_db import vector_db_service

router = APIRouter(prefix="/memories", tags=["memories"])

@router.get("", response_model=List[MemoryResponse])
async def list_memories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all memory records stored for the user, both active and inactive."""
    result = await db.execute(
        select(MemoryItem)
        .where(MemoryItem.user_id == current_user.id)
        .order_by(MemoryItem.created_at.desc())
    )
    return result.scalars().all()

@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory_status(
    memory_id: str,
    memory_in: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enable or disable a specific memory point."""
    result = await db.execute(
        select(MemoryItem)
        .where(MemoryItem.id == memory_id, MemoryItem.user_id == current_user.id)
    )
    memory = result.scalars().first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory item not found")
        
    memory.is_active = memory_in.is_active
    db.add(memory)
    await db.commit()
    await db.refresh(memory)
    
    # Sync with Vector DB
    if not memory.is_active:
        # Delete from Qdrant if deactivated
        await vector_db_service.delete_memory(memory.id)
    else:
        # If reactivated, we need to generate embeddings and upsert again
        from app.services.gemini import gemini_service
        embedding = await gemini_service.get_embedding(memory.fact)
        await vector_db_service.upsert_memory(
            memory_id=memory.id,
            user_id=current_user.id,
            fact=memory.fact,
            category=memory.category,
            vector=embedding
        )
        
    return memory

@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Permanently delete a memory record from both SQLite and Qdrant."""
    result = await db.execute(
        select(MemoryItem)
        .where(MemoryItem.id == memory_id, MemoryItem.user_id == current_user.id)
    )
    memory = result.scalars().first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory item not found")
        
    # Delete from Qdrant vector database
    await vector_db_service.delete_memory(memory.id)
    
    # Delete from relational database
    await db.delete(memory)
    await db.commit()
    return

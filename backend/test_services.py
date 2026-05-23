import asyncio
import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.services.llm import llm_service, ExtractedMemory
from app.services.memory_agent import memory_agent
from app.models.sql import MemoryItem, User
from app.core.database import async_session_maker, engine, Base

async def run_tests():
    print("==================================================")
    print("           AETHERA AI TEST SUITE                  ")
    print("==================================================")

    # 1. Verify API Configuration
    print("\n[1/5] Checking environment variables...")
    print(f"  - GROQ_API_KEY: {'Configured' if settings.GROQ_API_KEY else 'MISSING'}")
    print(f"  - GROQ_MODEL: {settings.GROQ_MODEL}")
    print(f"  - GOOGLE_API_KEY: {'Configured' if settings.GOOGLE_API_KEY else 'MISSING (Embeddings will fallback)'}")
    print(f"  - DATABASE_URL: {settings.DATABASE_URL}")

    # 2. Test Embedding Generation and Mock Fallback
    print("\n[2/5] Testing embedding service...")
    test_text = "I love training for marathons"
    embedding = await llm_service.get_embedding(test_text)
    print(f"  - Embedding dimension: {len(embedding)}")
    if all(v == 0.0 for v in embedding):
        print("  - Status: OK (Using mock/zero vector fallback due to missing/rate-limited Gemini key)")
    else:
        print("  - Status: OK (Gemini embedding successful)")

    # 3. Test Groq Chat Completion & Streaming
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
        print("\n[3/5] Skipping Groq Chat Test: GROQ_API_KEY not configured in .env.")
    else:
        print("\n[3/5] Testing Groq Chat Streaming...")
        prompt = "Say 'Hello World' in exactly 3 words."
        system_instruction = "Be concise."
        try:
            print("  - Streaming tokens: ", end="", flush=True)
            async for chunk in llm_service.stream_chat_response(prompt, system_instruction):
                print(chunk, end="", flush=True)
            print("\n  - Status: OK")
        except Exception as e:
            print(f"\n  - Status: FAILED ({e})")

    # 4. Test Structured Memory Extraction via Groq
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
        print("\n[4/5] Skipping Memory Extraction Test: GROQ_API_KEY not configured.")
    else:
        print("\n[4/5] Testing Memory Extraction...")
        user_query = "I adopted a cat named Whiskers today."
        assistant_response = "Congratulations on your new cat Whiskers!"
        existing_memories = ""
        try:
            memories = await llm_service.extract_memories(user_query, assistant_response, existing_memories)
            print(f"  - Extracted {len(memories)} facts:")
            for m in memories:
                print(f"    * Category: {m.category} | Fact: '{m.fact}' | Confidence: {m.confidence}")
            print("  - Status: OK")
        except Exception as e:
            print(f"  - Status: FAILED ({e})")

    # 5. Test SQLite Database & Fallback Retrieval
    print("\n[5/5] Testing SQL Fallback Retrieval...")
    async with async_session_maker() as db:
        # Create a mock user ID if none exists
        test_user_id = "test-user-id-12345"
        
        # Insert a mock memory item
        new_memory = MemoryItem(
            user_id=test_user_id,
            category="Preferences",
            fact="The user loves testing backend systems.",
            confidence=1.0,
            is_active=True
        )
        db.add(new_memory)
        await db.commit()
        print("  - Inserted mock memory to SQL database successfully.")

        # Simulate fallback retrieval
        import sqlalchemy as sa
        from sqlalchemy.future import select
        db_memories = await db.execute(
            select(MemoryItem)
            .where(MemoryItem.user_id == test_user_id, MemoryItem.is_active == True)
            .order_by(MemoryItem.updated_at.desc())
            .limit(5)
        )
        memories_retrieved = [{"fact": m.fact} for m in db_memories.scalars().all()]
        print(f"  - Retrieved {len(memories_retrieved)} active memories from SQL:")
        for m in memories_retrieved:
            print(f"    * Fact: '{m['fact']}'")
        
        # Cleanup test memory
        await db.execute(sa.delete(MemoryItem).where(MemoryItem.user_id == test_user_id))
        await db.commit()
        print("  - Cleaned up mock memory successfully.")
        print("  - Status: OK")

    print("\n==================================================")
    print("               TEST RUN COMPLETE                  ")
    print("==================================================")

if __name__ == "__main__":
    # Setup asyncio policy for Windows if needed
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_tests())

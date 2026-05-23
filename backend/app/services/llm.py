from typing import List, Optional, AsyncGenerator
from google import genai
from pydantic import BaseModel, Field
from app.core.config import settings

# Define structured output schemas for memory extraction
class ExtractedMemory(BaseModel):
    category: str = Field(
        description="Category of the fact (e.g., 'Preferences', 'Relationships', 'Professional', 'Personal Details', 'Hobbies', 'Goals')"
    )
    fact: str = Field(
        description="The clean third-person declarative fact extracted (e.g. 'The user loves matcha tea', 'The user's birthday is October 15')"
    )
    confidence: float = Field(
        description="Confidence level of this fact being true and explicitly stated/strongly implied, from 0.0 to 1.0"
    )
    is_contradiction: bool = Field(
        description="True if this newly extracted fact contradicts or overrides any of the existing memories"
    )
    contradicted_memory_text: Optional[str] = Field(
        default=None,
        description="If is_contradiction is True, specify the text of the existing memory that it contradicts/overrides"
    )

class MemoryExtractionResult(BaseModel):
    extracted_memories: List[ExtractedMemory] = Field(
        description="A list of newly extracted memories/facts from the dialogue"
    )

class LLMService:
    def __init__(self):
        # Initialize Groq client
        self.groq_client = None
        if settings.GROQ_API_KEY:
            try:
                from groq import AsyncGroq
                self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
                print("Groq client initialized successfully.")
            except Exception as e:
                print(f"Error initializing Groq client: {e}")
        else:
            print("Warning: GROQ_API_KEY is not set. Chat features will not work.")
            
        # Initialize Gemini client for embeddings
        self.gemini_client = None
        if settings.GOOGLE_API_KEY:
            try:
                self.gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)
                print("Gemini client initialized for embeddings.")
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini client: {e}")
        else:
            print("Info: GOOGLE_API_KEY is not set. Using mock embedding fallback.")

    async def get_embedding(self, text: str) -> List[float]:
        """Generate high-dimensional vector embeddings for a given text using Gemini if configured."""
        if not self.gemini_client:
            # Fallback mock embedding dimension (768 for text-embedding-004)
            return [0.0] * 768
            
        try:
            response = self.gemini_client.models.embed_content(
                model=settings.EMBEDDING_MODEL,
                contents=text
            )
            return response.embeddings[0].values
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.0] * 768

    async def stream_chat_response(self, prompt: str, system_instruction: str) -> AsyncGenerator[str, None]:
        """Stream response tokens from Groq."""
        if not self.groq_client:
            yield "\n[Error: Groq client not initialized. Please configure GROQ_API_KEY in .env]"
            return
            
        try:
            response_stream = await self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                stream=True
            )
            async for chunk in response_stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            yield f"\n[Generation Error via Groq: {e}]"

    async def extract_memories(
        self,
        user_query: str,
        assistant_response: str,
        existing_memories_text: str
    ) -> List[ExtractedMemory]:
        """Run memory extraction agent on the conversation turn with structured JSON output from Groq."""
        if not self.groq_client:
            print("Groq client not initialized. Skipping memory extraction.")
            return []
            
        prompt = f"""
Analyze the following recent conversation turn between a User and the Assistant.
Your task is to identify and extract any new facts, preferences, goals, career details, hobbies, or relationships that the User has revealed about themselves or people/pets close to them (e.g., spouse, children, friends, coworkers, pets).

Do not extract facts about the Assistant.
Do not extract temporary states (e.g. "User is hungry right now").
Only extract long-term preferences, facts, or attributes.

Here is the existing memory we have about the user to help check for contradictions:
{existing_memories_text}

---
Recent Conversation Turn:
User: {user_query}
Assistant: {assistant_response}
---

You must respond ONLY with a valid JSON object containing a list of newly extracted memory facts.
The JSON object must strictly conform to this JSON schema:
{{
  "extracted_memories": [
    {{
      "category": "string (e.g., 'Preferences', 'Relationships', 'Professional', 'Personal Details', 'Hobbies', 'Goals')",
      "fact": "string (e.g., 'The user loves matcha tea', 'The user's birthday is October 15')",
      "confidence": "number between 0.0 and 1.0",
      "is_contradiction": "boolean",
      "contradicted_memory_text": "string or null (specify the text of the existing memory that it contradicts/overrides)"
    }}
  ]
}}
"""
        try:
            response = await self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise information extraction system. You MUST respond ONLY with a valid JSON object matching the requested schema."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            import json
            content = response.choices[0].message.content
            data = json.loads(content)
            
            extracted = []
            for item in data.get("extracted_memories", []):
                extracted.append(ExtractedMemory(
                    category=item.get("category", "General"),
                    fact=item.get("fact", ""),
                    confidence=float(item.get("confidence", 1.0)),
                    is_contradiction=bool(item.get("is_contradiction", False)),
                    contradicted_memory_text=item.get("contradicted_memory_text")
                ))
            return extracted
        except Exception as e:
            print(f"Error during memory extraction via Groq: {e}")
            return []

# Instantiate singleton service
llm_service = LLMService()

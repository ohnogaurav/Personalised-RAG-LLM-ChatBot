from typing import List, Optional, AsyncGenerator
from google import genai
from google.genai import types
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

class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.model = settings.MODEL
        self.embedding_model = settings.EMBEDDING_MODEL

    async def get_embedding(self, text: str) -> List[float]:
        """Generate high-dimensional vector embeddings for a given text."""
        # Using run_in_executor or direct synchronous call since SDK is sync.
        # For simplicity and speed we run it directly.
        try:
            response = self.client.models.embed_content(
                model=self.embedding_model,
                contents=text
            )
            # The embeddings are returned as a list inside the embedding property
            return response.embeddings[0].values
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Fallback mock embedding dimension (768 for text-embedding-004) if API fails
            return [0.0] * 768

    async def stream_chat_response(self, prompt: str, system_instruction: str) -> AsyncGenerator[str, None]:
        """Stream response tokens from Gemini 2.5 Flash."""
        try:
            response_stream = self.client.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                )
            )
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"\n[Generation Error: {e}]"

    async def extract_memories(
        self,
        user_query: str,
        assistant_response: str,
        existing_memories_text: str
    ) -> List[ExtractedMemory]:
        """Run memory extraction agent on the conversation turn with structured JSON output."""
        prompt = f"""
Analyze the following recent conversation turn between a User and the Assistant.
Your task is to identify and extract any new facts, preferences, goals, career details, hobbies, or relationships that the User has revealed about themselves.

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

Return a list of newly extracted memory facts. Check if any new fact directly overrides or contradicts an existing memory listed above (e.g. if the user says "I hate coffee now" and the existing memory says "The user loves coffee", mark it as a contradiction and specify "The user loves coffee" as the contradicted text).
"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MemoryExtractionResult,
                    temperature=0.1
                )
            )
            
            # The SDK auto-parses the response if schema was provided, but let's safely parse JSON
            import json
            data = json.loads(response.text)
            
            extracted = []
            for item in data.get("extracted_memories", []):
                extracted.append(ExtractedMemory(**item))
            return extracted
        except Exception as e:
            print(f"Error during memory extraction: {e}")
            return []

# Instantiate singleton service
gemini_service = GeminiService()

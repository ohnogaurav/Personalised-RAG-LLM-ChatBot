import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from app.core.config import settings

class VectorDBService:
    def __init__(self):
        self._client = None
        self.collection_name = "user_memories"

    @property
    def client(self) -> QdrantClient:
        if self._client is None:
            # Configure client based on QDRANT_URL
            if settings.QDRANT_URL == "memory":
                # Zero-config local persistent vector store (saves to a local folder)
                if os.name != 'nt':
                    db_path = "/tmp/qdrant_db"
                else:
                    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "qdrant_db")
                self._client = QdrantClient(path=db_path)
                print(f"📦 Qdrant client initialized with local persistent path: {db_path}")
            elif settings.QDRANT_URL.startswith("/") or settings.QDRANT_URL.startswith("./") or "/" in settings.QDRANT_URL or "\\" in settings.QDRANT_URL:
                # Persistent storage to a custom folder path
                self._client = QdrantClient(path=settings.QDRANT_URL)
                print(f"📦 Qdrant client initialized with persistent path: {settings.QDRANT_URL}")
            else:
                # Connect to a running docker or cloud instance
                self._client = QdrantClient(url=settings.QDRANT_URL)
                print(f"📦 Qdrant client connected to: {settings.QDRANT_URL}")
            
            self._ensure_collection_exists()
        return self._client

    def _ensure_collection_exists(self):
        """Creates the memories collection if it doesn't already exist."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                # text-embedding-004 has 768 dimensions
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                )
                print(f"✅ Created Qdrant collection: {self.collection_name}")
        except Exception as e:
            print(f"⚠️ Error ensuring collection exists: {e}")

    async def upsert_memory(
        self,
        memory_id: str,
        user_id: str,
        fact: str,
        category: str,
        vector: List[float]
    ):
        """Upsert a memory vector along with user tenancy metadata."""
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=memory_id,
                        vector=vector,
                        payload={
                            "user_id": user_id,
                            "fact": fact,
                            "category": category
                        }
                    )
                ]
            )
        except Exception as e:
            print(f"❌ Failed to upsert vector: {e}")

    async def search_memories(
        self,
        user_id: str,
        query_vector: List[float],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories matching the query, with user ID tenancy filtering."""
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="user_id",
                            match=models.MatchValue(value=user_id),
                        )
                    ]
                ),
                limit=limit
            )
            
            results = []
            for hit in search_result:
                results.append({
                    "id": hit.id,
                    "fact": hit.payload.get("fact"),
                    "category": hit.payload.get("category"),
                    "score": hit.score
                })
            return results
        except Exception as e:
            print(f"❌ Failed to search vector DB: {e}")
            return []

    async def delete_memory(self, memory_id: str):
        """Delete a vector point from the Qdrant DB."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=[memory_id])
            )
        except Exception as e:
            print(f"❌ Failed to delete vector point: {e}")

# Instantiate singleton service
vector_db_service = VectorDBService()

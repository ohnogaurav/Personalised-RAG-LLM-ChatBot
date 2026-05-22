from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# --- User Schemas ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

# --- Chat & Message Schemas ---
class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatSessionCreate(BaseModel):
    title: Optional[str] = "New Conversation"

class ChatSessionUpdate(BaseModel):
    title: str

class ChatSessionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChatSessionDetailResponse(ChatSessionResponse):
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True

# --- Memory Schemas ---
class MemoryCreate(BaseModel):
    category: str
    fact: str
    confidence: float = 1.0

class MemoryUpdate(BaseModel):
    is_active: bool

class MemoryResponse(BaseModel):
    id: str
    user_id: str
    category: str
    fact: str
    confidence: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class MemoryTimelineResponse(BaseModel):
    memories: List[MemoryResponse]
    total_active: int

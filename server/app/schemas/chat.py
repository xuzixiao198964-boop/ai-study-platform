from pydantic import BaseModel
from datetime import datetime


class ChatMessageRequest(BaseModel):
    session_id: str
    content: str
    scene: str = "chat"


class ChatMessageResponse(BaseModel):
    reply: str
    message_type: str = "text"
    scene: str = "chat"
    scene_changed: bool = False
    new_scene: str | None = None


class ChatHistoryItem(BaseModel):
    id: int
    role: str
    content: str
    message_type: str
    scene: str
    created_at: datetime

    class Config:
        from_attributes = True

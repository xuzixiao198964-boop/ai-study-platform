from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.models.student_profile import StudentProfile
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, ChatHistoryItem
from app.services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    req: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    ai_name = profile.ai_name if profile else "小智"

    history_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == user.id, ChatMessage.session_id == req.session_id)
        .order_by(ChatMessage.created_at)
        .limit(30)
    )
    history = [
        {"role": m.role, "content": m.content} for m in history_result.scalars().all()
    ]

    result = await chat_service.process_message(
        content=req.content,
        scene=req.scene,
        ai_name=ai_name,
        history=history,
    )

    user_msg = ChatMessage(
        user_id=user.id,
        session_id=req.session_id,
        role="user",
        content=req.content,
        message_type="text",
        scene=req.scene,
    )
    ai_msg = ChatMessage(
        user_id=user.id,
        session_id=req.session_id,
        role="assistant",
        content=result["reply"],
        message_type=result["message_type"],
        scene=result["scene"],
    )
    db.add(user_msg)
    db.add(ai_msg)
    await db.commit()

    return ChatMessageResponse(**result)


@router.get("/history/{session_id}", response_model=list[ChatHistoryItem])
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == user.id, ChatMessage.session_id == session_id)
        .order_by(desc(ChatMessage.created_at))
        .limit(limit)
    )
    messages = list(reversed(result.scalars().all()))
    return messages

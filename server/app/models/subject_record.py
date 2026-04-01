from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SubjectRecord(Base):
    """OCR识别结果按科目/章节归类存储"""
    __tablename__ = "subject_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    subject: Mapped[str] = mapped_column(String(50), index=True)
    chapter: Mapped[str] = mapped_column(String(200), default="")
    knowledge_point: Mapped[str] = mapped_column(String(200), default="")
    question_text: Mapped[str] = mapped_column(Text, default="")
    student_answer: Mapped[str] = mapped_column(Text, default="")
    correct_answer: Mapped[str] = mapped_column(Text, default="")
    is_correct: Mapped[bool | None] = mapped_column(nullable=True)
    error_reason: Mapped[str] = mapped_column(String(50), default="")
    image_url: Mapped[str] = mapped_column(String(500), default="")
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    record_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

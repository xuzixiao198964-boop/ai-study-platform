from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class ApprovalStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    REGENERATING = "regenerating"


class ErrorBook(Base):
    __tablename__ = "error_books"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200), default="")
    subject: Mapped[str] = mapped_column(String(50), default="")

    approval_status: Mapped[ApprovalStatus] = mapped_column(
        SAEnum(ApprovalStatus), default=ApprovalStatus.DRAFT
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(50), nullable=True)

    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    statistics: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="error_books")
    items = relationship("ErrorBookItem", back_populates="error_book", lazy="selectin")


class ErrorBookItem(Base):
    __tablename__ = "error_book_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    error_book_id: Mapped[int] = mapped_column(Integer, ForeignKey("error_books.id"), index=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), index=True)

    original_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    question_text: Mapped[str] = mapped_column(Text, default="")
    student_answer: Mapped[str] = mapped_column(Text, default="")
    correct_answer: Mapped[str] = mapped_column(Text, default="")
    error_analysis: Mapped[str] = mapped_column(Text, default="")
    knowledge_tags: Mapped[list | None] = mapped_column(JSON, nullable=True)

    similar_questions: Mapped[list | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    error_book = relationship("ErrorBook", back_populates="items")

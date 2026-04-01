from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class QuestionType(str, enum.Enum):
    CHOICE = "choice"
    FILL_BLANK = "fill_blank"
    CALCULATION = "calculation"
    APPLICATION = "application"
    SHORT_ANSWER = "short_answer"
    OTHER = "other"


class Subject(str, enum.Enum):
    MATH = "math"
    CHINESE = "chinese"
    ENGLISH = "english"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    HISTORY = "history"
    GEOGRAPHY = "geography"
    POLITICS = "politics"
    OTHER = "other"


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    session_id: Mapped[str] = mapped_column(String(100), index=True)
    sequence_no: Mapped[int] = mapped_column(Integer, default=0)

    subject: Mapped[Subject] = mapped_column(SAEnum(Subject), default=Subject.OTHER)
    question_type: Mapped[QuestionType] = mapped_column(SAEnum(QuestionType), default=QuestionType.OTHER)
    question_text: Mapped[str] = mapped_column(Text, default="")
    student_answer: Mapped[str] = mapped_column(Text, default="")
    correct_answer: Mapped[str] = mapped_column(Text, default="")
    ocr_raw_text: Mapped[str] = mapped_column(Text, default="")

    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    region_bbox: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    knowledge_points: Mapped[list | None] = mapped_column(JSON, nullable=True)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    correction = relationship("CorrectionResult", back_populates="question", uselist=False, lazy="selectin")
    images = relationship("QuestionImage", back_populates="question", lazy="selectin")


class QuestionImage(Base):
    __tablename__ = "question_images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), index=True)
    image_url: Mapped[str] = mapped_column(String(500))
    image_type: Mapped[str] = mapped_column(String(50), default="original")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    question = relationship("Question", back_populates="images")

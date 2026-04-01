from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class CorrectionStatus(str, enum.Enum):
    PENDING = "pending"
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIAL = "partial"


class ErrorReason(str, enum.Enum):
    CALCULATION_ERROR = "calculation_error"
    MISREAD_QUESTION = "misread_question"
    CONCEPT_CONFUSION = "concept_confusion"
    FORMULA_ERROR = "formula_error"
    MISSING_STEPS = "missing_steps"
    LOGIC_ERROR = "logic_error"
    OTHER = "other"


class CorrectionResult(Base):
    __tablename__ = "correction_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)

    status: Mapped[CorrectionStatus] = mapped_column(SAEnum(CorrectionStatus), default=CorrectionStatus.PENDING)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    score: Mapped[int] = mapped_column(Integer, default=0)

    standard_answer: Mapped[str] = mapped_column(Text, default="")
    solution_steps: Mapped[str] = mapped_column(Text, default="")
    explanation: Mapped[str] = mapped_column(Text, default="")

    error_reason: Mapped[ErrorReason | None] = mapped_column(SAEnum(ErrorReason), nullable=True)
    error_analysis: Mapped[str] = mapped_column(Text, default="")

    knowledge_points: Mapped[list | None] = mapped_column(JSON, nullable=True)
    similar_question_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)

    ai_confidence: Mapped[float | None] = mapped_column(nullable=True)
    manually_corrected: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    question = relationship("Question", back_populates="correction")

from datetime import datetime, timezone
from sqlalchemy import Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, index=True)

    ai_answer_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    ai_explanation_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    ai_similar_questions_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    change_log: Mapped[list | None] = mapped_column(JSON, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="permissions")

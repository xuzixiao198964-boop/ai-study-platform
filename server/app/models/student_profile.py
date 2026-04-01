from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    grade: Mapped[int] = mapped_column(Integer, default=1)
    region: Mapped[str] = mapped_column(String(200), default="")
    ai_name: Mapped[str] = mapped_column(String(50), default="小智")
    ai_voice: Mapped[str] = mapped_column(String(50), default="gentle_female")
    ai_speed: Mapped[str] = mapped_column(String(20), default="medium")
    subject_catalog: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    auto_push_errors: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", backref="profile", uselist=False)

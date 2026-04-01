from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class DeviceType(str, enum.Enum):
    STUDENT_IPAD = "student_ipad"
    PARENT_ANDROID = "parent_android"


class DeviceStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    device_type: Mapped[DeviceType] = mapped_column(SAEnum(DeviceType))
    device_name: Mapped[str] = mapped_column(String(200), default="")
    device_token: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[DeviceStatus] = mapped_column(SAEnum(DeviceStatus), default=DeviceStatus.OFFLINE)
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="devices")

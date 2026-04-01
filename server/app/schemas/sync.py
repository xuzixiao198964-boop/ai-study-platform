from pydantic import BaseModel
from datetime import datetime


class DeviceStatusResponse(BaseModel):
    student_online: bool = False
    parent_online: bool = False
    student_device_name: str = ""
    parent_device_name: str = ""
    last_student_active: datetime | None = None
    last_parent_active: datetime | None = None


class SyncMessage(BaseModel):
    type: str
    payload: dict
    timestamp: str
    sender_device: str


class ScreenShareFrame(BaseModel):
    session_id: str
    frame_base64: str
    timestamp: str
    annotations: list[dict] | None = None


class VideoCallToken(BaseModel):
    channel_name: str
    token: str
    uid: int
    app_id: str

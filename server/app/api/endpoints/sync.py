from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import get_settings
from app.models.user import User
from app.models.device import Device, DeviceType, DeviceStatus
from app.schemas.sync import DeviceStatusResponse, VideoCallToken

router = APIRouter(prefix="/sync", tags=["数据同步"])
settings = get_settings()


@router.get("/device-status", response_model=DeviceStatusResponse)
async def get_device_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Device).where(Device.user_id == user.id))
    devices = result.scalars().all()

    resp = DeviceStatusResponse()
    for d in devices:
        if d.device_type == DeviceType.STUDENT_IPAD:
            resp.student_online = d.status == DeviceStatus.ONLINE
            resp.student_device_name = d.device_name
            resp.last_student_active = d.last_active_at
        elif d.device_type == DeviceType.PARENT_ANDROID:
            resp.parent_online = d.status == DeviceStatus.ONLINE
            resp.parent_device_name = d.device_name
            resp.last_parent_active = d.last_active_at
    return resp


@router.post("/video-call-token", response_model=VideoCallToken)
async def get_video_call_token(
    user: User = Depends(get_current_user),
):
    """生成声网Agora视频通话Token"""
    if not settings.AGORA_APP_ID:
        raise HTTPException(status_code=503, detail="视频通话服务未配置")

    channel_name = f"study_{user.id}"

    from app.services.agora_service import agora_service
    token = agora_service.generate_token(channel_name, user.id)

    return VideoCallToken(
        channel_name=channel_name,
        token=token,
        uid=user.id,
        app_id=settings.AGORA_APP_ID,
    )

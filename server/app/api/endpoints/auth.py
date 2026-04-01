from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token, get_current_user
from app.models.user import User
from app.models.device import Device, DeviceType, DeviceStatus
from app.models.permission import Permission
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    ChangePasswordRequest,
)

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.username == req.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        username=req.username,
        hashed_password=get_password_hash(req.password),
        nickname=req.nickname or req.username,
    )
    db.add(user)
    await db.flush()

    permission = Permission(user_id=user.id)
    db.add(permission)
    await db.flush()

    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        nickname=user.nickname,
        device_type="student_ipad",
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    device_type = DeviceType(req.device_type)
    existing_device = await db.execute(
        select(Device).where(Device.user_id == user.id, Device.device_type == device_type)
    )
    device = existing_device.scalar_one_or_none()
    if device:
        device.status = DeviceStatus.ONLINE
        device.device_name = req.device_name or device.device_name
        device.last_active_at = datetime.now(timezone.utc)
    else:
        device = Device(
            user_id=user.id,
            device_type=device_type,
            device_name=req.device_name,
            status=DeviceStatus.ONLINE,
            last_active_at=datetime.now(timezone.utc),
        )
        db.add(device)

    await db.flush()
    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        nickname=user.nickname,
        device_type=req.device_type,
    )


@router.post("/logout")
async def logout(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    devices = await db.execute(
        select(Device).where(Device.user_id == user.id, Device.status == DeviceStatus.ONLINE)
    )
    for device in devices.scalars().all():
        device.status = DeviceStatus.OFFLINE
    return {"message": "已退出登录"}


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return user


@router.post("/change-password")
async def change_password(
    req: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(req.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="原密码错误")
    user.hashed_password = get_password_hash(req.new_password)
    return {"message": "密码修改成功"}

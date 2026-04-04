import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.config import get_settings, reload_settings
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.models.question import Question

router = APIRouter(prefix="/admin", tags=["admin"])

admin_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/admin/login", auto_error=False)

MANAGED_KEYS = [
    ("DEEPSEEK_API_KEY", "DeepSeek API Key"),
    ("AGORA_APP_ID", "声网 App ID"),
    ("AGORA_APP_CERTIFICATE", "声网 App Certificate"),
    ("VOLCANO_APP_ID", "火山引擎 App ID"),
    ("VOLCANO_ACCESS_KEY", "火山引擎 Access Key"),
    ("VOLCANO_SECRET_KEY", "火山引擎 Secret Key"),
    ("TENCENT_SECRET_ID", "腾讯云 Secret ID"),
    ("TENCENT_SECRET_KEY", "腾讯云 Secret Key"),
]

_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"


def _mask(value: str) -> str:
    if not value or len(value) <= 8:
        return "****" if value else ""
    return value[:4] + "*" * (len(value) - 8) + value[-4:]


def _read_env_file() -> dict[str, str]:
    """Read .env file directly (bypasses per-worker cache)."""
    values: dict[str, str] = {}
    if not _ENV_PATH.exists():
        return values
    for line in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            values[k.strip()] = v.strip()
    return values


def _create_admin_token(settings) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=4)
    return jwt.encode(
        {"sub": "admin", "role": "admin", "exp": expire},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


async def get_admin_user(token: str | None = Depends(admin_oauth2)):
    settings = get_settings()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="非管理员")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token无效或已过期")
    return payload


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ApiKeyItem(BaseModel):
    key: str
    label: str
    value: str
    masked_value: str


class ApiKeysUpdateRequest(BaseModel):
    keys: dict[str, str]


class PlatformStats(BaseModel):
    total_users: int
    today_active_users: int
    total_messages: int
    total_questions: int


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(req: AdminLoginRequest):
    settings = get_settings()
    if req.username != settings.ADMIN_USERNAME or req.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="账号或密码错误")
    token = _create_admin_token(settings)
    return AdminLoginResponse(access_token=token)


@router.get("/api-keys", response_model=list[ApiKeyItem])
async def get_api_keys(_=Depends(get_admin_user)):
    env_values = _read_env_file()
    result = []
    for key_name, label in MANAGED_KEYS:
        value = env_values.get(key_name, "")
        result.append(ApiKeyItem(
            key=key_name,
            label=label,
            value=value,
            masked_value=_mask(value),
        ))
    return result


@router.put("/api-keys")
async def update_api_keys(req: ApiKeysUpdateRequest, _=Depends(get_admin_user)):
    valid_keys = {k for k, _ in MANAGED_KEYS}

    if not _ENV_PATH.exists():
        raise HTTPException(status_code=500, detail=".env file not found")

    content = _ENV_PATH.read_text(encoding="utf-8")

    updated = []
    for key_name, value in req.keys.items():
        if key_name not in valid_keys:
            continue
        pattern = re.compile(rf"^{re.escape(key_name)}=.*$", re.MULTILINE)
        if pattern.search(content):
            content = pattern.sub(f"{key_name}={value}", content)
        else:
            content += f"\n{key_name}={value}"
        os.environ[key_name] = value
        updated.append(key_name)

    _ENV_PATH.write_text(content, encoding="utf-8")
    reload_settings()

    return {"updated": updated, "message": "API Key 已更新，配置已重载"}


@router.get("/stats", response_model=PlatformStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_admin_user),
):
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_active = (await db.execute(
        select(func.count(func.distinct(ChatMessage.user_id)))
        .where(ChatMessage.created_at >= today_start)
    )).scalar() or 0

    total_messages = (await db.execute(select(func.count(ChatMessage.id)))).scalar() or 0
    total_questions = (await db.execute(select(func.count(Question.id)))).scalar() or 0

    return PlatformStats(
        total_users=total_users,
        today_active_users=today_active,
        total_messages=total_messages,
        total_questions=total_questions,
    )


# ---- User management ----

class AdminUserItem(BaseModel):
    id: int
    username: str
    plain_password: str
    nickname: str
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}


class AdminResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=100)


@router.get("/users", response_model=list[AdminUserItem])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_admin_user),
):
    result = await db.execute(select(User).order_by(User.id))
    users = result.scalars().all()
    return [
        AdminUserItem(
            id=u.id,
            username=u.username,
            plain_password=u.plain_password or "(历史用户-密码未记录)",
            nickname=u.nickname,
            is_active=u.is_active,
            created_at=u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else "",
        )
        for u in users
    ]


@router.put("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    req: AdminResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_admin_user),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.hashed_password = get_password_hash(req.new_password)
    user.plain_password = req.new_password
    await db.commit()
    return {"message": f"用户 {user.username} 密码已重置"}


@router.put("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_admin_user),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.is_active = not user.is_active
    await db.commit()
    status_text = "启用" if user.is_active else "禁用"
    return {"message": f"用户 {user.username} 已{status_text}", "is_active": user.is_active}

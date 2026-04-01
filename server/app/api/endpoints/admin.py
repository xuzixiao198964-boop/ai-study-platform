import os
import re
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.config import get_settings, reload_settings
from app.core.database import get_db
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


def _mask(value: str) -> str:
    if not value or len(value) <= 8:
        return "****" if value else ""
    return value[:4] + "*" * (len(value) - 8) + value[-4:]


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
    settings = get_settings()
    result = []
    for key_name, label in MANAGED_KEYS:
        value = getattr(settings, key_name, "")
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
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env")

    if not os.path.exists(env_path):
        raise HTTPException(status_code=500, detail=".env file not found")

    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()

    updated = []
    for key_name, value in req.keys.items():
        if key_name not in valid_keys:
            continue
        pattern = re.compile(rf"^{re.escape(key_name)}=.*$", re.MULTILINE)
        if pattern.search(content):
            content = pattern.sub(f"{key_name}={value}", content)
        else:
            content += f"\n{key_name}={value}"
        updated.append(key_name)

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)

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

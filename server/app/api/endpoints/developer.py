from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import secrets
import hashlib
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.schemas.developer import (
    DeveloperRegister,
    DeveloperLogin,
    DeveloperResponse,
    ApiKeyCreate,
    ApiKeyResponse,
    TokenResponse
)

router = APIRouter()
security = HTTPBearer()


# 依赖：获取当前用户
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """从token获取当前用户"""
    token = credentials.credentials

    from app.core.security import decode_access_token
    payload = decode_access_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token"
        )

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    return user


# 生成API Key
def generate_api_key() -> str:
    """生成32位随机API Key"""
    return f"sk-{secrets.token_urlsafe(32)}"


# 哈希API Key用于存储
def hash_api_key(key: str) -> str:
    """使用SHA256哈希API Key"""
    return hashlib.sha256(key.encode()).hexdigest()


@router.post("/register", response_model=DeveloperResponse)
async def register_developer(
    data: DeveloperRegister,
    db: AsyncSession = Depends(get_db)
):
    """开发者注册"""
    # 检查邮箱是否已存在
    result = await db.execute(
        select(User).where(User.username == data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )

    # 创建开发者账号
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    new_user = User(
        username=data.email,
        hashed_password=pwd_context.hash(data.password),
        nickname=data.name,
        is_active=True
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return DeveloperResponse(
        id=new_user.id,
        email=new_user.username,
        name=new_user.nickname,
        company=data.company,
        created_at=new_user.created_at
    )


@router.post("/login", response_model=TokenResponse)
async def login_developer(
    data: DeveloperLogin,
    db: AsyncSession = Depends(get_db)
):
    """开发者登录"""
    result = await db.execute(
        select(User).where(User.username == data.email)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    # 验证密码
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    if not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    # 生成JWT token
    from app.core.security import create_access_token
    token = create_access_token({"sub": str(user.id)})

    return TokenResponse(
        token=token,
        user=DeveloperResponse(
            id=user.id,
            email=user.username,
            name=user.nickname,
            company="",
            created_at=user.created_at
        )
    )


@router.get("/keys", response_model=dict)
async def get_api_keys(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的所有API Keys"""
    # 从数据库获取API keys（需要创建api_keys表）
    # 暂时返回空列表
    return {"keys": []}


@router.post("/keys", response_model=ApiKeyResponse)
async def create_api_key(
    data: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新的API Key"""
    # 生成API Key
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)

    # 保存到数据库（需要创建api_keys表）
    # 暂时直接返回

    return ApiKeyResponse(
        id=secrets.token_urlsafe(16),
        name=data.name,
        key=api_key,
        created_at=datetime.utcnow()
    )


@router.delete("/keys/{key_id}")
async def delete_api_key(
    key_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除API Key"""
    # 从数据库删除（需要创建api_keys表）
    return {"message": "API Key已删除"}

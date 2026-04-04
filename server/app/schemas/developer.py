from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class DeveloperRegister(BaseModel):
    """开发者注册"""
    company: str
    name: str
    email: EmailStr
    password: str
    use_case: str


class DeveloperLogin(BaseModel):
    """开发者登录"""
    email: EmailStr
    password: str


class DeveloperResponse(BaseModel):
    """开发者信息响应"""
    id: int
    email: str
    name: str
    company: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """登录token响应"""
    token: str
    user: DeveloperResponse


class ApiKeyCreate(BaseModel):
    """创建API Key"""
    name: str


class ApiKeyResponse(BaseModel):
    """API Key响应"""
    id: str
    name: str
    key: str
    created_at: datetime

    class Config:
        from_attributes = True

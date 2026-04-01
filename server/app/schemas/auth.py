from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    nickname: str = Field(default="", max_length=100)


class LoginRequest(BaseModel):
    username: str
    password: str
    device_type: str = Field(default="student_ipad", pattern="^(student_ipad|parent_android)$")
    device_name: str = Field(default="")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    nickname: str
    device_type: str


class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str
    avatar_url: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=100)

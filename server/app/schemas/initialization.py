from pydantic import BaseModel


class InitSetupRequest(BaseModel):
    grade: int
    region: str
    ai_name: str = "小智"
    ai_voice: str = "gentle_female"
    ai_speed: str = "medium"


class AIConfigUpdateRequest(BaseModel):
    ai_name: str | None = None
    ai_voice: str | None = None
    ai_speed: str | None = None


class StudentProfileResponse(BaseModel):
    grade: int
    region: str
    ai_name: str
    ai_voice: str
    ai_speed: str
    subject_catalog: dict | None = None
    auto_push_errors: bool = False

    class Config:
        from_attributes = True


FORBIDDEN_AI_NAMES = [
    "爸爸", "妈妈", "爷爷", "奶奶", "外公", "外婆",
    "爸", "妈", "爷", "奶", "姥爷", "姥姥",
    "父亲", "母亲", "祖父", "祖母", "外祖父", "外祖母",
]

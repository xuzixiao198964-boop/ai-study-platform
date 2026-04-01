from pydantic import BaseModel
from datetime import datetime


class PermissionResponse(BaseModel):
    ai_answer_enabled: bool
    ai_explanation_enabled: bool
    ai_similar_questions_enabled: bool
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PermissionUpdateRequest(BaseModel):
    ai_answer_enabled: bool | None = None
    ai_explanation_enabled: bool | None = None
    ai_similar_questions_enabled: bool | None = None


class PermissionLogEntry(BaseModel):
    field: str
    old_value: bool
    new_value: bool
    changed_at: str
    changed_by: str

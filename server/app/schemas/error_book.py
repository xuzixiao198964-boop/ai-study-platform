from pydantic import BaseModel
from datetime import datetime


class ErrorBookResponse(BaseModel):
    id: int
    user_id: int
    title: str
    subject: str
    approval_status: str
    rejection_reason: str | None
    approved_at: datetime | None
    total_questions: int
    statistics: dict | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ErrorBookItemResponse(BaseModel):
    id: int
    error_book_id: int
    question_id: int
    question_text: str
    student_answer: str
    correct_answer: str
    error_analysis: str
    knowledge_tags: list | None
    original_image_url: str | None
    similar_questions: list | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ErrorBookDetailResponse(BaseModel):
    error_book: ErrorBookResponse
    items: list[ErrorBookItemResponse]


class ApproveRequest(BaseModel):
    approved: bool
    rejection_reason: str | None = None


class ErrorBookEditRequest(BaseModel):
    item_id: int
    question_text: str | None = None
    correct_answer: str | None = None
    error_analysis: str | None = None
    knowledge_tags: list[str] | None = None

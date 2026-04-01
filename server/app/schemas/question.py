from pydantic import BaseModel
from datetime import datetime


class QuestionCreate(BaseModel):
    session_id: str
    sequence_no: int = 0
    subject: str = "other"
    question_type: str = "other"
    image_url: str | None = None
    region_bbox: dict | None = None


class QuestionResponse(BaseModel):
    id: int
    session_id: str
    sequence_no: int
    subject: str
    question_type: str
    question_text: str
    student_answer: str
    correct_answer: str
    image_url: str | None
    knowledge_points: list | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CorrectionResponse(BaseModel):
    id: int
    question_id: int
    status: str
    is_correct: bool
    standard_answer: str
    solution_steps: str
    explanation: str
    error_reason: str | None
    error_analysis: str
    knowledge_points: list | None
    ai_confidence: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class OCRRequest(BaseModel):
    image_base64: str
    detect_handwriting: bool = True


class OCRResponse(BaseModel):
    questions: list[dict]
    raw_text: str
    regions: list[dict]


class VisionCorrectRequest(BaseModel):
    image_base64: str
    question_text: str = ""


class VisionCorrectResponse(BaseModel):
    question_text: str
    student_answer: str
    status: str
    is_correct: bool
    score: int = 0
    standard_answer: str
    solution_steps: str
    explanation: str
    error_reason: str | None = None
    error_analysis: str = ""
    knowledge_points: list[str] = []
    ai_confidence: float | None = None


class FingerPointRequest(BaseModel):
    image_base64: str
    question_regions: list[dict]


class FingerPointResponse(BaseModel):
    detected: bool
    finger_tip_x: float | None = None
    finger_tip_y: float | None = None
    pointed_question_id: int | None = None
    pointed_region: dict | None = None
    confidence: float = 0.0


class AIExplanationRequest(BaseModel):
    question_id: int


class AIExplanationResponse(BaseModel):
    question_id: int
    explanation_text: str
    solution_steps: str
    knowledge_points: list[str]
    tips: list[str]


class SimilarQuestionRequest(BaseModel):
    question_id: int
    count: int = 3


class SimilarQuestionResponse(BaseModel):
    original_question_id: int
    similar_questions: list[dict]

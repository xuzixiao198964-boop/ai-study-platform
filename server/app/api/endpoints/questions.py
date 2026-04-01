from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.question import Question
from app.models.correction import CorrectionResult
from app.models.permission import Permission
from app.schemas.question import (
    QuestionCreate,
    QuestionResponse,
    CorrectionResponse,
    OCRRequest,
    OCRResponse,
    VisionCorrectRequest,
    VisionCorrectResponse,
    FingerPointRequest,
    FingerPointResponse,
    AIExplanationRequest,
    AIExplanationResponse,
    SimilarQuestionRequest,
    SimilarQuestionResponse,
)

router = APIRouter(prefix="/questions", tags=["试题"])


@router.post("/ocr", response_model=OCRResponse)
async def recognize_questions(
    req: OCRRequest,
    user: User = Depends(get_current_user),
):
    from app.services.ocr_service import ocr_service
    result = await ocr_service.recognize(req.image_base64, req.detect_handwriting)
    return result


@router.post("/finger-point", response_model=FingerPointResponse)
async def detect_finger_point(
    req: FingerPointRequest,
    user: User = Depends(get_current_user),
):
    from app.services.finger_service import finger_service
    result = await finger_service.detect_and_map(req.image_base64, req.question_regions)
    return result


@router.post("/", response_model=QuestionResponse)
async def create_question(
    req: QuestionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    question = Question(user_id=user.id, **req.model_dump())
    db.add(question)
    await db.flush()
    return question


@router.get("/session/{session_id}", response_model=list[QuestionResponse])
async def get_session_questions(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Question)
        .where(Question.user_id == user.id, Question.session_id == session_id)
        .order_by(Question.sequence_no)
    )
    return result.scalars().all()


@router.post("/{question_id}/correct", response_model=CorrectionResponse)
async def correct_question(
    question_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    perm_result = await db.execute(select(Permission).where(Permission.user_id == user.id))
    perm = perm_result.scalar_one_or_none()
    if perm and not perm.ai_answer_enabled:
        raise HTTPException(status_code=403, detail="家长已关闭AI解答权限，请联系家长")

    question = await db.get(Question, question_id)
    if not question or question.user_id != user.id:
        raise HTTPException(status_code=404, detail="题目不存在")

    from app.services.ai_service import ai_service
    correction_data = await ai_service.correct_question(question)

    correction = CorrectionResult(
        question_id=question.id,
        user_id=user.id,
        **correction_data,
    )
    db.add(correction)
    await db.flush()
    return correction


@router.post("/{question_id}/explain", response_model=AIExplanationResponse)
async def explain_question(
    question_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    perm_result = await db.execute(select(Permission).where(Permission.user_id == user.id))
    perm = perm_result.scalar_one_or_none()
    if perm and not perm.ai_explanation_enabled:
        raise HTTPException(status_code=403, detail="家长已关闭AI讲解权限，请联系家长")

    question = await db.get(Question, question_id)
    if not question or question.user_id != user.id:
        raise HTTPException(status_code=404, detail="题目不存在")

    from app.services.ai_service import ai_service
    explanation = await ai_service.explain_question(question)
    return AIExplanationResponse(question_id=question_id, **explanation)


@router.post("/{question_id}/similar", response_model=SimilarQuestionResponse)
async def generate_similar(
    question_id: int,
    count: int = 3,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    perm_result = await db.execute(select(Permission).where(Permission.user_id == user.id))
    perm = perm_result.scalar_one_or_none()
    if perm and not perm.ai_similar_questions_enabled:
        raise HTTPException(status_code=403, detail="家长已关闭相似题推送权限，请联系家长")

    question = await db.get(Question, question_id)
    if not question or question.user_id != user.id:
        raise HTTPException(status_code=404, detail="题目不存在")

    from app.services.ai_service import ai_service
    similar = await ai_service.generate_similar_questions(question, count)
    return SimilarQuestionResponse(original_question_id=question_id, similar_questions=similar)


@router.post("/vision-correct", response_model=VisionCorrectResponse)
async def vision_correct(
    req: VisionCorrectRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """直接发图片给DeepSeek Vision，一步完成识别+批改"""
    perm_result = await db.execute(select(Permission).where(Permission.user_id == user.id))
    perm = perm_result.scalar_one_or_none()
    if perm and not perm.ai_answer_enabled:
        raise HTTPException(status_code=403, detail="家长已关闭AI解答权限，请联系家长")

    from app.services.ai_service import ai_service
    result = await ai_service.correct_question_with_image(req.image_base64, req.question_text)
    return result


@router.post("/upload-image")
async def upload_question_image(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    from app.services.storage_service import storage_service
    url = await storage_service.upload_file(file, f"questions/{user.id}")
    return {"url": url}

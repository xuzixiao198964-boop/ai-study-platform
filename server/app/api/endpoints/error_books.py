from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.error_book import ErrorBook, ErrorBookItem, ApprovalStatus
from app.models.correction import CorrectionResult, CorrectionStatus
from app.models.question import Question
from app.schemas.error_book import (
    ErrorBookResponse,
    ErrorBookDetailResponse,
    ErrorBookItemResponse,
    ApproveRequest,
    ErrorBookEditRequest,
)

router = APIRouter(prefix="/error-books", tags=["错题集"])


@router.post("/generate", response_model=ErrorBookResponse)
async def generate_error_book(
    session_id: str,
    subject: str = "other",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI自动生成错题集草稿，提交家长审批"""
    result = await db.execute(
        select(CorrectionResult)
        .join(Question, CorrectionResult.question_id == Question.id)
        .where(
            Question.user_id == user.id,
            Question.session_id == session_id,
            CorrectionResult.is_correct == False,
        )
    )
    wrong_corrections = result.scalars().all()
    if not wrong_corrections:
        raise HTTPException(status_code=404, detail="当前学习会话没有错题")

    from app.services.ai_service import ai_service

    error_book = ErrorBook(
        user_id=user.id,
        title=f"错题集 - {subject}",
        subject=subject,
        approval_status=ApprovalStatus.PENDING_APPROVAL,
        total_questions=len(wrong_corrections),
    )
    db.add(error_book)
    await db.flush()

    for correction in wrong_corrections:
        question = await db.get(Question, correction.question_id)
        analysis = await ai_service.analyze_error(question, correction)

        item = ErrorBookItem(
            error_book_id=error_book.id,
            question_id=question.id,
            original_image_url=question.image_url,
            question_text=question.question_text,
            student_answer=question.student_answer,
            correct_answer=correction.standard_answer,
            error_analysis=analysis.get("error_analysis", ""),
            knowledge_tags=analysis.get("knowledge_tags", []),
        )
        db.add(item)

    await db.flush()

    from app.services.sync_service import sync_service
    await sync_service.notify_parent(user.id, "error_book_pending", {
        "error_book_id": error_book.id,
        "title": error_book.title,
        "total_questions": error_book.total_questions,
    })

    return error_book


@router.get("/", response_model=list[ErrorBookResponse])
async def list_error_books(
    status: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(ErrorBook).where(ErrorBook.user_id == user.id)
    if status:
        query = query.where(ErrorBook.approval_status == ApprovalStatus(status))
    query = query.order_by(ErrorBook.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{error_book_id}", response_model=ErrorBookDetailResponse)
async def get_error_book(
    error_book_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    book = await db.get(ErrorBook, error_book_id)
    if not book or book.user_id != user.id:
        raise HTTPException(status_code=404, detail="错题集不存在")
    items_result = await db.execute(
        select(ErrorBookItem).where(ErrorBookItem.error_book_id == error_book_id)
    )
    items = items_result.scalars().all()
    return ErrorBookDetailResponse(
        error_book=ErrorBookResponse.model_validate(book),
        items=[ErrorBookItemResponse.model_validate(i) for i in items],
    )


@router.post("/{error_book_id}/approve")
async def approve_error_book(
    error_book_id: int,
    req: ApproveRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """家长审批错题集"""
    book = await db.get(ErrorBook, error_book_id)
    if not book or book.user_id != user.id:
        raise HTTPException(status_code=404, detail="错题集不存在")

    if req.approved:
        book.approval_status = ApprovalStatus.APPROVED
        book.approved_at = datetime.now(timezone.utc)
        book.approved_by = "parent"

        from app.services.sync_service import sync_service
        await sync_service.notify_student(user.id, "error_book_approved", {
            "error_book_id": book.id,
        })
    else:
        book.approval_status = ApprovalStatus.REJECTED
        book.rejection_reason = req.rejection_reason

        from app.services.sync_service import sync_service
        await sync_service.notify_student(user.id, "error_book_rejected", {
            "error_book_id": book.id,
            "reason": req.rejection_reason,
        })

    return {"message": "审批完成", "status": book.approval_status.value}


@router.post("/{error_book_id}/regenerate", response_model=ErrorBookResponse)
async def regenerate_error_book(
    error_book_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """驳回后重新生成错题集"""
    book = await db.get(ErrorBook, error_book_id)
    if not book or book.user_id != user.id:
        raise HTTPException(status_code=404, detail="错题集不存在")
    if book.approval_status != ApprovalStatus.REJECTED:
        raise HTTPException(status_code=400, detail="仅被驳回的错题集可重新生成")

    book.approval_status = ApprovalStatus.REGENERATING

    from app.services.ai_service import ai_service
    items_result = await db.execute(
        select(ErrorBookItem).where(ErrorBookItem.error_book_id == error_book_id)
    )
    items = items_result.scalars().all()
    for item in items:
        question = await db.get(Question, item.question_id)
        correction = await db.execute(
            select(CorrectionResult).where(CorrectionResult.question_id == item.question_id)
        )
        corr = correction.scalar_one_or_none()
        if question and corr:
            analysis = await ai_service.analyze_error(question, corr)
            item.error_analysis = analysis.get("error_analysis", item.error_analysis)
            item.knowledge_tags = analysis.get("knowledge_tags", item.knowledge_tags)

    book.approval_status = ApprovalStatus.PENDING_APPROVAL
    book.rejection_reason = None
    await db.flush()

    from app.services.sync_service import sync_service
    await sync_service.notify_parent(user.id, "error_book_pending", {
        "error_book_id": book.id,
        "title": book.title,
        "regenerated": True,
    })

    return book


@router.put("/{error_book_id}/items")
async def edit_error_book_item(
    error_book_id: int,
    req: ErrorBookEditRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """家长手动编辑错题集内容"""
    book = await db.get(ErrorBook, error_book_id)
    if not book or book.user_id != user.id:
        raise HTTPException(status_code=404, detail="错题集不存在")

    item = await db.get(ErrorBookItem, req.item_id)
    if not item or item.error_book_id != error_book_id:
        raise HTTPException(status_code=404, detail="错题项不存在")

    if req.question_text is not None:
        item.question_text = req.question_text
    if req.correct_answer is not None:
        item.correct_answer = req.correct_answer
    if req.error_analysis is not None:
        item.error_analysis = req.error_analysis
    if req.knowledge_tags is not None:
        item.knowledge_tags = req.knowledge_tags

    from app.services.sync_service import sync_service
    await sync_service.notify_student(user.id, "error_book_updated", {
        "error_book_id": book.id,
        "item_id": item.id,
    })

    return {"message": "修改成功"}

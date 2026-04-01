from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.permission import Permission
from app.schemas.permission import PermissionResponse, PermissionUpdateRequest

router = APIRouter(prefix="/permissions", tags=["权限管控"])


@router.get("/", response_model=PermissionResponse)
async def get_permissions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Permission).where(Permission.user_id == user.id))
    perm = result.scalar_one_or_none()
    if not perm:
        perm = Permission(user_id=user.id)
        db.add(perm)
        await db.flush()
    return perm


@router.put("/", response_model=PermissionResponse)
async def update_permissions(
    req: PermissionUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """家长端修改AI权限"""
    result = await db.execute(select(Permission).where(Permission.user_id == user.id))
    perm = result.scalar_one_or_none()
    if not perm:
        perm = Permission(user_id=user.id)
        db.add(perm)
        await db.flush()

    changes = []
    now_str = datetime.now(timezone.utc).isoformat()

    if req.ai_answer_enabled is not None and perm.ai_answer_enabled != req.ai_answer_enabled:
        changes.append({
            "field": "ai_answer_enabled",
            "old": perm.ai_answer_enabled,
            "new": req.ai_answer_enabled,
            "time": now_str,
        })
        perm.ai_answer_enabled = req.ai_answer_enabled

    if req.ai_explanation_enabled is not None and perm.ai_explanation_enabled != req.ai_explanation_enabled:
        changes.append({
            "field": "ai_explanation_enabled",
            "old": perm.ai_explanation_enabled,
            "new": req.ai_explanation_enabled,
            "time": now_str,
        })
        perm.ai_explanation_enabled = req.ai_explanation_enabled

    if req.ai_similar_questions_enabled is not None and perm.ai_similar_questions_enabled != req.ai_similar_questions_enabled:
        changes.append({
            "field": "ai_similar_questions_enabled",
            "old": perm.ai_similar_questions_enabled,
            "new": req.ai_similar_questions_enabled,
            "time": now_str,
        })
        perm.ai_similar_questions_enabled = req.ai_similar_questions_enabled

    if changes:
        log = perm.change_log or []
        log.extend(changes)
        perm.change_log = log

        from app.services.sync_service import sync_service
        await sync_service.notify_student(user.id, "permission_changed", {
            "ai_answer_enabled": perm.ai_answer_enabled,
            "ai_explanation_enabled": perm.ai_explanation_enabled,
            "ai_similar_questions_enabled": perm.ai_similar_questions_enabled,
        })

    return perm

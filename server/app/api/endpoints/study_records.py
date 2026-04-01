from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.study_record import StudyRecord

router = APIRouter(prefix="/study-records", tags=["学习记录"])


@router.get("/")
async def list_study_records(
    limit: int = 50,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StudyRecord)
        .where(StudyRecord.user_id == user.id)
        .order_by(StudyRecord.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    records = result.scalars().all()
    return {"records": records, "total": len(records)}


@router.get("/session/{session_id}")
async def get_session_records(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StudyRecord)
        .where(StudyRecord.user_id == user.id, StudyRecord.session_id == session_id)
        .order_by(StudyRecord.created_at)
    )
    return {"records": result.scalars().all()}

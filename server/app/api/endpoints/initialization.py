from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.schemas.initialization import (
    InitSetupRequest,
    AIConfigUpdateRequest,
    StudentProfileResponse,
    FORBIDDEN_AI_NAMES,
)
from app.services.ai_service import ai_service

router = APIRouter(prefix="/init", tags=["initialization"])


def _validate_ai_name(name: str):
    for forbidden in FORBIDDEN_AI_NAMES:
        if forbidden in name:
            msg = "AI名字不能包含亲属称谓[" + forbidden + "]，请换一个名字吧"
            raise HTTPException(status_code=400, detail=msg)


@router.post("/setup", response_model=StudentProfileResponse)
async def setup_student(
    req: InitSetupRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _validate_ai_name(req.ai_name)

    result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()

    catalog = await _generate_subject_catalog(req.grade, req.region)

    if profile:
        profile.grade = req.grade
        profile.region = req.region
        profile.ai_name = req.ai_name
        profile.ai_voice = req.ai_voice
        profile.ai_speed = req.ai_speed
        profile.subject_catalog = catalog
    else:
        profile = StudentProfile(
            user_id=user.id,
            grade=req.grade,
            region=req.region,
            ai_name=req.ai_name,
            ai_voice=req.ai_voice,
            ai_speed=req.ai_speed,
            subject_catalog=catalog,
        )
        db.add(profile)

    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/profile", response_model=StudentProfileResponse | None)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        return None
    return profile


@router.put("/ai-config", response_model=StudentProfileResponse)
async def update_ai_config(
    req: AIConfigUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="请先完成初始化设置")

    if req.ai_name is not None:
        _validate_ai_name(req.ai_name)
        profile.ai_name = req.ai_name
    if req.ai_voice is not None:
        profile.ai_voice = req.ai_voice
    if req.ai_speed is not None:
        profile.ai_speed = req.ai_speed

    await db.commit()
    await db.refresh(profile)
    return profile


async def _generate_subject_catalog(grade: int, region: str) -> dict:
    """让大模型根据年级和区域生成科目目录"""
    try:
        system_prompt = """你是一个中国K12教育专家。请根据学生的年级和就读区域，返回该年级对应的所有科目及每科的章节目录。
返回严格JSON格式：
{
    "subjects": [
        {
            "name": "数学",
            "chapters": [
                {"name": "第一章 xxx", "sections": ["1.1 xxx", "1.2 xxx"]}
            ]
        }
    ]
}
只返回JSON，不要其他内容。"""

        grade_name = f"{grade}年级" if grade <= 6 else f"{'初' if grade <= 9 else '高'}{grade - (6 if grade <= 9 else 9)}年级"
        user_prompt = f"学生信息：{grade_name}，就读区域：{region}。请返回该年级下学期的完整科目及章节目录。"

        result = await ai_service._chat_json(system_prompt, user_prompt)
        return result
    except Exception:
        return {"subjects": []}

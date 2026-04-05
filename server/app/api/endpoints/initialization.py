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


def _parse_grade(grade: int | str) -> int:
    """将年级字符串转换为整数（1-12）"""
    if isinstance(grade, int):
        return grade

    # 处理字符串格式
    grade_str = str(grade).strip()

    # 映射表
    grade_map = {
        "小学一年级": 1, "小学二年级": 2, "小学三年级": 3,
        "小学四年级": 4, "小学五年级": 5, "小学六年级": 6,
        "初中一年级": 7, "初一": 7, "初中二年级": 8, "初二": 8,
        "初中三年级": 9, "初三": 9,
        "高中一年级": 10, "高一": 10, "高中二年级": 11, "高二": 11,
        "高中三年级": 12, "高三": 12,
    }

    if grade_str in grade_map:
        return grade_map[grade_str]

    # 尝试直接转换为整数
    try:
        return int(grade_str)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效的年级格式: {grade_str}")


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

    # 转换grade为整数
    grade_int = _parse_grade(req.grade)

    province = req.province
    city = req.city
    district = req.district
    if province and city and district:
        region_str = f"{province} {city} {district}"
    elif req.region:
        region_str = req.region
    else:
        region_str = ""
    catalog = await _generate_subject_catalog(grade_int, region_str)

    if profile:
        profile.grade = grade_int
        profile.province = province
        profile.city = city
        profile.district = district
        profile.region = region_str
        profile.ai_name = req.ai_name
        profile.ai_voice = req.ai_voice
        profile.ai_speed = req.ai_speed
        profile.subject_catalog = catalog
    else:
        profile = StudentProfile(
            user_id=user.id,
            grade=grade_int,
            province=province,
            city=city,
            district=district,
            region=region_str,
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

        # 使用asyncio.wait_for设置超时，避免阻塞太久
        import asyncio
        result = await asyncio.wait_for(
            ai_service._chat_json(system_prompt, user_prompt),
            timeout=25.0  # 25秒超时
        )
        return result
    except asyncio.TimeoutError:
        # 超时返回空目录
        return {"subjects": []}
    except Exception:
        return {"subjects": []}

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/tts", tags=["tts"])


class VoiceOption(BaseModel):
    """TTS声音选项"""
    id: str
    name: str
    gender: str
    language: str
    description: str


# 腾讯云TTS标准音色列表
# 参考: https://cloud.tencent.com/document/product/1073/37995
TENCENT_VOICES = [
    # 中文女声
    VoiceOption(
        id="101001",
        name="智瑜",
        gender="female",
        language="zh-CN",
        description="温柔女声，音色柔和亲切"
    ),
    VoiceOption(
        id="101002",
        name="智聆",
        gender="female",
        language="zh-CN",
        description="通用女声，清晰自然"
    ),
    VoiceOption(
        id="101003",
        name="智美",
        gender="female",
        language="zh-CN",
        description="客服女声，专业亲和"
    ),
    VoiceOption(
        id="101004",
        name="智云",
        gender="female",
        language="zh-CN",
        description="活力女声，年轻有活力"
    ),
    VoiceOption(
        id="101005",
        name="智莉",
        gender="female",
        language="zh-CN",
        description="温暖女声，温柔体贴"
    ),
    VoiceOption(
        id="101006",
        name="智言",
        gender="female",
        language="zh-CN",
        description="情感女声，富有感染力"
    ),
    VoiceOption(
        id="101007",
        name="智娜",
        gender="female",
        language="zh-CN",
        description="客服女声，专业标准"
    ),
    VoiceOption(
        id="101008",
        name="智琪",
        gender="female",
        language="zh-CN",
        description="新闻女声，播音腔调"
    ),
    VoiceOption(
        id="101009",
        name="智芸",
        gender="female",
        language="zh-CN",
        description="知性女声，成熟稳重"
    ),
    VoiceOption(
        id="101010",
        name="智华",
        gender="female",
        language="zh-CN",
        description="通用女声，标准普通话"
    ),
    # 中文男声
    VoiceOption(
        id="101011",
        name="智刚",
        gender="male",
        language="zh-CN",
        description="沉稳男声，浑厚有力"
    ),
    VoiceOption(
        id="101012",
        name="智瑞",
        gender="male",
        language="zh-CN",
        description="通用男声，清晰自然"
    ),
    VoiceOption(
        id="101013",
        name="智博",
        gender="male",
        language="zh-CN",
        description="客服男声，专业亲和"
    ),
    VoiceOption(
        id="101014",
        name="智向",
        gender="male",
        language="zh-CN",
        description="开朗男声，阳光活力"
    ),
    VoiceOption(
        id="101015",
        name="智安",
        gender="male",
        language="zh-CN",
        description="温和男声，温暖亲切"
    ),
    VoiceOption(
        id="101016",
        name="智飞",
        gender="male",
        language="zh-CN",
        description="情感男声，富有感染力"
    ),
    VoiceOption(
        id="101017",
        name="智彦",
        gender="male",
        language="zh-CN",
        description="新闻男声，播音腔调"
    ),
    VoiceOption(
        id="101018",
        name="智宇",
        gender="male",
        language="zh-CN",
        description="通用男声，标准普通话"
    ),
]


@router.get("/voices", response_model=List[VoiceOption])
async def get_voices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取可用的TTS声音列表

    返回腾讯云TTS支持的所有标准音色
    """
    return TENCENT_VOICES

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
import httpx
import os

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


# 学习助手声音列表
TENCENT_VOICES = [
    # 女老师
    VoiceOption(
        id="0",
        name="宁老师",
        gender="female",
        language="zh-CN",
        description="温柔耐心，擅长鼓励引导"
    ),
    VoiceOption(
        id="5",
        name="安老师",
        gender="female",
        language="zh-CN",
        description="温和亲切，善于倾听"
    ),
    VoiceOption(
        id="7",
        name="欣老师",
        gender="female",
        language="zh-CN",
        description="富有感染力，生动有趣"
    ),
    VoiceOption(
        id="1001",
        name="瑜老师",
        gender="female",
        language="zh-CN",
        description="声音柔和，讲解细致"
    ),
    VoiceOption(
        id="1002",
        name="聆老师",
        gender="female",
        language="zh-CN",
        description="吐字清晰，表达自然"
    ),
    VoiceOption(
        id="1003",
        name="美老师",
        gender="female",
        language="zh-CN",
        description="专业标准，条理清楚"
    ),
    # 男老师
    VoiceOption(
        id="1",
        name="希老师",
        gender="male",
        language="zh-CN",
        description="年轻有活力，富有激情"
    ),
    VoiceOption(
        id="2",
        name="晚老师",
        gender="male",
        language="zh-CN",
        description="成熟稳重，知识渊博"
    ),
    VoiceOption(
        id="3",
        name="刚老师",
        gender="male",
        language="zh-CN",
        description="清晰明亮，思路清晰"
    ),
    VoiceOption(
        id="6",
        name="叶老师",
        gender="male",
        language="zh-CN",
        description="专业亲和，循循善诱"
    ),
]


@router.get("/voices", response_model=List[VoiceOption])
async def get_voices():
    """
    获取可用的TTS声音列表

    返回腾讯云TTS支持的所有标准音色
    """
    return TENCENT_VOICES


@router.get("/preview/{voice_id}")
async def preview_voice(voice_id: str):
    """
    试听指定声音

    调用腾讯云TTS API生成音频并返回
    """
    # 查找声音
    voice = next((v for v in TENCENT_VOICES if v.id == voice_id), None)
    if not voice:
        raise HTTPException(status_code=404, detail="声音不存在")

    # 试听文本
    text = f"你好，我是{voice.name}，{voice.description}"

    return _generate_tts_audio(voice_id, text)


@router.get("/speak")
async def speak_text(voice_id: str, text: str):
    """
    使用指定声音朗读文本

    调用腾讯云TTS API生成音频并返回
    """
    # 查找声音
    voice = next((v for v in TENCENT_VOICES if v.id == voice_id), None)
    if not voice:
        raise HTTPException(status_code=404, detail="声音不存在")

    if not text or len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="文本不能为空")

    return _generate_tts_audio(voice_id, text)


def _generate_tts_audio(voice_id: str, text: str):
    """
    生成TTS音频的通用方法
    """
    # 调用腾讯云TTS API
    try:
        secret_id = os.getenv("TENCENT_SECRET_ID")
        secret_key = os.getenv("TENCENT_SECRET_KEY")

        if not secret_id or not secret_key:
            raise HTTPException(status_code=500, detail="TTS服务未配置")

        # 使用腾讯云TTS SDK
        from tencentcloud.common import credential
        from tencentcloud.tts.v20190823 import tts_client, models

        cred = credential.Credential(secret_id, secret_key)
        client = tts_client.TtsClient(cred, "ap-guangzhou")

        req = models.TextToVoiceRequest()
        req.Text = text
        req.SessionId = f"tts_{voice_id}_{hash(text)}"
        req.VoiceType = int(voice_id)
        req.Codec = "mp3"
        req.SampleRate = 16000

        resp = client.TextToVoice(req)

        # 返回音频数据
        import base64
        audio_data = base64.b64decode(resp.Audio)

        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"inline; filename=tts_{voice_id}.mp3"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS生成失败: {str(e)}")


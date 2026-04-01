"""声网Agora视频通话Token生成服务"""

import hashlib
import hmac
import time
import struct

from app.core.config import get_settings

settings = get_settings()


class AgoraService:
    """生成Agora RTC Token用于视频通话"""

    def __init__(self):
        self.app_id = settings.AGORA_APP_ID
        self.app_certificate = settings.AGORA_APP_CERTIFICATE

    def generate_token(self, channel_name: str, uid: int, expire_seconds: int = 3600) -> str:
        """
        生成简易Token。
        生产环境建议使用 agora-token 官方SDK。
        """
        if not self.app_id or not self.app_certificate:
            return ""

        timestamp = int(time.time()) + expire_seconds
        raw = f"{self.app_id}{channel_name}{uid}{timestamp}{self.app_certificate}"
        token = hashlib.sha256(raw.encode()).hexdigest()

        return f"{self.app_id}:{token}:{timestamp}:{uid}"


agora_service = AgoraService()

"""数据同步服务 — 通过WebSocket向双端推送实时消息"""

import json
from datetime import datetime, timezone


class SyncService:
    def __init__(self):
        from app.websocket.manager import connection_manager
        self._manager = connection_manager

    async def notify_student(self, user_id: int, event_type: str, payload: dict):
        await self._manager.send_to_device(
            user_id,
            "student_ipad",
            {
                "type": event_type,
                "payload": payload,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sender_device": "parent_android",
            },
        )

    async def notify_parent(self, user_id: int, event_type: str, payload: dict):
        await self._manager.send_to_device(
            user_id,
            "parent_android",
            {
                "type": event_type,
                "payload": payload,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sender_device": "student_ipad",
            },
        )

    async def broadcast_to_user(self, user_id: int, event_type: str, payload: dict):
        await self._manager.send_to_user(
            user_id,
            {
                "type": event_type,
                "payload": payload,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sender_device": "server",
            },
        )


sync_service = SyncService()

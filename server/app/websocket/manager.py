import json
from fastapi import WebSocket


class ConnectionManager:
    """WebSocket连接管理器 — 管理双端实时通信"""

    def __init__(self):
        # {user_id: {device_type: WebSocket}}
        self.active_connections: dict[int, dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, device_type: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}

        old = self.active_connections[user_id].get(device_type)
        if old:
            try:
                await old.close(code=4001, reason="新设备已连接")
            except Exception:
                pass

        self.active_connections[user_id][device_type] = websocket

        peer = "parent_android" if device_type == "student_ipad" else "student_ipad"
        peer_ws = self.active_connections[user_id].get(peer)
        if peer_ws:
            try:
                await peer_ws.send_json({
                    "type": "device_online",
                    "payload": {"device_type": device_type},
                })
            except Exception:
                pass

    def disconnect(self, user_id: int, device_type: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].pop(device_type, None)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_to_device(self, user_id: int, device_type: str, message: dict):
        ws = self.active_connections.get(user_id, {}).get(device_type)
        if ws:
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(user_id, device_type)

    async def send_to_user(self, user_id: int, message: dict):
        connections = self.active_connections.get(user_id, {})
        for device_type, ws in list(connections.items()):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(user_id, device_type)

    def is_online(self, user_id: int, device_type: str) -> bool:
        return device_type in self.active_connections.get(user_id, {})


connection_manager = ConnectionManager()

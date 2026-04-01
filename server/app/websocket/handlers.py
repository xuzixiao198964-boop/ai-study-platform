import json

from fastapi import WebSocket, WebSocketDisconnect, Depends
from jose import JWTError, jwt

from app.core.config import get_settings
from app.websocket.manager import connection_manager

settings = get_settings()


async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket入口：ws://host/ws?token=xxx&device_type=student_ipad

    消息协议:
    {
        "type": "screen_share" | "annotation" | "voice_cmd" | "remote_cmd" | "chat" | "ping",
        "payload": { ... },
        "target_device": "student_ipad" | "parent_android" | "all"
    }
    """
    token = websocket.query_params.get("token")
    device_type = websocket.query_params.get("device_type", "student_ipad")

    if not token:
        await websocket.close(code=4000, reason="缺少token")
        return

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub", 0))
        if not user_id:
            await websocket.close(code=4001, reason="无效token")
            return
    except JWTError:
        await websocket.close(code=4001, reason="token验证失败")
        return

    await connection_manager.connect(websocket, user_id, device_type)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "payload": {"message": "无效的JSON"}})
                continue

            msg_type = message.get("type", "")
            target = message.get("target_device", "all")
            msg_payload = message.get("payload", {})

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            outgoing = {
                "type": msg_type,
                "payload": msg_payload,
                "sender_device": device_type,
            }

            if target == "all":
                await connection_manager.send_to_user(user_id, outgoing)
            else:
                await connection_manager.send_to_device(user_id, target, outgoing)

    except WebSocketDisconnect:
        connection_manager.disconnect(user_id, device_type)
        peer = "parent_android" if device_type == "student_ipad" else "student_ipad"
        await connection_manager.send_to_device(user_id, peer, {
            "type": "device_offline",
            "payload": {"device_type": device_type},
        })

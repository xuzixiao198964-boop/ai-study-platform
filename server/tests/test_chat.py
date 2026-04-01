"""TC-CHAT-xxx: 对话与场景切换（Mock DeepSeek）"""
import pytest


@pytest.mark.asyncio
async def test_chat_scene_switch_keywords(monkeypatch):
    from app.services.chat_service import chat_service

    async def fake_chat(*_a, **_k):
        return "ignored"

    monkeypatch.setattr("app.services.chat_service.ai_service._chat", fake_chat)

    out = await chat_service.process_message(
        "我要开始做作业了", "chat", "小智", []
    )
    assert out["scene"] == "camera"
    assert out["scene_changed"] is True
    assert "摄像头" in out["reply"]

    out2 = await chat_service.process_message(
        "关掉摄像头吧", "camera", "小智", []
    )
    assert out2["scene"] == "chat"
    assert out2["scene_changed"] is True


@pytest.mark.asyncio
async def test_chat_message_persisted(client, unique_username, monkeypatch):
    async def fake_chat(*_a, **_k):
        return "这是模拟的 AI 回复"

    monkeypatch.setattr("app.services.chat_service.ai_service._chat", fake_chat)

    reg = await client.post(
        "/api/v1/auth/register",
        json={"username": unique_username, "password": "secret12"},
    )
    assert reg.status_code == 200
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    msg = await client.post(
        "/api/v1/chat/message",
        headers=headers,
        json={"content": "你好", "scene": "chat", "session_id": "s1"},
    )
    assert msg.status_code == 200, msg.text
    body = msg.json()
    assert "reply" in body
    assert body["scene"] == "chat"

    hist = await client.get(
        "/api/v1/chat/history/s1",
        headers=headers,
    )
    assert hist.status_code == 200
    rows = hist.json()
    assert len(rows) >= 2

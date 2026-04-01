import json
from app.services.ai_service import ai_service


SCENE_SWITCH_KEYWORDS_CAMERA = [
    "做作业", "写作业", "开始作业", "打开摄像头", "看试卷", "看卷子", "看书",
    "批改", "帮我看看", "拍照", "扫描",
]
SCENE_SWITCH_KEYWORDS_CHAT = [
    "关掉摄像头", "关闭摄像头", "做完了", "写完了", "不做了", "聊天", "聊聊天",
]


class ChatService:
    async def process_message(
        self, content: str, scene: str, ai_name: str, history: list[dict]
    ) -> dict:
        scene_result = await self._detect_scene_switch(content, scene)

        system_prompt = self._build_system_prompt(ai_name, scene_result["scene"])

        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-20:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": content})

        reply = await ai_service._chat(
            system_prompt,
            content if not history else self._build_context(history[-10:], content),
            temperature=0.7,
        )

        if scene_result["changed"]:
            if scene_result["scene"] == "camera":
                reply = f"好的，我帮你打开摄像头，把试卷放在镜头前吧！"
            else:
                reply = f"好的，摄像头已关闭。有什么想和我聊的吗？"

        return {
            "reply": reply,
            "message_type": "scene_switch" if scene_result["changed"] else "text",
            "scene": scene_result["scene"],
            "scene_changed": scene_result["changed"],
            "new_scene": scene_result["scene"] if scene_result["changed"] else None,
        }

    async def _detect_scene_switch(self, content: str, current_scene: str) -> dict:
        content_lower = content.lower()

        if current_scene == "chat":
            for kw in SCENE_SWITCH_KEYWORDS_CAMERA:
                if kw in content_lower:
                    return {"scene": "camera", "changed": True}

        if current_scene == "camera":
            for kw in SCENE_SWITCH_KEYWORDS_CHAT:
                if kw in content_lower:
                    return {"scene": "chat", "changed": True}

        return {"scene": current_scene, "changed": False}

    def _build_system_prompt(self, ai_name: str, scene: str) -> str:
        base = f"""你是一个名叫"{ai_name}"的K12学习AI助手。你正在和一个小学/初中/高中生进行语音对话。

基本规则：
- 用你的名字"{ai_name}"自称
- 说话语气亲切友好，像一个耐心的大哥哥/大姐姐
- 回答要简洁口语化，因为会被语音合成播放出来
- 避免过长的段落，适合语音朗读的长度
- 如果学生问题不清楚，友好地追问"""

        if scene == "camera":
            base += """

当前处于摄像头模式（作业辅导）：
- 学生正在做作业，你可以看到试卷画面
- 如果学生指着题目问你，先确认："你想让我教你解这道题吗？"
- 得到肯定回答后再开始讲解
- 讲解要通俗易懂，步骤清晰"""

        return base

    def _build_context(self, history: list[dict], current: str) -> str:
        ctx_parts = []
        for msg in history:
            role = "学生" if msg["role"] == "user" else "AI"
            ctx_parts.append(f"{role}: {msg['content']}")
        ctx_parts.append(f"学生: {current}")
        return "\n".join(ctx_parts)


chat_service = ChatService()

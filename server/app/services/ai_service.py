import json
import httpx

from app.core.config import get_settings

settings = get_settings()

DEEPSEEK_HEADERS = {
    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
    "Content-Type": "application/json",
}


class AIService:
    def __init__(self):
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.chat_model = "deepseek-chat"
        self.vision_model = "deepseek-chat"

    async def _chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers=DEEPSEEK_HEADERS,
                json={
                    "model": self.chat_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": temperature,
                    "max_tokens": 4096,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def _chat_with_image(
        self, system_prompt: str, text_prompt: str, image_base64: str, temperature: float = 0.3
    ) -> str:
        """DeepSeek Vision 多模态调用：文本 + 图片"""
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers=DEEPSEEK_HEADERS,
                json={
                    "model": self.vision_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": text_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_base64}"
                                    },
                                },
                            ],
                        },
                    ],
                    "temperature": temperature,
                    "max_tokens": 4096,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    def _parse_json(self, raw: str) -> dict | list:
        raw = raw.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        return json.loads(raw.strip())

    async def _chat_json(self, system_prompt: str, user_prompt: str) -> dict:
        raw = await self._chat(system_prompt, user_prompt)
        return self._parse_json(raw)

    async def _vision_json(self, system_prompt: str, text_prompt: str, image_base64: str) -> dict:
        raw = await self._chat_with_image(system_prompt, text_prompt, image_base64)
        return self._parse_json(raw)

    # ==================== OCR：图片识别试题 ====================

    async def recognize_questions(self, image_base64: str) -> dict:
        """DeepSeek Vision 一步完成：OCR识别 + 试题结构化解析"""
        system_prompt = """你是一个K12教育试题识别专家。请仔细看这张试题图片，完成以下任务：
1. 识别图片中所有文字（包括印刷体和手写体）
2. 区分题目内容和学生手写的答案
3. 将每道题解析为结构化数据

返回严格的JSON格式：
{
    "raw_text": "图片中所有识别出的文字（按从上到下顺序拼接）",
    "questions": [
        {
            "sequence_no": 1,
            "question_text": "题目完整内容（不含学生答案）",
            "student_answer": "学生写的答案（如有手写答案则提取，没有则为空字符串）",
            "question_type": "choice/fill_blank/calculation/application/short_answer/other",
            "subject": "math/chinese/english/physics/chemistry/biology/other",
            "has_figure": false
        }
    ],
    "regions": [
        {
            "index": 0,
            "text": "该区域的文字",
            "bbox": {"left": 0.0, "top": 0.0, "width": 0.5, "height": 0.1}
        }
    ]
}

注意：
- bbox使用归一化坐标（0.0~1.0），表示文字区域在图片中的相对位置
- 如果有数学公式，用LaTeX格式表示
- 准确区分题目编号（如"1."、"（1）"、"第一题"等）
- 手写内容用学生答案字段记录"""

        text_prompt = "请识别这张试题图片中的所有内容，按要求返回结构化JSON。"

        result = await self._vision_json(system_prompt, text_prompt, image_base64)

        if "questions" not in result:
            result["questions"] = []
        if "raw_text" not in result:
            result["raw_text"] = ""
        if "regions" not in result:
            result["regions"] = []

        return result

    # ==================== AI批改 ====================

    async def correct_question(self, question) -> dict:
        system_prompt = """你是一个K12教育AI助手，专门负责批改学生试题。
请根据题目内容和学生答案进行批改，返回JSON格式：
{
    "status": "correct/incorrect/partial",
    "is_correct": true/false,
    "score": 0-100,
    "standard_answer": "标准答案",
    "solution_steps": "详细解题步骤",
    "explanation": "简要说明",
    "error_reason": "calculation_error/misread_question/concept_confusion/formula_error/missing_steps/logic_error/other 或 null",
    "error_analysis": "错因详细分析",
    "knowledge_points": ["知识点1", "知识点2"],
    "ai_confidence": 0.0-1.0
}"""
        user_prompt = f"""题目内容：{question.question_text}
学生答案：{question.student_answer}
科目：{question.subject}
题型：{question.question_type}
OCR原始识别：{question.ocr_raw_text}"""

        return await self._chat_json(system_prompt, user_prompt)

    async def correct_question_with_image(self, image_base64: str, question_text: str = "") -> dict:
        """直接看图片批改，无需预先OCR"""
        system_prompt = """你是一个K12教育AI助手。请看这张试题图片，识别题目和学生的作答，然后进行批改。
返回JSON格式：
{
    "question_text": "识别出的题目内容",
    "student_answer": "识别出的学生答案",
    "status": "correct/incorrect/partial",
    "is_correct": true/false,
    "score": 0-100,
    "standard_answer": "标准答案",
    "solution_steps": "详细解题步骤",
    "explanation": "简要说明",
    "error_reason": "calculation_error/misread_question/concept_confusion/formula_error/missing_steps/logic_error/other 或 null",
    "error_analysis": "错因详细分析",
    "knowledge_points": ["知识点1", "知识点2"],
    "ai_confidence": 0.0-1.0
}"""
        text = "请识别并批改这道试题。"
        if question_text:
            text += f"\n补充信息：{question_text}"

        return await self._vision_json(system_prompt, text, image_base64)

    # ==================== AI讲解 ====================

    async def explain_question(self, question) -> dict:
        system_prompt = """你是一个K12教育AI讲师，请为学生讲解题目。
语言要通俗易懂、步骤清晰、不超纲。返回JSON格式：
{
    "explanation_text": "完整讲解内容",
    "solution_steps": "分步骤解题过程",
    "knowledge_points": ["涉及的知识点"],
    "tips": ["易错点提醒"]
}"""
        user_prompt = f"""题目：{question.question_text}
科目：{question.subject}
题型：{question.question_type}"""

        return await self._chat_json(system_prompt, user_prompt)

    # ==================== 错因分析 ====================

    async def analyze_error(self, question, correction) -> dict:
        system_prompt = """你是一个K12教育分析师，请对学生的错题进行深入分析。返回JSON格式：
{
    "error_analysis": "错因详细分析，包含为什么会犯这个错误、如何避免",
    "knowledge_tags": ["知识点标签1", "知识点标签2"],
    "difficulty": 1-5,
    "improvement_suggestions": "改进建议"
}"""
        user_prompt = f"""题目：{question.question_text}
学生答案：{question.student_answer}
正确答案：{correction.standard_answer}
错误类型：{correction.error_reason}
科目：{question.subject}"""

        return await self._chat_json(system_prompt, user_prompt)

    # ==================== 相似题生成 ====================

    async def generate_similar_questions(self, question, count: int = 3) -> list[dict]:
        system_prompt = f"""你是一个K12教育出题专家。请生成{count}道与原题同知识点、同难度、同题型的相似练习题。
题目贴合教材考纲，无重复、无超纲。返回JSON数组格式：
[
    {{
        "question_text": "题目内容",
        "correct_answer": "正确答案",
        "solution_steps": "解题步骤",
        "knowledge_points": ["知识点"],
        "difficulty": 1-5
    }}
]"""
        user_prompt = f"""原题：{question.question_text}
科目：{question.subject}
题型：{question.question_type}
知识点：{question.knowledge_points}"""

        raw = await self._chat(system_prompt, user_prompt)
        return self._parse_json(raw)


ai_service = AIService()

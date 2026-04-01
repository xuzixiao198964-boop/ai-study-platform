"""OCR服务 — 基于DeepSeek Vision多模态识别

直接将试题图片发给DeepSeek，一步完成：
1. 文字识别（印刷体+手写体）
2. 数学公式识别
3. 试题结构化解析（题型、科目、题目、学生答案）
"""


class OCRService:
    """DeepSeek Vision 多模态OCR — 替代传统OCR API"""

    async def recognize(self, image_base64: str, detect_handwriting: bool = True) -> dict:
        from app.services.ai_service import ai_service
        return await ai_service.recognize_questions(image_base64)


ocr_service = OCRService()

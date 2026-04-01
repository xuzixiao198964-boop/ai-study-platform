"""手指指认服务 — 检测手指位置并映射到题目区域

端侧(Flutter)使用 MediaPipe 检测手指关键点，将指尖坐标发送到服务器。
服务器负责将指尖坐标与题目区域进行匹配。
"""

import base64
import numpy as np


class FingerService:

    FINGERTIP_DWELL_THRESHOLD = 1.0  # seconds

    async def detect_and_map(
        self, image_base64: str, question_regions: list[dict]
    ) -> dict:
        """
        接收端侧传来的指尖坐标或图片，匹配题目区域。

        question_regions 格式:
        [
            {
                "question_id": 1,
                "bbox": {"left": 100, "top": 200, "width": 500, "height": 100}
            },
            ...
        ]
        """
        finger_data = self._extract_finger_from_payload(image_base64)

        if not finger_data.get("detected"):
            return {
                "detected": False,
                "finger_tip_x": None,
                "finger_tip_y": None,
                "pointed_question_id": None,
                "pointed_region": None,
                "confidence": 0.0,
            }

        tip_x = finger_data["tip_x"]
        tip_y = finger_data["tip_y"]

        matched = self._match_region(tip_x, tip_y, question_regions)

        return {
            "detected": True,
            "finger_tip_x": tip_x,
            "finger_tip_y": tip_y,
            "pointed_question_id": matched.get("question_id") if matched else None,
            "pointed_region": matched.get("bbox") if matched else None,
            "confidence": matched.get("confidence", 0.0) if matched else 0.0,
        }

    def _extract_finger_from_payload(self, payload: str) -> dict:
        """
        payload 可以是:
        1. JSON字符串包含指尖坐标（端侧已检测）: "tip_x:0.5,tip_y:0.3"
        2. base64图片（需要服务端检测，备用方案）
        """
        if payload.startswith("tip_x:"):
            parts = payload.split(",")
            tip_x = float(parts[0].split(":")[1])
            tip_y = float(parts[1].split(":")[1])
            return {"detected": True, "tip_x": tip_x, "tip_y": tip_y}

        # 备用：服务端MediaPipe检测（通常在端侧完成以减少延迟）
        try:
            return self._detect_finger_server_side(payload)
        except Exception:
            return {"detected": False}

    def _detect_finger_server_side(self, image_base64: str) -> dict:
        """服务端MediaPipe手指检测（备用方案，优先使用端侧检测）"""
        try:
            import mediapipe as mp

            image_bytes = base64.b64decode(image_base64)
            nparr = np.frombuffer(image_bytes, np.uint8)

            import cv2
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                return {"detected": False}

            mp_hands = mp.solutions.hands
            with mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=1,
                min_detection_confidence=0.7,
            ) as hands:
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb)

                if not results.multi_hand_landmarks:
                    return {"detected": False}

                hand = results.multi_hand_landmarks[0]
                index_tip = hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                return {
                    "detected": True,
                    "tip_x": index_tip.x,
                    "tip_y": index_tip.y,
                }
        except ImportError:
            return {"detected": False}

    def _match_region(
        self, tip_x: float, tip_y: float, regions: list[dict]
    ) -> dict | None:
        """将归一化坐标的指尖位置匹配到最近的题目区域"""
        best_match = None
        best_distance = float("inf")

        for region in regions:
            bbox = region.get("bbox", {})
            left = bbox.get("left", 0)
            top = bbox.get("top", 0)
            width = bbox.get("width", 0)
            height = bbox.get("height", 0)

            center_x = left + width / 2
            center_y = top + height / 2

            if left <= tip_x <= left + width and top <= tip_y <= top + height:
                dist = ((tip_x - center_x) ** 2 + (tip_y - center_y) ** 2) ** 0.5
                if dist < best_distance:
                    best_distance = dist
                    best_match = {
                        "question_id": region.get("question_id"),
                        "bbox": bbox,
                        "confidence": max(0.5, 1.0 - dist / max(width, height, 1)),
                    }

        return best_match


finger_service = FingerService()

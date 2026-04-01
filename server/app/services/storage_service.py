import os
import uuid
from datetime import datetime

import aiofiles
from fastapi import UploadFile

from app.core.config import get_settings

settings = get_settings()


class StorageService:
    """文件存储服务 — 支持本地存储和MinIO"""

    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    async def upload_file(self, file: UploadFile, prefix: str = "") -> str:
        ext = os.path.splitext(file.filename or "image.jpg")[1]
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{uuid.uuid4().hex}{ext}"
        rel_path = os.path.join(prefix, date_str, filename)
        full_path = os.path.join(self.upload_dir, rel_path)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        async with aiofiles.open(full_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        return f"/static/uploads/{rel_path}"

    async def upload_base64(self, base64_data: str, prefix: str = "", ext: str = ".jpg") -> str:
        import base64

        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{uuid.uuid4().hex}{ext}"
        rel_path = os.path.join(prefix, date_str, filename)
        full_path = os.path.join(self.upload_dir, rel_path)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        image_bytes = base64.b64decode(base64_data)
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(image_bytes)

        return f"/static/uploads/{rel_path}"


storage_service = StorageService()

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/ai_study"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 2880  # 48 hours

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    AGORA_APP_ID: str = ""
    AGORA_APP_CERTIFICATE: str = ""

    # 火山引擎 STT
    VOLCANO_APP_ID: str = ""
    VOLCANO_ACCESS_KEY: str = ""
    VOLCANO_SECRET_KEY: str = ""

    # 腾讯云 TTS
    TENCENT_SECRET_ID: str = ""
    TENCENT_SECRET_KEY: str = ""

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "ai-study"

    UPLOAD_DIR: str = "./static/uploads"

    ADMIN_USERNAME: str = "wsxzx"
    ADMIN_PASSWORD: str = "Xuzi-xiao198964"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reload_settings():
    """Clear cached settings so next call re-reads .env"""
    get_settings.cache_clear()

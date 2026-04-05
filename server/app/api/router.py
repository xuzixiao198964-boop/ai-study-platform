from fastapi import APIRouter

from app.api.endpoints import (
    auth, questions, error_books, permissions, sync, study_records,
    chat, initialization, admin, regions, developer, tts,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(questions.router)
api_router.include_router(error_books.router)
api_router.include_router(permissions.router)
api_router.include_router(sync.router)
api_router.include_router(study_records.router)
api_router.include_router(chat.router)
api_router.include_router(initialization.router)
api_router.include_router(admin.router)
api_router.include_router(regions.router)
api_router.include_router(tts.router)
api_router.include_router(developer.router, prefix="/developer", tags=["developer"])

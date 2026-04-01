from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.websocket.handlers import websocket_endpoint
from app.core.redis import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_redis()


app = FastAPI(
    title="学习指认AI平台",
    description="K12学习辅导 — 学生端(iPad) + 家长端(Android) 双端协同",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router)

app.add_api_websocket_route("/ws", websocket_endpoint)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ai-study-platform"}

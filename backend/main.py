"""FastAPI アプリケーションエントリーポイント"""

import logging
import signal
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.api import api_router

logger = logging.getLogger(__name__)


# グレースフルシャットダウン
shutdown_flag = False


def handle_sigterm(*args):
    global shutdown_flag
    shutdown_flag = True
    print("SIGTERM received, shutting down gracefully...")
    sys.exit(0)


signal.signal(signal.SIGTERM, handle_sigterm)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル"""
    # 起動時
    print(f"Starting {settings.app_name}...")
    yield
    # 終了時
    print("Shutting down...")


# FastAPI アプリケーション
app = FastAPI(
    title=settings.app_name,
    description="勤怠異常検知・是正理由作成システム API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3847",
        "http://127.0.0.1:3847",
        "https://kintai-sensei.vercel.app",
        "https://kintai-sensei-*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# グローバル例外ハンドラ（トレースバック漏洩防止）
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s %s - %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "サーバー内部エラーが発生しました。しばらく経ってからお試しください。"},
    )


# APIルーター登録
app.include_router(api_router, prefix="/api")


@app.get("/api/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy", "app": settings.app_name}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8634,
        reload=settings.debug,
    )

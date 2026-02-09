"""APIルーター"""

from fastapi import APIRouter

from src.api import auth, users, stores, attendance, issues, reports, settings, billing


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["認証"])
api_router.include_router(users.router, prefix="/users", tags=["ユーザー"])
api_router.include_router(stores.router, prefix="/stores", tags=["店舗"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["勤怠"])
api_router.include_router(issues.router, prefix="/issues", tags=["異常"])
api_router.include_router(reports.router, prefix="/reports", tags=["レポート"])
api_router.include_router(settings.router, prefix="/settings", tags=["設定"])
api_router.include_router(billing.router, prefix="/billing", tags=["課金"])

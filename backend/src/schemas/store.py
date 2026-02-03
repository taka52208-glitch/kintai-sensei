"""店舗スキーマ"""

from datetime import datetime

from pydantic import BaseModel


class StoreResponse(BaseModel):
    """店舗レスポンス"""
    id: str
    code: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class StoreCreate(BaseModel):
    """店舗作成"""
    code: str
    name: str


class StoreUpdate(BaseModel):
    """店舗更新"""
    code: str | None = None
    name: str | None = None


class StoreListResponse(BaseModel):
    """店舗一覧レスポンス"""
    items: list[StoreResponse]
    total: int

"""店舗スキーマ"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelCaseModel(BaseModel):
    """camelCase出力用の基底クラス"""
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )


class StoreResponse(CamelCaseModel):
    """店舗レスポンス"""
    id: str
    code: str
    name: str
    created_at: datetime


class StoreCreate(BaseModel):
    """店舗作成"""
    code: str
    name: str


class StoreUpdate(BaseModel):
    """店舗更新"""
    code: str | None = None
    name: str | None = None


class StoreListResponse(CamelCaseModel):
    """店舗一覧レスポンス"""
    items: list[StoreResponse]
    total: int

"""ユーザースキーマ"""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    """ユーザーレスポンス"""
    id: str
    email: str
    name: str
    role: str
    store_id: str | None
    store_name: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """ユーザー作成"""
    email: EmailStr
    password: str
    name: str
    role: str = "store_manager"
    store_id: str | None = None


class UserUpdate(BaseModel):
    """ユーザー更新"""
    role: str | None = None
    store_id: str | None = None
    is_active: bool | None = None


class UserInvite(BaseModel):
    """ユーザー招待"""
    email: EmailStr
    role: str = "store_manager"
    store_id: str | None = None


class InviteResponse(BaseModel):
    """招待レスポンス（仮パスワード付き）"""
    user: UserResponse
    temporary_password: str
    message: str = "招待が完了しました。以下の仮パスワードをユーザーにお伝えください。"


class UserListResponse(BaseModel):
    """ユーザー一覧レスポンス"""
    items: list[UserResponse]
    total: int
    page: int
    page_size: int

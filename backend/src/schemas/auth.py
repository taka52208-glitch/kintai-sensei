"""認証スキーマ"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """ログインリクエスト"""
    email: EmailStr
    password: str


class UserInfo(BaseModel):
    """ユーザー情報（トークンレスポンス用）"""
    id: str
    email: str
    name: str
    role: str
    store_id: str | None
    store_name: str | None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """ログインレスポンス"""
    access_token: str
    refresh_token: str
    user: UserInfo


class TokenRefreshResponse(BaseModel):
    """トークンリフレッシュレスポンス"""
    access_token: str

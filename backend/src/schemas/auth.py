"""認証スキーマ"""

from pydantic import BaseModel, EmailStr, field_validator


class LoginRequest(BaseModel):
    """ログインリクエスト"""
    email: EmailStr
    password: str


def _validate_password(v: str) -> str:
    """パスワード強度バリデーション"""
    if len(v) < 8:
        raise ValueError("パスワードは8文字以上必要です")
    if not any(c.isupper() for c in v):
        raise ValueError("パスワードに大文字を含めてください")
    if not any(c.isdigit() for c in v):
        raise ValueError("パスワードに数字を含めてください")
    return v


class SignupRequest(BaseModel):
    """サインアップリクエスト"""
    organization_name: str
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        return _validate_password(v)


class UserInfo(BaseModel):
    """ユーザー情報（トークンレスポンス用）"""
    id: str
    email: str
    name: str
    role: str
    store_id: str | None
    store_name: str | None

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    """ログインレスポンス"""
    access_token: str
    refresh_token: str
    user: UserInfo


class TokenRefreshRequest(BaseModel):
    """トークンリフレッシュリクエスト"""
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """トークンリフレッシュレスポンス"""
    access_token: str


class LogoutRequest(BaseModel):
    """ログアウトリクエスト"""
    access_token: str | None = None
    refresh_token: str | None = None


class ChangePasswordRequest(BaseModel):
    """パスワード変更リクエスト"""
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return _validate_password(v)

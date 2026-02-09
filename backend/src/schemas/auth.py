"""認証スキーマ"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """ログインリクエスト"""
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    """サインアップリクエスト"""
    organization_name: str
    name: str
    email: EmailStr
    password: str

    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("パスワードは8文字以上必要です")
        if not any(c.isupper() for c in v):
            raise ValueError("パスワードに大文字を含めてください")
        if not any(c.isdigit() for c in v):
            raise ValueError("パスワードに数字を含めてください")
        return v

    def model_post_init(self, __context: object) -> None:
        self.validate_password_strength(self.password)


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

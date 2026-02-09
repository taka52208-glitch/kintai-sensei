"""アプリケーション設定"""

import warnings
from functools import lru_cache
from pydantic_settings import BaseSettings

_INSECURE_DEFAULT_SECRET = "your-secret-key-change-in-production"


class Settings(BaseSettings):
    """環境変数から設定を読み込む"""

    # アプリケーション
    app_name: str = "勤怠チェック"
    debug: bool = False

    # データベース（デフォルトはSQLite）
    database_url: str = "sqlite+aiosqlite:///./kintai_check.db"

    # JWT認証
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # OpenAI API
    openai_api_key: str = ""

    # Stripe決済
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_standard: str = ""  # Standard プラン (300円/人)
    stripe_price_pro: str = ""       # Pro プラン (500円/人)

    # フロントエンドURL（Stripe決済のリダイレクト先）
    frontend_url: str = "https://kintai-sensei.vercel.app"

    # セキュリティ
    max_login_attempts: int = 5
    lockout_minutes: int = 15

    # 検知ルールのデフォルト
    default_break_minutes_6h: int = 45
    default_break_minutes_8h: int = 60
    default_daily_work_hours_alert: int = 10
    default_night_start_hour: int = 22
    default_night_end_hour: int = 5

    class Config:
        env_file = ".env.local"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """シングルトンで設定を取得"""
    s = Settings()
    if s.jwt_secret_key == _INSECURE_DEFAULT_SECRET:
        if s.debug:
            warnings.warn(
                "JWT_SECRET_KEY がデフォルト値です。本番環境では必ず変更してください。",
                stacklevel=2,
            )
        else:
            raise RuntimeError(
                "JWT_SECRET_KEY がデフォルト値のまま起動しています。"
                "環境変数 JWT_SECRET_KEY を設定してください。"
            )
    return s


settings = get_settings()

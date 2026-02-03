"""アプリケーション設定"""

from functools import lru_cache
from pydantic_settings import BaseSettings


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


@lru_cache
def get_settings() -> Settings:
    """シングルトンで設定を取得"""
    return Settings()


settings = get_settings()

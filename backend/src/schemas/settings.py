"""設定スキーマ"""

from pydantic import BaseModel


class DetectionRuleResponse(BaseModel):
    """検知ルールレスポンス"""
    break_minutes_6h: int
    break_minutes_8h: int
    daily_work_hours_alert: int
    night_start_hour: int
    night_end_hour: int

    class Config:
        from_attributes = True


class DetectionRuleUpdate(BaseModel):
    """検知ルール更新"""
    break_minutes_6h: int | None = None
    break_minutes_8h: int | None = None
    daily_work_hours_alert: int | None = None
    night_start_hour: int | None = None
    night_end_hour: int | None = None

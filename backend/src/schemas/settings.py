"""設定スキーマ"""

from pydantic import BaseModel, ConfigDict, field_validator


class DetectionRuleResponse(BaseModel):
    """検知ルールレスポンス"""
    model_config = ConfigDict(from_attributes=True)

    break_minutes_6h: int
    break_minutes_8h: int
    daily_work_hours_alert: int
    night_start_hour: int
    night_end_hour: int


class DetectionRuleUpdate(BaseModel):
    """検知ルール更新"""
    break_minutes_6h: int | None = None
    break_minutes_8h: int | None = None
    daily_work_hours_alert: int | None = None
    night_start_hour: int | None = None
    night_end_hour: int | None = None

    @field_validator("break_minutes_6h", "break_minutes_8h")
    @classmethod
    def validate_break_minutes(cls, v: int | None) -> int | None:
        if v is not None and (v < 0 or v > 120):
            raise ValueError("休憩時間は0〜120分の範囲で指定してください")
        return v

    @field_validator("daily_work_hours_alert")
    @classmethod
    def validate_work_hours(cls, v: int | None) -> int | None:
        if v is not None and (v < 1 or v > 24):
            raise ValueError("勤務時間アラートは1〜24時間の範囲で指定してください")
        return v

    @field_validator("night_start_hour", "night_end_hour")
    @classmethod
    def validate_hour(cls, v: int | None) -> int | None:
        if v is not None and (v < 0 or v > 23):
            raise ValueError("時刻は0〜23の範囲で指定してください")
        return v


# テンプレート
class TemplateItem(BaseModel):
    """テンプレート1件"""
    model_config = ConfigDict(from_attributes=True)

    id: str | None = None
    template_type: str  # internal / employee / audit
    template_text: str


class TemplateListResponse(BaseModel):
    """テンプレート一覧"""
    templates: list[TemplateItem]


class TemplateUpdateRequest(BaseModel):
    """テンプレート更新"""
    templates: list[TemplateItem]


# 語彙辞書
class DictEntry(BaseModel):
    """語彙辞書1件"""
    model_config = ConfigDict(from_attributes=True)

    id: str | None = None
    original_word: str
    replacement_word: str


class DictListResponse(BaseModel):
    """語彙辞書一覧"""
    dictionary: list[DictEntry]


class DictUpdateRequest(BaseModel):
    """語彙辞書更新"""
    dictionary: list[DictEntry]

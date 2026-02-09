"""異常スキーマ"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelCaseModel(BaseModel):
    """camelCase出力用の基底クラス"""
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )


class AttendanceRecordResponse(CamelCaseModel):
    """勤怠レコードレスポンス"""
    id: str
    date: str
    clock_in: str | None
    clock_out: str | None
    break_minutes: int | None
    work_type: str | None


class IssueLogResponse(CamelCaseModel):
    """対応ログレスポンス"""
    id: str
    user_id: str
    user_name: str
    action: str
    memo: str | None
    created_at: datetime


class IssueResponse(CamelCaseModel):
    """異常レスポンス"""
    id: str
    attendance_record_id: str
    employee_id: str
    employee_name: str
    store_id: str
    store_name: str
    date: str
    type: str
    severity: str
    status: str
    rule_description: str
    detected_at: datetime
    attendance_record: AttendanceRecordResponse | None = None
    logs: list[IssueLogResponse] = []


class IssueListResponse(CamelCaseModel):
    """異常一覧レスポンス"""
    items: list[IssueResponse]
    total: int
    page: int
    page_size: int


class IssueUpdateRequest(BaseModel):
    """異常更新リクエスト"""
    status: str


class IssueLogCreate(BaseModel):
    """対応ログ作成"""
    action: str = Field(max_length=50)
    memo: str | None = Field(default=None, max_length=2000)


class GenerateReasonRequest(BaseModel):
    """是正理由文生成リクエスト"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
    template_type: str = Field(max_length=20)  # internal, employee, audit
    cause_category: str = Field(max_length=30)  # forgot_clock, device_issue, etc.
    cause_detail: str | None = Field(default=None, max_length=1000)
    action_taken: str = Field(max_length=30)  # correction_request, etc.
    prevention: str = Field(max_length=30)  # operation_notice, etc.


class GenerateReasonResponse(CamelCaseModel):
    """是正理由文生成レスポンス"""
    generated_text: str
    correction_reason_id: str

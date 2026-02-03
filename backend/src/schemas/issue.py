"""異常スキーマ"""

from datetime import datetime

from pydantic import BaseModel


class AttendanceRecordResponse(BaseModel):
    """勤怠レコードレスポンス"""
    id: str
    date: str
    clock_in: str | None
    clock_out: str | None
    break_minutes: int | None
    work_type: str | None

    class Config:
        from_attributes = True


class IssueLogResponse(BaseModel):
    """対応ログレスポンス"""
    id: str
    user_id: str
    user_name: str
    action: str
    memo: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class IssueResponse(BaseModel):
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

    class Config:
        from_attributes = True


class IssueListResponse(BaseModel):
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
    action: str
    memo: str | None = None


class GenerateReasonRequest(BaseModel):
    """是正理由文生成リクエスト"""
    template_type: str  # internal, employee, audit
    cause_category: str  # forgot_clock, device_issue, etc.
    cause_detail: str | None = None
    action_taken: str  # correction_request, etc.
    prevention: str  # operation_notice, etc.


class GenerateReasonResponse(BaseModel):
    """是正理由文生成レスポンス"""
    generated_text: str
    correction_reason_id: str

"""異常・是正モデル"""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Index, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class IssueType(str, Enum):
    """異常種別"""
    MISSING_CLOCK_IN = "missing_clock_in"
    MISSING_CLOCK_OUT = "missing_clock_out"
    INSUFFICIENT_BREAK = "insufficient_break"
    OVERTIME = "overtime"
    NIGHT_WORK = "night_work"
    INCONSISTENCY = "inconsistency"


class IssueSeverity(str, Enum):
    """重要度"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueStatus(str, Enum):
    """対応ステータス"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ReasonTemplateType(str, Enum):
    """理由文テンプレート種別"""
    INTERNAL = "internal"
    EMPLOYEE = "employee"
    AUDIT = "audit"


class CauseCategory(str, Enum):
    """原因カテゴリ"""
    FORGOT_CLOCK = "forgot_clock"
    DEVICE_ISSUE = "device_issue"
    WORK_REASON = "work_reason"
    APPLICATION_MISSING = "application_missing"
    OTHER = "other"


class ActionType(str, Enum):
    """対応種別"""
    CORRECTION_REQUEST = "correction_request"
    EMPLOYEE_CONFIRMATION = "employee_confirmation"
    OVERTIME_APPLICATION = "overtime_application"
    WARNING = "warning"
    ANNOUNCEMENT = "announcement"


class PreventionType(str, Enum):
    """再発防止種別"""
    OPERATION_NOTICE = "operation_notice"
    DEVICE_PLACEMENT = "device_placement"
    CHECKLIST = "checklist"
    DOUBLE_CHECK = "double_check"


class Issue(Base):
    """異常テーブル"""
    __tablename__ = "issues"
    __table_args__ = (
        Index("ix_issues_attendance", "attendance_record_id"),
        Index("ix_issues_status", "status"),
        Index("ix_issues_severity", "severity"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    attendance_record_id: Mapped[str] = mapped_column(String(36), ForeignKey("attendance_records.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    severity: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=IssueStatus.PENDING.value)
    rule_description: Mapped[str] = mapped_column(Text, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # リレーション
    attendance_record = relationship("AttendanceRecord", back_populates="issues")
    logs = relationship("IssueLog", back_populates="issue", cascade="all, delete-orphan")
    correction_reasons = relationship("CorrectionReason", back_populates="issue", cascade="all, delete-orphan")


class IssueLog(Base):
    """対応ログテーブル"""
    __tablename__ = "issue_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    issue_id: Mapped[str] = mapped_column(String(36), ForeignKey("issues.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # リレーション
    issue = relationship("Issue", back_populates="logs")
    user = relationship("User", back_populates="issue_logs")


class CorrectionReason(Base):
    """是正理由文テーブル"""
    __tablename__ = "correction_reasons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    issue_id: Mapped[str] = mapped_column(String(36), ForeignKey("issues.id"), nullable=False)
    template_type: Mapped[str] = mapped_column(String(20), nullable=False)
    cause_category: Mapped[str] = mapped_column(String(30), nullable=False)
    cause_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_taken: Mapped[str] = mapped_column(String(30), nullable=False)
    prevention: Mapped[str] = mapped_column(String(30), nullable=False)
    generated_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # リレーション
    issue = relationship("Issue", back_populates="correction_reasons")
    created_by_user = relationship("User", back_populates="correction_reasons")

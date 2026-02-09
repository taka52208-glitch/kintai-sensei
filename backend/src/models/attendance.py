"""勤怠レコードモデル"""

import uuid
from datetime import datetime, date, time, timezone

from sqlalchemy import Index, String, DateTime, Date, Time, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class AttendanceRecord(Base):
    """勤怠レコードテーブル"""
    __tablename__ = "attendance_records"
    __table_args__ = (
        Index("ix_attendance_employee_date", "employee_id", "date", unique=True),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id: Mapped[str] = mapped_column(String(36), ForeignKey("employees.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    clock_in: Mapped[time | None] = mapped_column(Time, nullable=True)
    clock_out: Mapped[time | None] = mapped_column(Time, nullable=True)
    break_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    work_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # リレーション
    employee = relationship("Employee", back_populates="attendance_records")
    issues = relationship("Issue", back_populates="attendance_record", cascade="all, delete-orphan")

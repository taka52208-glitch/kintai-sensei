"""ユーザーモデル"""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Index, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class UserRole(str, Enum):
    """ユーザーロール"""
    ADMIN = "admin"
    STORE_MANAGER = "store_manager"
    VIEWER = "viewer"


class User(Base):
    """ユーザーテーブル"""
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_org", "organization_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    store_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("stores.id"), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default=UserRole.STORE_MANAGER.value)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # リレーション
    organization = relationship("Organization", back_populates="users")
    store = relationship("Store", back_populates="users")
    issue_logs = relationship("IssueLog", back_populates="user")
    correction_reasons = relationship("CorrectionReason", back_populates="created_by_user")

    @property
    def role_enum(self) -> UserRole:
        return UserRole(self.role)

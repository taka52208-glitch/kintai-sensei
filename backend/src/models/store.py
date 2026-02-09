"""店舗・組織モデル"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class PlanType(str, Enum):
    """料金プラン"""
    FREE = "free"
    STANDARD = "standard"
    PRO = "pro"


class Organization(Base):
    """組織テーブル"""
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Stripe決済情報
    plan: Mapped[str] = mapped_column(String(20), default=PlanType.FREE.value, nullable=False)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employee_limit: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    stores = relationship("Store", back_populates="organization", cascade="all, delete-orphan")
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    employees = relationship("Employee", back_populates="organization", cascade="all, delete-orphan")
    detection_rules = relationship("DetectionRule", back_populates="organization", cascade="all, delete-orphan")
    reason_templates = relationship("ReasonTemplate", back_populates="organization", cascade="all, delete-orphan")
    vocabulary_dicts = relationship("VocabularyDict", back_populates="organization", cascade="all, delete-orphan")


class Store(Base):
    """店舗テーブル"""
    __tablename__ = "stores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    organization = relationship("Organization", back_populates="stores")
    users = relationship("User", back_populates="store")
    employees = relationship("Employee", back_populates="store")

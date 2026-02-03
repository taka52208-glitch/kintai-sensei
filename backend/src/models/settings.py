"""設定関連モデル"""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class DetectionRule(Base):
    """検知ルール設定テーブル"""
    __tablename__ = "detection_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    break_minutes_6h: Mapped[int] = mapped_column(Integer, default=45)
    break_minutes_8h: Mapped[int] = mapped_column(Integer, default=60)
    daily_work_hours_alert: Mapped[int] = mapped_column(Integer, default=10)
    night_start_hour: Mapped[int] = mapped_column(Integer, default=22)
    night_end_hour: Mapped[int] = mapped_column(Integer, default=5)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    organization = relationship("Organization", back_populates="detection_rules")


class ReasonTemplate(Base):
    """理由文テンプレートテーブル"""
    __tablename__ = "reason_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    template_type: Mapped[str] = mapped_column(String(20), nullable=False)
    template_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    organization = relationship("Organization", back_populates="reason_templates")


class VocabularyDict(Base):
    """語彙辞書テーブル"""
    __tablename__ = "vocabulary_dicts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    original_word: Mapped[str] = mapped_column(String(100), nullable=False)
    replacement_word: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # リレーション
    organization = relationship("Organization", back_populates="vocabulary_dicts")

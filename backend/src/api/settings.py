"""設定API"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.auth import CurrentUser, AdminUser
from src.models.settings import DetectionRule
from src.schemas.settings import DetectionRuleResponse, DetectionRuleUpdate
from src.config import settings as app_settings


router = APIRouter()


@router.get("/rules", response_model=DetectionRuleResponse)
async def get_rules(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """検知ルール取得"""
    result = await db.execute(
        select(DetectionRule)
        .where(DetectionRule.organization_id == current_user.organization_id)
    )
    rule = result.scalar_one_or_none()

    if rule is None:
        # デフォルト値を返す
        return DetectionRuleResponse(
            break_minutes_6h=app_settings.default_break_minutes_6h,
            break_minutes_8h=app_settings.default_break_minutes_8h,
            daily_work_hours_alert=app_settings.default_daily_work_hours_alert,
            night_start_hour=app_settings.default_night_start_hour,
            night_end_hour=app_settings.default_night_end_hour,
        )

    return DetectionRuleResponse(
        break_minutes_6h=rule.break_minutes_6h,
        break_minutes_8h=rule.break_minutes_8h,
        daily_work_hours_alert=rule.daily_work_hours_alert,
        night_start_hour=rule.night_start_hour,
        night_end_hour=rule.night_end_hour,
    )


@router.put("/rules", response_model=DetectionRuleResponse)
async def update_rules(
    request: DetectionRuleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """検知ルール更新（管理者のみ）"""
    result = await db.execute(
        select(DetectionRule)
        .where(DetectionRule.organization_id == current_user.organization_id)
    )
    rule = result.scalar_one_or_none()

    if rule is None:
        # 新規作成
        rule = DetectionRule(
            organization_id=current_user.organization_id,
            break_minutes_6h=request.break_minutes_6h or app_settings.default_break_minutes_6h,
            break_minutes_8h=request.break_minutes_8h or app_settings.default_break_minutes_8h,
            daily_work_hours_alert=request.daily_work_hours_alert or app_settings.default_daily_work_hours_alert,
            night_start_hour=request.night_start_hour or app_settings.default_night_start_hour,
            night_end_hour=request.night_end_hour or app_settings.default_night_end_hour,
        )
        db.add(rule)
    else:
        # 更新
        if request.break_minutes_6h is not None:
            rule.break_minutes_6h = request.break_minutes_6h
        if request.break_minutes_8h is not None:
            rule.break_minutes_8h = request.break_minutes_8h
        if request.daily_work_hours_alert is not None:
            rule.daily_work_hours_alert = request.daily_work_hours_alert
        if request.night_start_hour is not None:
            rule.night_start_hour = request.night_start_hour
        if request.night_end_hour is not None:
            rule.night_end_hour = request.night_end_hour

    await db.commit()
    await db.refresh(rule)

    return DetectionRuleResponse(
        break_minutes_6h=rule.break_minutes_6h,
        break_minutes_8h=rule.break_minutes_8h,
        daily_work_hours_alert=rule.daily_work_hours_alert,
        night_start_hour=rule.night_start_hour,
        night_end_hour=rule.night_end_hour,
    )


@router.get("/templates")
async def get_templates(current_user: AdminUser):
    """テンプレート取得"""
    # TODO: 実装
    return {"templates": []}


@router.put("/templates")
async def update_templates(current_user: AdminUser):
    """テンプレート更新"""
    # TODO: 実装
    return {"message": "updated"}


@router.get("/dictionary")
async def get_dictionary(current_user: AdminUser):
    """語彙辞書取得"""
    # TODO: 実装
    return {"dictionary": {}}


@router.put("/dictionary")
async def update_dictionary(current_user: AdminUser):
    """語彙辞書更新"""
    # TODO: 実装
    return {"message": "updated"}

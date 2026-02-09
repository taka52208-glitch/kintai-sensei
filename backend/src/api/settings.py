"""設定API"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.auth import CurrentUser, AdminUser
from src.models.settings import DetectionRule, ReasonTemplate, VocabularyDict
from src.schemas.settings import (
    DetectionRuleResponse, DetectionRuleUpdate,
    TemplateItem, TemplateListResponse, TemplateUpdateRequest,
    DictEntry, DictListResponse, DictUpdateRequest,
)
from src.config import settings as app_settings


router = APIRouter()

# デフォルトテンプレート
DEFAULT_TEMPLATES = [
    {
        "template_type": "internal",
        "template_text": (
            "【社内報告用】\n"
            "対象日: {date}\n対象者: {employee_name}\n"
            "異常内容: {issue_type} - {rule_description}\n"
            "原因: {cause_detail}\n"
            "対応: {action_taken}\n"
            "再発防止: {prevention}"
        ),
    },
    {
        "template_type": "employee",
        "template_text": (
            "【従業員向け通知】\n"
            "{employee_name}さん\n\n"
            "{date}の勤怠に関して確認事項があります。\n"
            "内容: {issue_type}\n詳細: {rule_description}\n\n"
            "お心当たりがあれば、店長までご連絡ください。"
        ),
    },
    {
        "template_type": "audit",
        "template_text": (
            "【監査提出用 是正報告書】\n"
            "報告日: {today}\n対象期間: {date}\n"
            "対象事業所: {store_name}\n"
            "対象者: {employee_name}\n\n"
            "1. 発生事象\n{issue_type}: {rule_description}\n\n"
            "2. 原因分析\n{cause_detail}\n\n"
            "3. 是正措置\n{action_taken}\n\n"
            "4. 再発防止策\n{prevention}\n\n"
            "※ 本報告は勤怠データの機械的検知結果に基づくものであり、"
            "法令違反の確定判断を行うものではありません。"
        ),
    },
]


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


@router.get("/templates", response_model=TemplateListResponse)
async def get_templates(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """テンプレート取得"""
    result = await db.execute(
        select(ReasonTemplate)
        .where(ReasonTemplate.organization_id == current_user.organization_id)
        .order_by(ReasonTemplate.template_type)
    )
    templates = result.scalars().all()

    if not templates:
        # デフォルトを返す
        return TemplateListResponse(
            templates=[
                TemplateItem(template_type=t["template_type"], template_text=t["template_text"])
                for t in DEFAULT_TEMPLATES
            ]
        )

    return TemplateListResponse(
        templates=[
            TemplateItem(
                id=str(t.id),
                template_type=t.template_type,
                template_text=t.template_text,
            )
            for t in templates
        ]
    )


@router.put("/templates", response_model=TemplateListResponse)
async def update_templates(
    request: TemplateUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """テンプレート更新（全置換）"""
    # 既存を削除
    await db.execute(
        delete(ReasonTemplate)
        .where(ReasonTemplate.organization_id == current_user.organization_id)
    )

    # 新規作成
    new_templates = []
    for item in request.templates:
        t = ReasonTemplate(
            organization_id=current_user.organization_id,
            template_type=item.template_type,
            template_text=item.template_text,
        )
        db.add(t)
        new_templates.append(t)

    await db.flush()

    return TemplateListResponse(
        templates=[
            TemplateItem(
                id=str(t.id),
                template_type=t.template_type,
                template_text=t.template_text,
            )
            for t in new_templates
        ]
    )


@router.get("/dictionary", response_model=DictListResponse)
async def get_dictionary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """語彙辞書取得"""
    result = await db.execute(
        select(VocabularyDict)
        .where(VocabularyDict.organization_id == current_user.organization_id)
        .order_by(VocabularyDict.original_word)
    )
    entries = result.scalars().all()

    return DictListResponse(
        dictionary=[
            DictEntry(
                id=str(e.id),
                original_word=e.original_word,
                replacement_word=e.replacement_word,
            )
            for e in entries
        ]
    )


@router.put("/dictionary", response_model=DictListResponse)
async def update_dictionary(
    request: DictUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """語彙辞書更新（全置換）"""
    # 既存を削除
    await db.execute(
        delete(VocabularyDict)
        .where(VocabularyDict.organization_id == current_user.organization_id)
    )

    # 新規作成
    new_entries = []
    for item in request.dictionary:
        e = VocabularyDict(
            organization_id=current_user.organization_id,
            original_word=item.original_word,
            replacement_word=item.replacement_word,
        )
        db.add(e)
        new_entries.append(e)

    await db.flush()

    return DictListResponse(
        dictionary=[
            DictEntry(
                id=str(e.id),
                original_word=e.original_word,
                replacement_word=e.replacement_word,
            )
            for e in new_entries
        ]
    )

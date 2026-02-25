"""プラン制限チェック"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.store import Organization, Store, PlanType

PLAN_LIMITS = {
    PlanType.FREE.value: {"clients": 3, "reason_gen_monthly": 3},
    PlanType.STANDARD.value: {"clients": 10, "reason_gen_monthly": 99999},
    PlanType.PRO.value: {"clients": 9999, "reason_gen_monthly": 99999},
}


async def check_client_limit(db: AsyncSession, organization_id: str) -> tuple[bool, str]:
    """顧問先数制限チェック。(制限内か, メッセージ) を返す"""
    org = await db.get(Organization, organization_id)
    if not org:
        return False, "組織が見つかりません"

    count_result = await db.execute(
        select(func.count(Store.id)).where(
            Store.organization_id == organization_id
        )
    )
    current_count = count_result.scalar() or 0
    limit = org.client_limit

    if current_count >= limit:
        plan_label = org.plan.capitalize()
        return False, (
            f"{plan_label}プランの顧問先上限（{limit}社）に達しています。"
            "プランをアップグレードしてください。"
        )

    return True, ""


async def get_client_count(db: AsyncSession, organization_id: str) -> int:
    """現在の顧問先数を取得"""
    result = await db.execute(
        select(func.count(Store.id)).where(
            Store.organization_id == organization_id
        )
    )
    return result.scalar() or 0

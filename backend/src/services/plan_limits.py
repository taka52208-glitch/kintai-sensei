"""プラン制限チェック"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.store import Organization, PlanType
from src.models.employee import Employee

PLAN_LIMITS = {
    PlanType.FREE.value: {"employees": 10, "reason_gen_monthly": 30},
    PlanType.STANDARD.value: {"employees": 50, "reason_gen_monthly": 500},
    PlanType.PRO.value: {"employees": 9999, "reason_gen_monthly": 99999},
}


async def check_employee_limit(db: AsyncSession, organization_id: str) -> tuple[bool, str]:
    """従業員数制限チェック。(制限内か, メッセージ) を返す"""
    org = await db.get(Organization, organization_id)
    if not org:
        return False, "組織が見つかりません"

    count_result = await db.execute(
        select(func.count(Employee.id)).where(
            Employee.organization_id == organization_id
        )
    )
    current_count = count_result.scalar() or 0
    limit = org.employee_limit

    if current_count >= limit:
        plan_label = org.plan.capitalize()
        return False, (
            f"{plan_label}プランの従業員上限（{limit}名）に達しています。"
            "プランをアップグレードしてください。"
        )

    return True, ""


async def get_employee_count(db: AsyncSession, organization_id: str) -> int:
    """現在の従業員数を取得"""
    result = await db.execute(
        select(func.count(Employee.id)).where(
            Employee.organization_id == organization_id
        )
    )
    return result.scalar() or 0

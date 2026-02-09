"""課金API"""

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.core.database import get_db
from src.core.auth import get_current_user
from src.models.user import User
from src.models.store import Organization, PlanType
from src.models.employee import Employee
from src.schemas.billing import (
    PlanInfo,
    CreateCheckoutRequest,
    CreateCheckoutResponse,
    BillingPortalResponse,
)

router = APIRouter()

PLAN_LIMITS = {
    PlanType.FREE.value: 10,
    PlanType.STANDARD.value: 50,
    PlanType.PRO.value: 9999,
}


def _init_stripe():
    """Stripe APIキーを設定"""
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="決済機能は現在利用できません")
    stripe.api_key = settings.stripe_secret_key


@router.get("/plan", response_model=PlanInfo)
async def get_current_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """現在のプラン情報を取得"""
    org = await db.get(Organization, current_user.organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="組織が見つかりません")

    # 従業員数カウント
    count_result = await db.execute(
        select(func.count(Employee.id)).where(
            Employee.organization_id == org.id
        )
    )
    employee_count = count_result.scalar() or 0

    return PlanInfo(
        plan=org.plan,
        employee_limit=org.employee_limit,
        employee_count=employee_count,
        stripe_customer_id=org.stripe_customer_id,
        stripe_subscription_id=org.stripe_subscription_id,
    )


@router.post("/checkout", response_model=CreateCheckoutResponse)
async def create_checkout_session(
    request: CreateCheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stripeチェックアウトセッションを作成"""
    _init_stripe()

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="管理者のみプランを変更できます")

    org = await db.get(Organization, current_user.organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="組織が見つかりません")

    # Stripe Customer 未作成なら作成
    if not org.stripe_customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=org.name,
            metadata={"organization_id": org.id},
        )
        org.stripe_customer_id = customer.id
        await db.flush()

    # チェックアウトセッション作成
    session = stripe.checkout.Session.create(
        customer=org.stripe_customer_id,
        mode="subscription",
        line_items=[{
            "price": request.price_id,
            "quantity": request.quantity,
        }],
        success_url=f"{_get_frontend_url()}/settings?billing=success",
        cancel_url=f"{_get_frontend_url()}/settings?billing=cancel",
        metadata={"organization_id": org.id},
    )

    return CreateCheckoutResponse(checkout_url=session.url)


@router.post("/portal", response_model=BillingPortalResponse)
async def create_billing_portal(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stripeカスタマーポータルを開く"""
    _init_stripe()

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="管理者のみ利用できます")

    org = await db.get(Organization, current_user.organization_id)
    if not org or not org.stripe_customer_id:
        raise HTTPException(status_code=400, detail="有料プランに登録されていません")

    session = stripe.billing_portal.Session.create(
        customer=org.stripe_customer_id,
        return_url=f"{_get_frontend_url()}/settings",
    )

    return BillingPortalResponse(portal_url=session.url)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Stripe Webhook処理"""
    if not settings.stripe_secret_key or not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook未設定")

    stripe.api_key = settings.stripe_secret_key
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # イベント処理
    if event["type"] == "checkout.session.completed":
        await _handle_checkout_completed(event["data"]["object"], db)
    elif event["type"] == "customer.subscription.updated":
        await _handle_subscription_updated(event["data"]["object"], db)
    elif event["type"] == "customer.subscription.deleted":
        await _handle_subscription_deleted(event["data"]["object"], db)

    return {"status": "ok"}


async def _handle_checkout_completed(session: dict, db: AsyncSession):
    """チェックアウト完了 → サブスクリプション有効化"""
    org_id = session.get("metadata", {}).get("organization_id")
    subscription_id = session.get("subscription")
    if not org_id or not subscription_id:
        return

    org = await db.get(Organization, org_id)
    if not org:
        return

    # サブスクリプション詳細を取得してプランを判定
    subscription = stripe.Subscription.retrieve(subscription_id)
    price_id = subscription["items"]["data"][0]["price"]["id"]

    plan, limit = _resolve_plan(price_id)
    org.stripe_subscription_id = subscription_id
    org.plan = plan
    org.employee_limit = limit
    await db.flush()


async def _handle_subscription_updated(subscription: dict, db: AsyncSession):
    """サブスクリプション更新"""
    customer_id = subscription.get("customer")
    if not customer_id:
        return

    result = await db.execute(
        select(Organization).where(Organization.stripe_customer_id == customer_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        return

    price_id = subscription["items"]["data"][0]["price"]["id"]
    plan, limit = _resolve_plan(price_id)
    org.stripe_subscription_id = subscription["id"]
    org.plan = plan
    org.employee_limit = limit
    await db.flush()


async def _handle_subscription_deleted(subscription: dict, db: AsyncSession):
    """サブスクリプション解約 → Freeプランに戻す"""
    customer_id = subscription.get("customer")
    if not customer_id:
        return

    result = await db.execute(
        select(Organization).where(Organization.stripe_customer_id == customer_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        return

    org.stripe_subscription_id = None
    org.plan = PlanType.FREE.value
    org.employee_limit = PLAN_LIMITS[PlanType.FREE.value]
    await db.flush()


def _resolve_plan(price_id: str) -> tuple[str, int]:
    """Price IDからプランと上限人数を判定"""
    if price_id == settings.stripe_price_standard:
        return PlanType.STANDARD.value, PLAN_LIMITS[PlanType.STANDARD.value]
    elif price_id == settings.stripe_price_pro:
        return PlanType.PRO.value, PLAN_LIMITS[PlanType.PRO.value]
    return PlanType.FREE.value, PLAN_LIMITS[PlanType.FREE.value]


def _get_frontend_url() -> str:
    """フロントエンドURL取得"""
    return settings.frontend_url.rstrip("/")

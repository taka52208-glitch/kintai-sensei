"""課金スキーマ"""

from pydantic import BaseModel


class PlanInfo(BaseModel):
    """現在のプラン情報"""
    plan: str
    client_limit: int
    client_count: int
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None

    class Config:
        from_attributes = True


class CreateCheckoutRequest(BaseModel):
    """チェックアウトセッション作成リクエスト"""
    price_id: str
    quantity: int = 1


class CreateCheckoutResponse(BaseModel):
    """チェックアウトセッションURL"""
    checkout_url: str


class BillingPortalResponse(BaseModel):
    """カスタマーポータルURL"""
    portal_url: str


class PlanChangeResult(BaseModel):
    """プラン変更結果"""
    plan: str
    client_limit: int
    message: str

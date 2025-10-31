from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from src.models.user_subscription import SubscriptionStatus


class UserSubscriptionCreate(BaseModel):
    subscription_id: int
    amount: float = Field(..., gt=0)


class UserSubscriptionUpdate(BaseModel):
    status: SubscriptionStatus | None = None


class UserSubscriptionResponse(BaseModel):
    id: UUID
    user_id: UUID
    plan_id: int
    status: str
    created_at: datetime
    updated_at: datetime | None = None


class UserSubscriptionPaymentResponse(BaseModel):
    id: UUID
    redirect_link: HttpUrl


class UserSubscriptionUpdateResponse(BaseModel):
    user_subscription_id: UUID
    status: str

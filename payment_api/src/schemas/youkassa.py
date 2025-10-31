from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class SubscriptionStatus(str, Enum):
    pending = "pending"
    active = "active"
    canceled = "canceled"
    expired = "expired"


class PaymentStatus(str, Enum):
    pending = "pending"
    succeeded = "succeeded"
    canceled = "canceled"


class PaymentCreate(BaseModel):
    amount: float = Field(..., gt=0)
    user_id: UUID
    user_subscription_id: UUID
    redirect_url: HttpUrl
    description: str


class PaymentResponse(BaseModel):
    youkassa_payment_id: UUID
    confirmation_url: HttpUrl
    status: PaymentStatus


class WebhookPaymentPayload(BaseModel):
    user_subscription_id: UUID
    user_id: UUID
    amount: float = Field(..., gt=0)
    description: Optional[str] = ""
    youkassa_payment_id: UUID
    status: PaymentStatus
    extra: Optional[Dict[str, Any]] = Field(default=None)

    @classmethod
    def from_webhook(cls, data: Dict[str, Any]) -> "WebhookPaymentPayload":
        """Создаёт объект модели из сырых данных вебхука, забирая только нужные поля"""
        obj = data.get("object", {})
        metadata = obj.get("metadata", {})

        return cls(
            user_subscription_id=UUID(metadata.get("user_subscription_id")),
            user_id=UUID(metadata.get("user_id")),
            amount=float(obj.get("amount", {}).get("value")),
            description=data.get("description", ""),
            youkassa_payment_id=UUID(obj.get("id")),
            status=PaymentStatus(obj.get("status")),
            extra=data,
        )

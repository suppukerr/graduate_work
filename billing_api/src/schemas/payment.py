from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from src.models.user_subscription import PaymentStatus


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

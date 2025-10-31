import enum
import uuid

from sqlalchemy import Column, Enum, Float, String
from sqlalchemy.dialects.postgresql import UUID

from src.db.postgres import Base


class SubscriptionStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    canceled = "canceled"
    expired = "expired"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    succeeded = "succeeded"
    canceled = "canceled"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_subscription_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    youkassa_payment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # из YooKassa

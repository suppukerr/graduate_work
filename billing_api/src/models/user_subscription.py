import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID

from src.db.postgres import Base


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    succeeded = "succeeded"
    canceled = "canceled"
    ## добавить какие еще есть


class SubscriptionStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    canceled = "canceled"
    expired = "expired"


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    subscription_id = Column(String, nullable=False)
    status = Column(Enum(SubscriptionStatus),
                    default=SubscriptionStatus.pending)

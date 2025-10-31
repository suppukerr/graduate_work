from sqlalchemy import (
    Column, Integer, String,
    ForeignKey, DateTime,
    Numeric, Enum, Text
    )
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
import uuid

Base = declarative_base()


class SubscriptionRepeat(str, enum.Enum):
    monthly = "monthly"
    annual = "annual"
    once = "once"


class Subscription(Base):
    __tablename__ = "subscription"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    period = Column(Integer)
    sum = Column(Numeric(10, 2))
    repeatition = Column(Enum(SubscriptionRepeat))
    repeats_number = Column(Integer)


class SubscriptionStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    canceled = "canceled"
    expired = "expired"


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
        )
    user_id = Column(
        UUID(as_uuid=True),
        nullable=False
        )
    subscription_id = Column(
        String,
        nullable=False
        )
    status = Column(
        Enum(SubscriptionStatus),
        default=SubscriptionStatus.pending
        )

    # Связь с платежами
    payments = relationship(
        "Payment",
        back_populates="user_subscription"
        )


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    succeeded = "succeeded"
    canceled = "canceled"


class RefundStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
        )
    user_subscription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_subscriptions.id")
        )
    amount = Column(
        Numeric(10, 2),
        nullable=False
        )
    status = Column(
        Enum(PaymentStatus),
        default=PaymentStatus.pending
        )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
        )

    user_subscription = relationship(
        "UserSubscription",
        back_populates="payments"
        )
    refunds = relationship(
        "Refund",
        back_populates="payment"
        )


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
        )
    payment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payments.id"),
        nullable=False
        )
    amount = Column(
        Numeric(10, 2),
        nullable=False
        )
    status = Column(
        Enum(RefundStatus),
        nullable=False,
        default=RefundStatus.pending
        )
    external_refund_id = Column(String, unique=True)
    reason = Column(Text)
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
        )
    processed_at = Column(DateTime)
    error_details = Column(Text)

    payment = relationship("Payment", back_populates="refunds")

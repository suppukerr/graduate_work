import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_subscription import UserSubscription, SubscriptionStatus
from src.schemas.user_subscription import UserSubscriptionUpdate


async def get_user_subscription(
        session: AsyncSession,
        user_subscription_id: uuid
) -> UserSubscription | None:

    return await session.scalar(
        select(UserSubscription).where(
            UserSubscription.id == user_subscription_id)
    )


async def create_user_subscription(
    user_id: uuid,
    subscription_id: uuid,
    session: AsyncSession
) -> UserSubscription:

    subscription = UserSubscription(
        id=str(uuid.uuid4()),
        user_id=str(user_id),
        subscription_id=str(subscription_id),
        status=SubscriptionStatus.pending.value,
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc)
    )
    session.add(subscription)
    await session.commit()
    await session.refresh(subscription)
    return subscription


async def update_user_subscription_status(
    session: AsyncSession,
    user_subscription: UserSubscription,
    update: UserSubscriptionUpdate
) -> UserSubscription:

    user_subscription.status = update.status

    session.add(user_subscription)
    await session.commit()
    await session.refresh(user_subscription)

    return user_subscription

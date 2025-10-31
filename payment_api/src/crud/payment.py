import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.payment import Payment as Payment_db
from src.schemas.youkassa import WebhookPaymentPayload

logger = logging.getLogger(__name__)


async def create_payment(
        session: AsyncSession,
        payload: WebhookPaymentPayload
) -> Payment_db:

    async with session.begin():
        payment = Payment_db(
            youkassa_payment_id=payload.youkassa_payment_id,  #
            amount=payload.amount,  #
            status=payload.status.value,
            user_subscription_id=payload.user_subscription_id,
            user_id=payload.user_id,  #
            description=payload.description,  #
        )
        merged = await session.merge(payment)
        await session.refresh(merged)
        return merged

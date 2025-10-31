import httpx
import logging
from fastapi import HTTPException
from src.core.config import settings

logger = logging.getLogger(__name__)


async def update_user_subsription(
        data: str,
        user_subscription_id: int
):
    subscriptions_url = f"{settings.subscription.update_url}{str(user_subscription_id)}"
    logger.info("subscriptions_url: %s", subscriptions_url)
    async with httpx.AsyncClient() as client:
        response = await client.patch(subscriptions_url, json=data)
        response.raise_for_status()

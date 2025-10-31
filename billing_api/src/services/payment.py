import httpx
from src.core.config import settings


async def create_payment(payment_payload):
    payment_payload_json_str = payment_payload.model_dump_json()
    url = settings.payment.create_url
    async with httpx.AsyncClient() as client:
        response = await client.post(url,
                                     content=payment_payload_json_str,
                                     headers={"Content-Type": "application/json"}
                                     )
        response.raise_for_status()  # выбросит ошибку, если статус не 2xx
        data = response.json()

    return data

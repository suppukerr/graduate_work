import logging
import uuid
import asyncio

from fastapi import APIRouter, Body, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from yookassa import Configuration, Payment

from src.core.config import settings
from src.crud.payment import create_payment
from src.db import postgres
from src.schemas.yookassa_webhook_examples import (
    YOOKASSA_WEBHOOK_FAILED,
    YOOKASSA_WEBHOOK_SUCCESS,
)
from src.schemas.youkassa import PaymentCreate, PaymentResponse, WebhookPaymentPayload
from src.services.user_subcription import update_user_subsription

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/payment/youkassa", tags=["youkassa"])
Configuration.account_id = settings.youkassa.SHOP_ID
Configuration.secret_key = settings.youkassa.SECRET_KEY


@router.post("/payment",
             response_model=PaymentResponse,
             summary="Создать оплату")
async def create_youkassa_payment(
    payload: PaymentCreate,
):
    """
    Отправляет запрос через YooKassa SDK,
    возвращает ID платежи, ссылку и статус.
    """

    # 1 Отправляем запрос в YooKassa API

    idempotence_key = str(uuid.uuid4())
    logger.info(f"idempotence_key для {payload.description}: {idempotence_key}")
    payment_data = {
        "amount": {
            "value": f"{payload.amount:.2f}",
            "currency": "RUB",
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": payload.redirect_url,
        },
        "description": payload.description,
        "metadata": {
            "user_id": str(payload.user_id),
            "user_subscription_id": str(payload.user_subscription_id),
        },
        "capture": True,
    }
    payment = await asyncio.to_thread(Payment.create,
                                      payment_data,
                                      idempotence_key)

    # 2 Возвращаем пользователю ID, ссылку и статус
    return PaymentResponse(
        youkassa_payment_id=str(payment.id),
        confirmation_url=payment.confirmation.confirmation_url,
        status=payment.status,
    )


@router.post("/webhook",
             summary="Обработка вебхука от YooKassa")
async def yookassa_webhook(
    request: Request,
    session: AsyncSession = Depends(postgres.get_db),
    _doc_example: dict = Body(..., example=YOOKASSA_WEBHOOK_SUCCESS)
) -> dict:
    """
    Принимает вебхук от YooKassa,
    обновляет платёж в БД,
    уведомляет сервис подписок.
    """

    #  0. валидируем и получаем данные из вебхука
    raw_data = await request.json()
    logger.info("Raw webhook JSON: %s", raw_data)
    logger.info("-------------------------------------")
    payload = WebhookPaymentPayload.from_webhook(raw_data)
    logger.info("Converted payload: %s", payload)

    #  1. Создаем платеж в бд
    await create_payment(session, payload)

    # 2. Обновляем статус подписки юзера (запрос в билинг апи)
    if payload.status.value == "succeeded":
        data = {"status": "active"}
        await update_user_subsription(data, payload.user_subscription_id)

    return {"status": "ok"}

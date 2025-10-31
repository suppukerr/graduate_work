import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, status

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth_depends import TokenPayload, get_token_data
from src.core.config import settings
from src.crud.user_subscriptions import (
    create_user_subscription,
    get_user_subscription,
    update_user_subscription_status,
)
from src.db import postgres
from src.models.user_subscription import SubscriptionStatus
from src.schemas.billing_event import BillingEventMessage, EventType
from src.schemas.payment import PaymentCreate
from src.schemas.user_subscription import (
    UserSubscriptionCreate,
    UserSubscriptionUpdate,
    UserSubscriptionPaymentResponse,
    UserSubscriptionUpdateResponse
)
from src.services.kafka import KafkaService, get_kafka_service
from src.services.payment import create_payment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


@router.post("/user-subscription",
             response_model=UserSubscriptionPaymentResponse,
             summary="Создать подписку пользователя")
async def create_user_subscription_and_payment(
    payload: UserSubscriptionCreate,
    session: AsyncSession = Depends(postgres.get_db),
    user_token_data: TokenPayload = Depends(get_token_data)
):

    # 1. Создаём UserSubscription (запрос в бд)
    user_subscription = await create_user_subscription(
        user_token_data.sub,
        payload.subscription_id,
        session
    )

    # 2. Создаем платеж (запрос в пеймент апи)
    payment_payload = PaymentCreate(
        amount=payload.amount,
        user_id=user_token_data.sub,
        user_subscription_id=user_subscription.id,
        redirect_url=settings.payment.redirect_url,
        # в будущем можно дописать урл, чтобы редиректил на страницу со статусом подписки
        description=f'Оплата: {payload.amount} руб'
        # можно еще подтянуть из бд название подписки по план_айди
    )
    payment = await create_payment(payment_payload)

    return UserSubscriptionPaymentResponse(
        id=user_subscription.id,
        redirect_link=payment.get("confirmation_url")
    )


@router.patch("/user-subscriptions/{user_subscription_id}",
              response_model=UserSubscriptionUpdateResponse,
              summary="Обновить подписку пользователя",
              )
async def update_subscription_status(
    user_subscription_id: str = Path(...),
    update: UserSubscriptionUpdate = ...,
    session: AsyncSession = Depends(postgres.get_db),
    kafka_service: KafkaService = Depends(get_kafka_service)
):
    if update.status:
        user_subscription = await get_user_subscription(session, user_subscription_id)

        if user_subscription is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Не удалось найти подписку пользователя с id {user_subscription_id}"
            )

        # Сохраняем старый статус для проверки изменений
        old_status = user_subscription.status

        user_subscription = await update_user_subscription_status(
            session,
            user_subscription,
            update
        )

        # Отправляем событие в Kafka при изменении статуса
        new_status = user_subscription.status
        
        # Определяем тип события на основе нового статуса
        event_type = None
        if new_status == SubscriptionStatus.active and old_status != SubscriptionStatus.active:
            event_type = EventType.SUBSCRIBE
        elif (new_status in (SubscriptionStatus.canceled, SubscriptionStatus.expired)
              and old_status == SubscriptionStatus.active):
            event_type = EventType.UNSUBSCRIBE
        
        # Отправляем событие если статус изменился на релевантный
        if event_type:
            try:
                message = BillingEventMessage(
                    user_id=str(user_subscription.user_id),
                    event_type=event_type.value
                )
                event_data = message.model_dump()
                event_data["timestamp"] = datetime.utcnow().isoformat()
                
                event_id = await kafka_service.send_billing_event(event_data)
                
                logger.info(
                    f"Billing event sent: event_id={event_id}, "
                    f"user_id={user_subscription.user_id}, "
                    f"event_type={event_type.value}, "
                    f"status_change={old_status.value}->{new_status.value}"
                )
            except Exception as e:
                logger.error(
                    f"Ошибка отправки события в Kafka для пользователя {user_subscription.user_id}: {e}"
                )
                # Не прерываем выполнение, т.к. статус уже обновлен в БД

    return UserSubscriptionUpdateResponse(
        user_subscription_id=user_subscription.id,
        status=user_subscription.status.value
    )

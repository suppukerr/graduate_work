import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth_depends import get_token_data
from src.db import postgres
from src.schemas.billing_event import BillingEventRequest, BillingEventMessage
from src.services.kafka import KafkaService, get_kafka_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/billing/health", tags=["health"])
# router = APIRouter(prefix="/health", tags=["health"])


@router.get("/service")
async def health_check():
    """Проверка состояния сервиса"""
    return {"status": "ok", "service": "billing-api"}


@router.get("/service-auth")
async def health_check_auth(current_user=Depends(get_token_data)):
    """Проверка состояния сервиса"""
    return {"status": "ok", "service": "billing-api"}


@router.get("/db")
async def database_check(db: AsyncSession = Depends(postgres.get_db)):
    """Проверка подключения к базе данных PostgreSQL"""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "postgresql", "connection": "healthy"}
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Database connection failed: {str(e)}"
        )


@router.post("/send-event", status_code=202)
async def debug_send_billing_event(
    event_request: BillingEventRequest,
    kafka_service: KafkaService = Depends(get_kafka_service),
):
    """
    [DEBUG] Ручная отправка события биллинга в Kafka для отладки.
    
    - **user_id**: UUID пользователя
    - **event_type**: Тип события (SUBSCRIBE/UNSUBSCRIBE)
    """
    try:
        message = BillingEventMessage.from_request(event_request)
        event_data = message.model_dump()
        event_data["timestamp"] = datetime.utcnow().isoformat()
        
        event_id = await kafka_service.send_billing_event(event_data)
        
        logger.info(
            f"[DEBUG] Billing event sent: event_id={event_id}, "
            f"user_id={event_request.user_id}, "
            f"event_type={event_request.event_type}"
        )
        
        return {
            "status": "accepted",
            "event_id": event_id,
            "message": "Event queued for processing",
        }
        
    except Exception as e:
        logger.error(f"Failed to send billing event: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send billing event: {str(e)}",
        )

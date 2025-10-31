from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Типы событий биллинга"""

    SUBSCRIBE = "SUBSCRIBE"
    UNSUBSCRIBE = "UNSUBSCRIBE"


class BillingEventRequest(BaseModel):
    """Схема запроса для создания события биллинга"""

    user_id: UUID = Field(..., description="Уникальный идентификатор пользователя")
    event_type: EventType = Field(..., description="Тип события")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "event_type": "SUBSCRIBE",
            }
        }


class BillingEventMessage(BaseModel):
    """Схема сообщения для отправки в Kafka"""

    user_id: str = Field(..., description="UUID пользователя в виде строки")
    event_type: str = Field(..., description="Тип события: SUBSCRIBE/UNSUBSCRIBE")

    @classmethod
    def from_request(cls, request: BillingEventRequest) -> "BillingEventMessage":
        """Создает сообщение из запроса"""
        return cls(
            user_id=str(request.user_id),
            event_type=request.event_type.value,
        )


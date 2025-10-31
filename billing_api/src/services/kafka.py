import json
import logging
from typing import Dict, Any
from uuid import uuid4

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from src.core.config import settings
from src.utils.backoff import backoff

logger = logging.getLogger(__name__)


class KafkaService:
    """Сервис для работы с Kafka."""
    
    def __init__(self):
        """Инициализация сервиса."""
        self.producer: AIOKafkaProducer | None = None
        self.bootstrap_servers = settings.kafka.bootstrap_servers
        self.billing_events_topic = settings.kafka.topic_billing_events
        logger.info(f"KafkaService инициализирован. Брокеры: {self.bootstrap_servers}")
    
    async def connect(self) -> None:
        """Подключение к Kafka."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                enable_idempotence=settings.kafka.enable_idempotence,
                acks=settings.kafka.acks,
                request_timeout_ms=settings.kafka.request_timeout_ms
            )
            await self.producer.start()
            logger.info("Подключение к Kafka установлено")
        except Exception as e:
            logger.error(f"Ошибка подключения к Kafka: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Отключение от Kafka."""
        if self.producer:
            try:
                await self.producer.stop()
                logger.info("Отключение от Kafka")
            except Exception as e:
                logger.error(f"Ошибка при отключении от Kafka: {e}")
        self.producer = None

    @backoff(0.1, 2, 10, logger)   
    async def send_event(self, topic: str, event_data: Dict[str, Any], key: str | None = None) -> str:
        """
        Отправка события в Kafka топик.
        
        Args:
            topic: Название топика
            event_data: Данные события
            key: Ключ сообщения (опционально)
            
        Returns:
            ID отправленного события
            
        Raises:
            KafkaError: При ошибке отправки
        """
        if not self.producer:
            await self.connect()
            
        event_id = str(uuid4())
        
        # Добавляем event_id к данным
        enriched_data = {
            **event_data,
            "event_id": event_id,
            "timestamp": event_data.get("timestamp")
        }
        if not key:
            key = event_data.get("user_id")

        try:
            # Отправляем сообщение
            record_metadata = await self.producer.send_and_wait(
                topic=topic,
                value=enriched_data,
                key=key
            )
            
            logger.info(
                f"Событие отправлено в топик '{topic}': "
                f"event_id={event_id}, partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}"
            )
            
            return event_id
            
        except KafkaError as e:
            logger.error(f"Ошибка отправки в Kafka: {e}")
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке: {e}")
            raise
    
    async def send_billing_event(self, event_data: Dict[str, Any]) -> str:
        """Отправка события биллинга в billing events топик."""
        return await self.send_event(self.billing_events_topic, event_data)


# Глобальный экземпляр сервиса
kafka_service = KafkaService()


async def get_kafka_service() -> KafkaService:
    """Получить экземпляр Kafka сервиса."""
    return kafka_service

import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.session import async_session_maker
from src.services.role_service import RoleService
from src.services.user_role_service import UserRoleService

logger = logging.getLogger(__name__)


class KafkaConsumerService:
    """Сервис для прослушивания событий из Kafka и обработки подписок."""

    def __init__(self):
        """Инициализация сервиса."""
        self.consumer: AIOKafkaConsumer | None = None
        self.bootstrap_servers = settings.kafka.bootstrap_servers
        self.topic = settings.kafka.topic_billing_events
        self.group_id = settings.kafka.consumer_group_id
        self.subscriber_role_name = settings.kafka.subscriber_role_name
        self._running = False
        logger.info(
            f"KafkaConsumerService инициализирован. "
            f"Брокеры: {self.bootstrap_servers}, топик: {self.topic}"
        )

    async def connect(self) -> None:
        """Подключение к Kafka."""
        try:
            self.consumer = AIOKafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset=settings.kafka.auto_offset_reset,
                enable_auto_commit=settings.kafka.enable_auto_commit,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                request_timeout_ms=settings.kafka.request_timeout_ms
            )
            await self.consumer.start()
            logger.info(f"Подключение к Kafka установлено. Слушаем топик: {self.topic}")
        except Exception as e:
            logger.error(f"Ошибка подключения к Kafka: {e}")
            raise

    async def disconnect(self) -> None:
        """Отключение от Kafka."""
        self._running = False
        if self.consumer:
            try:
                await self.consumer.stop()
                logger.info("Отключение от Kafka")
            except Exception as e:
                logger.error(f"Ошибка при отключении от Kafka: {e}")
        self.consumer = None

    async def _get_or_create_subscriber_role(self, db: AsyncSession) -> str | None:
        """Получить или создать роль подписчика."""
        from src.schemas.role import RoleCreate
        
        role_service = RoleService(db)
        role = await role_service.get_role_by_name(self.subscriber_role_name)
        
        if not role:
            # Создаем роль автоматически, как это делается с ролью USER
            try:
                role = await role_service.create_role(
                    RoleCreate(
                        name=self.subscriber_role_name,
                        description="Роль для пользователей с активной подпиской"
                    )
                )
                logger.info(f"Роль '{self.subscriber_role_name}' автоматически создана")
            except Exception as e:
                logger.error(
                    f"Не удалось создать роль '{self.subscriber_role_name}': {e}"
                )
                return None
        
        return str(role.id)

    async def _handle_subscribe_event(
        self,
        user_id: str,
        db: AsyncSession
    ) -> None:
        """Обработка события подписки - добавление роли SUBSCRIBER."""
        try:
            role_id = await self._get_or_create_subscriber_role(db)
            if not role_id:
                logger.error(
                    f"Не удалось обработать подписку для user_id={user_id}: "
                    f"роль '{self.subscriber_role_name}' не существует"
                )
                return

            user_role_service = UserRoleService(db)
            success = await user_role_service.assign_role_to_user(user_id, role_id)
            
            if success:
                logger.info(
                    f"Роль '{self.subscriber_role_name}' успешно назначена "
                    f"пользователю {user_id}"
                )
            else:
                logger.warning(
                    f"Не удалось назначить роль пользователю {user_id}. "
                    "Возможно, пользователь не существует."
                )
        except Exception as e:
            logger.error(f"Ошибка при обработке подписки для user_id={user_id}: {e}")

    async def _handle_unsubscribe_event(
        self,
        user_id: str,
        db: AsyncSession
    ) -> None:
        """Обработка события отписки - удаление роли SUBSCRIBER."""
        try:
            role_id = await self._get_or_create_subscriber_role(db)
            if not role_id:
                logger.error(
                    f"Не удалось обработать отписку для user_id={user_id}: "
                    f"роль '{self.subscriber_role_name}' не существует"
                )
                return

            user_role_service = UserRoleService(db)
            success = await user_role_service.remove_role_from_user(user_id, role_id)
            
            if success:
                logger.info(
                    f"Роль '{self.subscriber_role_name}' успешно удалена "
                    f"у пользователя {user_id}"
                )
            else:
                logger.warning(
                    f"Не удалось удалить роль у пользователя {user_id}. "
                    "Возможно, роль не была назначена."
                )
        except Exception as e:
            logger.error(f"Ошибка при обработке отписки для user_id={user_id}: {e}")

    async def _process_message(self, message) -> None:
        """Обработка одного сообщения из Kafka."""
        try:
            event_data = message.value
            event_type = event_data.get("event_type")
            user_id = event_data.get("user_id")

            if not event_type or not user_id:
                logger.warning(
                    f"Получено некорректное сообщение: {event_data}. "
                    "Отсутствует event_type или user_id."
                )
                return

            logger.info(
                f"Получено событие: event_type={event_type}, "
                f"user_id={user_id}, partition={message.partition}, "
                f"offset={message.offset}"
            )

            async with async_session_maker() as db:
                if event_type == "SUBSCRIBE":
                    await self._handle_subscribe_event(user_id, db)
                elif event_type == "UNSUBSCRIBE":
                    await self._handle_unsubscribe_event(user_id, db)
                else:
                    logger.warning(
                        f"Неизвестный тип события: {event_type}. "
                        "Поддерживаются: SUBSCRIBE, UNSUBSCRIBE."
                    )

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON: {e}")
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")

    async def start_consuming(self) -> None:
        """Запуск прослушивания событий из Kafka."""
        if not self.consumer:
            await self.connect()

        self._running = True
        logger.info("Запуск прослушивания Kafka топика...")

        try:
            async for message in self.consumer:
                if not self._running:
                    break
                await self._process_message(message)
        except KafkaError as e:
            logger.error(f"Ошибка Kafka при чтении сообщений: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при чтении сообщений: {e}")
        finally:
            await self.disconnect()


# Глобальный экземпляр сервиса
kafka_consumer_service = KafkaConsumerService()


async def start_kafka_consumer() -> None:
    """Запуск Kafka consumer в фоновом режиме."""
    try:
        await kafka_consumer_service.start_consuming()
    except Exception as e:
        logger.error(f"Критическая ошибка в Kafka consumer: {e}")


async def stop_kafka_consumer() -> None:
    """Остановка Kafka consumer."""
    await kafka_consumer_service.disconnect()


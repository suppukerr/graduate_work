from abc import ABC, abstractmethod


class CacheService(ABC):
    """Интерфейс для работы с кэшем"""

    @abstractmethod
    async def get(self, key: str) -> dict | None:
        """Получение данных из кэша"""
        pass

    @abstractmethod
    async def set(self, key: str, value: dict, expire: int) -> None:
        """Запись данных в кэш"""
        pass


class StorageService(ABC):
    """Интерфейс для работы с хранилищем данных"""

    pass

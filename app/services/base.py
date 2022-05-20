from abc import ABC, abstractmethod
from typing import Optional, Union


class BaseCacheStorage(ABC):
    @abstractmethod
    async def get_from_storage(self, key: str) -> Union[list, str]:
        """Прочитать данные из хранилища кэша"""

    @abstractmethod
    async def put_to_storage(self, key: str, value: Union[list, str]) -> None:
        """Сохранить данные в хранилище кэша"""


class BaseSearch(ABC):
    @abstractmethod
    async def search(self, index: str, **kwargs) -> Optional[Union[list, dict]]:
        """Найти данные в хранилище"""

    @abstractmethod
    async def get(self, index: str, id: str) -> Optional[dict]:
        """Прочитать данные из хранилища"""

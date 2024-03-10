from abc import abstractmethod
from uuid import UUID
from typing import Protocol

from spakky.domain.ports.persistency.repository import IAsyncGenericRepository

from apps.user.domain.models.user import User


class IAsyncUserRepository(IAsyncGenericRepository[User, UUID], Protocol):
    @abstractmethod
    async def get_by_username_or_none(self, username: str) -> User | None: ...

    @abstractmethod
    async def get_by_phone_number_or_none(self, phone_number: str) -> User | None: ...

    @abstractmethod
    async def contains_by_username(self, username: str) -> bool: ...

    @abstractmethod
    async def contains_by_phone_number(self, phone_number: str) -> bool: ...

    @abstractmethod
    async def get_by_password_reset_token_or_none(
        self, password_reset_token: str
    ) -> User | None: ...

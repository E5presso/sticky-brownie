from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.cryptography.jwt import JWT

from apps.user.domain.models.user import User


@runtime_checkable
class IAsyncTokenService(Protocol):
    @abstractmethod
    async def generate_token(self, user: User) -> JWT: ...

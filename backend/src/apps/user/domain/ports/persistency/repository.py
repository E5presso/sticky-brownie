from uuid import UUID
from typing import Protocol

from spakky.domain.ports.persistency.repository import IAsyncGenericRepository

from apps.user.domain.models.user import User


class IAsyncUserRepository(IAsyncGenericRepository[User, UUID], Protocol): ...

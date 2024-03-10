from abc import abstractmethod
from uuid import UUID
from typing import Protocol

from spakky.domain.ports.persistency.repository import IAsyncGenericRepository

from apps.file.domain.models.file import File


class IAsyncFileRepository(IAsyncGenericRepository[File, UUID], Protocol):
    @abstractmethod
    async def get_by_name_or_none(self, name: str) -> File | None: ...
    @abstractmethod
    async def contains_by_name(self, name: str) -> bool: ...

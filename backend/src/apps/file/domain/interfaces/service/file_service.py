from abc import abstractmethod
from typing import Protocol, AsyncGenerator, runtime_checkable

from apps.file.domain.models.file import File


@runtime_checkable
class IAsyncFileService(Protocol):
    @abstractmethod
    async def save(self, file: File, stream: AsyncGenerator[bytes, None]) -> None: ...

    @abstractmethod
    async def get_by_id(self, file: File) -> AsyncGenerator[bytes, None]: ...

    @abstractmethod
    async def delete(self, file: File) -> None: ...

from abc import abstractmethod
from typing import Protocol, AsyncIterable, runtime_checkable

from apps.file.domain.models.file import File


@runtime_checkable
class IAsyncInStream(Protocol):
    @abstractmethod
    async def read(self, size: int = -1) -> bytes: ...

    @abstractmethod
    async def close(self) -> None: ...


@runtime_checkable
class IAsyncOutStream(AsyncIterable[bytes], Protocol): ...


@runtime_checkable
class IAsyncFileService(Protocol):
    @abstractmethod
    async def save(self, file: File, stream: IAsyncInStream) -> None: ...

    @abstractmethod
    async def get_by_id(self, file: File) -> IAsyncOutStream: ...

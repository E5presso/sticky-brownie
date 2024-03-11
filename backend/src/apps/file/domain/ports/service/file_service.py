from abc import abstractmethod
from typing import Protocol, runtime_checkable

from apps.file.domain.models.file import File
from common.interfaces.stream import IAsyncInStream, IAsyncOutStream


@runtime_checkable
class IAsyncFileService(Protocol):
    @abstractmethod
    async def save(self, file: File, stream: IAsyncInStream) -> None: ...

    @abstractmethod
    async def get_by_id(self, file: File) -> IAsyncOutStream: ...

    @abstractmethod
    async def delete(self, file: File) -> None: ...

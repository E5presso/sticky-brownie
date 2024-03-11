from abc import abstractmethod
from typing import Protocol, AsyncIterable, runtime_checkable


@runtime_checkable
class IAsyncInStream(Protocol):
    @abstractmethod
    async def read(self, size: int = -1) -> bytes: ...

    @abstractmethod
    async def close(self) -> None: ...


@runtime_checkable
class IAsyncOutStream(AsyncIterable[bytes], Protocol): ...

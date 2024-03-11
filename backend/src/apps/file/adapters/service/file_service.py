from typing import AsyncIterator

import aiofiles
from spakky.bean.bean import Bean

from apps.file.domain.models.file import File
from apps.file.domain.ports.service.file_service import (
    IAsyncFileService,
    IAsyncInStream,
    IAsyncOutStream,
)
from common.settings.config import Config


class AsyncOutStream(IAsyncOutStream):
    path: str

    def __init__(self, path: str) -> None:
        self.path = path

    # pylint: disable=invalid-overridden-method
    async def __aiter__(self) -> AsyncIterator[bytes]:
        async with aiofiles.open(self.path, "rb") as stream:
            chunk: bytes = await stream.read(Config().file.chunk_size)
            while chunk:
                yield chunk
                chunk = await stream.read(Config().file.chunk_size)


@Bean()
class AsyncUploadFileService(IAsyncFileService):
    __prefix: str

    def __init__(self) -> None:
        self.__prefix = Config().file.prefix

    async def save(self, file: File, stream: IAsyncInStream) -> None:
        async with aiofiles.open(f"{self.__prefix}/{file.uid}", "ab+") as in_stream:
            chunk: bytes = await stream.read(Config().file.chunk_size)
            while chunk:
                await in_stream.write(chunk)
                chunk = await stream.read(Config().file.chunk_size)
        await stream.close()

    async def get_by_id(self, file: File) -> IAsyncOutStream:
        return AsyncOutStream(f"{self.__prefix}/{file.uid}")

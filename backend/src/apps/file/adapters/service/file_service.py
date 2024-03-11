from typing import AsyncIterator

import aiofiles
import aiofiles.os
from spakky.bean.bean import Bean
from spakky.extensions.logging import AsyncLogging

from apps.file.domain.interfaces.service.file_service import IAsyncFileService
from apps.file.domain.models.file import File
from common.interfaces.stream import IAsyncInStream, IAsyncOutStream
from common.settings.config import Config

CHUNK_SIZE: int = Config().file.chunk_size


class AsyncOutStream(IAsyncOutStream):
    path: str

    def __init__(self, path: str) -> None:
        self.path = path

    # pylint: disable=invalid-overridden-method
    async def __aiter__(self) -> AsyncIterator[bytes]:
        async with aiofiles.open(self.path, "rb") as stream:
            chunk: bytes = await stream.read(CHUNK_SIZE)
            while chunk:
                yield chunk
                chunk = await stream.read(CHUNK_SIZE)


@Bean()
class AsyncUploadFileService(IAsyncFileService):
    __prefix: str

    def __init__(self) -> None:
        self.__prefix = Config().file.prefix

    @AsyncLogging()
    async def save(self, file: File, stream: IAsyncInStream) -> None:
        async with aiofiles.open(f"{self.__prefix}/{file.uid}", "ab+") as in_stream:
            chunk: bytes = await stream.read(CHUNK_SIZE)
            while chunk:
                await in_stream.write(chunk)
                chunk = await stream.read(CHUNK_SIZE)

        await stream.close()

    @AsyncLogging()
    async def get_by_id(self, file: File) -> IAsyncOutStream:
        return AsyncOutStream(f"{self.__prefix}/{file.uid}")

    @AsyncLogging()
    async def delete(self, file: File) -> None:
        await aiofiles.os.remove(f"{self.__prefix}/{file.uid}")

from typing import AsyncGenerator
from logging import Logger

import aiofiles
import aiofiles.os
from spakky.bean.autowired import autowired
from spakky.bean.bean import Bean
from spakky.extensions.logging import AsyncLogging

from apps.file.domain.interfaces.service.file_service import IAsyncFileService
from apps.file.domain.models.file import File
from common.settings.config import Config

CHUNK_SIZE: int = Config().file.chunk_size


@Bean()
class AsyncUploadFileService(IAsyncFileService):
    __prefix: str
    __logger: Logger

    @autowired
    def __init__(self, logger: Logger) -> None:
        self.__prefix = Config().file.prefix
        self.__logger = logger

    @AsyncLogging()
    async def save(self, file: File, stream: AsyncGenerator[bytes, None]) -> None:
        self.__logger.info(f"save file: {file.uid} [0%]")
        async with aiofiles.open(f"{self.__prefix}/{file.uid}", "ab+") as in_stream:
            async for chunk in stream:
                await in_stream.write(chunk)

    @AsyncLogging()
    async def get_by_id(self, file: File) -> AsyncGenerator[bytes, None]:
        self.__logger.info(f"read file: {file.uid} [0%]")
        async with aiofiles.open(f"{self.__prefix}/{file.uid}", "rb") as stream:
            chunk: bytes = await stream.read(CHUNK_SIZE)
            while chunk:
                yield chunk
                chunk = await stream.read(CHUNK_SIZE)

    @AsyncLogging()
    async def delete(self, file: File) -> None:
        await aiofiles.os.remove(f"{self.__prefix}/{file.uid}")

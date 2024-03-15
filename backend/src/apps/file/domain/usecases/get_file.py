from typing import AsyncGenerator

from spakky.bean.autowired import autowired
from spakky.extensions.logging import AsyncLogging
from spakky.extensions.transactional import AsyncTransactional
from spakky.stereotype.usecase import UseCase

from apps.file.domain.errors import FileNameNotFoundError
from apps.file.domain.interfaces.event.publisher import IAsyncFileEventPublisher
from apps.file.domain.interfaces.persistency.repository import IAsyncFileRepository
from apps.file.domain.interfaces.service.file_service import IAsyncFileService
from apps.file.domain.interfaces.usecases.get_file import (
    GetFileQuery,
    IAsyncGetFileUseCase,
)
from apps.file.domain.models.file import File


@UseCase()
class AsyncGetFileUseCase(IAsyncGetFileUseCase):
    repository: IAsyncFileRepository
    event_publisher: IAsyncFileEventPublisher
    file_service: IAsyncFileService

    @autowired
    def __init__(
        self,
        repository: IAsyncFileRepository,
        event_publisher: IAsyncFileEventPublisher,
        file_service: IAsyncFileService,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher
        self.file_service = file_service

    @AsyncLogging()
    @AsyncTransactional()
    async def execute(
        self, query: GetFileQuery
    ) -> tuple[AsyncGenerator[bytes, None], str]:
        file: File | None = await self.repository.single_by_filename_or_none(
            query.filename
        )
        if file is None:
            raise FileNameNotFoundError(query.filename)
        return self.file_service.get_by_id(file), file.media_type

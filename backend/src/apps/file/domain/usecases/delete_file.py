from spakky.bean.autowired import autowired
from spakky.extensions.logging import AsyncLogging
from spakky.extensions.transactional import AsyncTransactional
from spakky.stereotype.usecase import UseCase

from apps.file.domain.errors import FileNameNotFoundError
from apps.file.domain.interfaces.event.publisher import IAsyncFileEventPublisher
from apps.file.domain.interfaces.persistency.repository import IAsyncFileRepository
from apps.file.domain.interfaces.service.file_service import IAsyncFileService
from apps.file.domain.interfaces.usecases.delete_file import (
    DeleteFileCommand,
    IAsyncDeleteFileUseCase,
)
from apps.file.domain.models.file import File


@UseCase()
class AsyncDeleteFileUseCase(IAsyncDeleteFileUseCase):
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
    async def execute(self, command: DeleteFileCommand) -> None:
        file: File | None = await self.repository.get_by_name_or_none(command.file_name)
        if file is None:
            raise FileNameNotFoundError(command.file_name)
        await self.file_service.delete(file)
        await self.repository.delete(file)
        await self.event_publisher.publish(file)

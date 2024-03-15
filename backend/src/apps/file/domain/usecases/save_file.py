from spakky.bean.autowired import autowired
from spakky.extensions.logging import AsyncLogging
from spakky.extensions.transactional import AsyncTransactional
from spakky.stereotype.usecase import UseCase

from apps.file.domain.errors import FileNameAlreadyExistsError
from apps.file.domain.interfaces.event.publisher import IAsyncFileEventPublisher
from apps.file.domain.interfaces.persistency.repository import IAsyncFileRepository
from apps.file.domain.interfaces.service.file_service import IAsyncFileService
from apps.file.domain.interfaces.usecases.save_file import (
    IAsyncSaveFileUseCase,
    SaveFileCommand,
)
from apps.file.domain.models.file import File


@UseCase()
class AsyncSaveFileUseCase(IAsyncSaveFileUseCase):
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
    async def execute(self, command: SaveFileCommand) -> None:
        if await self.repository.contains_by_filename(command.filename):
            raise FileNameAlreadyExistsError(command.filename)
        file: File = File.create(
            filename=command.filename,
            media_type=command.media_type,
        )
        await self.file_service.save(file, command.stream)
        await self.repository.save(file)
        await self.event_publisher.publish(file)

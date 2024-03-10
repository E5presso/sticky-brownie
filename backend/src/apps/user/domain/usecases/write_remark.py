from spakky.bean.autowired import autowired
from spakky.domain.ports.persistency.repository import EntityNotFoundError
from spakky.extensions.logging import AsyncLogging
from spakky.extensions.transactional import AsyncTransactional
from spakky.stereotype.usecase import UseCase

from apps.user.domain.errors import UserNotFoundError
from apps.user.domain.models.user import User
from apps.user.domain.ports.event.publisher import IAsyncUserEventPublisher
from apps.user.domain.ports.persistency.repository import IAsyncUserRepository
from apps.user.domain.ports.usecases.write_remark import (
    IAsyncWriteRemarkCommandUseCase,
    WriteRemarkCommand,
)


@UseCase()
class AsyncWriteRemarkCommandUseCase(IAsyncWriteRemarkCommandUseCase):
    repository: IAsyncUserRepository
    event_publisher: IAsyncUserEventPublisher

    @autowired
    def __init__(
        self,
        repository: IAsyncUserRepository,
        event_publisher: IAsyncUserEventPublisher,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher

    @AsyncLogging()
    @AsyncTransactional()
    async def execute(self, command: WriteRemarkCommand) -> None:
        try:
            user: User = await self.repository.single(command.user_id)
            user.write_remark(command.remark)
            await self.repository.save(user)
            await self.event_publisher.publish(user)
        except EntityNotFoundError as e:
            raise UserNotFoundError from e

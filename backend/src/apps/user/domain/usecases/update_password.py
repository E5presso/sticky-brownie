from spakky.bean.autowired import autowired
from spakky.domain.ports.persistency.repository import EntityNotFoundError
from spakky.extensions.logging import AsyncLogging
from spakky.extensions.transactional import AsyncTransactional
from spakky.stereotype.usecase import UseCase

from apps.user.domain.errors import UserNotFoundError
from apps.user.domain.interfaces.event.publisher import IAsyncUserEventPublisher
from apps.user.domain.interfaces.persistency.repository import IAsyncUserRepository
from apps.user.domain.interfaces.usecases.update_password import (
    IAsyncUpdatePasswordCommandUseCase,
    UpdatePasswordCommand,
)
from apps.user.domain.models.user import User


@UseCase()
class AsyncUpdatePasswordCommandUseCase(IAsyncUpdatePasswordCommandUseCase):
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
    async def execute(self, command: UpdatePasswordCommand) -> None:
        try:
            user: User = await self.repository.single(command.user_id)
            user.update_password(command.old_password, command.new_password)
            await self.repository.save(user)
            await self.event_publisher.publish(user)
        except EntityNotFoundError as e:
            raise UserNotFoundError from e

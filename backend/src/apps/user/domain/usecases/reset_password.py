from spakky.bean.autowired import autowired
from spakky.extensions.logging import AsyncLogging
from spakky.extensions.transactional import AsyncTransactional
from spakky.stereotype.usecase import UseCase

from apps.user.domain.errors import UserNotFoundError
from apps.user.domain.models.user import User
from apps.user.domain.ports.event.publisher import IAsyncUserEventPublisher
from apps.user.domain.ports.persistency.repository import IAsyncUserRepository
from apps.user.domain.ports.usecases.reset_password import (
    IAsyncResetPasswordCommandUseCase,
    ResetPasswordCommand,
)


@UseCase()
class AsyncResetPasswordCommandUseCase(IAsyncResetPasswordCommandUseCase):
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
    async def execute(self, command: ResetPasswordCommand) -> None:
        user: User | None = await self.repository.get_by_phone_number(
            command.username
        ) or await self.repository.get_by_phone_number(command.username)
        if user is None:
            raise UserNotFoundError
        user.reset_password(command.password_reset_token, command.new_password)
        await self.repository.save(user)
        await self.event_publisher.publish(user)

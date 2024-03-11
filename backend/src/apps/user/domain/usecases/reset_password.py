from spakky.bean.autowired import autowired
from spakky.extensions.logging import AsyncLogging
from spakky.extensions.transactional import AsyncTransactional
from spakky.stereotype.usecase import UseCase

from apps.user.domain.errors import UserNotFoundError
from apps.user.domain.interfaces.event.publisher import IAsyncUserEventPublisher
from apps.user.domain.interfaces.persistency.repository import IAsyncUserRepository
from apps.user.domain.interfaces.usecases.reset_password import (
    IAsyncResetPasswordCommandUseCase,
    ResetPasswordCommand,
)
from apps.user.domain.models.user import User


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
        user: User | None = await self.repository.get_by_phone_number_or_none(
            command.username
        ) or await self.repository.get_by_phone_number_or_none(command.username)
        if user is None:
            raise UserNotFoundError
        user.reset_password(command.password_reset_token, command.new_password)
        await self.repository.save(user)
        await self.event_publisher.publish(user)

from spakky.bean.autowired import autowired
from spakky.cryptography.key import Key
from spakky.extensions.logging import AsyncLogging
from spakky.extensions.transactional import AsyncTransactional
from spakky.stereotype.usecase import UseCase

from apps.user.domain.errors import UserNotFoundError
from apps.user.domain.models.user import User
from apps.user.domain.ports.event.publisher import IAsyncUserEventPublisher
from apps.user.domain.ports.persistency.repository import IAsyncUserRepository
from apps.user.domain.ports.usecases.forgot_password import (
    ForgotPasswordCommand,
    IAsyncForgotPasswordCommandUseCase,
)


@UseCase()
class AsyncForgotPasswordCommandUseCase(IAsyncForgotPasswordCommandUseCase):
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

    @AsyncLogging(masking_keys=["password", "token"])
    @AsyncTransactional()
    async def execute(self, command: ForgotPasswordCommand) -> None:
        user: User | None = await self.repository.get_by_username(
            command.username
        ) or await self.repository.get_by_phone_number(command.username)
        if user is None:
            raise UserNotFoundError
        user.forgot_password(Key(size=32).hex)
        await self.repository.save(user)
        await self.event_publisher.publish(user)

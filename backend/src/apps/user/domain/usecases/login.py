from spakky.bean.autowired import autowired
from spakky.cryptography.jwt import JWT
from spakky.extensions.logging import AsyncLogging
from spakky.extensions.transactional import AsyncTransactional
from spakky.stereotype.usecase import UseCase

from apps.user.domain.errors import AuthenticationFailedError
from apps.user.domain.models.user import User
from apps.user.domain.ports.event.publisher import IAsyncUserEventPublisher
from apps.user.domain.ports.persistency.repository import IAsyncUserRepository
from apps.user.domain.ports.service.token_service import IAsyncTokenService
from apps.user.domain.ports.usecases.login import (
    IAsyncLoginCommandUseCase,
    LoginCommand,
)


@UseCase()
class AsyncLoginCommandUseCase(IAsyncLoginCommandUseCase):
    repository: IAsyncUserRepository
    event_publisher: IAsyncUserEventPublisher
    token_service: IAsyncTokenService

    @autowired
    def __init__(
        self,
        repository: IAsyncUserRepository,
        event_publisher: IAsyncUserEventPublisher,
        token_service: IAsyncTokenService,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher
        self.token_service = token_service

    @AsyncLogging(masking_keys=["password", "token"])
    @AsyncTransactional()
    async def execute(self, command: LoginCommand) -> JWT:
        user: User | None = await self.repository.get_by_username(
            command.username
        ) or await self.repository.get_by_phone_number(command.username)
        if user is None:
            raise AuthenticationFailedError
        if user.login(command.password, command.ip_address, command.user_agent) is False:
            raise AuthenticationFailedError
        await self.repository.save(user)
        await self.event_publisher.publish(user)
        return await self.token_service.generate_token(user)

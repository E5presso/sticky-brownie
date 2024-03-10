from uuid import UUID
from datetime import datetime

from spakky.bean.autowired import autowired
from spakky.extensions.logging import AsyncLogging
from spakky.extensions.transactional import AsyncTransactional
from spakky.stereotype.usecase import UseCase

from apps.user.domain.errors import (
    CannotRegisterWithoutAgreementError,
    PhoneNumberAlreadyExistsError,
    UsernameAlreadyExistsError,
)
from apps.user.domain.models.user import User
from apps.user.domain.ports.event.publisher import IAsyncUserEventPublisher
from apps.user.domain.ports.persistency.repository import IAsyncUserRepository
from apps.user.domain.ports.usecases.create_user import (
    CreateUserCommand,
    IAsyncCreateUserUseCase,
)


@UseCase()
class CreateUserUseCase(IAsyncCreateUserUseCase):
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
    async def execute(self, command: CreateUserCommand) -> UUID:
        username_exists: bool = await self.repository.contains_by_username(
            command.username
        )
        phone_number_exists: bool = await self.repository.contains_by_phone_number(
            command.phone_number
        )
        if username_exists:
            raise UsernameAlreadyExistsError
        if phone_number_exists:
            raise PhoneNumberAlreadyExistsError
        if command.terms_and_conditions_agreement is False:
            raise CannotRegisterWithoutAgreementError
        user: User = User.create(
            username=command.username,
            password=command.password,
            role=command.role,
            name=command.name,
            address=command.address,
            phone_number=command.phone_number,
            gender=command.gender,
            birth_date=command.birth_date,
            billing_name=command.billing_name,
            terms_and_conditions_agreement=datetime.utcnow(),
            marketing_promotions_agreement=(
                datetime.utcnow()
                if command.marketing_promotions_agreement is True
                else None
            ),
        )
        await self.repository.save(user)
        await self.event_publisher.publish(user)
        return user.uid

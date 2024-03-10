from spakky.bean.autowired import autowired
from spakky.domain.ports.persistency.repository import EntityNotFoundError
from spakky.extensions.logging import AsyncLogging
from spakky.extensions.transactional import AsyncTransactional
from spakky.stereotype.usecase import UseCase

from apps.user.domain.errors import UserNotFoundError
from apps.user.domain.models.user import User
from apps.user.domain.ports.event.publisher import IAsyncUserEventPublisher
from apps.user.domain.ports.persistency.repository import IAsyncUserRepository
from apps.user.domain.ports.usecases.get_me import (
    GetMeQuery,
    GetMeResult,
    IAsyncGetMeQueryUseCase,
)


@UseCase()
class AsyncGetMeQueryUseCase(IAsyncGetMeQueryUseCase):
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
    async def execute(self, query: GetMeQuery) -> GetMeResult:
        try:
            user: User = await self.repository.single(query.user_id)
            return GetMeResult(
                user_id=user.uid,
                name=user.name,
                phone_number=user.phone_number,
                address=user.address,
                gender=user.gender,
                birth_date=user.birth_date,
                billing_name=user.billing_name,
            )
        except EntityNotFoundError as e:
            raise UserNotFoundError from e

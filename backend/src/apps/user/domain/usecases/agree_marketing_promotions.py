from spakky.bean.autowired import autowired
from spakky.domain.ports.persistency.repository import EntityNotFoundError
from spakky.extensions.logging import AsyncLogging
from spakky.extensions.transactional import AsyncTransactional
from spakky.stereotype.usecase import UseCase

from apps.user.domain.errors import UserNotFoundError
from apps.user.domain.interfaces.event.publisher import IAsyncUserEventPublisher
from apps.user.domain.interfaces.persistency.repository import IAsyncUserRepository
from apps.user.domain.interfaces.usecases.agree_marketing_promotions import (
    AgreeMarketingPromotionsCommand,
    IAsyncAgreeMarketingPromotionsCommandUseCase,
)
from apps.user.domain.models.user import User


@UseCase()
class AsyncAgreeMarketingPromotionsCommandUseCase(
    IAsyncAgreeMarketingPromotionsCommandUseCase
):
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
    async def execute(self, command: AgreeMarketingPromotionsCommand) -> None:
        try:
            user: User = await self.repository.single(command.user_id)
            if command.agreed is True:
                user.agree_marketing_promotions()
            else:
                user.disagree_marketing_promotions()
            await self.repository.save(user)
            await self.event_publisher.publish(user)
        except EntityNotFoundError as e:
            raise UserNotFoundError from e

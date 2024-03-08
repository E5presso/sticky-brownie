from spakky.bean.autowired import autowired
from spakky.domain.ports.persistency.repository import EntityNotFoundError
from spakky.extensions.logging import AsyncLogging
from spakky.extensions.transactional import AsyncTransactional
from spakky.stereotype.usecase import UseCase

from apps.user.domain.errors import UserNotFoundError
from apps.user.domain.models.user import User
from apps.user.domain.ports.event.publisher import IAsyncUserEventPublisher
from apps.user.domain.ports.persistency.repository import IAsyncUserRepository
from apps.user.domain.ports.usecases.agree_marketing_promotions import (
    AgreeMarketingPromotionsCommand,
    IAsyncAgreeMarketingPromotionsCommandUseCase,
)


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

    @AsyncLogging(masking_keys=["password", "token"])
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

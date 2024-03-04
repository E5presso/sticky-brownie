from uuid import UUID
from typing import Protocol

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase


@immutable
class AgreeMarketingPromotionsCommand(Command):
    user_id: UUID
    agreed: bool


class IAsyncAgreeMarketingPromotionsCommandUseCase(
    IAsyncCommandUseCase[AgreeMarketingPromotionsCommand, None], Protocol
): ...

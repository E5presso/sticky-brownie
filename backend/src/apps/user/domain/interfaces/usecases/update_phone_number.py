from uuid import UUID
from typing import Protocol

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase


@immutable
class UpdatePhoneNumberCommand(Command):
    user_id: UUID
    phone_number: str


class IAsyncUpdatePhoneNumberCommandUseCase(
    IAsyncCommandUseCase[UpdatePhoneNumberCommand, None], Protocol
): ...

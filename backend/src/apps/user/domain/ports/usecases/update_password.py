from uuid import UUID
from typing import Protocol

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase


@immutable
class UpdatePasswordCommand(Command):
    user_id: UUID
    old_password: str
    new_password: str


class IAsyncUpdatePasswordCommandUseCase(
    IAsyncCommandUseCase[UpdatePasswordCommand, None], Protocol
): ...

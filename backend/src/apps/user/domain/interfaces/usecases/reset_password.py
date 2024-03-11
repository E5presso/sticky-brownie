from typing import Protocol

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase


@immutable
class ResetPasswordCommand(Command):
    username: str
    password_reset_token: str
    new_password: str


class IAsyncResetPasswordCommandUseCase(
    IAsyncCommandUseCase[ResetPasswordCommand, None], Protocol
): ...

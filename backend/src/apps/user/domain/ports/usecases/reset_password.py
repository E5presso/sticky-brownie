from typing import Protocol

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase


@immutable
class ResetPasswordCommand(Command):
    phone_number: str | None
    account_name: str | None
    password_reset_token: str


class IAsyncResetPasswordCommandUseCase(
    IAsyncCommandUseCase[ResetPasswordCommand, None], Protocol
): ...

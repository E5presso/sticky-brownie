from typing import Protocol

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase


@immutable
class ForgotPasswordCommand(Command):
    phone_number: str | None
    account_name: str | None


class IAsyncForgotPasswordCommandUseCase(
    IAsyncCommandUseCase[ForgotPasswordCommand, None], Protocol
): ...

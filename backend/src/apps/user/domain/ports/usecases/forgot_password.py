from typing import Protocol

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase


@immutable
class ForgotPasswordCommand(Command):
    username: str


class IAsyncForgotPasswordCommandUseCase(
    IAsyncCommandUseCase[ForgotPasswordCommand, None], Protocol
): ...

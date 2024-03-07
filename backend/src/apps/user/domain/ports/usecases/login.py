from typing import Protocol

from spakky.core.mutability import immutable
from spakky.cryptography.jwt import JWT
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase


@immutable
class LoginCommand(Command):
    username: str
    password: str
    ip_address: str
    user_agent: str


class IAsyncLoginCommandUseCase(IAsyncCommandUseCase[LoginCommand, JWT], Protocol): ...

from typing import Protocol

from spakky.core.mutability import immutable
from spakky.cryptography.jwt import JWT
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase


@immutable
class LoginCommand(Command):
    phone_number: str | None
    account_name: str | None
    password: str
    ip_address: str
    user_agent: str


class IAsyncLoginCommandUseCase(IAsyncCommandUseCase[LoginCommand, JWT], Protocol): ...

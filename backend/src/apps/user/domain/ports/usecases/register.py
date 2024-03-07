from typing import Protocol
from datetime import date

from spakky.core.mutability import immutable
from spakky.cryptography.jwt import JWT
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase

from apps.user.domain.models.gender import Gender


@immutable
class RegisterCommand(Command):
    username: str
    password: str
    name: str
    address: str
    phone_number: str
    gender: Gender
    birth_date: date
    billing_name: str
    terms_and_conditions_agreement: bool
    marketing_promotions_agreement: bool


class IAsyncRegisterCommandUseCase(
    IAsyncCommandUseCase[RegisterCommand, JWT], Protocol
): ...

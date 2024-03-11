from uuid import UUID
from typing import Protocol
from datetime import date

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase

from common.enums.gender import Gender
from common.enums.user_role import UserRole


@immutable
class CreateUserCommand(Command):
    username: str
    password: str
    role: UserRole
    name: str
    address: str
    phone_number: str
    gender: Gender
    birth_date: date
    billing_name: str
    terms_and_conditions_agreement: bool
    marketing_promotions_agreement: bool


class IAsyncCreateUserUseCase(
    IAsyncCommandUseCase[CreateUserCommand, UUID], Protocol
): ...

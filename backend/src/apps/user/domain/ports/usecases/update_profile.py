from uuid import UUID
from typing import Protocol
from datetime import date

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase

from apps.user.domain.models.gender import Gender


@immutable
class UpdateProfileCommand(Command):
    user_id: UUID
    name: str
    address: str
    gender: Gender
    birth_date: date
    billing_name: str


class IAsyncUpdateProfilePasswordCommandUseCase(
    IAsyncCommandUseCase[UpdateProfileCommand, None], Protocol
): ...

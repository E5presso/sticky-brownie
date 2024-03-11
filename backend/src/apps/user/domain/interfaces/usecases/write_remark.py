from uuid import UUID
from typing import Protocol

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase


@immutable
class WriteRemarkCommand(Command):
    user_id: UUID
    remark: str


class IAsyncWriteRemarkCommandUseCase(
    IAsyncCommandUseCase[WriteRemarkCommand, None], Protocol
): ...

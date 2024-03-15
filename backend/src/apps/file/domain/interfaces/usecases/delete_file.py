from typing import Protocol

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase


@immutable
class DeleteFileCommand(Command):
    filename: str


class IAsyncDeleteFileUseCase(
    IAsyncCommandUseCase[DeleteFileCommand, None], Protocol
): ...

from typing import Protocol, AsyncGenerator

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase


@immutable
class SaveFileCommand(Command):
    filename: str
    media_type: str
    stream: AsyncGenerator[bytes, None]


class IAsyncSaveFileUseCase(IAsyncCommandUseCase[SaveFileCommand, None], Protocol): ...

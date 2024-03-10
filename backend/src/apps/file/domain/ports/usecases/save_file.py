from typing import Protocol

from spakky.core.mutability import immutable
from spakky.domain.usecases.command import Command, IAsyncCommandUseCase

from apps.file.domain.ports.service.file_service import IAsyncInStream


@immutable
class SaveFileCommand(Command):
    file_name: str
    media_type: str
    stream: IAsyncInStream


class IAsyncSaveFileUseCase(IAsyncCommandUseCase[SaveFileCommand, None], Protocol): ...

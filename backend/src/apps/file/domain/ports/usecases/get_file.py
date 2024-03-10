from typing import Protocol

from spakky.core.mutability import immutable
from spakky.domain.usecases.query import IAsyncQueryUseCase, Query

from apps.file.domain.ports.service.file_service import IAsyncOutStream


@immutable
class GetFileQuery(Query):
    file_name: str


class IAsyncGetFileUseCase(
    IAsyncQueryUseCase[GetFileQuery, tuple[IAsyncOutStream, str]], Protocol
): ...

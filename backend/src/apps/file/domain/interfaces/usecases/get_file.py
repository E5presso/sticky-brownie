from typing import Protocol, AsyncGenerator

from spakky.core.mutability import immutable
from spakky.domain.usecases.query import IAsyncQueryUseCase, Query


@immutable
class GetFileQuery(Query):
    filename: str


class IAsyncGetFileUseCase(
    IAsyncQueryUseCase[GetFileQuery, tuple[AsyncGenerator[bytes, None], str]], Protocol
): ...

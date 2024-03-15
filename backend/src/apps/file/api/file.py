from fastapi import status
from fastapi.responses import StreamingResponse
from spakky.bean.autowired import autowired
from spakky.extensions.logging import AsyncLogging
from spakky_fastapi.error import NotFound
from spakky_fastapi.routing import get
from spakky_fastapi.stereotypes.api_controller import ApiController

from apps.file.domain.errors import FileNameNotFoundError
from apps.file.domain.interfaces.usecases.get_file import (
    GetFileQuery,
    IAsyncGetFileUseCase,
)
from common.enums.api_catetory import ApiCatetory


@ApiController("/files", tags=[ApiCatetory.FILES])
class FilesRestApiController:
    get_file: IAsyncGetFileUseCase

    @autowired
    def __init__(
        self,
        get_file: IAsyncGetFileUseCase,
    ) -> None:
        self.get_file = get_file

    @AsyncLogging()
    @get(
        "/{filename}",
        name="파일 조회",
        response_class=StreamingResponse,
        status_code=status.HTTP_200_OK,
    )
    async def get_file_api(self, filename: str) -> StreamingResponse:
        try:
            stream, media_type = await self.get_file.execute(
                GetFileQuery(filename=filename)
            )
            return StreamingResponse(
                stream,
                status_code=status.HTTP_200_OK,
                media_type=media_type,
            )
        except FileNameNotFoundError as e:
            raise NotFound(error=e) from e

from fastapi import Request, status
from multipart.multipart import parse_options_header
from pydantic import BaseModel
from spakky.bean.autowired import autowired
from spakky.cryptography.jwt import JWT
from spakky.extensions.logging import AsyncLogging
from spakky_fastapi.error import BadRequest, Conflict, NotFound
from spakky_fastapi.jwt_auth import JWTAuth
from spakky_fastapi.routing import delete, post
from spakky_fastapi.stereotypes.api_controller import ApiController

from apps.file.domain.errors import (
    FileNameAlreadyExistsError,
    FileNameMustNotBeEmptyError,
    FileNameNotFoundError,
    MediaTypeMustNotBeEmptyError,
)
from apps.file.domain.interfaces.usecases.delete_file import (
    DeleteFileCommand,
    IAsyncDeleteFileUseCase,
)
from apps.file.domain.interfaces.usecases.save_file import (
    IAsyncSaveFileUseCase,
    SaveFileCommand,
)
from common.aspects.authorize import Authorize
from common.enums.api_catetory import ApiCatetory
from common.enums.user_role import UserRole
from common.settings.config import Config
from common.utils.singlepart import AsyncSinglePartStream, FileInfo

LOGIN_URL = Config().token.login_url


class FileSaveResponse(BaseModel):
    url: str


@ApiController("/backoffice/files", tags=[ApiCatetory.BACKOFFICE])
class FileManageRestApiController:
    save_file: IAsyncSaveFileUseCase
    delete_file: IAsyncDeleteFileUseCase

    @autowired
    def __init__(
        self,
        save_file: IAsyncSaveFileUseCase,
        delete_file: IAsyncDeleteFileUseCase,
    ) -> None:
        self.save_file = save_file
        self.delete_file = delete_file

    @AsyncLogging()
    @JWTAuth(LOGIN_URL)
    @Authorize({UserRole.BACKOFFICER})
    @post(
        "",
        name="파일 등록",
        status_code=status.HTTP_201_CREATED,
        openapi_extra={
            "requestBody": {
                "content": {
                    "multipart/form-data": {
                        "schema": {
                            "required": ["file"],
                            "type": "object",
                            "properties": {
                                "file": {"type": "file"},
                            },
                        }
                    }
                },
                "required": True,
            },
        },
    )
    async def save_file_api(self, _: JWT, request: Request) -> FileSaveResponse:
        content_type: str | None = request.headers.get("content-type")
        if content_type is None:
            raise BadRequest(MediaTypeMustNotBeEmptyError())
        __, params = parse_options_header(content_type)
        boundary = params.get(b"boundary")
        if boundary is None:
            raise BadRequest(MediaTypeMustNotBeEmptyError())
        stream = AsyncSinglePartStream(boundary, request.stream())
        field_data: FileInfo = await stream.get_file_info()
        if field_data.filename is None:
            raise BadRequest(FileNameMustNotBeEmptyError())
        if field_data.content_type is None:
            raise BadRequest(MediaTypeMustNotBeEmptyError())
        try:
            await self.save_file.execute(
                SaveFileCommand(
                    filename=field_data.filename,
                    media_type=field_data.content_type,
                    stream=stream.stream(),
                )
            )
            return FileSaveResponse(url=f"/files/{field_data.filename}")
        except FileNameAlreadyExistsError as e:
            raise Conflict(error=e) from e

    @AsyncLogging()
    @JWTAuth(LOGIN_URL)
    @Authorize({UserRole.BACKOFFICER})
    @delete("/{filename}", name="파일 삭제", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_file_api(self, _: JWT, filename: str) -> None:
        try:
            await self.delete_file.execute(DeleteFileCommand(filename=filename))
        except FileNameNotFoundError as e:
            raise NotFound(error=e) from e

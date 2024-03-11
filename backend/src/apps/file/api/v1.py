from fastapi import File, Path, UploadFile, status
from fastapi.responses import ORJSONResponse, StreamingResponse
from spakky.bean.autowired import autowired
from spakky.cryptography.jwt import JWT
from spakky.extensions.logging import AsyncLogging
from spakky.stereotype.controller import Controller
from spakky_fastapi.error import BadRequest, Conflict, NotFound
from spakky_fastapi.jwt_auth import JWTAuth
from spakky_fastapi.middlewares.error_handling import ErrorResponse
from spakky_fastapi.routing import delete, get, post

from apps.file.domain.errors import (
    FileNameAlreadyExistsError,
    FileNameMustNotBeEmptyError,
    FileNameNotFoundError,
    MediaTypeMustNotBeEmptyError,
)
from apps.file.domain.ports.usecases.delete_file import (
    DeleteFileCommand,
    IAsyncDeleteFileUseCase,
)
from apps.file.domain.ports.usecases.get_file import GetFileQuery, IAsyncGetFileUseCase
from apps.file.domain.ports.usecases.save_file import (
    IAsyncSaveFileUseCase,
    SaveFileCommand,
)
from common.aspects.authorize import Authorize
from common.enums.user_role import UserRole
from common.settings.config import Config


@Controller("/files")
class FileRestApiController:
    save_file: IAsyncSaveFileUseCase
    get_file: IAsyncGetFileUseCase
    delete_file: IAsyncDeleteFileUseCase

    @autowired
    def __init__(
        self,
        save_file: IAsyncSaveFileUseCase,
        get_file: IAsyncGetFileUseCase,
        delete_file: IAsyncDeleteFileUseCase,
    ) -> None:
        self.save_file = save_file
        self.get_file = get_file
        self.delete_file = delete_file

    @AsyncLogging()
    @JWTAuth(token_url=Config().token.login_url)
    @Authorize({UserRole.BACKOFFICER})
    @post(
        "",
        responses={
            status.HTTP_201_CREATED: {"model": None},
            status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
            status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
            status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
            status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        },
    )
    async def save_file_api(
        self,
        token: JWT,  # pylint: disable=unused-argument
        file: UploadFile = File(),
    ):
        if file.filename is None:
            raise BadRequest(FileNameMustNotBeEmptyError())
        if file.content_type is None:
            raise BadRequest(MediaTypeMustNotBeEmptyError())
        try:
            await self.save_file.execute(
                SaveFileCommand(
                    file_name=file.filename,
                    media_type=file.content_type,
                    stream=file,
                )
            )
            return ORJSONResponse(status_code=status.HTTP_201_CREATED, content=None)
        except FileNameAlreadyExistsError as e:
            raise Conflict(error=e) from e

    @AsyncLogging()
    @get(
        "/{file_name}",
        response_class=StreamingResponse,
        responses={
            status.HTTP_200_OK: {"model": None},
            status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        },
    )
    async def get_file_api(self, file_name: str):
        try:
            stream, media_type = await self.get_file.execute(
                GetFileQuery(file_name=file_name)
            )
            return StreamingResponse(
                stream,
                status_code=status.HTTP_200_OK,
                media_type=media_type,
            )
        except FileNameNotFoundError as e:
            raise NotFound(error=e) from e

    @AsyncLogging()
    @JWTAuth(token_url=Config().token.login_url)
    @Authorize({UserRole.BACKOFFICER})
    @delete(
        "/{file_name}",
        response_class=ORJSONResponse,
        responses={
            status.HTTP_200_OK: {"model": None},
            status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
            status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
            status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        },
    )
    async def delete_file_api(
        self,
        token: JWT,  # pylint: disable=unused-argument
        file_name: str = Path(),
    ):
        try:
            await self.delete_file.execute(DeleteFileCommand(file_name=file_name))
            return ORJSONResponse(status_code=status.HTTP_200_OK, content=None)
        except FileNameNotFoundError as e:
            raise NotFound(error=e) from e

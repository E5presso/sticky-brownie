from fastapi import File, UploadFile, status
from fastapi.responses import ORJSONResponse, StreamingResponse
from spakky.bean.autowired import autowired
from spakky.cryptography.jwt import JWT
from spakky.extensions.logging import AsyncLogging
from spakky.stereotype.controller import Controller
from spakky_fastapi.jwt_auth import JWTAuth
from spakky_fastapi.routing import get, post

from apps.file.domain.errors import FileNameAlreadyExistsError, FileNameNotFoundError
from apps.file.domain.ports.usecases.get_file import GetFileQuery, IAsyncGetFileUseCase
from apps.file.domain.ports.usecases.save_file import (
    IAsyncSaveFileUseCase,
    SaveFileCommand,
)
from common.aspects.authorize import Authorize
from common.enums.user_role import UserRole
from common.schemas.error_response import ErrorResponse
from common.settings.config import Config


@Controller("/files")
class FileRestApiController:
    save_file: IAsyncSaveFileUseCase
    get_file: IAsyncGetFileUseCase

    @autowired
    def __init__(
        self,
        save_file: IAsyncSaveFileUseCase,
        get_file: IAsyncGetFileUseCase,
    ) -> None:
        self.save_file = save_file
        self.get_file = get_file

    @AsyncLogging()
    @JWTAuth(token_url=Config().token.login_url)
    @Authorize({UserRole.BACKOFFICER})
    @post(
        "",
        responses={
            status.HTTP_201_CREATED: {"model": None},
            status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
            status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
            status.HTTP_403_FORBIDDEN: {"model": None},
            status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        },
    )
    async def save_file_api(
        self,
        token: JWT,  # pylint: disable=unused-argument
        file: UploadFile = File(),
    ):
        if file.filename is None:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ErrorResponse(
                    message="File name is required",
                ).model_dump(),
            )
        if file.content_type is None:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ErrorResponse(
                    message="File content-type is required",
                ).model_dump(),
            )
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
            return ORJSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=ErrorResponse(
                    message=e.message,
                ).model_dump(),
            )

    @AsyncLogging()
    @get(
        "/{file_name}",
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
                stream, status_code=status.HTTP_200_OK, media_type=media_type
            )
        except FileNameNotFoundError as e:
            return ORJSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(
                    message=e.message,
                ).model_dump(),
            )

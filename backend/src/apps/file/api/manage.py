from fastapi import File, Path, UploadFile, status
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

LOGIN_URL = Config().token.login_url


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
    @Authorize({UserRole.BACKOFFICER, UserRole.USER})
    @post("", name="파일 등록", status_code=status.HTTP_201_CREATED)
    async def save_file_api(
        self, token: JWT, file: UploadFile = File()  # pylint: disable=unused-argument
    ) -> None:
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
        except FileNameAlreadyExistsError as e:
            raise Conflict(error=e) from e

    @AsyncLogging()
    @JWTAuth(LOGIN_URL)
    @Authorize({UserRole.BACKOFFICER})
    @delete("/{file_name}", name="파일 삭제", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_file_api(
        self, token: JWT, file_name: str = Path()  # pylint: disable=unused-argument
    ) -> None:
        try:
            await self.delete_file.execute(DeleteFileCommand(file_name=file_name))
        except FileNameNotFoundError as e:
            raise NotFound(error=e) from e

from uuid import UUID
from datetime import date

from fastapi import Body, Path, status
from pydantic import BaseModel
from spakky.bean.autowired import autowired
from spakky.cryptography.jwt import JWT
from spakky.extensions.logging import AsyncLogging
from spakky_fastapi.error import Conflict, NotFound
from spakky_fastapi.jwt_auth import JWTAuth
from spakky_fastapi.routing import post, put
from spakky_fastapi.stereotypes.api_controller import ApiController

from apps.user.domain.errors import (
    PhoneNumberAlreadyExistsError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)
from apps.user.domain.interfaces.usecases.create_user import (
    CreateUserCommand,
    IAsyncCreateUserUseCase,
)
from apps.user.domain.interfaces.usecases.write_remark import (
    IAsyncWriteRemarkCommandUseCase,
    WriteRemarkCommand,
)
from common.aspects.authorize import Authorize
from common.enums.api_catetory import ApiCatetory
from common.enums.gender import Gender
from common.enums.user_role import UserRole
from common.settings.config import Config

LOGIN_URL = Config().token.login_url


class CreateUser(BaseModel):
    username: str
    password: str
    role: UserRole
    name: str
    address: str
    phone_number: str
    gender: Gender
    birth_date: date
    billing_name: str
    terms_and_conditions_agreement: bool
    marketing_promotions_agreement: bool


class WriteRemark(BaseModel):
    remark: str


@ApiController("/backoffice/users", tags=[ApiCatetory.BACKOFFICE])
class UserManageRestApiController:
    write_remark: IAsyncWriteRemarkCommandUseCase
    create_user: IAsyncCreateUserUseCase

    @autowired
    def __init__(
        self,
        write_remark: IAsyncWriteRemarkCommandUseCase,
        create_user: IAsyncCreateUserUseCase,
    ) -> None:
        self.write_remark = write_remark
        self.create_user = create_user

    @AsyncLogging()
    @JWTAuth(LOGIN_URL)
    @Authorize({UserRole.BACKOFFICER})
    @put("/{user_id}/remark", name="사용자 주석 추가", status_code=status.HTTP_200_OK)
    async def write_remark_api(
        self,
        token: JWT,  # pylint: disable=unused-argument
        user_id: UUID = Path(),
        request: WriteRemark = Body(),
    ) -> None:
        try:
            await self.write_remark.execute(
                WriteRemarkCommand(
                    user_id=user_id,
                    remark=request.remark,
                )
            )
        except UserNotFoundError as e:
            raise NotFound(error=e) from e

    @AsyncLogging()
    @JWTAuth(LOGIN_URL)
    @Authorize({UserRole.BACKOFFICER})
    @post("", name="사용자 추가", status_code=status.HTTP_201_CREATED)
    async def create_user_api(
        self, token: JWT, request: CreateUser = Body()  # pylint: disable=unused-argument
    ) -> None:
        try:
            await self.create_user.execute(
                CreateUserCommand(
                    username=request.username,
                    password=request.password,
                    role=request.role,
                    name=request.name,
                    address=request.address,
                    phone_number=request.phone_number,
                    gender=request.gender,
                    birth_date=request.birth_date,
                    billing_name=request.billing_name,
                    terms_and_conditions_agreement=request.terms_and_conditions_agreement,
                    marketing_promotions_agreement=request.marketing_promotions_agreement,
                )
            )
        except UsernameAlreadyExistsError as e:
            raise Conflict(error=e) from e
        except PhoneNumberAlreadyExistsError as e:
            raise Conflict(error=e) from e

from uuid import UUID
from datetime import date

from fastapi import Body, Depends, Header, Path, status
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from spakky.bean.autowired import autowired
from spakky.cryptography.jwt import JWT
from spakky.extensions.logging import AsyncLogging
from spakky.stereotype.controller import Controller
from spakky_fastapi.jwt_auth import JWTAuth
from spakky_fastapi.routing import get, post, put

from apps.user.domain.errors import (
    AuthenticationFailedError,
    CannotRegisterWithoutAgreementError,
    InvalidPasswordResetTokenError,
    PhoneNumberAlreadyExistsError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)
from apps.user.domain.ports.usecases.agree_marketing_promotions import (
    AgreeMarketingPromotionsCommand,
    IAsyncAgreeMarketingPromotionsCommandUseCase,
)
from apps.user.domain.ports.usecases.create_user import (
    CreateUserCommand,
    IAsyncCreateUserUseCase,
)
from apps.user.domain.ports.usecases.forgot_password import (
    ForgotPasswordCommand,
    IAsyncForgotPasswordCommandUseCase,
)
from apps.user.domain.ports.usecases.get_me import GetMeQuery, IAsyncGetMeQueryUseCase
from apps.user.domain.ports.usecases.login import (
    IAsyncLoginCommandUseCase,
    LoginCommand,
)
from apps.user.domain.ports.usecases.register import (
    IAsyncRegisterCommandUseCase,
    RegisterCommand,
)
from apps.user.domain.ports.usecases.reset_password import (
    IAsyncResetPasswordCommandUseCase,
    ResetPasswordCommand,
)
from apps.user.domain.ports.usecases.update_password import (
    IAsyncUpdatePasswordCommandUseCase,
    UpdatePasswordCommand,
)
from apps.user.domain.ports.usecases.update_phone_number import (
    IAsyncUpdatePhoneNumberCommandUseCase,
    UpdatePhoneNumberCommand,
)
from apps.user.domain.ports.usecases.update_profile import (
    IAsyncUpdateProfilePasswordCommandUseCase,
    UpdateProfileCommand,
)
from apps.user.domain.ports.usecases.write_remark import (
    IAsyncWriteRemarkCommandUseCase,
    WriteRemarkCommand,
)
from common.aspects.authorize import Authorize
from common.enums.gender import Gender
from common.enums.user_role import UserRole
from common.schemas.error_response import ErrorResponse
from common.settings.config import Config


class Register(BaseModel):
    username: str
    password: str
    name: str
    address: str
    phone_number: str
    gender: Gender
    birth_date: date
    billing_name: str
    terms_and_conditions_agreement: bool
    marketing_promotions_agreement: bool


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


class Login(BaseModel):
    username: str
    password: str


class ResetPassword(BaseModel):
    new_password: str


class UpdatePassword(BaseModel):
    old_password: str
    new_password: str


class UpdatePhoneNumber(BaseModel):
    phone_number: str


class UpdateProfile(BaseModel):
    name: str
    address: str
    gender: Gender
    birth_date: date
    billing_name: str


class WriteRemark(BaseModel):
    remark: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class GetMeResponse(BaseModel):
    user_id: UUID
    name: str
    phone_number: str
    address: str
    gender: Gender
    birth_date: date
    billing_name: str


class MarketingPromotionsAgreement(BaseModel):
    agreed: bool


@Controller("/users")
class UserRestApiController:
    agree_marketing_promotions: IAsyncAgreeMarketingPromotionsCommandUseCase
    forgot_password: IAsyncForgotPasswordCommandUseCase
    login: IAsyncLoginCommandUseCase
    register: IAsyncRegisterCommandUseCase
    reset_password: IAsyncResetPasswordCommandUseCase
    update_password: IAsyncUpdatePasswordCommandUseCase
    update_phone_number: IAsyncUpdatePhoneNumberCommandUseCase
    update_profile: IAsyncUpdateProfilePasswordCommandUseCase
    write_remark: IAsyncWriteRemarkCommandUseCase
    create_user: IAsyncCreateUserUseCase
    get_me: IAsyncGetMeQueryUseCase

    @autowired
    def __init__(
        self,
        agree_marketing_promotions: IAsyncAgreeMarketingPromotionsCommandUseCase,
        forgot_password: IAsyncForgotPasswordCommandUseCase,
        login: IAsyncLoginCommandUseCase,
        register: IAsyncRegisterCommandUseCase,
        reset_password: IAsyncResetPasswordCommandUseCase,
        update_password: IAsyncUpdatePasswordCommandUseCase,
        update_phone_number: IAsyncUpdatePhoneNumberCommandUseCase,
        update_profile: IAsyncUpdateProfilePasswordCommandUseCase,
        write_remark: IAsyncWriteRemarkCommandUseCase,
        create_user: IAsyncCreateUserUseCase,
        get_me: IAsyncGetMeQueryUseCase,
    ) -> None:
        self.agree_marketing_promotions = agree_marketing_promotions
        self.forgot_password = forgot_password
        self.login = login
        self.register = register
        self.reset_password = reset_password
        self.update_password = update_password
        self.update_phone_number = update_phone_number
        self.update_profile = update_profile
        self.write_remark = write_remark
        self.create_user = create_user
        self.get_me = get_me

    @AsyncLogging()
    @JWTAuth(token_url=Config().token.login_url)
    @put(
        "/me/marketing-promotions-agreement",
        status_code=status.HTTP_200_OK,
        response_model=None,
        responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
    )
    async def agree_marketing_promotions_api(
        self, token: JWT, request: MarketingPromotionsAgreement
    ):
        try:
            await self.agree_marketing_promotions.execute(
                AgreeMarketingPromotionsCommand(
                    user_id=UUID(token.payload["sub"]),
                    agreed=request.agreed,
                )
            )
            return ORJSONResponse(
                status_code=status.HTTP_200_OK,
                content=None,
            )
        except UserNotFoundError as e:
            return ORJSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(message=e.message).model_dump(),
            )

    @AsyncLogging()
    @put(
        "/{username}/password/forgot",
        status_code=status.HTTP_200_OK,
        response_model=None,
        responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
    )
    async def forgot_password_api(self, username: str):
        try:
            await self.forgot_password.execute(ForgotPasswordCommand(username=username))
            return ORJSONResponse(
                status_code=status.HTTP_200_OK,
                content=None,
            )
        except UserNotFoundError as e:
            return ORJSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(message=e.message).model_dump(),
            )

    @AsyncLogging()
    @post(
        "/login",
        status_code=status.HTTP_200_OK,
        response_model=TokenResponse,
        responses={status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse}},
    )
    async def login_api(
        self,
        request: OAuth2PasswordRequestForm = Depends(),
        x_forwarded_for: str | None = Header(default=None),
        ip_address: str | None = Header(default=None),
        user_agent: str | None = Header(default=None),
    ):
        try:
            token: JWT = await self.login.execute(
                command=LoginCommand(
                    username=request.username,
                    password=request.password,
                    ip_address=x_forwarded_for or ip_address or "0.0.0.0",
                    user_agent=user_agent or "Unknown",
                )
            )
            return ORJSONResponse(
                status_code=status.HTTP_201_CREATED,
                content=TokenResponse(
                    access_token=token.export(),
                    token_type="bearer",
                ).model_dump(),
            )
        except AuthenticationFailedError as e:
            return ORJSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=ErrorResponse(message=e.message).model_dump(),
            )

    @AsyncLogging()
    @post(
        "/register",
        status_code=status.HTTP_201_CREATED,
        response_model=TokenResponse,
        responses={
            status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
            status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        },
    )
    async def register_api(self, request: Register):
        try:
            token: JWT = await self.register.execute(
                command=RegisterCommand(
                    username=request.username,
                    password=request.password,
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
            return ORJSONResponse(
                status_code=status.HTTP_201_CREATED,
                content=TokenResponse(
                    access_token=token.export(),
                    token_type="bearer",
                ).model_dump(),
            )
        except UsernameAlreadyExistsError as e:
            return ORJSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=ErrorResponse(message=e.message).model_dump(),
            )
        except PhoneNumberAlreadyExistsError as e:
            return ORJSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=ErrorResponse(message=e.message).model_dump(),
            )
        except CannotRegisterWithoutAgreementError as e:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ErrorResponse(message=e.message).model_dump(),
            )

    @AsyncLogging()
    @put("/{username}/password/{password_reset_token}")
    async def reset_password_api(
        self,
        username: str,
        password_reset_token: str,
        request: ResetPassword,
    ):
        try:
            await self.reset_password.execute(
                ResetPasswordCommand(
                    username=username,
                    password_reset_token=password_reset_token,
                    new_password=request.new_password,
                )
            )
            return ORJSONResponse(
                status_code=status.HTTP_200_OK,
                content=None,
            )
        except UserNotFoundError as e:
            return ORJSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(message=e.message).model_dump(),
            )
        except InvalidPasswordResetTokenError as e:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ErrorResponse(message=e.message).model_dump(),
            )

    @AsyncLogging()
    @JWTAuth(token_url=Config().token.login_url)
    @put(
        "/me/password",
        status_code=status.HTTP_200_OK,
        response_model=None,
        responses={
            status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
            status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        },
    )
    async def update_password_api(self, token: JWT, request: UpdatePassword):
        try:
            await self.update_password.execute(
                UpdatePasswordCommand(
                    user_id=UUID(token.payload["sub"]),
                    old_password=request.old_password,
                    new_password=request.new_password,
                )
            )
            return ORJSONResponse(
                status_code=status.HTTP_200_OK,
                content=None,
            )
        except UserNotFoundError as e:
            return ORJSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(message=e.message).model_dump(),
            )
        except AuthenticationFailedError as e:
            return ORJSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=ErrorResponse(message=e.message).model_dump(),
            )

    @AsyncLogging()
    @JWTAuth(token_url=Config().token.login_url)
    @put(
        "/me/phone-number",
        status_code=status.HTTP_200_OK,
        response_model=None,
        responses={
            status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
            status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        },
    )
    async def update_phone_number_api(self, token: JWT, request: UpdatePhoneNumber):
        try:
            await self.update_phone_number.execute(
                UpdatePhoneNumberCommand(
                    user_id=UUID(token.payload["sub"]),
                    phone_number=request.phone_number,
                )
            )
            return ORJSONResponse(
                status_code=status.HTTP_200_OK,
                content=None,
            )
        except UserNotFoundError as e:
            return ORJSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(message=e.message).model_dump(),
            )

    @AsyncLogging()
    @JWTAuth(token_url=Config().token.login_url)
    @put(
        "/me/profile",
        status_code=status.HTTP_200_OK,
        response_model=None,
        responses={
            status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
            status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        },
    )
    async def update_profile_api(self, token: JWT, request: UpdateProfile):
        try:
            await self.update_profile.execute(
                UpdateProfileCommand(
                    user_id=UUID(token.payload["sub"]),
                    name=request.name,
                    address=request.address,
                    gender=request.gender,
                    birth_date=request.birth_date,
                    billing_name=request.billing_name,
                )
            )
            return ORJSONResponse(
                status_code=status.HTTP_200_OK,
                content=None,
            )
        except UserNotFoundError as e:
            return ORJSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(message=e.message).model_dump(),
            )

    @AsyncLogging()
    @JWTAuth(token_url=Config().token.login_url)
    @Authorize({UserRole.BACKOFFICER})
    @put(
        "/{user_id}/remark",
        status_code=status.HTTP_200_OK,
        response_model=None,
        responses={
            status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
            status.HTTP_403_FORBIDDEN: {"model": None},
            status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        },
    )
    async def write_remark_api(
        self,
        token: JWT,  # pylint: disable=unused-argument
        user_id: UUID = Path(),
        request: WriteRemark = Body(),
    ):
        try:
            await self.write_remark.execute(
                WriteRemarkCommand(
                    user_id=user_id,
                    remark=request.remark,
                )
            )
            return ORJSONResponse(
                status_code=status.HTTP_200_OK,
                content=None,
            )
        except UserNotFoundError as e:
            return ORJSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(message=e.message).model_dump(),
            )

    @AsyncLogging()
    @JWTAuth(token_url=Config().token.login_url)
    @Authorize({UserRole.BACKOFFICER})
    @post(
        "",
        status_code=status.HTTP_200_OK,
        response_model=None,
        responses={
            status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
            status.HTTP_403_FORBIDDEN: {"model": None},
            status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        },
    )
    async def create_user_api(
        self,
        token: JWT,  # pylint: disable=unused-argument
        request: CreateUser = Body(),
    ):
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
            return ORJSONResponse(
                status_code=status.HTTP_200_OK,
                content=None,
            )
        except UsernameAlreadyExistsError as e:
            return ORJSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(message=e.message).model_dump(),
            )
        except PhoneNumberAlreadyExistsError as e:
            return ORJSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(message=e.message).model_dump(),
            )

    @AsyncLogging()
    @JWTAuth(token_url=Config().token.login_url)
    @get(
        "/me",
        status_code=status.HTTP_200_OK,
        response_model=GetMeResponse,
        responses={
            status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
            status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        },
    )
    async def get_me_api(self, token: JWT):
        user_id: UUID = UUID(token.payload["sub"])
        try:
            result = await self.get_me.execute(GetMeQuery(user_id=user_id))
            return ORJSONResponse(
                status_code=status.HTTP_200_OK,
                content=GetMeResponse(
                    user_id=result.user_id,
                    name=result.name,
                    phone_number=result.phone_number,
                    address=result.address,
                    gender=result.gender,
                    birth_date=result.birth_date,
                    billing_name=result.billing_name,
                ).model_dump(),
            )
        except UserNotFoundError as e:
            return ORJSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(message=e.message).model_dump(),
            )

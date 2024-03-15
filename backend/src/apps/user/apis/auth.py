from typing import Annotated
from datetime import date

from fastapi import Depends, Header, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from spakky.bean.autowired import autowired
from spakky.cryptography.jwt import JWT
from spakky.extensions.logging import AsyncLogging
from spakky_fastapi.error import BadRequest, Conflict, NotFound, Unauthorized
from spakky_fastapi.routing import post, put
from spakky_fastapi.stereotypes.api_controller import ApiController

from apps.user.domain.errors import (
    AuthenticationFailedError,
    CannotRegisterWithoutAgreementError,
    InvalidPasswordResetTokenError,
    PhoneNumberAlreadyExistsError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)
from apps.user.domain.interfaces.usecases.forgot_password import (
    ForgotPasswordCommand,
    IAsyncForgotPasswordCommandUseCase,
)
from apps.user.domain.interfaces.usecases.login import (
    IAsyncLoginCommandUseCase,
    LoginCommand,
)
from apps.user.domain.interfaces.usecases.register import (
    IAsyncRegisterCommandUseCase,
    RegisterCommand,
)
from apps.user.domain.interfaces.usecases.reset_password import (
    IAsyncResetPasswordCommandUseCase,
    ResetPasswordCommand,
)
from common.enums.api_catetory import ApiCatetory
from common.enums.gender import Gender


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


class ResetPassword(BaseModel):
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


@ApiController("/auth", tags=[ApiCatetory.AUTH])
class AuthenticationRestApiController:
    forgot_password: IAsyncForgotPasswordCommandUseCase
    login: IAsyncLoginCommandUseCase
    register: IAsyncRegisterCommandUseCase
    reset_password: IAsyncResetPasswordCommandUseCase

    @autowired
    def __init__(
        self,
        forgot_password: IAsyncForgotPasswordCommandUseCase,
        login: IAsyncLoginCommandUseCase,
        register: IAsyncRegisterCommandUseCase,
        reset_password: IAsyncResetPasswordCommandUseCase,
    ) -> None:
        self.forgot_password = forgot_password
        self.login = login
        self.register = register
        self.reset_password = reset_password

    @AsyncLogging()
    @put(
        "/{username}/password/forgot",
        name="비밀번호 분실 설정",
        status_code=status.HTTP_200_OK,
    )
    async def forgot_password_api(self, username: str) -> None:
        try:
            await self.forgot_password.execute(ForgotPasswordCommand(username=username))
        except UserNotFoundError as e:
            raise NotFound(error=e) from e

    @AsyncLogging()
    @post("/login", name="로그인", status_code=status.HTTP_200_OK)
    async def login_api(
        self,
        request: Annotated[OAuth2PasswordRequestForm, Depends()],
        x_forwarded_for: Annotated[str | None, Header()] = None,
        ip_address: Annotated[str | None, Header()] = None,
        user_agent: Annotated[str | None, Header()] = None,
    ) -> TokenResponse:
        try:
            token: JWT = await self.login.execute(
                command=LoginCommand(
                    username=request.username,
                    password=request.password,
                    ip_address=x_forwarded_for or ip_address or "0.0.0.0",
                    user_agent=user_agent or "Unknown",
                )
            )
            return TokenResponse(access_token=token.export(), token_type="bearer")
        except AuthenticationFailedError as e:
            raise Unauthorized(error=e) from e

    @AsyncLogging()
    @post("/register", name="회원가입", status_code=status.HTTP_201_CREATED)
    async def register_api(self, request: Register) -> TokenResponse:
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
            return TokenResponse(access_token=token.export(), token_type="bearer")
        except UsernameAlreadyExistsError as e:
            raise Conflict(error=e) from e
        except PhoneNumberAlreadyExistsError as e:
            raise Conflict(error=e) from e
        except CannotRegisterWithoutAgreementError as e:
            raise BadRequest(error=e) from e

    @AsyncLogging()
    @put(
        "/{username}/password/{password_reset_token}",
        name="비밀번호 재설정",
        status_code=status.HTTP_200_OK,
    )
    async def reset_password_api(
        self,
        username: str,
        password_reset_token: str,
        request: ResetPassword,
    ) -> None:
        try:
            await self.reset_password.execute(
                ResetPasswordCommand(
                    username=username,
                    password_reset_token=password_reset_token,
                    new_password=request.new_password,
                )
            )
        except UserNotFoundError as e:
            raise NotFound(error=e) from e
        except InvalidPasswordResetTokenError as e:
            raise BadRequest(error=e) from e

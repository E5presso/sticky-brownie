from uuid import UUID
from datetime import date

from fastapi import Depends, Header, status
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from spakky.bean.autowired import autowired
from spakky.cryptography.jwt import JWT
from spakky.extensions.logging import AsyncLogging
from spakky.stereotype.controller import Controller
from spakky_fastapi.jwt_auth import JWTAuth
from spakky_fastapi.routing import post, put

from apps.user.domain.errors import (
    AuthenticationFailedError,
    CannotRegisterWithoutAgreementError,
    PhoneNumberAlreadyExistsError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)
from apps.user.domain.models.gender import Gender
from apps.user.domain.ports.usecases.agree_marketing_promotions import (
    AgreeMarketingPromotionsCommand,
    IAsyncAgreeMarketingPromotionsCommandUseCase,
)
from apps.user.domain.ports.usecases.login import (
    IAsyncLoginCommandUseCase,
    LoginCommand,
)
from apps.user.domain.ports.usecases.register import (
    IAsyncRegisterCommandUseCase,
    RegisterCommand,
)
from common.error_response import ErrorResponse


class RegisterRequest(BaseModel):
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


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class MarketingPromotionsAgreementRequest(BaseModel):
    agreed: bool


@Controller("/users/v1")
class UserRestApiController:
    register: IAsyncRegisterCommandUseCase
    login: IAsyncLoginCommandUseCase
    marketing_promotions_agreement: IAsyncAgreeMarketingPromotionsCommandUseCase

    @autowired
    def __init__(
        self,
        register: IAsyncRegisterCommandUseCase,
        login: IAsyncLoginCommandUseCase,
        marketing_promotions_agreement: IAsyncAgreeMarketingPromotionsCommandUseCase,
    ) -> None:
        self.register = register
        self.login = login
        self.marketing_promotions_agreement = marketing_promotions_agreement

    @AsyncLogging(masking_keys=["password", "token"])
    @post(
        "/register",
        status_code=status.HTTP_201_CREATED,
        response_model=TokenResponse,
        responses={
            status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
            status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        },
    )
    async def do_register(self, request: RegisterRequest):
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
                ),
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

    @AsyncLogging(masking_keys=["password", "token"])
    @post(
        "/login",
        status_code=status.HTTP_200_OK,
        response_model=TokenResponse,
        responses={status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse}},
    )
    async def do_login(
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

    @AsyncLogging(masking_keys=["password", "token"])
    @JWTAuth(token_url="users/v1/login")
    @put(
        "/me/marketing-promotions-agreement",
        status_code=status.HTTP_200_OK,
        response_model=None,
        responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
    )
    async def do_marketing_promotions_agreement(
        self, token: JWT, request: MarketingPromotionsAgreementRequest
    ):
        try:
            await self.marketing_promotions_agreement.execute(
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

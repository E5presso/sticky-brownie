from uuid import UUID
from datetime import date

from fastapi import status
from pydantic import BaseModel
from spakky.bean.autowired import autowired
from spakky.cryptography.jwt import JWT
from spakky.extensions.logging import AsyncLogging
from spakky_fastapi.error import NotFound, Unauthorized
from spakky_fastapi.jwt_auth import JWTAuth
from spakky_fastapi.routing import get, put
from spakky_fastapi.stereotypes.api_controller import ApiController

from apps.user.domain.errors import AuthenticationFailedError, UserNotFoundError
from apps.user.domain.interfaces.usecases.agree_marketing_promotions import (
    AgreeMarketingPromotionsCommand,
    IAsyncAgreeMarketingPromotionsCommandUseCase,
)
from apps.user.domain.interfaces.usecases.get_me import (
    GetMeQuery,
    IAsyncGetMeQueryUseCase,
)
from apps.user.domain.interfaces.usecases.update_password import (
    IAsyncUpdatePasswordCommandUseCase,
    UpdatePasswordCommand,
)
from apps.user.domain.interfaces.usecases.update_phone_number import (
    IAsyncUpdatePhoneNumberCommandUseCase,
    UpdatePhoneNumberCommand,
)
from apps.user.domain.interfaces.usecases.update_profile import (
    IAsyncUpdateProfilePasswordCommandUseCase,
    UpdateProfileCommand,
)
from common.enums.api_catetory import ApiCatetory
from common.enums.gender import Gender
from common.settings.config import Config

LOGIN_URL = Config().token.login_url


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


@ApiController("/users/me", tags=[ApiCatetory.USERS])
class UsersRestApiController:
    agree_marketing_promotions: IAsyncAgreeMarketingPromotionsCommandUseCase
    update_password: IAsyncUpdatePasswordCommandUseCase
    update_phone_number: IAsyncUpdatePhoneNumberCommandUseCase
    update_profile: IAsyncUpdateProfilePasswordCommandUseCase
    get_me: IAsyncGetMeQueryUseCase

    @autowired
    def __init__(
        self,
        agree_marketing_promotions: IAsyncAgreeMarketingPromotionsCommandUseCase,
        update_password: IAsyncUpdatePasswordCommandUseCase,
        update_phone_number: IAsyncUpdatePhoneNumberCommandUseCase,
        update_profile: IAsyncUpdateProfilePasswordCommandUseCase,
        get_me: IAsyncGetMeQueryUseCase,
    ) -> None:
        self.agree_marketing_promotions = agree_marketing_promotions
        self.update_password = update_password
        self.update_phone_number = update_phone_number
        self.update_profile = update_profile
        self.get_me = get_me

    @AsyncLogging()
    @JWTAuth(LOGIN_URL)
    @put(
        "/marketing-promotions-agreement",
        name="마케팅 프로모션 수신 동의 변경",
        status_code=status.HTTP_200_OK,
    )
    async def agree_marketing_promotions_api(
        self, token: JWT, request: MarketingPromotionsAgreement
    ) -> None:
        try:
            await self.agree_marketing_promotions.execute(
                AgreeMarketingPromotionsCommand(
                    user_id=UUID(token.payload["sub"]),
                    agreed=request.agreed,
                )
            )
        except UserNotFoundError as e:
            raise NotFound(error=e) from e

    @AsyncLogging()
    @JWTAuth(LOGIN_URL)
    @put("/password", name="비밀번호 변경", status_code=status.HTTP_200_OK)
    async def update_password_api(self, token: JWT, request: UpdatePassword) -> None:
        try:
            await self.update_password.execute(
                UpdatePasswordCommand(
                    user_id=UUID(token.payload["sub"]),
                    old_password=request.old_password,
                    new_password=request.new_password,
                )
            )
        except UserNotFoundError as e:
            raise NotFound(error=e) from e
        except AuthenticationFailedError as e:
            raise Unauthorized(error=e) from e

    @AsyncLogging()
    @JWTAuth(LOGIN_URL)
    @put("/phone-number", name="휴대폰 번호 변경", status_code=status.HTTP_200_OK)
    async def update_phone_number_api(
        self, token: JWT, request: UpdatePhoneNumber
    ) -> None:
        try:
            await self.update_phone_number.execute(
                UpdatePhoneNumberCommand(
                    user_id=UUID(token.payload["sub"]),
                    phone_number=request.phone_number,
                )
            )
        except UserNotFoundError as e:
            raise NotFound(error=e) from e

    @AsyncLogging()
    @JWTAuth(LOGIN_URL)
    @put("/profile", name="프로필 정보 수정", status_code=status.HTTP_200_OK)
    async def update_profile_api(self, token: JWT, request: UpdateProfile) -> None:
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
        except UserNotFoundError as e:
            raise NotFound(error=e) from e

    @AsyncLogging()
    @JWTAuth(LOGIN_URL)
    @get("", name="사용자 본인 정보 조회", status_code=status.HTTP_200_OK)
    async def get_me_api(self, token: JWT) -> GetMeResponse:
        user_id: UUID = UUID(token.payload["sub"])
        try:
            result = await self.get_me.execute(GetMeQuery(user_id=user_id))
            return GetMeResponse(
                user_id=result.user_id,
                name=result.name,
                phone_number=result.phone_number,
                address=result.address,
                gender=result.gender,
                birth_date=result.birth_date,
                billing_name=result.billing_name,
            )
        except UserNotFoundError as e:
            raise NotFound(error=e) from e

from typing import Any, Container
from logging import Logger
from dataclasses import dataclass

from spakky.aop.advice import Around
from spakky.aop.advisor import IAsyncAdvisor
from spakky.aop.aspect import AsyncAspect
from spakky.aop.error import SpakkyAOPError
from spakky.aop.order import Order
from spakky.bean.autowired import autowired
from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import AsyncFunc, P
from spakky.cryptography.jwt import JWT
from spakky_fastapi.error import Forbidden
from spakky_fastapi.jwt_auth import IAuthenticatedFunction, JWTAuth, R_co

from common.enums.user_role import UserRole


@dataclass
class Authorize(FunctionAnnotation):
    roles: Container[UserRole]

    def __call__(
        self, obj: IAuthenticatedFunction[P, R_co]
    ) -> IAuthenticatedFunction[P, R_co]:
        return super().__call__(obj)


class UserPermissionDeniedError(SpakkyAOPError):
    message = "인가되지 않은 접근입니다."


@Order(2)
@AsyncAspect()
class AsyncAuthorizeAdvisor(IAsyncAdvisor):
    __logger: Logger

    @autowired
    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.__logger = logger

    @Around(Authorize.contains)
    async def around_async(self, joinpoint: AsyncFunc, *args: Any, **kwargs: Any) -> Any:
        jwt_auth: JWTAuth = JWTAuth.single(joinpoint)
        for keyword in jwt_auth.token_keywords:
            jwt: JWT = kwargs[keyword]
            user_id: str | None = jwt.payload.get("sub", None)
            role: UserRole | None = jwt.payload.get("role", None)
            annotation: Authorize = Authorize.single(joinpoint)
            if role not in annotation.roles:
                self.__logger.info(
                    f"[{type(self).__name__}] [DENIED] {role!r}.{user_id} -> {annotation.roles!r} -> {joinpoint.__name__}"
                )
                raise Forbidden(UserPermissionDeniedError())
            self.__logger.info(
                f"[{type(self).__name__}] [GRANTED] {role!r}.{user_id} -> {annotation.roles!r} -> {joinpoint.__name__}"
            )
        return await joinpoint(*args, **kwargs)

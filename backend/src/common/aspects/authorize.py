from typing import Any, Container
from logging import Logger
from dataclasses import dataclass

from fastapi import Response, status
from spakky.aop.advice import Around
from spakky.aop.advisor import IAsyncAdvisor
from spakky.aop.aspect import AsyncAspect
from spakky.bean.autowired import autowired
from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import AsyncFunc, P
from spakky.cryptography.jwt import JWT
from spakky_fastapi.jwt_auth import IAuthenticatedFunction, R_co

from common.enums.user_role import UserRole


@dataclass
class Authorize(FunctionAnnotation):
    roles: Container[UserRole]

    def __call__(
        self, obj: IAuthenticatedFunction[P, R_co]
    ) -> IAuthenticatedFunction[P, R_co]:
        return super().__call__(obj)


@AsyncAspect()
class AsyncJWTAuthAdvisor(IAsyncAdvisor):
    __logger: Logger

    @autowired
    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.__logger = logger

    @Around(Authorize.contains)
    async def around_async(self, joinpoint: AsyncFunc, *args: Any, **kwargs: Any) -> Any:
        jwt: JWT = kwargs["token"]
        user_id: str | None = jwt.payload.get("sub", None)
        role: UserRole | None = jwt.payload.get("role", None)
        annotation: Authorize = Authorize.single(joinpoint)
        if role not in annotation.roles:
            self.__logger.info(
                f"[{type(self).__name__}] [DENIED] {role!r}.{user_id or "Unknown"} -> {annotation.roles!r} -> {joinpoint.__name__}"
            )
            return Response(content=None, status_code=status.HTTP_403_FORBIDDEN)
        self.__logger.info(
            f"[{type(self).__name__}] [GRANTED] {role!r}.{user_id or "Unknown"} -> {annotation.roles!r} -> {joinpoint.__name__}"
        )
        return await joinpoint(*args, **kwargs)

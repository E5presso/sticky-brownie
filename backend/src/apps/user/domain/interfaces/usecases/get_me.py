from uuid import UUID
from typing import Protocol, runtime_checkable
from datetime import date

from spakky.core.mutability import immutable
from spakky.domain.usecases.query import IAsyncQueryUseCase, Query

from common.enums.gender import Gender


@immutable
class GetMeQuery(Query):
    user_id: UUID


@immutable
class GetMeResult:
    user_id: UUID
    name: str
    phone_number: str
    address: str
    gender: Gender
    birth_date: date
    billing_name: str


@runtime_checkable
class IAsyncGetMeQueryUseCase(IAsyncQueryUseCase[GetMeQuery, GetMeResult], Protocol): ...

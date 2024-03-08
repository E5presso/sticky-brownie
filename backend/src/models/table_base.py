from abc import abstractmethod
from typing import Any, Self, Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

DomainT = TypeVar("DomainT", bound=Any)


class TableBase(AsyncAttrs, DeclarativeBase, Generic[DomainT]):
    __abstract__ = True

    @classmethod
    @abstractmethod
    async def from_domain(cls, domain: DomainT) -> Self: ...

    @abstractmethod
    async def to_domain(self) -> DomainT: ...

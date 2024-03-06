from abc import abstractmethod
from typing import Any, Self, Generic, TypeVar

from sqlalchemy.orm import DeclarativeBase

DomainT = TypeVar("DomainT", bound=Any)


class TableBase(DeclarativeBase, Generic[DomainT]):
    __abstract__ = True

    @classmethod
    @abstractmethod
    def from_domain(cls, domain: DomainT) -> Self: ...

    @abstractmethod
    def to_domain(self) -> DomainT: ...

from uuid import UUID
from typing import Self
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.user.domain.models.gender import Gender
from apps.user.domain.models.user import User
from apps.user.domain.models.user_status import UserStatus
from models.authentication_log import AuthenticationLogTable
from models.table_base import TableBase


class UserTable(TableBase[User]):
    __tablename__: str = "users"

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True)
    username: Mapped[str] = mapped_column(String())
    password: Mapped[str] = mapped_column(String())
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus, native_enum=False))
    name: Mapped[str] = mapped_column(String())
    address: Mapped[str] = mapped_column(String())
    phone_number: Mapped[str] = mapped_column(String())
    gender: Mapped[Gender] = mapped_column(Enum(Gender, native_enum=False))
    birth_date: Mapped[date] = mapped_column(Date())
    billing_name: Mapped[str] = mapped_column(String())
    password_reset_token: Mapped[str | None] = mapped_column(String(), nullable=True)
    terms_and_conditions_agreement: Mapped[datetime] = mapped_column(DateTime())
    marketing_promotions_agreement: Mapped[datetime | None]
    authentication_logs: Mapped[list[AuthenticationLogTable]] = relationship()
    remark: Mapped[str] = mapped_column(String())

    @classmethod
    def from_domain(cls, domain: User) -> Self:
        return cls(
            id=domain.uid,
            username=domain.username,
            password=domain.password,
            status=domain.status,
            name=domain.name,
            address=domain.address,
            phone_number=domain.phone_number,
            gender=domain.gender,
            birth_date=domain.birth_date,
            billing_name=domain.billing_name,
            password_reset_token=domain.password_reset_token,
            terms_and_conditions_agreement=domain.terms_and_conditions_agreement,
            marketing_promotions_agreement=domain.marketing_promotions_agreement,
            authentication_logs=[
                AuthenticationLogTable.from_domain(x) for x in domain.authentication_logs
            ],
            remark=domain.remark,
        )

    def to_domain(self) -> User:
        return User(
            uid=self.id,
            username=self.username,
            password=self.password,
            status=self.status,
            name=self.name,
            address=self.address,
            phone_number=self.phone_number,
            gender=self.gender,
            birth_date=self.birth_date,
            billing_name=self.billing_name,
            password_reset_token=self.password_reset_token,
            terms_and_conditions_agreement=self.terms_and_conditions_agreement,
            marketing_promotions_agreement=self.marketing_promotions_agreement,
            authentication_logs=[x.to_domain() for x in self.authentication_logs],
            remark=self.remark,
        )

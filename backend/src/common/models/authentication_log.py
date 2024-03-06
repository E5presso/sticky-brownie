from uuid import UUID
from typing import Self
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from common.models.table_base import TableBase
from src.apps.user.domain.models.authentication_log import AuthenticationLog


class AuthenticationLogTable(TableBase[AuthenticationLog]):
    __tablename__: str = "authentication_logs"

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    ip_address: Mapped[str] = mapped_column(String())
    user_agent: Mapped[str] = mapped_column(String())
    timestamp: Mapped[datetime] = mapped_column(DateTime())

    @classmethod
    def from_domain(cls, domain: AuthenticationLog) -> Self:
        return cls(
            id=domain.uid,
            ip_address=domain.ip_address,
            user_agent=domain.user_agent,
            timestamp=domain.timestamp,
        )

    def to_domain(self) -> AuthenticationLog:
        return AuthenticationLog(
            uid=self.id,
            ip_address=self.ip_address,
            user_agent=self.user_agent,
            timestamp=self.timestamp,
        )

from uuid import UUID
from typing import Self
from datetime import datetime

from sqlalchemy import DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from apps.file.domain.models.file import File
from models.table_base import TableBase


class FileTable(TableBase[File]):
    __tablename__: str = "files"

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True)
    filename: Mapped[str] = mapped_column(String())
    media_type: Mapped[str] = mapped_column(String())
    created_at: Mapped[datetime] = mapped_column(DateTime())
    updated_at: Mapped[datetime] = mapped_column(DateTime())

    @classmethod
    async def from_domain(cls, domain: File) -> Self:
        return cls(
            id=domain.uid,
            filename=domain.filename,
            media_type=domain.media_type,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )

    async def to_domain(self) -> File:
        return File(
            uid=self.id,
            filename=self.filename,
            media_type=self.media_type,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

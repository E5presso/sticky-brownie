from uuid import UUID, uuid4
from typing import Self
from datetime import datetime

from spakky.core.mutability import immutable, mutable
from spakky.domain.models.aggregate_root import AggregateRoot
from spakky.domain.models.domain_event import DomainEvent


@mutable
class File(AggregateRoot[UUID]):
    file_name: str
    """파일명"""
    media_type: str
    """미디어 유형"""
    created_at: datetime
    """생성 시각"""
    updated_at: datetime
    """수정 시각"""

    @immutable
    class FileCreated(DomainEvent):
        uid: UUID

    @classmethod
    def next_id(cls) -> UUID:
        return uuid4()

    @classmethod
    def create(cls, file_name: str, media_type: str) -> Self:
        return cls(
            uid=cls.next_id(),
            file_name=file_name,
            media_type=media_type,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

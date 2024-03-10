from uuid import UUID, uuid4
from typing import Self
from datetime import datetime

from spakky.core.mutability import immutable, mutable
from spakky.domain.models.aggregate_root import AggregateRoot
from spakky.domain.models.domain_event import DomainEvent


@mutable
class File(AggregateRoot[UUID]):
    name: str
    """파일명"""
    media_type: str
    """미디어 유형"""
    size: int
    """파일 크기"""
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
    def create(cls, name: str, media_type: str, size: int) -> Self:
        return cls(
            uid=cls.next_id(),
            name=name,
            media_type=media_type,
            size=size,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import field

from spakky.core.mutability import mutable
from spakky.domain.models.entity import Entity


@mutable
class AuthenticationLog(Entity[UUID]):
    ip_address: str
    user_agent: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def next_id(cls) -> UUID:
        return uuid4()

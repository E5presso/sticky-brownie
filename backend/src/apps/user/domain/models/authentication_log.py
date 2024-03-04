from datetime import datetime
from dataclasses import field

from spakky.core.mutability import immutable
from spakky.domain.models.value_object import ValueObject


@immutable
class AuthenticationLog(ValueObject):
    ip_address: str
    user_agent: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

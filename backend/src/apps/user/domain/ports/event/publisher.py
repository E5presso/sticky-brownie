from typing import Protocol, runtime_checkable

from spakky.domain.ports.event.event_publisher import IAsyncEventPublisher

from apps.user.domain.models.user import User


@runtime_checkable
class IAsyncUserEventPublisher(IAsyncEventPublisher[User], Protocol): ...

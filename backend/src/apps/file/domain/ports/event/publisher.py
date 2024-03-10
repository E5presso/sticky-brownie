from typing import Protocol, runtime_checkable

from spakky.domain.ports.event.event_publisher import IAsyncEventPublisher

from apps.files.domain.models.file import File


@runtime_checkable
class IAsyncFileEventPublisher(IAsyncEventPublisher[File], Protocol): ...

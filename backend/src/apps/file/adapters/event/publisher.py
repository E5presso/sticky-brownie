from logging import Logger
from dataclasses import asdict

from spakky.bean.autowired import autowired
from spakky.bean.bean import Bean

from apps.file.domain.models.file import File
from apps.file.domain.ports.event.publisher import IAsyncFileEventPublisher


@Bean()
class AsyncFileEventPublisher(IAsyncFileEventPublisher):
    __logger: Logger

    @autowired
    def __init__(self, logger: Logger) -> None:
        self.__logger = logger

    async def publish(self, aggregate: File) -> None:
        for event in aggregate.events:
            self.__logger.info(f"[{type(self).__name__}] {asdict(event)!r}")

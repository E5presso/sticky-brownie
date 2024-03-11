from logging import Logger
from dataclasses import asdict

from spakky.bean.autowired import autowired
from spakky.bean.bean import Bean

from apps.user.domain.interfaces.event.publisher import IAsyncUserEventPublisher
from apps.user.domain.models.user import User


@Bean()
class AsyncUserEventPublisher(IAsyncUserEventPublisher):
    __logger: Logger

    @autowired
    def __init__(self, logger: Logger) -> None:
        self.__logger = logger

    async def publish(self, aggregate: User) -> None:
        for event in aggregate.events:
            self.__logger.info(f"[{type(self).__name__}] {asdict(event)!r}")

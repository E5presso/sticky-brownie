from logging import Logger
from dataclasses import asdict

from spakky.bean.autowired import autowired
from spakky.bean.bean import Bean

from src.apps.user.domain.models.user import User
from src.apps.user.domain.ports.event.publisher import IAsyncUserEventPublisher


@Bean()
class AsyncEventPublisher(IAsyncUserEventPublisher):
    __logger: Logger

    @autowired
    def __init__(self, logger: Logger) -> None:
        self.__logger = logger

    async def publish(self, aggregate: User) -> None:
        for event in aggregate.events:
            self.__logger.info(f"[{type(self).__name__}] {asdict(event)!r}")

from uuid import UUID
from typing import Protocol
from logging import Logger
from dataclasses import asdict

from spakky.bean.autowired import autowired
from spakky.bean.bean import Bean
from spakky.domain.models.aggregate_root import AggregateRoot
from spakky.domain.ports.event.event_publisher import IAsyncEventPublisher


@Bean()
class AsyncEventPublisher(IAsyncEventPublisher[UUID], Protocol):
    __logger: Logger

    @autowired
    def __init__(self, logger: Logger) -> None:
        self.__logger = logger

    async def publish(self, aggregate: AggregateRoot[UUID]) -> None:
        for event in aggregate.events:
            self.__logger.info(f"[{type(self).__name__}] {asdict(event)!r}")

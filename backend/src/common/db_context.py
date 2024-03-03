from types import TracebackType
from typing import Self
from asyncio import current_task

from common.config import Config
from spakky.bean.autowired import autowired
from spakky.bean.bean import Bean
from spakky.core.interfaces.disposable import IAsyncDisposable
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)


@Bean()
class AsyncDbContext(IAsyncDisposable):
    __engine: AsyncEngine
    __session: AsyncSession | None
    __scoped_sessionmaker: async_scoped_session[AsyncSession]

    @property
    def engine(self) -> AsyncEngine:
        return self.__engine

    @property
    def session(self) -> AsyncSession:
        if self.__session is None:
            self.__session = self.__scoped_sessionmaker()
        return self.__session

    @autowired
    def __init__(self, config: Config) -> None:
        self.__engine = create_async_engine(
            url=config.database.url,
            pool_size=config.database.pool_size,
            echo=config.debug,
        )
        self.__scoped_sessionmaker = async_scoped_session(
            session_factory=async_sessionmaker(
                bind=self.__engine,
                expire_on_commit=False,
            ),
            scopefunc=current_task,
        )
        self.__session = None

    async def __aenter__(self) -> Self:
        await self.initialize()
        return self

    async def __aexit__(
        self,
        __exc_type: type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> bool | None:
        await self.dispose()

    async def initialize(self) -> None:
        self.__session = self.__scoped_sessionmaker()

    async def dispose(self) -> None:
        if self.__session is not None:
            await self.__session.close()
        await self.__scoped_sessionmaker.remove()

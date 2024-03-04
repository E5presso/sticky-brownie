from asyncio import current_task

from spakky.bean.autowired import autowired
from spakky.bean.bean import Bean
from spakky.domain.ports.persistency.transaction import AbstractAsyncTranasction
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from src.common.config import Config


@Bean()
class AsyncTransaction(AbstractAsyncTranasction):
    __engine: AsyncEngine
    __scoped_sessionmaker: async_scoped_session[AsyncSession]
    __session: AsyncSession | None

    @autowired
    def __init__(self, config: Config) -> None:
        super().__init__(True)
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

    async def initialize(self) -> None:
        self.__session = self.__scoped_sessionmaker()

    async def dispose(self) -> None:
        if self.__session is not None:
            await self.__session.close()
        await self.__scoped_sessionmaker.remove()

    async def commit(self) -> None:
        if self.__session is not None:
            await self.__session.commit()

    async def rollback(self) -> None:
        if self.__session is not None:
            await self.__session.rollback()

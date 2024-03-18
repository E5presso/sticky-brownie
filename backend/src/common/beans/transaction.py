from spakky.bean.autowired import autowired
from spakky.bean.bean import Bean
from spakky.domain.ports.persistency.transaction import AbstractAsyncTranasction
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from common.settings.config import Config


@Bean()
class AsyncTransaction(AbstractAsyncTranasction):
    __engine: AsyncEngine
    __scoped_sessionmaker: async_sessionmaker[AsyncSession]
    __session: AsyncSession | None

    @property
    def session(self) -> AsyncSession:
        if self.__session is None:
            self.__session = self.__scoped_sessionmaker()
        return self.__session

    @autowired
    def __init__(self) -> None:
        super().__init__(True)
        config: Config = Config()
        self.__engine = create_async_engine(
            url=config.database.url,
            pool_size=config.database.pool_size,
            echo=config.common.debug,
        )
        self.__scoped_sessionmaker = async_sessionmaker(
            bind=self.__engine,
            expire_on_commit=False,
        )
        self.__session = None

    async def initialize(self) -> None:
        self.__session = self.__scoped_sessionmaker()

    async def dispose(self) -> None:
        if self.__session is not None:
            await self.__session.close()

    async def commit(self) -> None:
        if self.__session is not None:
            await self.__session.commit()

    async def rollback(self) -> None:
        if self.__session is not None:
            await self.__session.rollback()

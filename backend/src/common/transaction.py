from common.db_context import AsyncDbContext
from spakky.bean.autowired import autowired
from spakky.bean.bean import Bean
from spakky.domain.infrastructures.persistency.transaction import (
    AbstractAsyncTranasction,
)


@Bean()
class AsyncTransaction(AbstractAsyncTranasction):
    db_context: AsyncDbContext

    @autowired
    def __init__(self, db_context: AsyncDbContext) -> None:
        super().__init__(True)
        self.db_context = db_context

    async def initialize(self) -> None:
        await self.db_context.initialize()

    async def dispose(self) -> None:
        await self.db_context.dispose()

    async def commit(self) -> None:
        await self.db_context.session.commit()

    async def rollback(self) -> None:
        await self.db_context.session.rollback()

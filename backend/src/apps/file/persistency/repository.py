from uuid import UUID
from typing import Sequence

from spakky.bean.autowired import autowired
from spakky.domain.ports.persistency.repository import EntityNotFoundError
from spakky.extensions.logging import AsyncLogging
from spakky.stereotype.repository import Repository
from sqlalchemy import select

from apps.file.domain.models.file import File
from apps.file.domain.ports.persistency.repository import IAsyncFileRepository
from common.beans.transaction import AsyncTransaction
from models.file import FileTable


@Repository()
class AsyncFileRepository(IAsyncFileRepository):
    transaction: AsyncTransaction

    @autowired
    def __init__(self, transaction: AsyncTransaction) -> None:
        self.transaction = transaction

    @AsyncLogging()
    async def single(self, aggregate_id: UUID) -> File:
        try:
            return await (
                (
                    await self.transaction.session.execute(
                        select(FileTable).where(FileTable.id == aggregate_id)
                    )
                )
                .unique()
                .scalar_one()
                .to_domain()
            )
        except Exception as e:
            raise EntityNotFoundError(aggregate_id) from e

    @AsyncLogging()
    async def single_or_none(self, aggregate_id: UUID) -> File | None:
        result = (
            (
                await self.transaction.session.execute(
                    select(FileTable).where(FileTable.id == aggregate_id)
                )
            )
            .unique()
            .scalar_one_or_none()
        )
        return await result.to_domain() if result is not None else None

    @AsyncLogging()
    async def get_by_name_or_none(self, name: str) -> File | None:
        result = (
            (
                await self.transaction.session.execute(
                    select(FileTable).where(FileTable.name == name)
                )
            )
            .unique()
            .scalar_one_or_none()
        )
        return await result.to_domain() if result is not None else None

    @AsyncLogging()
    async def contains(self, aggregate_id: UUID) -> bool:
        return (
            await self.transaction.session.execute(
                select(FileTable.id).where(FileTable.id == aggregate_id)
            )
        ).scalar_one_or_none() is not None

    @AsyncLogging()
    async def contains_by_name(self, name: str) -> bool:
        return (
            await self.transaction.session.execute(
                select(FileTable.id).where(FileTable.name == name)
            )
        ).scalar_one_or_none() is not None

    @AsyncLogging()
    async def range(self, aggregate_ids: Sequence[UUID]) -> Sequence[File]:
        result: Sequence[FileTable] = (
            (
                await self.transaction.session.execute(
                    select(FileTable).where(FileTable.id.in_(aggregate_ids))
                )
            )
            .unique()
            .scalars()
            .all()
        )
        return [await x.to_domain() for x in result]

    @AsyncLogging()
    async def save(self, aggregate: File) -> File:
        from_domain: FileTable = await FileTable.from_domain(aggregate)
        merged: FileTable = await self.transaction.session.merge(from_domain)
        self.transaction.session.add(merged)
        return await merged.to_domain()

    @AsyncLogging()
    async def save_all(self, aggregates: Sequence[File]) -> Sequence[File]:
        processed: Sequence[FileTable] = []
        for x in aggregates:
            from_domain: FileTable = await FileTable.from_domain(x)
            merged: FileTable = await self.transaction.session.merge(from_domain)
            self.transaction.session.add(merged)
            processed.append(merged)
        return [await x.to_domain() for x in processed]

    @AsyncLogging()
    async def delete(self, aggregate: File) -> File:
        from_domain: FileTable = await FileTable.from_domain(aggregate)
        merged: FileTable = await self.transaction.session.merge(from_domain)
        await self.transaction.session.delete(merged)
        return await merged.to_domain()

    @AsyncLogging()
    async def delete_all(self, aggregates: Sequence[File]) -> Sequence[File]:
        processed: Sequence[FileTable] = []
        for x in aggregates:
            from_domain: FileTable = await FileTable.from_domain(x)
            merged: FileTable = await self.transaction.session.merge(from_domain)
            await self.transaction.session.delete(merged)
            processed.append(merged)
        return [await x.to_domain() for x in processed]

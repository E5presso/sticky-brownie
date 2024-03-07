from uuid import UUID
from typing import Sequence

from spakky.bean.autowired import autowired
from spakky.domain.ports.persistency.repository import EntityNotFoundError
from spakky.extensions.logging import AsyncLogging
from spakky.stereotype.repository import Repository
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from apps.user.domain.models.user import User
from apps.user.domain.ports.persistency.repository import IAsyncUserRepository
from common.transaction import AsyncTransaction
from models.user import UserTable


@Repository()
class AsyncUserRepository(IAsyncUserRepository):
    transaction: AsyncTransaction

    @autowired
    def __init__(self, transaction: AsyncTransaction) -> None:
        self.transaction = transaction

    @AsyncLogging()
    async def single(self, aggregate_id: UUID) -> User:
        try:
            return (
                (
                    await self.transaction.session.execute(
                        select(UserTable)
                        .options(joinedload(UserTable.authentication_logs))
                        .where(UserTable.id == aggregate_id)
                    )
                )
                .unique()
                .scalar_one()
                .to_domain()
            )
        except Exception as e:
            raise EntityNotFoundError(aggregate_id) from e

    @AsyncLogging()
    async def single_or_none(self, aggregate_id: UUID) -> User | None:
        result = (
            (
                await self.transaction.session.execute(
                    select(UserTable)
                    .options(joinedload(UserTable.authentication_logs))
                    .where(UserTable.id == aggregate_id)
                )
            )
            .unique()
            .scalar_one_or_none()
        )
        return result.to_domain() if result is not None else None

    @AsyncLogging()
    async def get_by_username(self, username: str) -> User | None:
        result = (
            (
                await self.transaction.session.execute(
                    select(UserTable)
                    .options(joinedload(UserTable.authentication_logs))
                    .where(UserTable.username == username)
                )
            )
            .unique()
            .scalar_one_or_none()
        )
        return result.to_domain() if result is not None else None

    @AsyncLogging()
    async def get_by_phone_number(self, phone_number: str) -> User | None:
        result = (
            (
                await self.transaction.session.execute(
                    select(UserTable)
                    .options(joinedload(UserTable.authentication_logs))
                    .where(UserTable.phone_number == phone_number)
                )
            )
            .unique()
            .scalar_one_or_none()
        )
        return result.to_domain() if result is not None else None

    @AsyncLogging()
    async def contains(self, aggregate_id: UUID) -> bool:
        return (
            await self.transaction.session.execute(
                select(UserTable.id).where(UserTable.id == aggregate_id)
            )
        ).scalar_one_or_none() is not None

    @AsyncLogging()
    async def contains_by_username(self, username: str) -> bool:
        return (
            await self.transaction.session.execute(
                select(UserTable.id).where(UserTable.username == username)
            )
        ).scalar_one_or_none() is not None

    @AsyncLogging()
    async def contains_by_phone_number(self, phone_number: str) -> bool:
        return (
            await self.transaction.session.execute(
                select(UserTable.id).where(UserTable.phone_number == phone_number)
            )
        ).scalar_one_or_none() is not None

    @AsyncLogging()
    async def range(self, aggregate_ids: Sequence[UUID]) -> Sequence[User]:
        result: Sequence[UserTable] = (
            (
                await self.transaction.session.execute(
                    select(UserTable)
                    .options(joinedload(UserTable.authentication_logs))
                    .where(UserTable.id.in_(aggregate_ids))
                )
            )
            .unique()
            .scalars()
            .all()
        )
        return [x.to_domain() for x in result]

    @AsyncLogging()
    async def save(self, aggregate: User) -> User:
        from_domain: UserTable = UserTable.from_domain(aggregate)
        merged: UserTable = await self.transaction.session.merge(from_domain)
        self.transaction.session.add(merged)
        return merged.to_domain()

    @AsyncLogging()
    async def save_all(self, aggregates: Sequence[User]) -> Sequence[User]:
        processed: Sequence[UserTable] = []
        for x in aggregates:
            from_domain: UserTable = UserTable.from_domain(x)
            merged: UserTable = await self.transaction.session.merge(from_domain)
            self.transaction.session.add(merged)
            processed.append(merged)
        return [x.to_domain() for x in processed]

    @AsyncLogging()
    async def delete(self, aggregate: User) -> User:
        from_domain: UserTable = UserTable.from_domain(aggregate)
        merged: UserTable = await self.transaction.session.merge(from_domain)
        await self.transaction.session.delete(merged)
        return merged.to_domain()

    @AsyncLogging()
    async def delete_all(self, aggregates: Sequence[User]) -> Sequence[User]:
        processed: Sequence[UserTable] = []
        for x in aggregates:
            from_domain: UserTable = UserTable.from_domain(x)
            merged: UserTable = await self.transaction.session.merge(from_domain)
            await self.transaction.session.delete(merged)
            processed.append(merged)
        return [x.to_domain() for x in processed]

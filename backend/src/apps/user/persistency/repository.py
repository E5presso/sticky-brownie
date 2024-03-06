from uuid import UUID
from typing import Sequence

from spakky.bean.autowired import autowired
from spakky.domain.ports.persistency.repository import EntityNotFoundError
from spakky.stereotype.repository import Repository
from sqlalchemy import select

from src.apps.user.domain.models.user import User
from src.apps.user.domain.ports.persistency.repository import IAsyncUserRepository
from src.common.models.user import UserTable
from src.common.transaction import AsyncTransaction


@Repository()
class AsyncUserRepository(IAsyncUserRepository):
    transaction: AsyncTransaction

    @autowired
    def __init__(self, transaction: AsyncTransaction) -> None:
        self.transaction = transaction

    async def single(self, aggregate_id: UUID) -> User:
        try:
            return (
                (
                    await self.transaction.session.execute(
                        select(UserTable).where(UserTable.id == aggregate_id)
                    )
                )
                .scalar_one()
                .to_domain()
            )
        except Exception as e:
            raise EntityNotFoundError(aggregate_id) from e

    async def single_or_none(self, aggregate_id: UUID) -> User | None:
        result = (
            await self.transaction.session.execute(
                select(UserTable).where(UserTable.id == aggregate_id)
            )
        ).scalar_one_or_none()
        return result.to_domain() if result is not None else None

    async def get_by_username(self, username: str) -> User | None:
        result = (
            await self.transaction.session.execute(
                select(UserTable).where(UserTable.username == username)
            )
        ).scalar_one_or_none()
        return result.to_domain() if result is not None else None

    async def get_by_phone_number(self, phone_number: str) -> User | None:
        result = (
            await self.transaction.session.execute(
                select(UserTable).where(UserTable.phone_number == phone_number)
            )
        ).scalar_one_or_none()
        return result.to_domain() if result is not None else None

    async def contains(self, aggregate_id: UUID) -> bool:
        return (
            await self.transaction.session.execute(
                select(UserTable.id).where(UserTable.id == aggregate_id)
            )
        ).scalar_one_or_none() is not None

    async def contains_by_username(self, username: str) -> bool:
        return (
            await self.transaction.session.execute(
                select(UserTable.id).where(UserTable.username == username)
            )
        ).scalar_one_or_none() is not None

    async def contains_by_phone_number(self, phone_number: str) -> bool:
        return (
            await self.transaction.session.execute(
                select(UserTable.id).where(UserTable.phone_number == phone_number)
            )
        ).scalar_one_or_none() is not None

    async def range(self, aggregate_ids: Sequence[UUID]) -> Sequence[User]:
        result: Sequence[UserTable] = (
            (
                await self.transaction.session.execute(
                    select(UserTable).where(UserTable.id.in_(aggregate_ids))
                )
            )
            .scalars()
            .all()
        )
        return [x.to_domain() for x in result]

    async def save(self, aggregate: User) -> User:
        from_domain: UserTable = UserTable.from_domain(aggregate)
        merged: UserTable = await self.transaction.session.merge(from_domain)
        self.transaction.session.add(merged)
        return merged.to_domain()

    async def save_all(self, aggregates: Sequence[User]) -> Sequence[User]:
        processed: Sequence[UserTable] = []
        for x in aggregates:
            from_domain: UserTable = UserTable.from_domain(x)
            merged: UserTable = await self.transaction.session.merge(from_domain)
            self.transaction.session.add(merged)
            processed.append(merged)
        return [x.to_domain() for x in processed]

    async def delete(self, aggregate: User) -> User:
        from_domain: UserTable = UserTable.from_domain(aggregate)
        merged: UserTable = await self.transaction.session.merge(from_domain)
        await self.transaction.session.delete(merged)
        return merged.to_domain()

    async def delete_all(self, aggregates: Sequence[User]) -> Sequence[User]:
        processed: Sequence[UserTable] = []
        for x in aggregates:
            from_domain: UserTable = UserTable.from_domain(x)
            merged: UserTable = await self.transaction.session.merge(from_domain)
            await self.transaction.session.delete(merged)
            processed.append(merged)
        return [x.to_domain() for x in processed]

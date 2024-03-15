import asyncio
from typing import Sequence, AsyncGenerator
from datetime import UTC, date, datetime
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio.engine import AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from apps.user.domain.models.user import User
from common.enums.gender import Gender
from common.enums.user_role import UserRole
from common.settings.config import Config
from models.user import UserTable

BACKOFFICERS: Sequence[User] = [
    User.create(
        username="jieun",
        password="Pa55word!!",
        role=UserRole.BACKOFFICER,
        name="강지은",
        address="인천광역시 서구 청라커낼로300 B동 1505호",
        phone_number="01022445124",
        gender=Gender.FEMALE,
        birth_date=date.fromisoformat("1998-11-25"),
        billing_name="강지은",
        terms_and_conditions_agreement=datetime.now(UTC),
        marketing_promotions_agreement=None,
    )
]


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    config: Config = Config()
    engine: AsyncEngine = create_async_engine(
        url=config.database.url,
        pool_size=config.database.pool_size,
        echo=config.debug,
    )
    session: AsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False)()
    yield session
    await session.commit()
    await session.close()


async def main() -> None:
    async with get_session() as session:
        for backofficer in BACKOFFICERS:
            session.add(await UserTable.from_domain(backofficer))


if __name__ == "__main__":
    asyncio.run(main())

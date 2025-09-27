# isort:skip_file
import sys

sys.path.extend(["./", "../"])
import typer
from app.core.config import settings
from adi_rag_utils.audit.models import User as UserORM
from app.infrastructure.postgres.queries.user import UserQueries
from app.infrastructure.postgres.session import acreate_sessionmaker
from loguru import logger
import asyncio
from app.domain.user.schema import User

app = typer.Typer()


@app.command()
def seed_anonymous_user() -> None:
    asyncio.run(aseed_anonymous_user())


async def aseed_anonymous_user() -> None:
    async_db_session = acreate_sessionmaker(
        connection_uri=settings.ASYNC_SQLALCHEMY_DATABASE_URI
    )
    async with async_db_session() as db_session:
        user_queries = UserQueries(db_session=db_session)
        anonymous_user = await user_queries.get_by_id(id=settings.ANONMYOUS_USER_UID)
        if anonymous_user:
            logger.info("Anonymous user already exists in database")
            return
        logger.info("Anonymous user does not existing, creating")
        await user_queries.create(
            user=UserORM(
                user_id=settings.ANONMYOUS_USER_UID, email=settings.ANONYMOUS_USER_EMAIL
            )
        )
        await db_session.commit()
        await db_session.close()
        logger.info("Anonymous user successfully created")


@app.command()
def fetch_user(user_id: str) -> None:
    asyncio.run(afetch_user(user_id=user_id))


async def afetch_user(user_id: str) -> None:
    async_db_session = acreate_sessionmaker(
        connection_uri=settings.ASYNC_SQLALCHEMY_DATABASE_URI
    )
    async with async_db_session() as db_session:
        user_queries = UserQueries(db_session=db_session)
        user = await user_queries.get_by_id(id=user_id)
        logger.info(User.create_from_orm(user))


if __name__ == "__main__":
    app()

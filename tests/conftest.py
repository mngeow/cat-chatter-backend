import random
import string
from typing import Generator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from loguru import logger
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.domain.user.schema import User
from app.main import app
from app.routes.deps.security import validate_api_key, validate_azure_oidc_token

settings.APFS_CHAT_MULTI_INDEX_RAG = True


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def client() -> Generator:
    with TestClient(app, backend="asyncio") as c:
        yield c


def generate_random_string(length: int = 10):
    """Generate a random string of uppercase and lowercase letters with the given length."""
    letters = string.ascii_letters
    return "".join(random.choice(letters) for i in range(length))


def validate_api_key_override():
    """
    This override is to bypass api key verification for testing
    """
    pass


def validate_azure_sso_token_override():
    return User(id="user1", email="user1@example.com")


@pytest.fixture(scope="session", autouse=True)
def prepare_database() -> None:
    from sqlalchemy import create_engine, text
    from sqlalchemy_utils import create_database, database_exists, drop_database

    from app.core.config import settings

    logger.info("Preparing database")
    logger.info(settings.SQLALCHEMY_DATABASE_URI)

    try:
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
        if not database_exists(engine.url):
            create_database(engine.url)
    except Exception as ex:
        logger.error(
            f"Error creating database {settings.SQLALCHEMY_DATABASE_URI}, {str(ex) or repr(ex)}"
        )

    alembic_cfg = Config("alembic.ini")

    command.upgrade(alembic_cfg, "head")

    with open(f"{settings.SEED_DATA_PATH}/sample_chat_data.sql", "r") as file:
        sql_file_text = file.read()
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.execute(text(sql_file_text))
            session.commit()
            logger.info("Sample data successfully seeded!")
        except Exception as ex:
            logger.error(f"Something failed: {str(ex)}")
            session.rollback()
        finally:
            session.close()

    yield

    logger.success("Done!")

    drop_database(url=settings.SQLALCHEMY_DATABASE_URI)


app.dependency_overrides[validate_api_key] = validate_api_key_override
app.dependency_overrides[validate_azure_oidc_token] = validate_azure_sso_token_override

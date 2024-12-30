from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session
from sqlalchemy.pool import NullPool
from typing import Generator
from loguru import logger

engine = create_engine(
    url=settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True
)

def create_session(connection_uri: str) -> scoped_session:
    if settings.ENABLE_DB_CONNECTION_POOLING:
        engine = create_engine(
            connection_uri,
            pool_pre_ping=True,
            pool_size=settings.DB_CONNECTION_POOL_SIZE,
            max_overflow=settings.DB_CONNECTION_POOL_MAX_OVERFLOW,
        )
    else:
        engine = create_engine(connection_uri, pool_pre_ping=True, poolclass=NullPool)
    return Session(autoflush=True, bind=engine)

def get_session() -> Generator:
    SessionLocal = Session(autocommit=False, autoflush=False, bind=engine)
    try:
        yield SessionLocal
        SessionLocal.commit()
    except Exception as ex:
        logger.error(
            f"Something failed, rolling back database transaction. {str(ex) or repr(ex)}"
        )
        SessionLocal.rollback()
        raise
    finally:
        SessionLocal.close()
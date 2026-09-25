"""Database engine and declarative models shared by the API and Alembic."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is required")
    return url


engine = create_engine(database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

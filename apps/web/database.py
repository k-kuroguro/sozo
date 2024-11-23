from contextlib import contextmanager
from typing import ContextManager, Generator

from sqlmodel import Session, SQLModel, create_engine

from .constants import SQLITE_URL

_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})


def create_db_and_tables() -> None:
    from . import schemas  # noqa: F401

    SQLModel.metadata.create_all(_engine)


def get_session_generator() -> Generator[Session, None, None]:
    with Session(_engine) as session:
        yield session


def get_session_context() -> ContextManager[Session]:
    return contextmanager(get_session_generator)()

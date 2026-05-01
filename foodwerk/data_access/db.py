"""Database facade (SQLModel + SQLite).

Design pattern: Facade — hides engine creation, schema init, and session
management behind a single object. The rest of the app only calls
``Database.init_schema_and_seed()`` and ``Database.engine``.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, Session, create_engine, select

from ..domain.models import User
from .seed import FoodWerkSeeder


class Database:
    """Database facade: engine creation, schema init, and session scope."""

    def __init__(self, database_url: Optional[str] = None, *, echo: bool = False) -> None:
        self._database_url = database_url or os.getenv("DATABASE_URL") or self._default_sqlite_url()
        self._engine: Engine = create_engine(
            self._database_url,
            echo=echo,
            connect_args={"check_same_thread": False},
        )

    @staticmethod
    def _default_sqlite_url() -> str:
        Path("data").mkdir(parents=True, exist_ok=True)
        return "sqlite:///data/foodwerk.db"

    @property
    def engine(self) -> Engine:
        return self._engine

    def init_schema_and_seed(self) -> None:
        """Create all tables and seed demo data if the DB is empty."""
        SQLModel.metadata.create_all(self._engine)
        with Session(self._engine) as session:
            if session.exec(select(User)).first() is None:
                FoodWerkSeeder().seed(session)
                session.commit()

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        """Transactional session scope — commits on success, rolls back on error."""
        session = Session(self._engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

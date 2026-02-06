import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from base import Base


class DatabaseConnection:
    def __init__(self):
        self._engine = create_engine(
            self._get_database_url(),
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
        self._SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine
        )

    def get_session(self):
        return self._SessionLocal()

    def _get_database_url(self) -> str:
        return os.getenv("DATABASE_URL")

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker




class DatabaseConnection:
    def __init__(self, database_url: str):
        if not database_url:
            raise ValueError("DATABASE_URL is not provided")
        self._engine = create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
        self._Session = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine
        )

    def get_session(self):
        return self._Session()

    def _get_database_url(self) -> str:
        return os.getenv("DATABASE_URL")

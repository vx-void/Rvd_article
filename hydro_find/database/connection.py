# hydro_find/database/connection.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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
        self._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

    def get_session(self):
        return self._SessionLocal()

    def create_all_tables(self):
        Base.metadata.create_all(bind=self._engine)

    def _get_database_url(self) -> str:
        url = os.getenv("DATABASE_URL")
        if url:
            return url
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "password")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "hydro_db")
        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

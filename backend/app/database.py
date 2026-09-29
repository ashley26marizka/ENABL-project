from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings


def _make_engine(url: str):
    is_sqlite = url.startswith("sqlite")
    # Ensure psycopg2 driver is used for plain postgresql:// URLs
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    return create_engine(url, pool_pre_ping=not is_sqlite, connect_args=connect_args)


engine = _make_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def _engine_kwargs(database_url: str) -> dict[str, Any]:
    """Restituisce engine kwargs tuned by backend type."""
    kwargs: dict[str, Any] = {
        "pool_pre_ping": True,
    }
    if database_url.startswith("sqlite"):
        # Needed for SQLite when used via FastAPI dependency/threading.
        kwargs["connect_args"] = {"check_same_thread": False}
    return kwargs


engine = create_engine(
    settings.database_url,
    echo=settings.sql_echo,
    **_engine_kwargs(settings.database_url),
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency che restituisce una sessione DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

"""
Questo modulo contiene il "motore" del database.

- Engine: Gestisce le connessioni del database (low-level). "Ponte" verso Postgres.
- Session: Rappresenta l'unità di lavoro (high-level). Usiamo una session per request.
"""

# Crea l'engine usando il DATABASE_URL dai settings (.env o default) 
engine = create_engine(settings.database_url, pool_pre_ping=True)

# Session factory: crea Session objects legati all'engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency che fornisce una DB session ad ogni request
    e la chiude al termine della request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

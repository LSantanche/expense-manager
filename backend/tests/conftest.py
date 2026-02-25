import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import get_db
from app.main import create_app
from app.models.base import Base
from app.models.document import Document  # noqa: F401
from app.models.expense import Expense  # noqa: F401

# Expense va importato comunque altrimenti create_all potrebbe non creare tabelle

@pytest.fixture()
def engine():
    # DB SQLite in-memory per test: veloce, gratis, riproducibile
    engine = create_engine(
        "sqlite+pysqlite:///:memory:", # DB in RAM, sparisce a fine test run
        connect_args={"check_same_thread": False}, # SQLite blocca di default i thread diversi (mentre TestClient può usarli)
        poolclass=StaticPool, # Assicura stessa connessione
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture()
def db_session(engine):
    """Crea una session SQLAlchemy isolata per test"""
    SessionTesting = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    session = SessionTesting()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    """Aggancia DB in-memory all'API"""
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

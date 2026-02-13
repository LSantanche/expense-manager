from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Classe base per i modelli SQLAlchemy.
    Tutte le tabelle partono da questa struttura

    Alembic userà Base.metadata per sapere quale tabella esiste.
    """
    pass

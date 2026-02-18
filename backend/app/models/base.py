from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Convenzione per i nomi di vincoli/indici.
# Aiuta Alembic (autogenerate) a produrre migrazioni più stabili e leggibili.
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata_obj = MetaData(naming_convention=NAMING_CONVENTION)


class Base(DeclarativeBase):
    """
    Classe base per i modelli SQLAlchemy.

    - Tutte le tabelle ereditano da questa classe.
    - Alembic userà Base.metadata per capire quali tabelle/colonne esistono.
    """
    metadata = metadata_obj


class TimestampMixin:
    """
    Mixin riutilizzabile per i timestamp di auditing.

    Utile per:
    - debug
    - tracciamento (anche in ottica MLOps/logging)
    - gestione modifiche nel tempo
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

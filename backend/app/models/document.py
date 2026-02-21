from __future__ import annotations

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Document(TimestampMixin, Base):
    __tablename__ = "documents"

    # UUID come stringa (più semplice da gestire cross-db)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # path relativo (es: data/documents/<id>/original.pdf)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)

    sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="uploaded", index=True)

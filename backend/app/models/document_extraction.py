from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class DocumentExtraction(TimestampMixin, Base):
    __tablename__ = "document_extractions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False, index=True)

    # versione dell'estrattore (es: "rule_v0")
    extraction_version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # JSON string (serializzato) con fields + needs_review
    payload_json: Mapped[str] = mapped_column(Text(), nullable=False)

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Expense(Base, TimestampMixin):
    """
    Tabella delle spese.

    È una "core business entity": una singola spesa inserita manualmente
    o (in futuro) estratta da una ricevuta tramite OCR/estrazione.
    """

    __tablename__ = "expenses"

    # Identificativo univoco della riga
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Importo: usiamo Decimal (tramite Numeric) per evitare errori di arrotondamento dei float
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Codice valuta ISO 4217 (es. "EUR"). Default lato applicazione.
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")

    # Data della transazione/spesa
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Esercente/merchant (manuale o OCR). Nullable perché l'OCR può fallire e vogliamo comunque salvare il record.
    merchant: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Categoria (sarà utile per analytics/forecast e per la classificazione futura)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Metodo di pagamento (opzionale)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Note libere (utile anche per RAG/ricerche testuali future)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Origine del dato: oggi "manual", domani anche "ocr"
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")

    # Flag per revisione human-in-the-loop (bassa confidence, incongruenze, ecc.)
    needs_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

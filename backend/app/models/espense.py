from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Expense(Base):
    """
    Tabella delle spese.

    Questa è una core business entity:
    una singola spesa inserita manualmente o estratta da una ricevuta.
    """

    __tablename__ = "expenses"

    # Primary key (id unico per ogni riga)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Cifra pagata (usiamo Numeric essendo una cifra)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # ISO currency code, e.g. "EUR"
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")

    # Quando è avvenuta la spesa
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Venditore (input utente o output OCR)
    merchant: Mapped[str] = mapped_column(String(255), nullable=False)

    # Campi opzionali: categoria spesa, metodo di pagamento, eventuali note
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Flag usata per la revisione human-in-the-loop (OCR con bassa confidence, inconsistenze, etc.)
    needs_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Timestamps per auditing (utile per prodotto e debugging)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

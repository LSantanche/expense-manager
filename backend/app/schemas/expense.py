from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ExpenseBase(BaseModel):
    """Schema base di una spesa (campi condivisi)."""

    amount: Decimal = Field(..., ge=0)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    expense_date: date

    merchant: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=100)
    payment_method: str | None = Field(default=None, max_length=50)
    notes: str | None = None

    # Utile per macro OCR: oggi "manual", domani "ocr"
    source: str = Field(default="manual", max_length=20)

    # Utile per HITL: coda di revisione
    needs_review: bool = False


class ExpenseCreate(ExpenseBase):
    """Input per creare una spesa."""
    pass


class ExpenseRead(ExpenseBase):
    """Output di lettura spesa."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ExpenseListResponse(BaseModel):
    """Risposta paginata per lista spese."""
    items: list[ExpenseRead]
    total: int
    limit: int
    offset: int

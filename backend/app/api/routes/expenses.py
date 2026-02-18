from __future__ import annotations

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.expense import ExpenseCreate, ExpenseListResponse, ExpenseRead, ExpenseUpdate
from app.services.expenses import (
    create_expense,
    delete_expense,
    get_expense,
    list_expenses,
    update_expense,
)

router = APIRouter(prefix="/expenses", tags=["expenses"])
db_dep = Depends(get_db)
db_query = Query(default=None)
db_query_ge0 = Query(default=None, ge=0)


@router.post("", response_model=ExpenseRead, status_code=201)
def create_expense_endpoint(payload: ExpenseCreate, db: Session = db_dep) -> ExpenseRead:
    """Crea una spesa (manuale per ora)."""
    return create_expense(db, payload)


@router.get("", response_model=ExpenseListResponse)
def list_expenses_endpoint(
    db: Session = db_dep,
    date_from: date | None = db_query,
    date_to: date | None = db_query,
    merchant: str | None = db_query,
    category: str | None = db_query,
    source: str | None = db_query,
    needs_review: bool | None = db_query,
    min_amount: Decimal | None = db_query_ge0,
    max_amount: Decimal | None = db_query_ge0,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> ExpenseListResponse:
    """Lista spese con filtri base + paginazione."""
    items, total = list_expenses(
        db,
        date_from=date_from,
        date_to=date_to,
        merchant=merchant,
        category=category,
        source=source,
        needs_review=needs_review,
        min_amount=min_amount,
        max_amount=max_amount,
        limit=limit,
        offset=offset,
    )
    return ExpenseListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense_endpoint(
    expense_id: int = Path(..., ge=1),
    db: Session = db_dep,
) -> ExpenseRead:
    """Ritorna una singola spesa per id."""
    expense = get_expense(db, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.patch("/{expense_id}", response_model=ExpenseRead)
def update_expense_endpoint(
    payload: ExpenseUpdate,
    expense_id: int = Path(..., ge=1),
    db: Session = db_dep,
) -> ExpenseRead:
    """Update parziale di una spesa (utile per correzioni HITL)."""
    expense = update_expense(db, expense_id, payload)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.delete("/{expense_id}", status_code=204)
def delete_expense_endpoint(
    expense_id: int = Path(..., ge=1),
    db: Session = db_dep,
) -> Response:
    """Elimina una spesa."""
    ok = delete_expense(db, expense_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Expense not found")
    return Response(status_code=204)

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


def create_expense(db: Session, payload: ExpenseCreate) -> Expense:
    """Crea una spesa a DB e ritorna l'oggetto persistito."""
    expense = Expense(**payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def _apply_filters(
    stmt: Select,
    *,
    date_from: date | None,
    date_to: date | None,
    merchant: str | None,
    category: str | None,
    source: str | None,
    needs_review: bool | None,
    min_amount: Decimal | None,
    max_amount: Decimal | None,
) -> Select:
    """Applica filtri opzionali alla select (riusata per list e count)."""
    if date_from is not None:
        stmt = stmt.where(Expense.expense_date >= date_from)
    if date_to is not None:
        stmt = stmt.where(Expense.expense_date <= date_to)

    if merchant is not None:
        # Ricerca parziale case-insensitive (comoda lato UI)
        stmt = stmt.where(Expense.merchant.ilike(f"%{merchant}%"))
    if category is not None:
        stmt = stmt.where(Expense.category == category)
    if source is not None:
        stmt = stmt.where(Expense.source == source)

    if needs_review is not None:
        stmt = stmt.where(Expense.needs_review == needs_review)

    if min_amount is not None:
        stmt = stmt.where(Expense.amount >= min_amount)
    if max_amount is not None:
        stmt = stmt.where(Expense.amount <= max_amount)

    return stmt


def list_expenses(
    db: Session,
    *,
    date_from: date | None,
    date_to: date | None,
    merchant: str | None,
    category: str | None,
    source: str | None,
    needs_review: bool | None,
    min_amount: Decimal | None,
    max_amount: Decimal | None,
    limit: int,
    offset: int,
) -> tuple[list[Expense], int]:
    """Lista paginata + total count (per UI e per evaluation)."""
    base_stmt = select(Expense).order_by(Expense.expense_date.desc(), Expense.id.desc())
    base_stmt = _apply_filters(
        base_stmt,
        date_from=date_from,
        date_to=date_to,
        merchant=merchant,
        category=category,
        source=source,
        needs_review=needs_review,
        min_amount=min_amount,
        max_amount=max_amount,
    )

    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = int(db.scalar(count_stmt) or 0)

    items_stmt = base_stmt.limit(limit).offset(offset)
    items = list(db.scalars(items_stmt).all())
    return items, total


def get_expense(db: Session, expense_id: int) -> Expense | None:
    """Ritorna una spesa per id, oppure None se non esiste."""
    return db.get(Expense, expense_id)


def update_expense(db: Session, expense_id: int, payload: ExpenseUpdate) -> Expense | None:
    """Aggiorna parzialmente una spesa (PATCH semantics)."""
    expense = db.get(Expense, expense_id)
    if expense is None:
        return None

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(expense, field, value)

    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense_id: int) -> bool:
    """Elimina una spesa. True se eliminata, False se non trovata."""
    expense = db.get(Expense, expense_id)
    if expense is None:
        return False

    db.delete(expense)
    db.commit()
    return True

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    # Crea la tabella "expenses" (spese).
    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),

        # Importo: Numeric(12,2) è più adatto dei float per valori monetari
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),

        # Valuta: di default EUR (default lato DB, così è robusto anche senza passarlo)
        sa.Column("currency", sa.String(length=3), nullable=False, server_default=sa.text("'EUR'")),

        # Data della spesa
        sa.Column("expense_date", sa.Date(), nullable=False),

        # Esercente/merchant
        sa.Column("merchant", sa.String(length=255), nullable=False),

        # Campi opzionali
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("payment_method", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),

        # Flag per human-in-the-loop (più avanti)
        sa.Column("needs_review", sa.Boolean(), nullable=False, server_default=sa.text("false")),

        # Timestamp “da prodotto”
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    # Elimina la tabella "expenses" (rollback della migrazione).
    op.drop_table("expenses")

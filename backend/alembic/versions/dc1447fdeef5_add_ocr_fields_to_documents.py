"""add ocr fields to documents

Revision ID: dc1447fdeef5
Revises: 0b8de384c16c
Create Date: 2026-02-22 21:53:31.801281

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'dc1447fdeef5'
down_revision: str | Sequence[str] | None = '0b8de384c16c'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("ocr_text_plain", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("ocr_json_path", sa.String(length=500), nullable=True))
    op.add_column("documents", sa.Column("error_message", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("documents", "error_message")
    op.drop_column("documents", "ocr_json_path")
    op.drop_column("documents", "ocr_text_plain")

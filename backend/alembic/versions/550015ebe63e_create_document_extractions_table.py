"""create document_extractions table

Revision ID: 550015ebe63e
Revises: e944ce668afe
Create Date: 2026-03-18 22:54:31.619015

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '550015ebe63e'
down_revision: str | Sequence[str] | None = 'e944ce668afe'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "document_extractions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("document_id", sa.String(length=36), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("extraction_version", sa.String(length=50), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_document_extractions_document_id", "document_extractions", ["document_id"])
    op.create_index("ix_document_extractions_extraction_version", "document_extractions", ["extraction_version"])


def downgrade() -> None:
    op.drop_index("ix_document_extractions_extraction_version", table_name="document_extractions")
    op.drop_index("ix_document_extractions_document_id", table_name="document_extractions")
    op.drop_table("document_extractions")

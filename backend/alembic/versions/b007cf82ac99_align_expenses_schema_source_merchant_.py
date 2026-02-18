from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "<LASCIATO_DAL_FILE_GENERATO>"
down_revision: str | Sequence[str] | None = "d54903da836e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Batch mode: compatibile anche con SQLite
    with op.batch_alter_table("expenses") as batch_op:
        # 1) Aggiungo "source" con default robusto lato DB
        batch_op.add_column(
            sa.Column("source", sa.String(length=20), nullable=False, server_default=sa.text("'manual'"))
        )

        # 2) Rendo merchant nullable (OCR può fallire)
        batch_op.alter_column("merchant", existing_type=sa.String(length=255), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("expenses") as batch_op:
        batch_op.alter_column("merchant", existing_type=sa.String(length=255), nullable=False)
        batch_op.drop_column("source")

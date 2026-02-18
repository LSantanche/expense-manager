from __future__ import annotations

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.core.config import settings
from app.models import Base  # Importa anche i modelli tramite app.models/__init__.py

# Config Alembic: legge alembic.ini e permette override a runtime
config = context.config

# Impostiamo l'URL del DB a partire dalle impostazioni dell'app (backend/.env)
config.set_main_option("sqlalchemy.url", settings.database_url)

# Configura il logging usando la sezione di logging in alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata dei modelli ORM: serve per autogenerate (diff tra modelli e DB)
target_metadata = Base.metadata


def _configure_context_common(**kwargs):
    """
    Impostazioni comuni per context.configure().

    - compare_type=True: Alembic rileva cambi tipo colonna (utile in evoluzione schema)
    - compare_server_default=True: rileva cambi sui default lato DB
    """
    return dict(
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        **kwargs,
    )


def run_migrations_offline() -> None:
    """
    Modalità offline: Alembic genera SQL senza aprire connessioni al DB.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **_configure_context_common(),
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Modalità online: Alembic si connette al DB ed esegue direttamente le migrazioni.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Per SQLite, le alter table sono limitate: render_as_batch aiuta nelle migrazioni future.
        render_as_batch = connection.dialect.name == "sqlite"

        context.configure(
            connection=connection,
            render_as_batch=render_as_batch,
            **_configure_context_common(),
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

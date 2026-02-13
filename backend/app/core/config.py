from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Legge da .env se presente (in backend/)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Ci aspettiamo una variabile APP_ENV (default: local)
    app_env: str = "local"
    # Ci aspettiamo un DATABASE_URL (default: postgresql+psycopg://expense:expense@localhost:5432/expense_db)
    database_url: str = "postgresql+psycopg://expense:expense@localhost:5432/expense_db"


settings = Settings()

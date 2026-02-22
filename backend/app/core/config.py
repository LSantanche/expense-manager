from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    # Carica sempre backend/.env indipendentemente dalla working directory.
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = "local"
    database_url: str = "postgresql+psycopg://expense:expense@localhost:5432/expense_db"
    sql_echo: bool = False
    # Directory base dove salviamo file e artefatti locali (upload, OCR json, ecc.)
    storage_dir: str = "data"
    # OCR: percorso opzionale a tesseract.exe (se non è nel PATH)
    tesseract_cmd: str | None = None
    # OCR: lingue tesseract (es: "eng" oppure "ita+eng" se installi i language pack)
    tesseract_lang: str = "eng"

    @property
    def storage_path(self) -> Path:
        # Percorso assoluto: backend/<storage_dir>
        return BACKEND_DIR / self.storage_dir

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

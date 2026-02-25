from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import UploadFile

ALLOWED_MIME_PREFIXES = ("image/",)
ALLOWED_MIME_EXACT = ("application/pdf",)


def is_allowed_mime(mime_type: str) -> bool:
    return mime_type.startswith(ALLOWED_MIME_PREFIXES) or mime_type in ALLOWED_MIME_EXACT


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_uploaded_document(
    *,
    base_dir: Path,
    upload: UploadFile,
) -> dict[str, Any]:
    """
    Salva un UploadFile su disco in:
    base_dir/documents/<uuid>/original.<ext>
    e crea anche metadata.json.

    Ritorna un dizionario con metadati utili per API response.
    """
    document_id = str(uuid4())
    doc_dir = base_dir / "documents" / document_id
    ensure_dir(doc_dir)

    original_name = upload.filename or "uploaded_file"
    mime_type = upload.content_type or "application/octet-stream"

    # Estensione: se manca, usiamo un default in base al mime
    suffix = Path(original_name).suffix
    if not suffix:
        if mime_type == "application/pdf":
            suffix = ".pdf"
        elif mime_type.startswith("image/"):
            # fallback generico, non perfetto ma ok per storage
            suffix = ".img"
        else:
            suffix = ".bin"

    stored_name = f"original{suffix}"
    stored_path = doc_dir / stored_name

    sha256 = hashlib.sha256()
    size_bytes = 0

    # Scrittura a chunk per non caricare tutto in RAM
    with stored_path.open("wb") as f:
        while True:
            chunk = upload.file.read(1024 * 1024)  # 1MB
            if not chunk:
                break
            f.write(chunk)
            sha256.update(chunk)
            size_bytes += len(chunk)

    # Chiudiamo il file upload
    upload.file.close()

    created_at = datetime.now(UTC).isoformat()
    stored_rel = Path("documents") / document_id / stored_name

    metadata = {
        "document_id": document_id,
        "original_filename": original_name,
        "mime_type": mime_type,
        "size_bytes": size_bytes,
        "sha256": sha256.hexdigest(),
        "stored_relative_path": str(stored_rel),
        "created_at": created_at,
    }

    # Salviamo metadata.json accanto al file
    (doc_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    # Per la response torniamo path relativo "backend/<...>" (utile in locale)
    return {
        "document_id": document_id,
        "original_filename": original_name,
        "mime_type": mime_type,
        "size_bytes": size_bytes,
        "sha256": metadata["sha256"],
        "stored_relative_path": metadata["stored_relative_path"],
        "created_at": created_at,
    }

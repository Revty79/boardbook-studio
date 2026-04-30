from pathlib import Path

from fastapi import UploadFile

from app.core.config import get_settings


def save_upload_file(upload_file: UploadFile, *, folder: str) -> str:
    settings = get_settings()
    media_root = Path(settings.media_dir)
    target_dir = media_root / folder
    target_dir.mkdir(parents=True, exist_ok=True)

    safe_name = upload_file.filename or "upload.bin"
    target_path = target_dir / safe_name

    bytes_data = upload_file.file.read()
    with target_path.open("wb") as out:
        out.write(bytes_data)

    return str(target_path.relative_to(media_root)).replace("\\", "/")

from fastapi import HTTPException, UploadFile
from app.config.base import PROJECT_URL
from pathlib import Path
from io import BytesIO
from PIL import Image
import uuid


def full_url(path: str) -> str:
    return f"{path}"


def verify_image(data: bytes, filename: str) -> None:
    try:
        img = Image.open(BytesIO(data))
        img.verify()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image: {filename}"
        )


def convert_to_webp(data: bytes) -> bytes:
    img = Image.open(BytesIO(data)).convert("RGB")

    out = BytesIO()
    img.save(out, format="WEBP", quality=80)
    return out.getvalue()


def save_file(content: bytes, base_dir: Path) -> str:
    name = f"{uuid.uuid4()}.webp"
    path = base_dir / name
    path.write_bytes(content)
    return name


def process_image(file: UploadFile, base_dir: Path) -> str:
    raw = file.file.read()
    verify_image(raw, file.filename or "image")
    webp = convert_to_webp(raw)
    filename = save_file(webp, base_dir)
    return filename
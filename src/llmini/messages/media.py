import base64
import mimetypes
from pathlib import Path

from PIL import ExifTags, Image


def encode_image(image_path: str) -> str | None:
    path = Path(image_path)

    if not path.exists() or not path.is_file():
        return None

    mime, _ = mimetypes.guess_type(image_path)
    mime = mime or "application/octet-stream"

    with path.open("rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime};base64,{b64}"


def get_image_metadata(image_path: str) -> dict[str, str] | None:
    path = Path(image_path)

    if not path.exists() or not path.is_file():
        return None

    try:
        with Image.open(path) as img:
            metadata: dict[str, str] = {}

            metadata["file_size_bytes"] = str(path.stat().st_size)
            metadata["format"] = str(img.format)
            metadata["mode"] = str(img.mode)
            metadata["width"] = str(img.width)
            metadata["height"] = str(img.height)

            exif = img.getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    try:
                        metadata[str(tag)] = str(value)
                    except Exception:
                        metadata[str(tag)] = repr(value)

            return metadata

    except Exception:
        return None

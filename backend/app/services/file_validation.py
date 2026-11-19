"""Cheap file validation before expensive forensic processing."""
import io
from PIL import Image

IMAGE_SIGNATURES=((b"\xff\xd8\xff","image/jpeg"),(b"\x89PNG\r\n\x1a\n","image/png"),(b"RIFF","riff"))
def validate_upload(filename: str, raw: bytes, content_type: str) -> tuple[bool,str]:
    if not raw: return False,"Empty file"
    head=raw[:16]
    ext=filename.lower().rsplit(".",1)[-1] if "." in filename else ""
    if ext in {"jpg","jpeg","png","webp","tif","tiff","bmp"}:
        try:
            with Image.open(io.BytesIO(raw)) as im:
                im.verify()
            return True,"ok"
        except Exception as exc:
            return False,f"Invalid image: {exc}"
    if ext in {"mp4","mov","avi","mkv","webm","wav","mp3","m4a","flac","ogg","aac"}:
        return True,"container validation delegated to media parser"
    return False,"Unsupported extension"

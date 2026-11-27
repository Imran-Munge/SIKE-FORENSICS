import os
from datetime import datetime, timezone
from pathlib import Path
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
SUPABASE_BUCKET = os.getenv("SUPABASE_MEDIA_BUCKET", "original-media").strip()

_client: Client | None = None

def enabled() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)

def client() -> Client:
    global _client
    if not enabled():
        raise RuntimeError("Supabase is not configured")
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _client

def save_case(result: dict, raw: bytes | None = None, filename: str | None = None, content_type: str | None = None) -> dict:
    if not enabled():
        raise RuntimeError("Supabase is not configured")

    c = client()
    case_id = result["case_id"]
    now = result.get("analyzed_at") or datetime.now(timezone.utc).isoformat()
    media_path = None

    if raw is not None and filename:
        suffix = Path(filename).suffix.lower()
        media_path = f"{case_id}/{case_id}{suffix}"
        c.storage.from_(SUPABASE_BUCKET).upload(
            media_path,
            raw,
            {"content-type": content_type or "application/octet-stream", "upsert": "true"},
        )

    case_row = {
        "case_id": case_id,
        "filename": result.get("filename"),
        "media_type": result.get("media_type"),
        "mime_type": result.get("mime_type"),
        "size_bytes": result.get("size_bytes"),
        "sha256": result.get("sha256"),
        "verdict": result.get("verdict"),
        "confidence": result.get("confidence"),
        "analyzed_at": now,
        "result": result,
    }
    c.table("cases").upsert(case_row, on_conflict="case_id").execute()

    if media_path:
        c.table("media_files").upsert({
            "case_id": case_id,
            "storage_bucket": SUPABASE_BUCKET,
            "storage_path": media_path,
            "original_filename": filename,
            "mime_type": content_type,
            "size_bytes": len(raw),
            "sha256": result.get("sha256"),
        }, on_conflict="case_id,storage_path").execute()

    return result

def get_case(case_id: str) -> dict | None:
    rows = client().table("cases").select("result").eq("case_id", case_id).limit(1).execute().data
    return rows[0]["result"] if rows else None

def list_cases(limit: int = 100) -> list[dict]:
    return client().table("cases").select(
        "case_id,filename,media_type,verdict,confidence,analyzed_at"
    ).order("analyzed_at", desc=True).limit(limit).execute().data

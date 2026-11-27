import io
from PIL import Image
from app.services.analyzer import analyze_media

def test_unknown_is_inconclusive():
    r=analyze_media("x.bin","application/octet-stream",b"abc")
    assert r["media_type"]=="unknown"
    assert r["verdict"] in {"INCONCLUSIVE","SUSPICIOUS","HIGH_RISK_INDICATOR"}

def test_case_hash():
    buf=io.BytesIO()
    Image.new("RGB",(8,8),(255,255,255)).save(buf,format="JPEG")
    r=analyze_media("x.jpg","image/jpeg",buf.getvalue())
    assert r["case_id"].endswith(r["sha256"][:12])

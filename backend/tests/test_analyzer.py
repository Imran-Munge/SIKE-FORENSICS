from app.services.analyzer import analyze_media
def test_unknown_is_inconclusive():
    r=analyze_media("x.bin","application/octet-stream",b"abc")
    assert r["media_type"]=="unknown"
    assert r["verdict"] in {"INCONCLUSIVE","SUSPICIOUS","HIGH_RISK_INDICATOR"}
def test_case_hash():
    r=analyze_media("x.jpg","image/jpeg",b"abc")
    assert r["case_id"].endswith(r["sha256"][:12])

from app.services.evidence import fuse_signals
from app.services.case_store import save_case, load_case

def test_fusion_is_uncertain_by_default():
    r=fuse_signals({"signals":{"provenance":{"c2pa_marker_detected":False}}})
    assert r["verdict"]=="NO_STRONG_INDICATOR"
    assert 0 <= r["score"] <= 1

def test_case_roundtrip(tmp_path, monkeypatch):
    import app.services.case_store as cs
    monkeypatch.setattr(cs,"DATA",tmp_path)
    data={"case_id":"case-test123","verdict":"INCONCLUSIVE"}
    save_case(data)
    assert load_case("case-test123")==data

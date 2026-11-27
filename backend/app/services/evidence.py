def _item(name, score, source, reliability, explanation, model=None):
    x={"signal":name,"score":round(float(score),3),"source":source,"reliability":reliability,"explanation":explanation}
    if model: x["model_id"]=model
    return x

def fuse_signals(analysis):
    s=analysis.get("signals",{}); evidence=[]; score=0.0
    image=s.get("image",{}); ela=image.get("ela_mean")
    if ela is not None:
        v=0.25 if ela>12 else 0.10 if ela>5 else 0.0
        evidence.append(_item("recompression",v,"ELA","medium","Elevated recompression error can indicate editing, but also occurs in normal image pipelines."))
        score+=v
    if s.get("provenance",{}).get("c2pa_marker_detected"):
        evidence.append(_item("content_credentials_marker",0,"C2PA marker","high","A marker was detected; cryptographic provenance verification is still required."))
    detector=s.get("detectors",{})
    for d in detector.get("results",[]):
        if isinstance(d,dict) and isinstance(d.get("score"),(int,float)):
            ds=float(d["score"]); score=max(score,ds)
            evidence.append(_item("ai_detector",ds,"licensed detector","medium","Model output is an indicator, not proof.",d.get("model") or d.get("model_id")))
    score=min(max(score,0),0.99)
    verdict="SUSPICIOUS" if score>=0.65 else "INCONCLUSIVE"
    if score>=0.85: verdict="HIGH_RISK_INDICATOR"
    band="low" if score<0.35 else "medium" if score<0.65 else "high"
    return {"score":round(score,3),"verdict":verdict,"confidence_band":band,"evidence":evidence,
            "reasons":[e["explanation"] for e in evidence],"method":"multi-signal, non-conclusive fusion"}

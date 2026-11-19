def fuse_signals(analysis):
    signals=analysis.get("signals",{})
    score=0.0; reasons=[]
    image=signals.get("image",{})
    ela=image.get("ela_mean")
    if ela is not None:
        if ela>12: score+=0.25; reasons.append("Elevated recompression error signal.")
        elif ela>5: score+=0.10; reasons.append("Moderate recompression error signal.")
    ent=signals.get("entropy")
    if ent is not None and ent<2.0: reasons.append("Low byte entropy in sampled data.")
    if signals.get("provenance",{}).get("c2pa_marker_detected"): reasons.append("Content-credential marker detected; provenance still requires verification.")
    score=min(score,0.95)
    verdict="SUSPICIOUS" if score>=0.5 else "INCONCLUSIVE"
    return {"score":round(score,3),"verdict":verdict,"reasons":reasons,
            "confidence_band":"low" if score<0.5 else "medium"}

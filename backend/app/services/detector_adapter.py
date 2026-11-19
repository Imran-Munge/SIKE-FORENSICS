"""Optional ForensiX runtime adapter.
The core API remains usable without model packages/weights. Model loading is
explicit and gated by the SIKE model registry.
"""
import os
from typing import Any

ENABLED = os.getenv("SIKE_ENABLE_FORENSIX", "0") == "1"

def run_forensix(path: str, models: list[str]) -> dict[str, Any]:
    if not ENABLED:
        return {"status":"disabled","models":models,"results":[],"reason":"SIKE_ENABLE_FORENSIX=1 is required"}
    try:
        import forensix
    except Exception as exc:
        return {"status":"unavailable","models":models,"results":[],"reason":str(exc)}
    results=[]
    for name in models:
        try:
            det=forensix.load(name)
            pred=det.predict(path)
            results.append({"model":name,"label":getattr(pred,"label",None),"score":getattr(pred,"score",None),"details":getattr(pred,"details",{})})
        except Exception as exc:
            results.append({"model":name,"error":str(exc)})
    return {"status":"ok","models":models,"results":results}

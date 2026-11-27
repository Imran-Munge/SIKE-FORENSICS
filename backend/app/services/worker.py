import os
from .detector_adapter import run_forensix

ENABLED=os.getenv("SIKE_ENABLE_FORENSIX","0")=="1"

def run_detectors(path, modality, models):
    requested=[m["name"] for m in models if m.get("enabled", True) and m.get("commercial_ok", False)]
    if not requested:
        return {"status":"disabled","modality":modality,"results":[],"message":"No production-enabled licensed detector is configured."}
    if modality=="image" and ENABLED:
        return {"status":"ok","modality":modality,"results":run_forensix(path, requested)}
    return {"status":"planned","modality":modality,"results":[],"message":"Detector worker is not enabled for this modality in the current deployment."}

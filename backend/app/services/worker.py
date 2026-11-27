import os, tempfile
from pathlib import Path
from .detector_adapter import run_forensix

def run_optional_detectors(kind, filename, raw, model_names):
    enabled=os.getenv("SIKE_ENABLE_AI_WORKERS","0")=="1"
    if not enabled:
        return {"status":"disabled","models":model_names,"results":[],"reason":"Set SIKE_ENABLE_AI_WORKERS=1 only after installing and licensing the selected models."}
    suffix=Path(filename).suffix or ".bin"
    with tempfile.NamedTemporaryFile(delete=False,suffix=suffix) as f:
        f.write(raw); path=f.name
    try:
        return run_forensix(path, model_names)
    finally:
        Path(path).unlink(missing_ok=True)

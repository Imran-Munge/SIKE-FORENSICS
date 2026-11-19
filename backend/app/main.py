from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from .services.analyzer import analyze_media
from .services.report import build_report
from .services.cleaner import clean_metadata
from .services.removal import build_removal_request

app = FastAPI(title="SIKE FORENSICS API", version="0.1.0")
DATA = Path("data"); DATA.mkdir(exist_ok=True)

@app.get("/health")
def health(): return {"status":"ok","service":"sike-forensics"}

@app.post("/api/v1/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.filename: raise HTTPException(400, "Filename is required")
    raw = await file.read()
    if len(raw) > 250 * 1024 * 1024: raise HTTPException(413, "File exceeds 250 MB limit")
    return JSONResponse(analyze_media(file.filename, file.content_type or "", raw))

@app.post("/api/v1/report")
async def report(file: UploadFile = File(...)):
    raw = await file.read()
    return JSONResponse(build_report(analyze_media(file.filename, file.content_type or "", raw)))

@app.post("/api/v1/clean")
async def clean(file: UploadFile = File(...)):
    raw = await file.read()
    cleaned, info = clean_metadata(file.filename, raw)
    out = DATA / ("cleaned-" + Path(file.filename).name)
    out.write_bytes(cleaned)
    return {"filename": out.name, "path": str(out), "actions": info}

@app.post("/api/v1/removal-request")
async def removal(file: UploadFile = File(...)):
    raw = await file.read()
    return JSONResponse(build_removal_request(analyze_media(file.filename, file.content_type or "", raw)))

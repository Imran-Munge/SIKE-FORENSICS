from pathlib import Path
import hashlib,os
from fastapi import FastAPI,File,UploadFile,HTTPException
from fastapi.responses import JSONResponse,HTMLResponse,Response
from fastapi.middleware.cors import CORSMiddleware
from .services.analyzer import analyze_media
from .services.report import build_report
from .services.report_html import render_report
from .services.evidence_package import build_package
from .services.cleaner import clean_metadata
from .services.removal import build_removal_request
from .services.file_validation import validate_upload
from .services.case_store import save_case,load_case
app=FastAPI(title="SIKE FORENSICS API",version="1.1.0")
origins=[x.strip() for x in os.getenv("SIKE_CORS_ORIGINS","http://localhost:3000").split(",") if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
DATA=Path("data");DATA.mkdir(exist_ok=True);MAX_BYTES=250*1024*1024
@app.get("/health")
def health():return {"status":"ok","service":"sike-forensics","version":"1.1.0","max_upload_bytes":MAX_BYTES}
async def read_upload(file):
    if not file.filename:raise HTTPException(400,"Filename is required")
    raw=await file.read()
    if len(raw)>MAX_BYTES:raise HTTPException(413,"File exceeds 250 MB limit")
    ok,reason=validate_upload(file.filename,raw,file.content_type or "")
    if not ok:raise HTTPException(415,reason)
    return raw
async def analyze_and_store(file):
    raw=await read_upload(file);r=analyze_media(file.filename,file.content_type or "",raw);save_case(r);return r
@app.post("/api/v1/analyze")
async def analyze(file:UploadFile=File(...)):return JSONResponse(await analyze_and_store(file))
@app.get("/api/v1/cases")
def list_cases():
    cases=[]
    for p in sorted((DATA/"cases").glob("case-*.json"),key=lambda x:x.stat().st_mtime,reverse=True):
        try:
            r=load_case(p.stem);cases.append({k:r.get(k) for k in ("case_id","filename","media_type","verdict","confidence","analyzed_at")})
        except Exception:continue
    return {"cases":cases[:100]}
@app.get("/api/v1/cases/{case_id}")
def get_case(case_id:str):
    r=load_case(case_id)
    if not r:raise HTTPException(404,"Case not found")
    return JSONResponse(r)
@app.get("/api/v1/cases/{case_id}/report.html",response_class=HTMLResponse)
def case_report_html(case_id:str):
    r=load_case(case_id)
    if not r:raise HTTPException(404,"Case not found")
    return HTMLResponse(render_report(r))
@app.get("/api/v1/cases/{case_id}/package")
def case_package(case_id:str):
    r=load_case(case_id)
    if not r:raise HTTPException(404,"Case not found")
    data,h=build_package(r)
    return Response(data,media_type="application/zip",headers={"Content-Disposition":f'attachment; filename="{case_id}-evidence.zip"',"X-Package-SHA256":h})
@app.get("/api/v1/cases/{case_id}/removal-request")
def case_removal(case_id:str):
    r=load_case(case_id)
    if not r:raise HTTPException(404,"Case not found")
    return JSONResponse(build_removal_request(r))
@app.post("/api/v1/report")
async def report(file:UploadFile=File(...)):
    return JSONResponse(build_report(await analyze_and_store(file)))
@app.post("/api/v1/clean")
async def clean(file:UploadFile=File(...)):
    raw=await read_upload(file);cleaned,info=clean_metadata(file.filename,raw)
    original=hashlib.sha256(raw).hexdigest();cleaned_hash=hashlib.sha256(cleaned).hexdigest()
    return Response(cleaned,media_type=file.content_type or "application/octet-stream",headers={"Content-Disposition":f'attachment; filename="cleaned-{Path(file.filename).name}"',"X-Original-SHA256":original,"X-Cleaned-SHA256":cleaned_hash,"X-Cleaning-Actions":"; ".join(info)})
@app.post("/api/v1/removal-request")
async def removal(file:UploadFile=File(...)):return JSONResponse(build_removal_request(await analyze_and_store(file)))

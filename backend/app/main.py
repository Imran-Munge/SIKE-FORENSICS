from pathlib import Path
import hashlib
from fastapi import FastAPI,File,UploadFile,HTTPException
from fastapi.responses import JSONResponse,HTMLResponse,Response
from .services.analyzer import analyze_media
from .services.report import build_report
from .services.report_html import render_report
from .services.evidence_package import build_package
from .services.cleaner import clean_metadata
from .services.removal import build_removal_request
from .services.file_validation import validate_upload
from .services.case_store import save_case,load_case

app=FastAPI(title="SIKE FORENSICS API",version="1.0.0")
DATA=Path("data");DATA.mkdir(exist_ok=True)
MAX_BYTES=250*1024*1024

@app.get("/health")
def health(): return {"status":"ok","service":"sike-forensics","version":"1.0.0"}

async def read_upload(file:UploadFile):
    if not file.filename: raise HTTPException(400,"Filename is required")
    raw=await file.read()
    if len(raw)>MAX_BYTES: raise HTTPException(413,"File exceeds 250 MB limit")
    ok,reason=validate_upload(file.filename,raw,file.content_type or "")
    if not ok: raise HTTPException(415,reason)
    return raw

@app.post("/api/v1/analyze")
async def analyze(file:UploadFile=File(...)):
    raw=await read_upload(file); result=analyze_media(file.filename,file.content_type or "",raw); save_case(result); return JSONResponse(result)

@app.get("/api/v1/cases/{case_id}")
def get_case(case_id:str):
    result=load_case(case_id)
    if not result: raise HTTPException(404,"Case not found")
    return JSONResponse(result)

@app.get("/api/v1/cases/{case_id}/report.html",response_class=HTMLResponse)
def case_report_html(case_id:str):
    result=load_case(case_id)
    if not result: raise HTTPException(404,"Case not found")
    return HTMLResponse(render_report(result))

@app.get("/api/v1/cases/{case_id}/package")
def case_package(case_id:str):
    result=load_case(case_id)
    if not result: raise HTTPException(404,"Case not found")
    data,package_hash=build_package(result)
    return Response(data,media_type="application/zip",headers={"Content-Disposition":f'attachment; filename="{case_id}-evidence.zip"',"X-Package-SHA256":package_hash})

@app.post("/api/v1/report")
async def report(file:UploadFile=File(...)):
    raw=await read_upload(file); result=analyze_media(file.filename,file.content_type or "",raw); save_case(result); return JSONResponse(build_report(result))

@app.post("/api/v1/clean")
async def clean(file:UploadFile=File(...)):
    raw=await read_upload(file); cleaned,info=clean_metadata(file.filename,raw); out=DATA/("cleaned-"+Path(file.filename).name); out.write_bytes(cleaned)
    return {"filename":out.name,"actions":info,"original_sha256":hashlib.sha256(raw).hexdigest(),"cleaned_sha256":hashlib.sha256(cleaned).hexdigest()}

@app.post("/api/v1/removal-request")
async def removal(file:UploadFile=File(...)):
    raw=await read_upload(file); result=analyze_media(file.filename,file.content_type or "",raw); save_case(result); return JSONResponse(build_removal_request(result))

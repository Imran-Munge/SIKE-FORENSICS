import io, hashlib
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ExifTags
import numpy as np
from .provenance import inspect_provenance
from .media import video_info, audio_info
from .evidence import fuse_signals


def detector_plan(kind):
    return {"image":[{"name":"commfor","role":"AI-generated image detector","license_gate":"required"},{"name":"rine","role":"AI-generated image detector","license_gate":"required"},{"name":"safe","role":"lightweight image detector","license_gate":"required"},{"name":"classical","role":"ELA/noise/frequency/copy-move","license_gate":"open-source"}],"video":[{"name":"gend","role":"temporal/face deepfake detector","license_gate":"required"},{"name":"dfdet-clip","role":"video deepfake detector","license_gate":"required"},{"name":"syncnet","role":"audio-video synchronization","license_gate":"required"}],"audio":[{"name":"aasist","role":"synthetic speech/spoof detector","license_gate":"required"},{"name":"nes2net-x-itw","role":"real-world speech anti-spoofing","license_gate":"required"}]}.get(kind,[])
from .analysis_pipeline import image_signal_bundle, explain_signals

IMAGE_EXT={".jpg",".jpeg",".png",".webp",".tif",".tiff",".bmp"}
VIDEO_EXT={".mp4",".mov",".avi",".mkv",".webm"}
AUDIO_EXT={".wav",".mp3",".m4a",".flac",".ogg",".aac"}

def sha256(b): return hashlib.sha256(b).hexdigest()

def entropy(b):
    if not b: return 0.0
    x=np.frombuffer(b,dtype=np.uint8); _,c=np.unique(x,return_counts=True); p=c/len(x)
    return float(-(p*np.log2(p)).sum())

def image_forensics(raw):
    im=Image.open(io.BytesIO(raw)); exif={}
    try:
        for k,v in im.getexif().items(): exif[str(ExifTags.TAGS.get(k,k))]=str(v)[:500]
    except Exception: pass
    gray=np.asarray(im.convert("L"),dtype=np.float32); ela=None
    if im.format in {"JPEG","WEBP"}:
        buf=io.BytesIO(); im.save(buf,format=im.format,quality=90)
        b=np.asarray(Image.open(io.BytesIO(buf.getvalue())).convert("RGB"),dtype=np.float32)
        a=np.asarray(im.convert("RGB"),dtype=np.float32); ela=float(np.mean(np.abs(a-b)))
    return {"dimensions":[im.width,im.height],"format":im.format,"mode":im.mode,"exif":exif,
            "ela_mean":ela,"pixel_mean":float(gray.mean()),"pixel_std":float(gray.std())}

def analyze_media(filename, content_type, raw):
    ext=Path(filename).suffix.lower()
    kind="image" if ext in IMAGE_EXT else "video" if ext in VIDEO_EXT else "audio" if ext in AUDIO_EXT else "unknown"
    r={"case_id":"case-"+sha256(raw)[:12],"filename":filename,"media_type":kind,"mime":content_type,
       "size_bytes":len(raw),"sha256":sha256(raw),"analyzed_at":datetime.now(timezone.utc).isoformat(),
       "signals":{},"verdict":"INCONCLUSIVE","confidence":0.0,"limitations":[]}
    r["signals"]["entropy"]=entropy(raw[:2_000_000])
    r["signals"]["provenance"]=inspect_provenance(raw)\n    r["signals"]["detector_plan"]=detector_plan(kind)
    if kind=="image":\n        r["signals"]["image"]=image_forensics(raw)\n        try:\n            r["signals"]["classical"]=image_signal_bundle(raw)\n            r["signals"]["analysis_notes"]=explain_signals(r["signals"]["classical"])\n        except Exception as e:\n            r["limitations"].append("Classical image analysis failed: "+str(e))
    elif kind=="video":
        try: r["signals"]["video"]=video_info(raw)
        except Exception as e: r["signals"]["video"]={"error":str(e)}
        r["limitations"].append("AI deepfake and temporal model inference is a planned worker.")
    elif kind=="audio":
        try: r["signals"]["audio"]=audio_info(filename,raw)
        except Exception as e: r["signals"]["audio"]={"error":str(e)}
        r["limitations"].append("Synthetic-voice model inference is a planned worker.")
    else: r["limitations"].append("Unsupported media type.")
    fused=fuse_signals(r); r["verdict"]=fused["verdict"]; r["confidence"]=fused["score"]; r["signals"]["evidence_fusion"]=fused
    return r

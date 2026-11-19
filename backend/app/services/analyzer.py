import io, hashlib
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ExifTags
import numpy as np
from .provenance import inspect_provenance
from .media import video_info, audio_info
from .evidence import fuse_signals
from .analysis_pipeline import image_signal_bundle, explain_signals

IMAGE_EXT={".jpg",".jpeg",".png",".webp",".tif",".tiff",".bmp"}
VIDEO_EXT={".mp4",".mov",".avi",".mkv",".webm"}
AUDIO_EXT={".wav",".mp3",".m4a",".flac",".ogg",".aac"}

def detector_plan(kind):
    return {
      "image":[{"name":"commfor","role":"AI-generated image detector"},{"name":"rine","role":"AI-generated image detector"},{"name":"safe","role":"lightweight image detector"},{"name":"classical","role":"ELA/noise/frequency/copy-move"}],
      "video":[{"name":"gend","role":"temporal/face deepfake detector"},{"name":"dfdet-clip","role":"video deepfake detector"},{"name":"syncnet","role":"audio-video synchronization"}],
      "audio":[{"name":"aasist","role":"synthetic speech/spoof detector"},{"name":"nes2net-x-itw","role":"real-world speech anti-spoofing"}]
    }.get(kind,[])

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
    r["signals"]["provenance"]=inspect_provenance(raw)
    r["signals"]["detector_plan"]=detector_plan(kind)
    if kind=="image":
        r["signals"]["image"]=image_forensics(raw)
        try:
            r["signals"]["classical"]=image_signal_bundle(raw)
            r["signals"]["analysis_notes"]=explain_signals(r["signals"]["classical"])
        except Exception as e:
            r["limitations"].append("Classical image analysis failed: "+str(e))
        r["limitations"].append("AI detector inference runs through the optional licensed worker.")
    elif kind=="video":
        try: r["signals"]["video"]=video_info(raw)
        except Exception as e: r["signals"]["video"]={"error":str(e)}
        r["limitations"].append("AI deepfake, temporal and A/V-sync inference runs through the optional licensed worker.")
    elif kind=="audio":
        try: r["signals"]["audio"]=audio_info(filename,raw)
        except Exception as e: r["signals"]["audio"]={"error":str(e)}
        r["limitations"].append("Synthetic-voice inference runs through the optional licensed worker.")
    else:
        r["limitations"].append("Unsupported media type.")
    fused=fuse_signals(r)
    r["verdict"]=fused["verdict"]; r["confidence"]=fused["score"]; r["signals"]["evidence_fusion"]=fused
    return r

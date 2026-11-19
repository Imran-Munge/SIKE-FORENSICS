import hashlib, io
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ExifTags
import numpy as np

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
    gray=np.asarray(im.convert("L"),dtype=np.float32)
    ela=None
    if im.format in {"JPEG","WEBP"}:
        buf=io.BytesIO(); im.save(buf,format=im.format,quality=90)
        b=np.asarray(Image.open(io.BytesIO(buf.getvalue())).convert("RGB"),dtype=np.float32)
        a=np.asarray(im.convert("RGB"),dtype=np.float32)
        ela=float(np.mean(np.abs(a-b)))
    return {"dimensions":[im.width,im.height],"format":im.format,"mode":im.mode,
            "exif":exif,"ela_mean":ela,"pixel_mean":float(gray.mean()),
            "pixel_std":float(gray.std())}

def analyze_media(filename, content_type, raw):
    ext=Path(filename).suffix.lower()
    kind="image" if ext in IMAGE_EXT else "video" if ext in VIDEO_EXT else "audio" if ext in AUDIO_EXT else "unknown"
    r={"case_id":"case-"+sha256(raw)[:12],"filename":filename,"media_type":kind,
       "mime":content_type,"size_bytes":len(raw),"sha256":sha256(raw),
       "analyzed_at":datetime.now(timezone.utc).isoformat(),"signals":{},
       "verdict":"INCONCLUSIVE","confidence":0.0,"limitations":[]}
    r["signals"]["entropy"]=entropy(raw[:2_000_000])
    if kind=="image": r["signals"]["image"]=image_forensics(raw)
    elif kind=="video":
        r["signals"]["video"]={"status":"sample-ready","note":"Add frame, temporal, face and A/V model workers."}
        r["limitations"].append("Deepfake and temporal model inference is not enabled in foundation build.")
    elif kind=="audio":
        r["signals"]["audio"]={"status":"sample-ready","note":"Add spectrogram, codec, prosody and synthetic-voice workers."}
        r["limitations"].append("Synthetic-voice model inference is not enabled in foundation build.")
    else: r["limitations"].append("Unsupported media type.")
    return r

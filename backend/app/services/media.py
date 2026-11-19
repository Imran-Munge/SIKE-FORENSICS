import io, wave
from pathlib import Path
import cv2
from mutagen import File as MutagenFile

def video_info(raw):
    p=Path("/tmp/sike-video-analysis")
    p.write_bytes(raw)
    cap=cv2.VideoCapture(str(p))
    fps=cap.get(cv2.CAP_PROP_FPS); frames=cap.get(cv2.CAP_PROP_FRAME_COUNT)
    width=cap.get(cv2.CAP_PROP_FRAME_WIDTH); height=cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    duration=(frames/fps) if fps else None
    cap.release(); p.unlink(missing_ok=True)
    return {"width":int(width),"height":int(height),"fps":round(fps,3) if fps else 0,
            "frame_count":int(frames),"duration_seconds":duration}

def audio_info(filename,raw):
    out={"format":Path(filename).suffix.lower(),"tags":{}}
    try:
        f=MutagenFile(io.BytesIO(raw))
        if f:
            out["tags"]={str(k):str(v)[:300] for k,v in (f.tags or {}).items()}
            out["length_seconds"]=getattr(f.info,"length",None)
            out["bitrate"]=getattr(f.info,"bitrate",None)
    except Exception: pass
    if Path(filename).suffix.lower()==".wav":
        try:
            w=wave.open(io.BytesIO(raw)); out.update({"channels":w.getnchannels(),"sample_rate":w.getframerate(),"sample_width":w.getsampwidth()}); w.close()
        except Exception: pass
    return out

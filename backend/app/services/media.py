import io, tempfile, wave
from pathlib import Path
import cv2
from mutagen import File as MutagenFile

def _temp(raw, suffix):
    f=tempfile.NamedTemporaryFile(delete=False,suffix=suffix); f.write(raw); f.close(); return Path(f.name)

def video_info(raw, sample_limit=12):
    p=_temp(raw,".video"); cap=cv2.VideoCapture(str(p))
    if not cap.isOpened(): p.unlink(missing_ok=True); raise ValueError("Unable to decode video")
    fps=cap.get(cv2.CAP_PROP_FPS) or 0; frames=cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    width=cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0; height=cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0
    duration=frames/fps if fps else None; samples=[]
    if frames and fps:
        n=min(sample_limit,int(frames))
        for i in range(n):
            idx=int(i*(frames-1)/max(1,n-1)); cap.set(cv2.CAP_PROP_POS_FRAMES,idx); ok,frame=cap.read()
            if ok: samples.append({"frame":idx,"time_seconds":round(idx/fps,3),"mean_luma":round(float(frame.mean()),3),"std_luma":round(float(frame.std()),3)})
    cap.release(); p.unlink(missing_ok=True)
    return {"width":int(width),"height":int(height),"fps":round(fps,3),"frame_count":int(frames),"duration_seconds":round(duration,3) if duration else None,"sampled_frames":samples}

def audio_info(filename,raw):
    out={"format":Path(filename).suffix.lower(),"tags":{}}
    try:
        f=MutagenFile(io.BytesIO(raw))
        if f:
            out["tags"]={str(k):str(v)[:300] for k,v in (f.tags or {}).items()}
            out["length_seconds"]=getattr(f.info,"length",None); out["bitrate"]=getattr(f.info,"bitrate",None)
    except Exception as exc: out["parse_warning"]=str(exc)
    if Path(filename).suffix.lower()==".wav":
        try:
            w=wave.open(io.BytesIO(raw)); out.update({"channels":w.getnchannels(),"sample_rate":w.getframerate(),"sample_width":w.getsampwidth()})
            frames=w.readframes(min(w.getnframes(),w.getframerate()*30)); w.close()
            import numpy as np
            x=np.frombuffer(frames,dtype=np.int16).astype(np.float32)
            if x.size:
                out["waveform_preview"]=[round(float(v),4) for v in x[::max(1,len(x)//256)][:256]]
                spec=np.abs(np.fft.rfft(x[:min(len(x),65536)])); out["spectral_energy_mean"]=round(float(spec.mean()),4)
        except Exception as exc: out["parse_warning"]=str(exc)
    return out

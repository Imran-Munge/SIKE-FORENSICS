import io
from pathlib import Path
from PIL import Image

def clean_metadata(filename, raw):
    ext=Path(filename).suffix.lower()
    if ext in {".jpg",".jpeg",".png",".webp",".tif",".tiff"}:
        im=Image.open(io.BytesIO(raw)); out=io.BytesIO()
        fmt=im.format or ("JPEG" if ext in {".jpg",".jpeg"} else "PNG")
        kw={"format":fmt}
        if fmt=="JPEG": kw["quality"]=95
        im.save(out,**kw)
        return out.getvalue(),["Re-encoded image without source EXIF metadata."]
    return raw,["No safe built-in cleaner for this media type; original bytes preserved."]

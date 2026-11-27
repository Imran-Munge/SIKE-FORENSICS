import json,zipfile,io,hashlib
def build_package(result):
    payload=json.dumps(result,indent=2,ensure_ascii=False).encode()
    mem=io.BytesIO()
    with zipfile.ZipFile(mem,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("case.json",payload)
        z.writestr("README.txt","SIKE FORENSICS evidence package. Preserve the original file separately. This package contains analysis output and SHA-256 identifiers; it is not a substitute for the original evidence.")
    return mem.getvalue(),hashlib.sha256(mem.getvalue()).hexdigest()

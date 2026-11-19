def inspect_provenance(raw):
    markers=[]
    for marker in (b"c2pa",b"jumbf",b"Content Credentials",b"contentcredentials"):
        if marker.lower() in raw.lower(): markers.append(marker.decode("ascii","ignore"))
    return {"c2pa_marker_detected":bool(markers),"markers":sorted(set(markers)),
            "status":"marker-detected" if markers else "not-detected",
            "note":"Marker detection is not equivalent to cryptographic C2PA verification."}

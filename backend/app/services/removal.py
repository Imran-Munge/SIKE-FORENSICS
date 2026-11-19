def build_removal_request(a):
    return {"subject":"Request for removal/review of suspected manipulated media",
            "case_id":a["case_id"],"file":a["filename"],"sha256":a["sha256"],
            "reason":"The attached forensic assessment identified signals that warrant authenticity review.",
            "evidence_summary":a["signals"],
            "recommended_action":"Request human review and preserve the original evidence before removal."}

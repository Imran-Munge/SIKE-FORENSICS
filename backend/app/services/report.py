from datetime import datetime, timezone
def build_report(a):
    return {"report_id":"report-"+a["case_id"][5:],"generated_at":datetime.now(timezone.utc).isoformat(),
            "assessment":{"verdict":a["verdict"],"confidence":a["confidence"],
            "warning":"Automated indicators are not proof."},"evidence":a}

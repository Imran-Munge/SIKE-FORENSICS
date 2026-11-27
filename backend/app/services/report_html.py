from html import escape

def _rows(obj, prefix=""):
    rows=[]
    if isinstance(obj, dict):
        for k,v in obj.items():
            rows.extend(_rows(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(obj, list):
        rows.append((prefix, ", ".join(str(x) for x in obj[:20])))
    else:
        rows.append((prefix, obj))
    return rows

def render_report_html(report: dict) -> str:
    a=report.get("evidence", report)
    assessment=report.get("assessment", {})
    rows=_rows(a)
    table="".join(f"<tr><td>{escape(str(k))}</td><td>{escape(str(v))}</td></tr>" for k,v in rows)
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{escape(report.get("report_id","SIKE FORENSICS Report"))}</title>
<style>
body{{font-family:Inter,Arial,sans-serif;margin:40px;color:#111827;background:#f6f7f9}}main{{max-width:1050px;margin:auto}}
header,.card{{background:white;border:1px solid #e4e7ec;border-radius:18px;padding:24px;margin-bottom:18px}}
h1{{margin:0 0 8px}}.muted{{color:#667085}}.verdict{{font-size:28px;font-weight:800}}table{{width:100%;border-collapse:collapse}}td{{padding:9px;border-bottom:1px solid #eef0f3;vertical-align:top}}td:first-child{{width:32%;font-weight:650}}
.warn{{padding:12px;background:#fff7ed;border:1px solid #fed7aa;border-radius:12px}}
</style></head><body><main>
<header><div class="muted">SIKE / FORENSICS</div><h1>Forensic Evidence Report</h1><div class="muted">{escape(str(report.get("report_id","")))}</div></header>
<section class="card"><div class="verdict">{escape(str(assessment.get("verdict",a.get("verdict","INCONCLUSIVE"))))}</div>
<p>Confidence score: {escape(str(assessment.get("confidence",a.get("confidence",0))))}</p>
<div class="warn">Automated forensic indicators are probabilistic. This report is an analytical aid, not proof of authenticity, authorship, intent, or legal conclusions.</div></section>
<section class="card"><h2>Evidence record</h2><table>{table}</table></section>
</main></body></html>"""

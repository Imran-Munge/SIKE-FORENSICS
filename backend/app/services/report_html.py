import html,json
def render_report(result):
    esc=lambda x:html.escape(str(x))
    title=f"SIKE FORENSICS — {esc(result['case_id'])}"
    body=json.dumps(result,indent=2,ensure_ascii=False)
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>{title}</title><style>body{{font-family:Arial,sans-serif;max-width:1000px;margin:40px auto;padding:0 20px;color:#111827}}h1{{font-size:28px}}.card{{border:1px solid #e5e7eb;border-radius:14px;padding:18px;margin:14px 0}}pre{{white-space:pre-wrap;background:#f8fafc;padding:16px;border-radius:10px;overflow:auto}}.accent{{color:#ea580c}}</style></head><body><h1>SIKE <span class='accent'>FORENSICS</span></h1><div class='card'><b>Case</b> {esc(result['case_id'])}<br><b>Verdict</b> {esc(result['verdict'])}<br><b>Confidence</b> {esc(result['confidence'])}<br><b>SHA-256</b> {esc(result['sha256'])}</div><div class='card'><b>Evidence record</b><pre>{esc(body)}</pre></div></body></html>"""

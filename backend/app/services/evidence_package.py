import io, json, zipfile
from .report_html import render_report_html

def build_evidence_package(result):
    report={"report_id":"report-"+result["case_id"][5:],"assessment":{"verdict":result["verdict"],"confidence":result["confidence"]},"evidence":result}
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("case.json",json.dumps(result,indent=2,default=str))
        z.writestr("report.json",json.dumps(report,indent=2,default=str))
        z.writestr("report.html",render_report_html(report))
        z.writestr("README.txt","SIKE FORENSICS evidence package. Automated indicators are probabilistic and must be independently reviewed.")
    return buf.getvalue()

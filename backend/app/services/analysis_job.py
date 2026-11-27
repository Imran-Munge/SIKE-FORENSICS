from .case_store import load_case
def job_status(case_id):
    r=load_case(case_id)
    if not r:return {"case_id":case_id,"status":"not_found"}
    return {"case_id":case_id,"status":"complete","verdict":r.get("verdict"),"confidence":r.get("confidence")}

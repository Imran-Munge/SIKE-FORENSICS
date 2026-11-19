from pathlib import Path
import json
DATA=Path("data/cases"); DATA.mkdir(parents=True,exist_ok=True)
def save_case(result:dict)->str:
    cid=result["case_id"]; (DATA/f"{cid}.json").write_text(json.dumps(result,indent=2,default=str))
    return str(DATA/f"{cid}.json")
def load_case(case_id:str)->dict|None:
    p=DATA/f"{case_id}.json"
    return json.loads(p.read_text()) if p.exists() else None

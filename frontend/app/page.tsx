"use client";
import {useState} from "react";
const API=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000";
const tabs=["Overview","Metadata","Provenance","AI Detection","Pixel Forensics","Video","Audio","Evidence","Reports","Evidence Package","Cleaning","Removal Request"];
function Card({title,children}:{title:string,children:any}){return <section className="card"><div className="cardTitle">{title}</div>{children}</section>}
function Json({value}:{value:any}){return <pre className="json">{JSON.stringify(value,null,2)}</pre>}
export default function Home(){
 const[file,setFile]=useState<File|null>(null),[result,setResult]=useState<any>(null),[busy,setBusy]=useState(false),[error,setError]=useState(""),[tab,setTab]=useState("Overview");
 async function analyze(){
  if(!file)return;setBusy(true);setError("");setResult(null);
  try{const fd=new FormData();fd.append("file",file);const r=await fetch(API+"/api/v1/analyze",{method:"POST",body:fd});const d=await r.json();if(!r.ok)throw Error(d.detail||"Analysis failed");setResult(d);setTab("Overview")}
  catch(e:any){setError(e.message||"Unable to analyze media")}finally{setBusy(false)}
 }
 const s=result?.signals||{};
 const download=(path:string)=>window.open(API+path,"_blank");
 return <main>
  <nav className="nav"><div><div className="logo">SIKE / FORENSICS</div><div className="sub">Digital media investigation workspace</div></div><div className="badge">LIGHT · EVIDENCE FIRST</div></nav>
  <div className="topgrid">
   <section className="intro"><div className="eyebrow">IMAGE · VIDEO · AUDIO</div><h1>Investigate media.<br/>Preserve the evidence.</h1><p>One workspace for provenance, metadata, classical forensics and licensed AI indicators. Every conclusion stays traceable and explicitly uncertain where the evidence is weak.</p></section>
   <Card title="New investigation"><div className="drop"><div className="uploadIcon">＋</div><strong>{file?file.name:"Choose evidence"}</strong><span>Image, video or audio · maximum 250 MB</span><input type="file" accept="image/*,video/*,audio/*" onChange={e=>setFile(e.target.files?.[0]||null)}/><button className="button" onClick={analyze} disabled={!file||busy}>{busy?"Analyzing…":"Analyze evidence"}</button>{error&&<span className="error">{error}</span>}</div></Card>
  </div>
  {result&&<div className="workspace">
   <aside className="tabs">{tabs.map(t=><button key={t} className={tab===t?"active":""} onClick={()=>setTab(t)}>{t}</button>)}</aside>
   <section className="content">
    <div className="casebar"><div><span className="label">CASE</span><b>{result.case_id}</b></div><div><span className="label">SHA-256</span><code>{result.sha256}</code></div><button className="button small" onClick={()=>download("/api/v1/cases/"+result.case_id+"/report.html")}>Open report</button></div>
    {tab==="Overview"&&<><div className="metrics"><div><span>Assessment</span><b>{result.verdict}</b></div><div><span>Confidence indicator</span><b>{Number(result.confidence).toFixed(3)}</b></div><div><span>Media</span><b>{result.media_type.toUpperCase()}</b></div><div><span>Size</span><b>{(result.size_bytes/1024/1024).toFixed(2)} MB</b></div></div><Card title="Evidence fusion"><Json value={s.evidence_fusion}/></Card><Card title="Limitations"><ul>{result.limitations.map((x:string)=><li key={x}>{x}</li>)}</ul></Card></>}
    {tab==="Metadata"&&<Card title="File & metadata"><Json value={{filename:result.filename,mime:result.mime,size_bytes:result.size_bytes,sha256:result.sha256,entropy:s.entropy,image:s.image?.exif||null,media:s.video||s.audio||null}}/></Card>}
    {tab==="Provenance"&&<Card title="C2PA / provenance"><Json value={s.provenance}/><p className="note">Markers are not treated as verified credentials. Cryptographic validation must be performed by a trusted provenance verifier.</p></Card>}
    {tab==="AI Detection"&&<Card title="AI detector status"><Json value={{plan:s.detector_plan,runtime:s.detectors}}/><p className="note">No model output is invented. A detector appears here only when its licensed runtime is installed and enabled.</p></Card>}
    {tab==="Pixel Forensics"&&<Card title="Image forensic signals"><Json value={{image:s.image,classical:s.classical,notes:s.analysis_notes}}/></Card>}
    {tab==="Video"&&<Card title="Video analysis"><Json value={s.video||{message:"Not a video case"}}/></Card>}
    {tab==="Audio"&&<Card title="Audio analysis"><Json value={s.audio||{message:"Not an audio case"}}/></Card>}
    {tab==="Evidence"&&<Card title="Normalized evidence signals"><Json value={s.evidence_fusion?.evidence||[]}/></Card>}
    {tab==="Reports"&&<Card title="Case report"><p>Generate the reproducible HTML report from this case.</p><button className="button" onClick={()=>download("/api/v1/cases/"+result.case_id+"/report.html")}>View HTML report</button></Card>}
    {tab==="Evidence Package"&&<Card title="Evidence package"><p>Download a ZIP containing the case JSON and package instructions.</p><button className="button" onClick={()=>download("/api/v1/cases/"+result.case_id+"/package")}>Download evidence package</button></Card>}
    {tab==="Cleaning"&&<Card title="Metadata cleaning"><p>Cleaning creates a derivative file. The original evidence hash remains unchanged.</p><button className="button" onClick={()=>download("/api/v1/cases/"+result.case_id+"/report.html")}>Review case before cleaning</button></Card>}
    {tab==="Removal Request"&&<Card title="Removal request"><p>Use the removal workflow to prepare a structured request based on the investigated case.</p><Json value={{case_id:result.case_id,status:"ready_for_request",sha256:result.sha256}}/></Card>}
   </section>
  </div>}
  {!result&&<section className="features"><Card title="Provenance">C2PA/content-credential markers and metadata are separated from model indicators.</Card><Card title="Forensics">ELA, noise, frequency, copy-move candidates, hashes and file structure remain auditable.</Card><Card title="Case management">Every investigation gets a deterministic case ID, SHA-256 and reproducible report.</Card></section>}
 </main>
}
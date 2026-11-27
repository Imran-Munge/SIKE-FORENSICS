"use client";
import {useState} from "react";
const API=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000";
const tabs=["Overview","Metadata","Provenance","AI Detection","Pixel Forensics","Video","Audio","Evidence","Reports","Evidence Package","Cleaning","Removal Request"];
function Card({title,children}:{title:string;children:any}){return <section className="card"><div className="cardTitle">{title}</div>{children}</section>}
function Json({value}:{value:any}){return <pre className="json">{JSON.stringify(value,null,2)}</pre>}
export default function Home(){
 const[file,setFile]=useState<File|null>(null),[result,setResult]=useState<any>(null),[busy,setBusy]=useState(false),[error,setError]=useState(""),[tab,setTab]=useState("Overview"),[drag,setDrag]=useState(false);
 async function analyze(){if(!file)return;setBusy(true);setError("");try{const f=new FormData();f.append("file",file);const r=await fetch(API+"/api/v1/analyze",{method:"POST",body:f});const d=await r.json();if(!r.ok)throw Error(d.detail||"Analysis failed");setResult(d);setTab("Overview")}catch(e:any){setError(e.message||"Analysis failed")}finally{setBusy(false)}}
 function choose(f:File|null){if(f){setFile(f);setResult(null);setError("")}}
 async function download(path:string,name:string,method="GET"){try{const opts:any={method};if(method==="POST"){const f=new FormData();f.append("file",file!);opts.body=f}const r=await fetch(API+path,opts);if(!r.ok)throw Error("Request failed");const blob=await r.blob();const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=name;a.click();URL.revokeObjectURL(a.href)}catch(e:any){setError(e.message)}}
 const s=result?.signals||{},score=Number(result?.confidence||0);
 return <main>
  <nav className="nav"><div><div className="logo">SIKE / FORENSICS</div><div className="sub">Digital media investigation workspace</div></div><div className="badge">LIGHT · EVIDENCE FIRST</div></nav>
  {!result?<div className="topgrid">
   <section className="intro"><div className="eyebrow">IMAGE · VIDEO · AUDIO</div><h1>Investigate media.<br/>Preserve the evidence.</h1><p>One workspace for provenance, metadata, classical forensics and licensed AI indicators. Conclusions remain traceable and explicitly uncertain where evidence is weak.</p></section>
   <Card title="New investigation"><div className={"drop "+(drag?"drag":"")} onDragOver={e=>{e.preventDefault();setDrag(true)}} onDragLeave={()=>setDrag(false)} onDrop={e=>{e.preventDefault();setDrag(false);choose(e.dataTransfer.files?.[0]||null)}}><div className="uploadIcon">＋</div><strong>{file?file.name:"Drop evidence here"}</strong><span>Image, video or audio · maximum 250 MB</span><input type="file" accept="image/*,video/*,audio/*" onChange={e=>choose(e.target.files?.[0]||null)}/><button className="button" onClick={analyze} disabled={!file||busy}>{busy?"Analyzing…":"Analyze evidence"}</button>{error&&<span className="error">{error}</span>}</div></Card>
  </div>:
  <div className="workspace">
   <aside className="tabs"><div className="sidecase"><span>CASE</span><b>{result.case_id}</b></div>{tabs.map(t=><button key={t} className={tab===t?"active":""} onClick={()=>setTab(t)}>{t}</button>)}<button onClick={()=>{setResult(null);setFile(null)}} className="reset">＋ New investigation</button></aside>
   <section className="content">
    <div className="casebar"><div><span className="label">CASE</span><b>{result.case_id}</b></div><div><span className="label">SHA-256</span><code>{result.sha256}</code></div><button className="button small" onClick={()=>window.open(API+"/api/v1/cases/"+result.case_id+"/report.html","_blank")}>Open report</button></div>
    {tab==="Overview"&&<><div className="metrics"><div><span>Assessment</span><b>{result.verdict}</b></div><div><span>Indicator score</span><b>{score.toFixed(3)}</b></div><div><span>Media</span><b>{result.media_type.toUpperCase()}</b></div><div><span>Size</span><b>{(result.size_bytes/1048576).toFixed(2)} MB</b></div></div><Card title="Evidence fusion"><Json value={s.evidence_fusion}/></Card><Card title="Limitations"><ul>{result.limitations.map((x:string)=><li key={x}>{x}</li>)}</ul></Card></>}
    {tab==="Metadata"&&<Card title="File & metadata"><Json value={{filename:result.filename,mime:result.mime,size_bytes:result.size_bytes,sha256:result.sha256,entropy:s.entropy,exif:s.image?.exif||{},video:s.video||null,audio:s.audio||null}}/></Card>}
    {tab==="Provenance"&&<Card title="C2PA / provenance"><Json value={s.provenance}/><p className="note">A byte marker is not cryptographic verification. Signed Content Credentials should be verified with a trusted verifier before making consequential claims.</p></Card>}
    {tab==="AI Detection"&&<Card title="AI detector status"><Json value={{plan:s.detector_plan,runtime:s.detectors}}/><p className="note">No model output is invented. Production activation requires verified code, weight and dataset licensing.</p></Card>}
    {tab==="Pixel Forensics"&&<Card title="Image forensic signals"><Json value={{image:s.image,classical:s.classical,notes:s.analysis_notes}}/></Card>}
    {tab==="Video"&&<Card title="Video structure & sampled timeline"><Json value={s.video||{message:"Not a video case"}}/></Card>}
    {tab==="Audio"&&<Card title="Audio structure & WAV spectral preview"><Json value={s.audio||{message:"Not an audio case"}}/></Card>}
    {tab==="Evidence"&&<Card title="Normalized evidence signals"><Json value={s.evidence_fusion?.evidence||[]}/></Card>}
    {tab==="Reports"&&<Card title="Forensic report"><p>Open the reproducible HTML report generated from the stored case.</p><button className="button" onClick={()=>window.open(API+"/api/v1/cases/"+result.case_id+"/report.html","_blank")}>Open HTML report</button></Card>}
    {tab==="Evidence Package"&&<Card title="Evidence package"><p>ZIP includes the case record and preservation instructions. Keep the original file separately.</p><button className="button" onClick={()=>download("/api/v1/cases/"+result.case_id+"/package",result.case_id+"-evidence.zip")}>Download evidence ZIP</button></Card>}
    {tab==="Cleaning"&&<Card title="Metadata cleaning"><p>Creates a derivative image. Original bytes are never modified.</p><button className="button" disabled={!file} onClick={()=>download("/api/v1/clean","cleaned-"+result.filename,"POST")}>Download cleaned derivative</button></Card>}
    {tab==="Removal Request"&&<Card title="Removal / review request"><p>Generate the structured request from the stored case.</p><button className="button" onClick={()=>window.open(API+"/api/v1/cases/"+result.case_id+"/removal-request","_blank")}>Open request JSON</button></Card>}
   </section>
  </div>}
  {!result&&<section className="features"><Card title="Provenance">C2PA markers, metadata and hashes remain separate from model indicators.</Card><Card title="Forensics">ELA, noise, frequency, copy-move candidates and media structure remain auditable.</Card><Card title="Case management">Deterministic case IDs, SHA-256 evidence hashes and reproducible reports.</Card></section>}
 </main>
}
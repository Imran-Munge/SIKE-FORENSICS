"use client";
import {useState} from "react";
const API=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000";
export default function Home(){
 const[file,setFile]=useState<File|null>(null),[result,setResult]=useState<any>(null),[busy,setBusy]=useState(false),[error,setError]=useState("");
 async function analyze(){
  if(!file)return;setBusy(true);setError("");setResult(null);
  try{const fd=new FormData();fd.append("file",file);const r=await fetch(API+"/api/v1/analyze",{method:"POST",body:fd});const data=await r.json();if(!r.ok)throw new Error(data.detail||"Analysis failed");setResult(data)}
  catch(e:any){setError(e.message||"Unable to analyze media")}finally{setBusy(false)}
 }
 return <main>
  <nav className="nav"><div className="logo">SIKE / FORENSICS</div><div className="badge">Evidence-first media analysis</div></nav>
  <section className="hero">
   <div><div className="eyebrow">IMAGE · VIDEO · AUDIO</div><h1>See the evidence behind media.</h1><p>Analyze provenance, metadata and forensic signals, then combine them into an explainable assessment with uncertainty instead of pretending a detector is absolute proof.</p></div>
   <div className="panel">
    <div className="drop">
     <div><p className="fileName">{file?file.name:"Choose an image, video or audio file"}</p>
      <input type="file" accept="image/*,video/*,audio/*" onChange={e=>setFile(e.target.files?.[0]||null)}/><br/><br/>
      <button className="button" onClick={analyze} disabled={!file||busy}>{busy?"Analyzing evidence…":"Analyze evidence"}</button>
      {error&&<p style={{color:"var(--bad)"}}>{error}</p>}
     </div>
    </div>
    {result&&<div className="result"><div className="verdict">{result.verdict}</div><div className="score">Confidence score: {Number(result.confidence||0).toFixed(3)} · Case {result.case_id}</div><pre style={{whiteSpace:"pre-wrap",overflow:"auto",maxHeight:320}}>{JSON.stringify(result,null,2)}</pre></div>}
   </div>
  </section>
  <section className="features"><div className="feature"><strong>Provenance</strong>C2PA and content-credential signals can be inspected alongside the original evidence.</div><div className="feature"><strong>Forensics</strong>Metadata, hashes, compression, ELA, noise and pixel-level indicators are kept separate from AI scores.</div><div className="feature"><strong>Case reports</strong>Every analysis receives a reproducible case ID and SHA-256 evidence hash.</div></section>
 </main>
}
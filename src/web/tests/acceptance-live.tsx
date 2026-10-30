import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { AcceptanceOperations } from '../src/components/chat/AcceptanceOperations';
import '../src/styles/globals.css';
import '../src/styles/chat-workbench.css';
function App() {
  const [samples,setSamples]=useState<{stage:string;conversation_id:string}[]>([]);
  const [index,setIndex]=useState(0);const [theme,setTheme]=useState('light');
  useEffect(()=>{fetch('/api/v1/acceptance-test/context').then(r=>r.json()).then(value=>setSamples(value.samples));},[]);
  return <main className={`requirement-center theme-${theme} chat-shell`} data-theme={theme} style={{display:'block',minHeight:'100vh',padding:24,overflow:'auto'}}>
    <section className="chat-main" style={{display:'block',maxWidth:820,width:'100%',margin:'auto'}}>
      <p>合成会话交互验收 · 真实 API · 不调用模型</p>
      <label>验收样本阶段 <select style={{background:"var(--rc-panel)",color:"var(--rc-text)",border:"1px solid var(--rc-border)",padding:4}} aria-label="验收样本阶段" value={index} onChange={event=>setIndex(Number(event.target.value))}>{samples.map((s,i)=><option key={s.stage} value={i}>{s.stage}</option>)}</select></label>
      <label>主题 <select style={{background:"var(--rc-panel)",color:"var(--rc-text)",border:"1px solid var(--rc-border)",padding:4}} aria-label="主题" value={theme} onChange={event=>setTheme(event.target.value)}><option value="light">浅色</option><option value="dark">深色</option></select></label>
      <h2>Chat · 本次交付验收</h2><p>请检查当前改动，并保留验收结果。</p>
      {samples[index] && <AcceptanceOperations key={samples[index].conversation_id} conversationId={samples[index].conversation_id}/>}
      <textarea aria-label="会话输入" disabled placeholder="此样本不发起模型请求" style={{width:'100%',marginTop:24,background:'var(--rc-panel)',color:'var(--rc-muted)',border:'1px solid var(--rc-border)',padding:8,boxSizing:'border-box'}}/>
    </section>
  </main>;
}
createRoot(document.getElementById('root')!).render(<App/>);

import React from 'react';
import {createRoot} from 'react-dom/client';
import {AcceptanceOperationSkeleton} from '../src/components/chat/AcceptanceOperationSkeleton';
import '../src/styles/globals.css';
const theme=new URLSearchParams(location.search).get('theme')==='dark'?'dark':'light';
createRoot(document.getElementById('root')!).render(<main className={`requirement-center theme-${theme}`} data-theme={theme} style={{minHeight:'100vh',padding:24,display:'block'}}>
  <div style={{maxWidth:820,width:'100%',margin:'0 auto'}}><header style={{display:'flex',justifyContent:'space-between',marginBottom:32}}><strong>MoonBox · 项目 Chat</strong><span>验收详情骨架</span></header>
  <p>当前需求 · Chat 隔离验收环境编排</p><p style={{marginBottom:24}}>完成当前变更后，检查应用并返回验收结果。</p>
  <AcceptanceOperationSkeleton/><p style={{marginTop:24}}>原消息正文与历史轮次保留在同一会话中。</p>
  <div style={{marginTop:80,padding:16,border:'1px solid var(--rc-border)',color:'var(--rc-muted)'}}>在当前会话继续交流…</div></div>
</main>);

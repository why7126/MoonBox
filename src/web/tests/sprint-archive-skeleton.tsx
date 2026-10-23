import React,{useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Archive} from 'lucide-react';
import {SprintArchiveDraft} from '../src/components/chat/SprintArchiveDraft';
import '../src/styles/globals.css';
import '../src/styles/chat-workbench.css';
import '../src/components/chat/sprint-archive-draft.css';
function Preview(){const [conflict,setConflict]=useState(true);return <main className="requirement-center theme-light" data-theme="light" style={{display:'block',padding:32,minHeight:'100vh',boxSizing:'border-box'}}>
<div style={{maxWidth:1100,margin:'auto'}}><p>UI 骨架审阅 · 合成数据，不调用 API，不执行归档</p><h1>需求研发流转看板</h1>
<section aria-label="当前迭代容量" style={{display:'flex',alignItems:'center',gap:28,padding:20,border:'1px solid #DDE3EE',background:'#fff',borderRadius:6}}><strong>sprint-099</strong><div style={{flex:1}}>24 / 30 人天<div style={{height:6,background:'#DDE3EE',marginTop:10}}><div style={{width:'80%',height:6,background:'#B9832E'}}/></div></div><button aria-label="归档迭代 sprint-099" data-testid="current-iteration-archive-action" style={{width:34,height:34,padding:0,border:0,borderRadius:6,background:'transparent',color:'#677085'}}><Archive size={18}/></button></section>
<p data-testid="current-iteration-archive-summary">范围内对象均已完成。点击进入会话，发送后检查最终归档条件。</p>
<section style={{border:'1px solid #DDE3EE',background:'#fff',borderRadius:6,marginTop:32,paddingTop:18}}><header style={{padding:'0 24px'}}><h2>sprint-099 · 迭代归档</h2><p>演示项目 / SPRINT / sprint-099</p></header><div style={{height:120,padding:24,color:'#677085'}}>保留已有会话历史与执行状态</div>{conflict&&<SprintArchiveDraft sprintId="sprint-099" onKeep={()=>setConflict(false)} onReplace={()=>setConflict(false)}/>}
<div style={{margin:'0 24px 24px',padding:16,border:'1px solid #DDE3EE',borderRadius:6}}><p data-testid="chat-prompt">请先帮我整理迭代复盘要点。</p><p style={{color:'#677085',fontSize:12}}>附件与 Skill 上下文保留</p><button disabled>发送</button></div></section></div></main>};
createRoot(document.getElementById('root')!).render(<Preview/>);

import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { ConversationMessages } from '../src/components/chat/ConversationMessages';
import { QuestionPanel } from '../src/components/chat/QuestionPanel';
import '../src/styles/globals.css';
import '../src/styles/chat-workbench.css';
localStorage.setItem('moonbox.session', JSON.stringify({ username:'synthetic', access_token:'synthetic-fixture-only' }));
function App() {
 const [data,setData]=useState<any>(null),[index,setIndex]=useState(0),[live,setLive]=useState(false);
 useEffect(()=>{let stop=false; let timer:ReturnType<typeof setTimeout>; const read=async()=>{const next=await fetch('/api/fixture/questions').then(r=>r.json());if(!stop){setData(next);timer=setTimeout(read,1000);}};void read();return()=>{stop=true;clearTimeout(timer);};},[]);
 const tid=live?data?.live.turn_id:data?.scenes[index]?.turn_id;
 return <main className="requirement-center theme-dark chat-shell" data-theme="dark" style={{display:'block',padding:24,overflow:'auto',height:'100vh'}}><div className="chat-main" style={{maxWidth:860,margin:'0 auto',display:'block'}}>
 <h1>执行中问答 · 隔离验收</h1><p>合成身份和独立数据库；卡片使用真实 API。模型轮次单独标记。</p>
 <label>状态样本<select aria-label="状态样本" value={index} onChange={e=>{setLive(false);setIndex(Number(e.target.value));}}>{data?.scenes.map((s:any,i:number)=><option value={i} key={s.id}>{s.state}</option>)}</select></label>
 <button onClick={()=>{setLive(true);void fetch('/api/fixture/questions/live',{method:'POST'});}}>真实模型同轮验证</button>
 {live&&<pre data-testid="live-result">{JSON.stringify(data?.live)}</pre>}
 {live && data?.live.conversation_id ? <ConversationMessages conversationId={data.live.conversation_id} onTrace={()=>{}}/> : tid&&<QuestionPanel key={tid} turnId={tid}/>}
 </div></main>;
}
createRoot(document.getElementById('root')!).render(<App/>);

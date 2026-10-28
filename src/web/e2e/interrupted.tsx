import React,{useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {TurnActivity} from '../src/components/chat/TurnActivity';
import {OperationVerification} from '../src/components/chat/OperationVerification';
import '../src/styles/globals.css';
import '../src/styles/tokens.generated.css';
import '../src/styles/workbench.css';
import '../src/styles/chat-workbench.css';
import '../src/components/chat/recovery-operation.css';
localStorage.setItem('moonbox.session',JSON.stringify({username:'isolated-test',access_token:'isolated-fixture-only'}));
function Sample(){
 const [turn,setTurn]=useState('');
 useEffect(()=>{void fetch('/api/fixture/scene').then(r=>r.json()).then(r=>setTurn(r.turn_id));},[]);
 return <main style={{padding:24,maxWidth:900,margin:'auto'}}><h1>后续完成核验</h1><p>隔离样本 · 原 Chat 已停止 · 使用真实核验接口</p>
 <button onClick={()=>void fetch('/api/fixture/stale/true',{method:'POST'})}>使验收输入过期</button>
 <button onClick={()=>void fetch('/api/fixture/stale/false',{method:'POST'})}>恢复有效输入</button>
 {turn&&<><section aria-label="需求卡片核验"><h2>卡片状态详情</h2><OperationVerification facts={{view_turn_id:turn}} onRefresh={()=>{}}/></section><TurnActivity turnId={turn} onTrace={()=>{}}/></>}</main>;
}
createRoot(document.getElementById('root')!).render(<Sample/>);

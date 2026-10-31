import React from 'react';import {createRoot} from 'react-dom/client';
import {RuntimePreflight} from '../src/components/chat/RuntimePreflight';
import '../src/styles/globals.css';
import '../src/styles/tokens.generated.css';
let scene='unavailable';
window.fetch=async()=>{
 if(scene==='loading')await new Promise(r=>setTimeout(r,10000));
 if(scene==='error')return new Response('{}',{status:503});
 return new Response(JSON.stringify({code:0,data:{conversation_id:'synthetic',checked_at:new Date().toISOString(),environment_key:null,template_key:null,acceptance_passed:false,status:scene,checks:['python','frontend','browser','worker'].map(name=>({name,status:scene==='configured'?'configured':'unavailable',reason_code:scene==='configured'?'runtime_probe_required':'verification_worker_unavailable'}))}}),{status:200,headers:{'Content-Type':'application/json'}});
};
function Fixture(){const[key,setKey]=React.useState(0);return <main className="requirement-center" data-theme="dark" style={{display:'block',maxWidth:1050,margin:'32px auto',padding:24}}><h2>验收能力卡片 · 合成状态验证</h2><label>测试场景 <select aria-label="测试场景" onChange={e=>{scene=e.target.value;setKey(v=>v+1);}}>{['unavailable','configured','loading','error'].map(x=><option key={x}>{x}</option>)}</select></label><RuntimePreflight key={key} conversationId="synthetic"/></main>}
createRoot(document.getElementById('root')!).render(<Fixture/>);

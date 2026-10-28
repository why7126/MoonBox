import {useEffect,useRef,useState} from 'react';
import {GovernanceError,governanceRequest} from '../workbench/governanceApi';
import type {DirectVerificationResponse} from '../../api/generated/governance';
import {directVerificationReasons as reasons} from './directVerificationReasons';
type Facts = DirectVerificationResponse;
const done=(f:Facts|null)=>!!f&&(['validated','recovered_valid','historical'].includes(f.state)||f.available===false||f.auto_verification?.state==='blocked');

export function useDirectVerification(turnId:string,autoFollow:boolean,expanded:boolean,onState:(state:string)=>void) {
 const [facts,setFacts]=useState<Facts|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState(''),[paused,setPaused]=useState(false);
 const observer=useRef(onState);observer.current=onState;
 const actions=useRef({read:()=>{},verify:()=>{}});
 const expansion=useRef(expanded);expansion.current=expanded;
 const generation=useRef(0);
 useEffect(()=>{
  const epoch=++generation.current;
  const url=`/api/v1/chat/turns/${encodeURIComponent(turnId)}/completion-verification`;
  let stopped=false,inflight=false,forbidden=false,count=0,current:Facts|null=null;
  let timer:ReturnType<typeof setTimeout>|undefined,controller:AbortController|undefined;
  const started=Date.now(),deadline=started+180000;
  const budgetTimer=setTimeout(()=>{
   if(!stopped&&autoFollow&&!done(current)){controller?.abort();inflight=false;clearTimeout(timer);setPaused(true);}
  },180000);
  const live=()=>!stopped&&generation.current===epoch;
  setFacts(null);setBusy(false);setError('');setPaused(false);
  const publish=(f:Facts)=>{
   current=f;setFacts(f);setError('');
   observer.current(['validated','recovered_valid'].includes(f.state)?f.state:
    ['pending','checking'].includes(f.auto_verification?.state||'')?'auto_checking':
    f.auto_verification?.state==='blocked'?'verification_blocked':autoFollow&&f.state==='needs_review'?'verification_waiting':f.state);
  };
  const schedule=()=>{
   clearTimeout(timer);
   if(!live()||!autoFollow||forbidden||done(current))return;
   if(count>=18||Date.now()>=deadline){setPaused(true);return;}
   if(document.hidden)return;
   timer=setTimeout(()=>void read(false),Math.min([2000,4000,8000,10000][Math.min(Math.max(count-1,0),3)],deadline-Date.now()));
  };
  const read=async(manual:boolean)=>{
   if(!live()||inflight||forbidden)return;
   if(!manual&&(count>=18||Date.now()>=deadline)){setPaused(true);return;}
   clearTimeout(timer);inflight=true;count++;controller=new AbortController();
   const requestController=controller;
   try {
    const f=await governanceRequest<Facts>(url,{signal:requestController.signal});
    if(live()&&!requestController.signal.aborted)publish(f);
   }catch(e){
    if(live()&&!requestController.signal.aborted){
     forbidden=e instanceof GovernanceError&&[401,403,404].includes(e.status);
     setError('核验状态暂不可读，请稍后重试。');
    }
   }finally {if(live()&&controller===requestController){inflight=false;schedule();}}
  };
  const verify=async()=>{
   if(!live()||inflight||forbidden||!current?.can_verify||!current.version)return;
   clearTimeout(timer);inflight=true;setBusy(true);controller=new AbortController();
   const requestController=controller;
   try{
    const f=await governanceRequest<Facts>(url,{method:'POST',body:JSON.stringify({expected_version:current.version}),signal:requestController.signal});
    if(live()&&!requestController.signal.aborted){publish(f);window.dispatchEvent(new Event('governance-operation-verified'));}
   }catch(e){
    if(live()&&!requestController.signal.aborted){
     forbidden=e instanceof GovernanceError&&[401,403,404].includes(e.status);
     setError(e instanceof GovernanceError?(reasons[e.kind||'']||e.message):'核验未通过，原成果和保护已保留。');
    }
   }finally{if(live()&&controller===requestController){inflight=false;setBusy(false);schedule();}}
  };
  actions.current={read:()=>void read(true),verify:()=>void verify()};
  const visibility=()=>{if(document.hidden)clearTimeout(timer);else schedule();};
  document.addEventListener('visibilitychange',visibility);
  if(autoFollow||expansion.current)void read(false);
  return()=>{stopped=true;controller?.abort();clearTimeout(timer);clearTimeout(budgetTimer);document.removeEventListener('visibilitychange',visibility);};
 },[turnId,autoFollow]);
 useEffect(()=>{if(expanded&&!autoFollow)actions.current.read();},[expanded,autoFollow,turnId]);
 return {facts,busy,error,paused,read:()=>actions.current.read(),verify:()=>actions.current.verify()};
}

import {useEffect,useRef,useState} from 'react';
import type {DeliverySource} from './DeliveryCardIdentity';

/** A navigation confirmation only; sending still requires Chat confirmation. */
export function DeliveryActionDialog({changeId,sources,project,label,command,onClose,onContinue}: {
 changeId:string;sources:DeliverySource[];project:string;label:string;command:string;
 onClose:()=>void;onContinue:(sourceId:string)=>void;
}) {
 const [sourceId,setSourceId]=useState(sources.length===1?sources[0].id:'');
 const dialog=useRef<HTMLElement>(null);
 useEffect(()=>{
  const trigger=document.activeElement instanceof HTMLElement?document.activeElement:null;
  dialog.current?.querySelector<HTMLButtonElement>('button')?.focus();
  return ()=>trigger?.focus();
 },[]);
 const valid=sources.some(source=>source.id===sourceId);
 return <div className="rc-settings-mask rc-action-mask rc-delivery-mask" role="presentation" onMouseDown={onClose}>
  <section ref={dialog} className="rc-flow-dialog rc-action-dialog rc-delivery-confirmation" role="dialog" aria-modal="true" aria-label="确认交付目标" onMouseDown={event=>event.stopPropagation()} onKeyDown={event=>{
   if(event.key==='Escape'){event.preventDefault();event.stopPropagation();onClose();}
   if(event.key==='Tab'){
    const nodes=Array.from(dialog.current?.querySelectorAll<HTMLElement>('button:not(:disabled),select')||[]);
    if(event.shiftKey&&document.activeElement===nodes[0]){event.preventDefault();nodes[nodes.length-1]?.focus();}
    else if(!event.shiftKey&&document.activeElement===nodes[nodes.length-1]){event.preventDefault();nodes[0]?.focus();}
   }
  }}>
   <header className="rc-dialog-head"><h2>确认交付目标</h2><button type="button" aria-label="关闭交付目标确认" onClick={onClose}>×</button></header>
   <div className="rc-action-body">
    <p>项目：{project}</p><p>目标 Change：<strong >{changeId}</strong></p>
    <label>来源事项<select aria-label="选择来源事项" value={sourceId} onChange={event=>setSourceId(event.target.value)}>
     <option value="" disabled>请选择本次来源</option>
     {sources.map(source=><option key={source.id} value={source.id}>{source.id} · {source.title}</option>)}
    </select></label>
    <div className="rc-action-command" >{valid?`${command} ${sourceId}`:'选择来源后生成命令'}</div>
    <p>将在此 Change 的 Chat 会话中预填命令，由你确认发送。</p>
   </div>
   <footer className="rc-dialog-actions"><p><kbd>Esc</kbd> 关闭</p><div><button className="rc-secondary-action" type="button" onClick={onClose}>取消</button><button className="rc-primary-action" type="button" disabled={!valid} onClick={()=>onContinue(sourceId)}>{label} · 前往 Chat</button></div></footer>
  </section>
 </div>;
}

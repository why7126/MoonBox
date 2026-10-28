import React,{useState,useEffect} from 'react';
import {createRoot} from 'react-dom/client';
import {DirectCompletion} from '../src/components/chat/DirectCompletion';
import {governanceRequest} from '../src/components/workbench/governanceApi';
const params=new URLSearchParams(location.search);
function Probe(){
 const [state,setState]=useState('加载中'),[answer,setAnswer]=useState('');
 useEffect(()=>{void governanceRequest<{items:{text:string}[]}>(`/api/v1/chat/turns/${params.get('turn')}/results?stream_id=final`).then(r=>setAnswer(r.items.map(x=>x.text).join('')));},[]);
 return <main style={{fontFamily:'sans-serif',maxWidth:900,margin:'40px auto'}}><h1>Chat 隔离验收</h1><p>执行终态：completed</p><p data-testid="state">{state}</p><article data-testid="answer">{answer}</article><DirectCompletion turnId={params.get('turn')!} autoFollow expanded onState={setState}/></main>;
}
createRoot(document.getElementById('root')!).render(<Probe/>);

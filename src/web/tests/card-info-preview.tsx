import React from 'react';
import {createRoot} from 'react-dom/client';
import {CardInfoTags, CardInfoFacts} from '../src/pages/catalog/CardInfoTags';
import '../src/styles/globals.css';
import '../src/styles/tokens.generated.css';
const samples: CardInfoFacts[] = [{type:'requirement'}, {type:'requirement',estimate_status:'available',estimated_person_days:.5}, {type:'bug',root_cause_state:'pending'}, {type:'bug',root_cause_state:'confirmed',estimate_status:'available',estimated_person_days:3}];
function Preview(){return <main className="requirement-center" style={{padding:32}}><h1>标签结构验证 · 合成样本</h1><div style={{display:'flex',gap:16,flexWrap:'wrap'}}>{samples.map((facts,i)=><article className={`rc-card ${facts.type}`} key={i} style={{width:320}}><strong>结构样本 {i+1}</strong><h2 className="rc-card-title">根因状态与开发人天</h2><div className="rc-card-meta rc-card-tags"><span className="rc-tag">P2</span><span className="rc-tag rc-owner-tag">产品团队</span><CardInfoTags facts={facts} onRootCause={()=>{}}/></div></article>)}</div></main>}
createRoot(document.getElementById('root')!).render(<Preview/>);

// Isolated read-only preview; never imported by the production entry.
import {createRoot} from 'react-dom/client';
import {RequirementCenterPage} from '../pages/catalog/RequirementCenterPage';
import {deliveryFixture} from './delivery-fixture';
import {saveUiTheme} from '../pages/home/uiPreferences';
import '../styles/globals.css';
import '../styles/tokens.generated.css';
const params=new URLSearchParams(location.search);
saveUiTheme(params.get('theme')==='light'?'light':'dark');
const sources=['updated','created','execution_completed','execution_started','missing'] as const;
const fixture={...deliveryFixture,issues:sources.map((source,index)=>({...deliveryFixture.issues[2],
 id:`time-${source}`,object_id:`time-${source}`,target_change_id:`time-${source}`,title:`可信时间验收 ${source}`,
 stage:index%2===0?'acceptance':'development',card_time:source==='missing'?null:'2026-10-31T04:15:00Z',card_time_source:source,
 source_issues:[],sources:[],checks_deferred:true,acceptance_blocked_reason:'验收待检查',
 action:{label:'完成 / 归档',command:'',disabled_reason:'验收待检查'},
}))};
window.fetch=async (_input,init)=>new Response(JSON.stringify({data:fixture}),{status:init?.method && init.method!=='GET'?403:200,headers:{'Content-Type':'application/json'}});
createRoot(document.getElementById('root')!).render(<RequirementCenterPage/>);

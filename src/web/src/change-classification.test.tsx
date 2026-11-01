import {act,cleanup,render,screen} from '@testing-library/react';
import {afterEach,it,expect,vi,describe} from 'vitest';
import {RequirementCenterPage} from './pages/catalog/RequirementCenterPage';
afterEach(()=>{cleanup();vi.unstubAllGlobals();localStorage.clear()});
describe.each(['ready-dev','development','acceptance','done'])('阶段 %s',stage=>{it.each([
 ['severity','valid','high','严重性 high'],
 ['severity','missing','','严重性待评估'],
 ['severity','invalid','','严重性待核实'],
 ['priority','valid','P1','优先级 P1'],
 ['priority','invalid','','优先级待核实'],
 ['priority','missing','','优先级待评估'],
])('独立卡片只读展示 %s/%s',async(dimension,state,value,label)=>{
 localStorage.setItem('moonbox.session',JSON.stringify({access_token:'test',username:'tester'}));
 const issue={id:'standalone',type:'change',card_kind:'delivery',source_issues:[],title:'只读交付卡',stage,owner:'产品',documents:[],document_entries:[],classification_dimension:dimension,classification_state:state,[dimension]:value,can_edit_priority:true,priority_version:'legacy'};
 const data={current_user:{name:'测试'},workspaces:[],issues:[issue],stats:{total:1,requirements:0,bugs:0,blocked:0,drift:0},projects:[{space_id:'space',repository_id:'repo',status:'connected',readonly:false}]};
 const fetcher=vi.fn(async()=>({ok:true,status:200,json:async()=>({code:0,data})}));vi.stubGlobal('fetch',fetcher);
 await act(async()=>{render(<RequirementCenterPage/>)});
 expect(screen.getByText(label)).toBeTruthy();
 expect(screen.queryByTestId('change-priority-edit')).toBeNull();
 expect(screen.queryByTestId('change-priority-editor')).toBeNull();
 expect(fetcher.mock.calls.every(args=>!JSON.stringify(args).includes('PUT'))).toBe(true);
});});

import { act, cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { RequirementCenterPage } from './pages/catalog/RequirementCenterPage';

const card = {id:'BUG-0099',object_id:'BUG-0099-sample',type:'bug',title:'摘要卡片',stage:'acceptance',
  severity:'high',owner:'产品',updated_at:'now',checks_deferred:true,acceptance_blocked_reason:'验收待检查',
  documents:[],document_entries:[],can_send:false,execution_state:'needs_review',view_turn_id:'stopped',verification_reason:'direct_sync_missing'};
const context = {current_user:{name:'测试账号'},workspaces:[{workspace_id:'space',name:'测试空间'}],
  selected_workspace_id:'space',snapshot_revision:'summary',issues:[card],
  stats:{total:1,requirements:0,bugs:1,blocked:1,drift:0}};
const ok=(data:unknown)=>({ok:true,status:200,json:async()=>({code:0,data})});
beforeEach(()=>{vi.useFakeTimers();localStorage.setItem('moonbox.session',JSON.stringify({access_token:'test',username:'tester'}));});
afterEach(()=>{cleanup();vi.useRealTimers();vi.unstubAllGlobals();localStorage.clear();});

it('验收卡不显示检查行且保留摘要加载和刷新策略',async()=>{
  const fetcher=vi.fn(async(input:RequestInfo|URL)=>String(input).includes('/projects')
    ?ok({...context,projects:[{space_id:'space',repository_id:'repo',status:'connected',readonly:false}]}) :ok(context));
  vi.stubGlobal('fetch',fetcher);
  await act(async()=>{render(<RequirementCenterPage/>);});
  expect(screen.getByText('摘要卡片')).toBeTruthy();
  expect(screen.queryByTestId('acceptance-check')).toBeNull();
  expect(screen.queryByTestId('acceptance-readiness')).toBeNull();
  expect(screen.queryByRole('button',{name:'检查验收条件'})).toBeNull();
  expect(screen.queryByRole('dialog',{name:'归档准备'})).toBeNull();
  await act(async()=>{await vi.advanceTimersByTimeAsync(35000);});
  expect(fetcher.mock.calls.filter(([url])=>String(url).includes('/context'))).toHaveLength(1);
  await act(async()=>{fireEvent.click(screen.getByRole('button',{name:'刷新需求中心'}));});
  expect(fetcher.mock.calls.filter(([url])=>String(url).includes('view=summary'))).toHaveLength(2);
  expect(fetcher.mock.calls.some(([url])=>String(url).includes('object_id='))).toBe(false);
});

it('活动执行仅查询轻量状态',async()=>{
  const fetcher=vi.fn(async(input:RequestInfo|URL)=>{
    const url=String(input);
    if(url.includes('/projects'))return ok({...context,projects:[{space_id:'space',repository_id:'repo',status:'connected',readonly:false}]});
    if(url.includes('/status?'))return ok({items:[{object_id:card.object_id,execution_state:'running',can_send:false}]});
    return ok({...context,issues:[{...card,execution_state:'running'}]});
  });
  vi.stubGlobal('fetch',fetcher);
  await act(async()=>{render(<RequirementCenterPage/>);});
  await act(async()=>{await vi.advanceTimersByTimeAsync(30000);});
  expect(fetcher.mock.calls.filter(([url])=>String(url).includes('/context'))).toHaveLength(1);
  expect(fetcher.mock.calls.filter(([url])=>String(url).includes('/status?')).length).toBeGreaterThan(0);
});

it('既有迭代检查仍可调用，失败后可重试且不新增弹窗',async()=>{
  let checks=0;
  const data={...context,current_iteration_capacity:[{sprint_id:'sprint-018',archive_readiness:{safe_summary:'归档条件待检查'}}]};
  const fetcher=vi.fn(async(input:RequestInfo|URL)=>{
    const url=String(input);
    if(url.includes('/projects'))return ok({...data,projects:[{space_id:'space',repository_id:'repo',status:'connected',readonly:false}]});
    if(url.includes('/context')&&!url.includes('view=summary')){checks++;if(checks===1)throw new Error('network');}
    return ok(data);
  });
  vi.stubGlobal('fetch',fetcher);
  await act(async()=>{render(<RequirementCenterPage/>);});
  await act(async()=>{fireEvent.click(screen.getByRole('button',{name:'检查迭代归档条件'}));});
  await act(async()=>{fireEvent.click(screen.getByRole('button',{name:'检查迭代归档条件'}));});
  expect(checks).toBe(2);
  expect(screen.queryByTestId('acceptance-check')).toBeNull();
});

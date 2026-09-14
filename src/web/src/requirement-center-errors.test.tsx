import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { RequirementCenterPage } from "./pages/catalog/RequirementCenterPage";
import { RequirementCenterErrorDetails, readFailure } from "./pages/catalog/RequirementCenterError";
import { GovernanceError } from "./components/workbench/governanceApi";
const doc="/api/v1/requirement-center/issues/REQ-0099-test/documents/capture.md";
const context={current_user:{name:"测试账号"},workspaces:[{workspace_id:"space",name:"测试空间"}],selected_workspace_id:"space",snapshot_revision:"same",stats:{total:1,requirements:1,bugs:0,blocked:0,drift:0},issues:[{id:"REQ-0099",type:"requirement",title:"保留看板",stage:"capture",priority:"P2",owner:"产品",documents:["capture.md"],document_entries:[{name:"capture.md",type:"markdown",editable:true,url:doc}],updated_at:"now"}]};
const ok=(data:unknown)=>({ok:true,status:200,json:async()=>({code:0,data})});
const failed=(status=503,kind?:string)=>({ok:false,status,headers:new Headers({'X-Request-ID':'test-request'}),json:async()=>({code:2603,message:"private raw text",data:kind?{kind}:null})});
let failContext=false,failDocument=false,denied=false,hidden=false;
function setup(){const fetch=vi.fn(async(input:RequestInfo|URL)=>{
 const url=String(input);
 if(url.includes('/projects'))return ok({...context,projects:[{space_id:'space',repository_id:'repo',status:'connected',readonly:false}]});
 if(url.includes('/context'))return denied?failed(403):failContext?failed():ok({...context,issues:hidden?[]:context.issues});
 return failDocument?failed(503,'source_invalid'):ok({content:'# 当前文档',version:'a'.repeat(64)});
});vi.stubGlobal('fetch',fetch);return fetch;}
beforeEach(()=>{failContext=false;failDocument=false;denied=false;hidden=false;localStorage.setItem('moonbox.session',JSON.stringify({access_token:'test',username:'tester'}));});
afterEach(()=>{cleanup();vi.unstubAllGlobals();vi.restoreAllMocks();localStorage.clear();});
it('首次失败不自动弹窗，旧2603不推断格式问题，重试恢复',async()=>{
 failContext=true;setup();render(<RequirementCenterPage/>);await screen.findByText('需求中心暂时无法加载');expect(screen.queryByRole('dialog')).toBeNull();
 fireEvent.click(screen.getByTestId('rc-error-details-trigger'));expect(screen.getByText('项目数据暂时无法读取。')).toBeTruthy();expect(screen.queryByText('private raw text')).toBeNull();
 fireEvent.keyDown(document,{key:'Escape'});failContext=false;fireEvent.click(screen.getByTestId('rc-error-retry'));await screen.findByText('保留看板');expect(screen.queryByText('需求中心暂时无法加载')).toBeNull();
});
it.each(['denied','hidden'])('刷新失败保留结果，%s时清空对象与文档',async mode=>{
 setup();render(<RequirementCenterPage/>);await screen.findByText('保留看板');fireEvent.click(screen.getByRole('button',{name:/capture.md/}));await screen.findByRole('heading',{name:'当前文档'});
 failContext=true;fireEvent.click(screen.getByRole('button',{name:'刷新需求中心'}));await screen.findByLabelText('更新失败');expect(screen.getAllByText('保留看板').length).toBeGreaterThan(0);
 failContext=false;denied=mode==='denied';hidden=mode==='hidden';fireEvent.click(screen.getByRole('button',{name:'刷新需求中心'}));await waitFor(()=>expect(screen.queryAllByText('保留看板')).toHaveLength(0));expect(screen.queryByTestId('markdown-drawer')).toBeNull();
});
it('文档详情Esc只关最上层并恢复焦点，重试恢复文档',async()=>{
 failDocument=true;setup();render(<RequirementCenterPage/>);await screen.findByText('保留看板');fireEvent.click(screen.getByRole('button',{name:/capture.md/}));await screen.findByText('文档暂时无法加载');
 const trigger=screen.getByTestId('rc-document-error-details-trigger');trigger.focus();fireEvent.click(trigger);expect(screen.getByText('项目数据格式暂不可解析。')).toBeTruthy();
 fireEvent.keyDown(document,{key:'Escape'});expect(screen.queryByTestId('rc-error-details-dialog')).toBeNull();expect(screen.getByTestId('markdown-drawer')).toBeTruthy();expect(document.activeElement).toBe(trigger);
 failDocument=false;fireEvent.click(screen.getByTestId('rc-document-error-retry'));await screen.findByRole('heading',{name:'当前文档'});
});
it('迟到文档响应不重新打开关闭的抽屉',async()=>{
 const original=setup();let resolve!:(value:unknown)=>void;
 vi.stubGlobal('fetch',vi.fn((input:RequestInfo|URL)=>String(input).includes('/documents/')?new Promise(r=>resolve=r):original(input)));
 render(<RequirementCenterPage/>);await screen.findByText('保留看板');fireEvent.click(screen.getByRole('button',{name:/capture.md/}));await waitFor(()=>expect(resolve).toBeTruthy());fireEvent.click(screen.getByRole('button',{name:'关闭右侧抽屉'}));
 resolve(ok({content:'# 迟到文档',version:'b'}));await new Promise(r=>setTimeout(r,0));expect(screen.queryByTestId('markdown-drawer')).toBeNull();
});
it('安全复制、Tab焦点限制和内部点击不关闭',async()=>{
 const writeText=vi.fn().mockResolvedValue(undefined);Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText}});
 const close=vi.fn();render(<RequirementCenterErrorDetails onClose={close} failure={readFailure(new GovernanceError('secret',503,2603,'source_invalid','request-safe'))}/>);
 fireEvent.click(screen.getByText('项目数据格式暂不可解析。'));expect(close).not.toHaveBeenCalled();fireEvent.keyDown(document,{key:'Tab'});expect(document.activeElement).toBe(screen.getByTestId('rc-error-details-close'));fireEvent.keyDown(document,{key:'Tab',shiftKey:true});expect((document.activeElement as HTMLElement).textContent).toBe('关闭');
 fireEvent.click(screen.getByTestId('rc-error-copy'));await screen.findByText('已复制');expect(writeText.mock.calls[0][0]).toContain('request-safe');expect(writeText.mock.calls[0][0]).not.toContain('secret');
});
it('缺失或不可信编号不伪造',()=>{
 expect(readFailure(new GovernanceError('raw',503,2603,'other','/private/path'))).toEqual({status:503,code:2603,kind:undefined,requestId:undefined});render(<RequirementCenterErrorDetails onClose={()=>{}} failure={{}}/>);expect(screen.getByText('本次响应未提供请求编号')).toBeTruthy();
});
it('复制失败给出反馈，点击遮罩关闭且内部点击保持打开',async()=>{
 Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:vi.fn().mockRejectedValue(new Error('denied'))}});
 const close=vi.fn();render(<RequirementCenterErrorDetails onClose={close} failure={{code:2603}}/>);
 fireEvent.click(screen.getByTestId('rc-error-copy'));await screen.findByText('复制失败，请手动选择诊断信息');expect(close).not.toHaveBeenCalled();
 fireEvent.click(screen.getByTestId('rc-error-details-dialog').parentElement!);expect(close).toHaveBeenCalledTimes(1);
});
it('稳定格式错误暂停自动刷新，手动重试仍可恢复',async()=>{
 const original=setup();let repaired=false;
 const fetch=vi.fn((input:RequestInfo|URL)=>String(input).includes('/context')&&!repaired?Promise.resolve(failed(503,'source_invalid')):original(input));vi.stubGlobal('fetch',fetch);
 render(<RequirementCenterPage/>);await screen.findByText('需求中心暂时无法加载');fireEvent(window,new Event('focus'));fireEvent(document,new Event('visibilitychange'));
 expect(fetch.mock.calls.filter(([url])=>String(url).includes('/context'))).toHaveLength(1);
 repaired=true;fireEvent.click(screen.getByTestId('rc-error-retry'));await screen.findByText('保留看板');expect(fetch.mock.calls.filter(([url])=>String(url).includes('/context'))).toHaveLength(2);
});

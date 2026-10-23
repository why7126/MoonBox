import {describe,it,expect,vi,afterEach} from 'vitest';
import {render,screen,fireEvent,cleanup,waitFor} from '@testing-library/react';
import {projectRunStatus} from './components/chat/turnStatus';
import {RecoveryOperationPanel,type RecoveryOperation} from './components/chat/RecoveryOperationPanel';
import {governanceRequest} from './components/workbench/governanceApi';
vi.mock('./components/workbench/governanceApi',()=>({governanceRequest:vi.fn()}));
const op:RecoveryOperation={id:'op',object_id:'REQ-test',action:'req-review',stage:'complete',state:'completed',version:2,execution_terminal:'completed',reason_code:null,auto_retry_count:0,manual_count:0,next_retry_at:null,recovery_expires_at:null,candidate_id:'c',application_id:'a',allowed_actions:['evidence','refresh'],historical_result:'verified',admission_state:'blocked',verification_reason:'dependency_conflict',verification_actions:['verify'],verification_differences:['对象成果：修改 1 项']};
afterEach(()=>{cleanup();vi.resetAllMocks()});
describe('可信轮次投影',()=>{
 it.each([['queued','排队中'],['connecting','准备中'],['running','执行中'],['stopping','停止中'],['failed','执行失败'],['stopped','已停止'],['unknown','结果待确认']])('%s保留执行语义',(status,label)=>expect(projectRunStatus({status}).label).toBe(label));
 it('普通聊天完成不显示业务校验',()=>expect(projectRunStatus({status:'completed',hasBody:true})).toEqual({label:'已完成',detail:'',notes:[]}));
 it('正常流式partial不是截断',()=>expect(projectRunStatus({status:'running',partial:true}).notes).toEqual([]));
 it('业务结果不由模型完成推断',()=>expect(projectRunStatus({status:'completed',business:true}).label).toBe('结果待确认'));
 it('历史完成和当前准入冲突并存',()=>expect(projectRunStatus({status:'completed',operation:op}).detail).toContain('下一步暂不可执行'));
 it('读取失败保留完成，但不得复用权限',()=>expect(projectRunStatus({status:'completed',operation:op,error:true}).notes).toContain('上次确认，更新失败；写操作暂不可用'));
 it('正文缺口与完成独立',()=>expect(projectRunStatus({status:'completed',operation:op,truncated:true}).notes).toEqual(['输出内容不完整']));
 it('无正文失败不虚构保留内容',()=>expect(projectRunStatus({status:'failed'}).notes).toEqual(['未收到可展示的输出']));
 it('完成证明与运行矛盾不放行',()=>expect(projectRunStatus({status:'running',operation:op}).label).toBe('结果待确认'));
});
it('非空草稿取消不覆盖，不发送请求',async()=>{
 vi.mocked(governanceRequest).mockResolvedValue({...op,allowed_actions:['regenerate']});const draft=vi.fn();render(<RecoveryOperationPanel operationId="op" draftText="未完成的草稿" onDraft={draft}/>);
 fireEvent.click(await screen.findByTestId('recovery-regenerate'));fireEvent.click(screen.getByText('取消'));expect(draft).not.toHaveBeenCalled();expect(vi.mocked(governanceRequest).mock.calls.every(([,o])=>!o?.method)).toBe(true);
});
it('核验只调用verifications，不调用恢复或模型',async()=>{
 vi.mocked(governanceRequest).mockResolvedValue(op);render(<RecoveryOperationPanel operationId="op" onDraft={vi.fn()}/>);fireEvent.click(await screen.findByTestId('operation-verify'));
 await waitFor(()=>expect(vi.mocked(governanceRequest).mock.calls.filter(([,o])=>o?.method==='POST')).toHaveLength(1));expect(vi.mocked(governanceRequest).mock.calls.find(([,o])=>o?.method==='POST')![0]).toContain('/verifications');
 fireEvent.click(screen.getByTestId('operation-differences'));expect(screen.getByTestId('operation-differences-dialog').textContent).toContain('对象成果：修改 1 项');fireEvent.keyDown(document,{key:'Escape'});expect(screen.queryByTestId('operation-differences-dialog')).toBeNull();
});
it('核验提交期间重复点击只发一次写入',async()=>{
 let finish!:()=>void;vi.mocked(governanceRequest).mockImplementation(async(_path,options)=>{if(options?.method==='POST')await new Promise<void>(resolve=>{finish=resolve});return op as never;});
 render(<RecoveryOperationPanel operationId="op" onDraft={vi.fn()}/>);const button=await screen.findByTestId('operation-verify');fireEvent.click(button);fireEvent.click(button);
 expect(vi.mocked(governanceRequest).mock.calls.filter(([,o])=>o?.method==='POST')).toHaveLength(1);finish();await waitFor(()=>expect((button as HTMLButtonElement).disabled).toBe(false));
});
it('操作切换后迟到响应不能覆盖新操作',async()=>{
 let old!:(value:unknown)=>void;vi.mocked(governanceRequest).mockImplementation(path=>path.endsWith('/old')?new Promise(resolve=>{old=resolve}):Promise.resolve({...op,id:'new',object_id:'REQ-new'}) as never);
 const view=render(<RecoveryOperationPanel operationId="old" onDraft={vi.fn()}/>);view.rerender(<RecoveryOperationPanel operationId="new" onDraft={vi.fn()}/>);await screen.findByText('REQ-new');old({...op,object_id:'REQ-old'});await waitFor(()=>expect(screen.queryByText('REQ-old')).toBeNull());
});
it('读取权限失效清空敏感详情并关闭写入',async()=>{
 vi.mocked(governanceRequest).mockResolvedValueOnce(op).mockRejectedValue(Object.assign(new Error('当前无权限'),{status:403}));render(<RecoveryOperationPanel operationId="op" onDraft={vi.fn()}/>);
 fireEvent.click(await screen.findByTestId('recovery-refresh'));await screen.findByText('当前无权限');expect(screen.queryByTestId('operation-verify')).toBeNull();expect(screen.queryByTestId('operation-differences')).toBeNull();
});
it.each(['running','completed','failed','stopped'])('%s截断只显示一个缺口',(status)=>{expect(projectRunStatus({status,truncated:true,partial:true,hasBody:true}).notes).toEqual(['输出内容不完整']);});
it('待校验与恢复实际阶段区分',()=>{
 expect(projectRunStatus({status:'completed',business:true}).detail).toBe('结果待校验');
 for(const [stage,label] of [['validation','校验中'],['apply','应用中'],['readback','确认中']]){
 const facts={...op,state:'active',stage,historical_result:'unverified',execution_terminal:'failed'};
 expect(projectRunStatus({status:'failed',operation:facts}).label).toBe(label);
 }
});

it('已完成模型的应用阶段恢复也保留恢复来源',()=>{expect(projectRunStatus({status:'completed',operation:{...op,auto_retry_count:1}}).detail).toContain('经恢复完成');});

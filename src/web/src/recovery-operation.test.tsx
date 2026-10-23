import {render, screen, fireEvent, waitFor, cleanup, act} from '@testing-library/react';
import {afterEach, expect, it, vi} from 'vitest';
import {RecoveryOperationPanel, type RecoveryOperation} from './components/chat/RecoveryOperationPanel';
import {governanceRequest} from './components/workbench/governanceApi';
vi.mock('./components/workbench/governanceApi',()=>({governanceRequest:vi.fn()}));
const original: RecoveryOperation={id:'op',object_id:'REQ-9000-isolated',action:'req-review',stage:'validation',state:'waiting',version:4,execution_terminal:'stopped',reason_code:null,allowed_actions:['refresh','evidence','resume'],auto_retry_count:3,manual_count:0,next_retry_at:null,recovery_expires_at:'2026-10-26T00:00:00Z',candidate_id:'candidate',application_id:null};
afterEach(()=>{cleanup();vi.useRealTimers();vi.clearAllMocks()});
it('rechecks after a long generation exhausts polling when the turn reaches terminal state',async()=>{
 vi.useFakeTimers();
 const request=vi.mocked(governanceRequest);
 request.mockResolvedValue({...original,stage:'generation',state:'active',execution_terminal:null});
 const props={operationId:'op',onDraft:vi.fn()};
 const view=render(<RecoveryOperationPanel {...props} refreshKey="running:running"/>);
 await act(async()=>{await vi.advanceTimersByTimeAsync(63000)});
 const count=request.mock.calls.length;
 await act(async()=>{await vi.advanceTimersByTimeAsync(30000)});
 expect(request.mock.calls.length).toBe(count);
 request.mockResolvedValue({...original,state:'completed',stage:'complete',version:5,execution_terminal:'completed'});
 await act(async()=>{view.rerender(<RecoveryOperationPanel {...props} refreshKey="completed:applied"/>);});
 expect(screen.getByText('业务已完成')).toBeTruthy();
 expect(request.mock.calls.length).toBe(count+1);
 expect(request.mock.calls.every(([,o])=>!o?.method)).toBe(true);
});
it('reads without writing and resumes only after explicit confirmation',async()=>{
 const request=vi.mocked(governanceRequest); request.mockResolvedValue(original);
 render(<RecoveryOperationPanel operationId="op" onDraft={vi.fn()}/>);
 await screen.findByTestId('recovery-resume');
 expect(request.mock.calls.every(([,o])=>!o?.method)).toBe(true);
 fireEvent.click(screen.getByTestId('recovery-resume'));
 expect(screen.getByTestId('recovery-resume-dialog')).toBeTruthy();
 expect(request.mock.calls.every(([,o])=>!o?.method)).toBe(true);
 fireEvent.click(screen.getByTestId('recovery-confirm'));
 await waitFor(()=>expect(request.mock.calls.some(([,o])=>o?.method==='POST')).toBe(true));
 const post=request.mock.calls.find(([,o])=>o?.method==='POST')!;
 expect(JSON.parse(post[1]!.body as string)).toMatchObject({expected_version:4,confirmed:true});
 expect(screen.queryByText('业务已完成')).toBeNull();
 expect(screen.getByText('原执行：已停止')).toBeTruthy();
});
it('expired regeneration only fills a draft',async()=>{
 vi.mocked(governanceRequest).mockResolvedValue({...original,reason_code:'recovery_expired',allowed_actions:['refresh','regenerate']});
 const draft=vi.fn();render(<RecoveryOperationPanel operationId="op" onDraft={draft}/>);
 fireEvent.click(await screen.findByTestId('recovery-regenerate'));
 expect(draft).toHaveBeenCalledWith('/req-review REQ-9000-isolated');
 expect(screen.queryByTestId('recovery-resume')).toBeNull();
 expect(vi.mocked(governanceRequest).mock.calls.every(([,o])=>!o?.method)).toBe(true);
});
it('permission read failures remove stale actions and evidence',async()=>{
 vi.mocked(governanceRequest).mockRejectedValue(new Error('无权访问'));
 render(<RecoveryOperationPanel operationId="op" onDraft={vi.fn()}/>);
 await screen.findByText('无权访问');
 expect(screen.queryByTestId('recovery-evidence')).toBeNull();
 expect(screen.queryByTestId('recovery-resume')).toBeNull();
});
it('ignores a late read response after a newer completed read',async()=>{
 vi.useFakeTimers();
 try {
  let first!: (value: RecoveryOperation)=>void;
  let second!: (value: RecoveryOperation)=>void;
  const request=vi.mocked(governanceRequest);
  request.mockImplementationOnce(()=>new Promise(resolve=>{first=resolve}));
  request.mockImplementationOnce(()=>new Promise(resolve=>{second=resolve}));
  const {act}=await import('@testing-library/react');
  render(<RecoveryOperationPanel operationId="op" onDraft={vi.fn()}/>);
  await act(async()=>{vi.advanceTimersByTime(3000)});
  await act(async()=>{second({...original,version:5,state:'completed',stage:'complete',allowed_actions:['refresh','evidence']})});
  await act(async()=>{first(original)});
  expect(screen.getByText('业务已完成')).toBeTruthy();
  expect(screen.queryByTestId('recovery-resume')).toBeNull();
 } finally {vi.useRealTimers()}
});
it('does not silently confirm a different version after polling updates',async()=>{
 vi.useFakeTimers();
 try {
  const request=vi.mocked(governanceRequest);request.mockResolvedValue(original);
  const {act}=await import('@testing-library/react');
  render(<RecoveryOperationPanel operationId="op" onDraft={vi.fn()}/>);
  await act(async()=>{});
  fireEvent.click(screen.getByTestId('recovery-resume'));
  request.mockResolvedValue({...original,version:5});
  await act(async()=>{vi.advanceTimersByTime(3000)});
  expect((screen.getByTestId('recovery-confirm') as HTMLButtonElement).disabled).toBe(true);
  expect(screen.getByText('状态已变化，请关闭后重新确认。')).toBeTruthy();
  expect(request.mock.calls.every(([,o])=>!o?.method)).toBe(true);
 } finally {vi.useRealTimers()}
});

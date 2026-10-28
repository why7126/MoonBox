import {render,screen,act,cleanup} from '@testing-library/react';
import {afterEach,expect,it,vi} from 'vitest';
import {DirectCompletion} from './components/chat/DirectCompletion';
vi.mock('./components/workbench/governanceApi',async(importOriginal)=>({...await importOriginal<typeof import('./components/workbench/governanceApi')>(),governanceRequest:vi.fn()}));
import {governanceRequest,GovernanceError} from './components/workbench/governanceApi';
const pending={available:true,state:'needs_review',version:1,can_verify:true,auto_verification:{state:'pending'}};
const request=vi.mocked(governanceRequest);
afterEach(()=>{cleanup();vi.useRealTimers();vi.resetAllMocks();});
async function mount(autoFollow=true){
 vi.useFakeTimers();const state=vi.fn();
 const view=render(<DirectCompletion turnId="one" expanded autoFollow={autoFollow} onState={state}/>);
 await act(async()=>{});
 return {state,...view};
}
it('follows automatic confirmation without clicks and stops',async()=>{
 request.mockResolvedValueOnce(pending).mockResolvedValue({state:'validated',version:1,can_verify:false});
 const {state}=await mount();
 expect(screen.getByText('正在自动核验，无需重复操作。')).toBeTruthy();
 await act(async()=>{await vi.advanceTimersByTimeAsync(2000);});
 expect(state).toHaveBeenLastCalledWith('validated');
 await act(async()=>{await vi.advanceTimersByTimeAsync(200000);});
 expect(request).toHaveBeenCalledTimes(2);
 expect(request.mock.calls.every(x=>!x[1]?.method)).toBe(true);
});
it('caps reads and leaves safe refresh rather than business failure',async()=>{
 request.mockResolvedValue(pending);await mount();
 await act(async()=>{await vi.advanceTimersByTimeAsync(200000);});
 expect(request).toHaveBeenCalledTimes(18);
 expect(screen.getByText('自动跟进已暂停，可刷新状态。')).toBeTruthy();
});
it('does not poll historical turns',async()=>{
 request.mockResolvedValue(pending);await mount(false);
 await act(async()=>{await vi.advanceTimersByTimeAsync(200000);});
 expect(request).toHaveBeenCalledTimes(1);
});
it.each([401,403,404])('stops on authorization or missing status %s',async(status)=>{
 request.mockRejectedValue(new GovernanceError('denied',status));await mount();
 await act(async()=>{await vi.advanceTimersByTimeAsync(200000);});
 expect(request).toHaveBeenCalledTimes(1);
});
it('drops responses after switching turns even if transport ignores abort',async()=>{
 let resolve!:(v:unknown)=>void;
 request.mockImplementationOnce(()=>new Promise(r=>{resolve=r;})).mockResolvedValue({state:'validated',version:2,can_verify:false});
 const {state,rerender}=await mount();
 rerender(<DirectCompletion turnId="two" expanded autoFollow onState={state}/>);
 await act(async()=>{});
 await act(async()=>{resolve(pending);});
 expect(state).toHaveBeenLastCalledWith('validated');
 expect(screen.queryByText('正在自动核验，无需重复操作。')).toBeNull();
 expect((request.mock.calls[0][1]?.signal as AbortSignal).aborted).toBe(true);
});
it('stops blocked queue and does not overlap slow reads',async()=>{
 let resolve!:(v:unknown)=>void;
 request.mockImplementationOnce(()=>new Promise(r=>{resolve=r;}));
 await mount();
 await act(async()=>{await vi.advanceTimersByTimeAsync(15000);});
 expect(request).toHaveBeenCalledTimes(1);
 await act(async()=>resolve({...pending,auto_verification:{state:'blocked',reason_code:'retry_exhausted'}}));
 await act(async()=>{await vi.advanceTimersByTimeAsync(200000);});
 expect(request).toHaveBeenCalledTimes(1);
});
it('pauses hidden tabs without resetting the deadline and aborts hung requests',async()=>{
 request.mockResolvedValue(pending);await mount();
 vi.spyOn(document,'hidden','get').mockReturnValue(true);
 document.dispatchEvent(new Event('visibilitychange'));
 await act(async()=>{await vi.advanceTimersByTimeAsync(180000);});
 expect(request).toHaveBeenCalledTimes(1);
 expect(screen.getByText('自动跟进已暂停，可刷新状态。')).toBeTruthy();
 vi.restoreAllMocks();
});
it('aborts on unmount and ignores a late verification response',async()=>{
 const {fireEvent}=await import('@testing-library/react');
 let resolve!:(v:unknown)=>void;
 request.mockResolvedValueOnce(pending).mockImplementationOnce(()=>new Promise(r=>{resolve=r;}));
 const {state,unmount}=await mount(false);
 fireEvent.click(screen.getByTestId('direct-completion-verify'));
 const count=state.mock.calls.length;
 unmount();
 await act(async()=>resolve({state:'validated',version:1,can_verify:false}));
 expect(state.mock.calls.length).toBe(count);
 expect((request.mock.calls[1][1]?.signal as AbortSignal).aborted).toBe(true);
});

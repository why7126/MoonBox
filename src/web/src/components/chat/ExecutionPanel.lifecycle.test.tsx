import { act, cleanup, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { ExecutionPanel } from './ExecutionPanel';
import { chatRequest } from './chatApi';
import { readChatEvents } from './chatEvents';
import { readTurnSummary } from './sharedChatRead';
vi.mock('./chatApi', async importOriginal => ({...await importOriginal<object>(), chatRequest:vi.fn()}));
vi.mock('./chatEvents', () => ({readChatEvents:vi.fn()}));
vi.mock('./sharedChatRead', () => ({readTurnSummary:vi.fn()}));
vi.mock('../../pages/home/frontendSession', () => ({readValidFrontendSession:()=>({access_token:'test'})}));
vi.mock('./ObjectArchivePanel', () => ({ObjectArchivePanel:()=>null}));
vi.mock('./SavedResults', () => ({SavedResults:()=>null}));
vi.mock('./DiffView', () => ({DiffView:()=>null}));
vi.mock('./TrajectoryView', () => ({TrajectoryView:({events}:any)=><output data-testid="sequences">{events.map((e:any)=>e.sequence).join(',')}</output>}));
const conversation = {id:'c'} as any;
const turn = {id:'t',status:'completed',created_at:'2026-10-01',updated_at:'2026-10-01'};
beforeEach(()=>{vi.clearAllMocks();vi.mocked(chatRequest).mockImplementation(async path => path.includes('/conversations/') ? {items:[turn]} : path.endsWith('/context') ? [] : {} as any);});
afterEach(()=>{cleanup();vi.useRealTimers();});
it('does not read hidden details for 15 seconds', async()=>{
 vi.useFakeTimers();render(<ExecutionPanel conversation={conversation} visible={false}/>);
 await act(async()=>vi.advanceTimersByTimeAsync(15000));
 expect(chatRequest).not.toHaveBeenCalled();expect(readChatEvents).not.toHaveBeenCalled();
});
it.each([199,200,401,1000,1001])('reads %i events in ordered bounded windows and reuses after authorization',async count=>{
 vi.mocked(readTurnSummary).mockResolvedValue({...turn,event_sequence:count} as any);
 vi.mocked(readChatEvents).mockImplementation(async (_id,after)=>Array.from({length:Math.min(200,count-after)},(_,i)=>({sequence:after+i+1,type:'execution.tool',payload:{}})));
 const {rerender}=render(<ExecutionPanel conversation={conversation}/>);
 await waitFor(()=>expect(screen.getByTestId('sequences').textContent?.split(',')).toHaveLength(Math.min(count,1000)));
 await waitFor(()=>expect(chatRequest).toHaveBeenCalledWith('/turns/t/context',expect.anything()));
 expect(screen.getByTestId('sequences').textContent).toBe(Array.from({length:Math.min(count,1000)},(_,i)=>i+1).join(','));
 const reads=vi.mocked(readChatEvents).mock.calls.length;
 rerender(<ExecutionPanel conversation={conversation} visible={false}/>);
 rerender(<ExecutionPanel conversation={conversation}/>);
 await waitFor(()=>expect(screen.getByTestId('sequences').textContent?.split(',')).toHaveLength(Math.min(count,1000)));
 expect(readChatEvents).toHaveBeenCalledTimes(reads);
 expect(readTurnSummary).toHaveBeenCalledTimes(reads+1);
 expect(screen.queryByText('读取后续事件')!==null).toBe(count>1000);
});
it('clears cached detail when authorization is revoked',async()=>{
 vi.mocked(readTurnSummary).mockResolvedValue({...turn,event_sequence:1} as any);
 vi.mocked(readChatEvents).mockResolvedValue([{sequence:1,type:'execution.tool',payload:{}}]);
 const {rerender}=render(<ExecutionPanel conversation={conversation}/>);
 await screen.findByTestId('sequences');
 await waitFor(()=>expect(chatRequest).toHaveBeenCalledWith('/turns/t/context',expect.anything()));
 rerender(<ExecutionPanel conversation={conversation} visible={false}/>);
 vi.mocked(readTurnSummary).mockRejectedValue(new Error('无权读取'));
 rerender(<ExecutionPanel conversation={conversation}/>);
 await screen.findByText('无权读取');expect(screen.queryByTestId('sequences')).toBeNull();
});
it('continues after the 1000-event window without duplicating earlier events',async()=>{
 vi.mocked(readTurnSummary).mockResolvedValue({...turn,event_sequence:1001} as any);
 vi.mocked(readChatEvents).mockImplementation(async (_id,after)=>Array.from({length:Math.min(200,1001-after)},(_,i)=>({sequence:after+i+1,type:'execution.tool',payload:{}})));
 render(<ExecutionPanel conversation={conversation}/>);
 const next=await screen.findByText('读取后续事件');
 await act(async()=>{next.click();});
 await waitFor(()=>expect(screen.getByTestId('sequences').textContent).toBe('1001'));
 expect(readChatEvents).toHaveBeenLastCalledWith('t',1000,expect.any(AbortSignal));
});
it('cancels a detail request when the panel closes',async()=>{
 vi.mocked(readTurnSummary).mockResolvedValue({...turn,event_sequence:200} as any);
 let signal:AbortSignal|undefined;
 vi.mocked(readChatEvents).mockImplementation((_id,_after,current)=>{signal=current;return new Promise(()=>{});});
 const {rerender}=render(<ExecutionPanel conversation={conversation}/>);
 await waitFor(()=>expect(signal).toBeDefined());
 rerender(<ExecutionPanel conversation={conversation} visible={false}/>);
 expect(signal?.aborted).toBe(true);
 expect(chatRequest).not.toHaveBeenCalledWith('/turns/t/diff',expect.anything());
});

it('preserves the requested historical turn when opening the panel',async()=>{
 vi.mocked(chatRequest).mockImplementation(async path=>path.includes('/conversations/')?{items:[{...turn,id:'latest'},turn]}:path.endsWith('/context')?[]:{} as any);
 vi.mocked(readTurnSummary).mockResolvedValue({...turn,event_sequence:0} as any);
 const {rerender}=render(<ExecutionPanel conversation={conversation} visible={false}/>);
 rerender(<ExecutionPanel conversation={conversation} visible focusTurn="t" focusVersion={1}/>);
 await waitFor(()=>expect((screen.getByTestId('chat-turn-select') as HTMLSelectElement).value).toBe('t'));
 expect(readTurnSummary).toHaveBeenCalledWith('t',expect.any(AbortSignal));
});

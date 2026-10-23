import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {afterEach,expect,it,vi} from 'vitest';
import {cleanup} from '@testing-library/react';
import {DirectCompletion} from './components/chat/DirectCompletion';
vi.mock('./components/workbench/governanceApi',()=>({governanceRequest:vi.fn()}));
import {governanceRequest} from './components/workbench/governanceApi';
afterEach(()=>{cleanup();vi.resetAllMocks();});
it('revalidates original turn at the server version without replaying its command',async()=>{
 const request=vi.mocked(governanceRequest);
 request.mockResolvedValueOnce({state:'needs_review',version:3,can_verify:true,historical_evidence_missing:true}).mockResolvedValueOnce({state:'recovered_valid',version:3,can_verify:false});
 const state=vi.fn();render(<DirectCompletion turnId="original" expanded onState={state}/>);
 const button=await screen.findByTestId('direct-completion-verify');fireEvent.click(button);fireEvent.click(button);
 await waitFor(()=>expect(state).toHaveBeenLastCalledWith('recovered_valid'));
 expect(request).toHaveBeenCalledTimes(2);
 expect(request.mock.calls[1][1]).toEqual({method:'POST',body:JSON.stringify({expected_version:3})});
 expect(screen.queryByTestId('direct-completion-verify')).toBeNull();
});
it('retains failed proof and offers a read retry',async()=>{
 vi.mocked(governanceRequest).mockRejectedValueOnce(new Error('offline'));
 render(<DirectCompletion turnId="original" expanded onState={()=>{}}/>);
 expect(await screen.findByText('核验状态暂不可读，请稍后重试。')).toBeTruthy();
 expect(screen.queryByTestId('direct-completion-verify')).toBeNull();
});
it('historical verification never offers recovery of the current operation',async()=>{
 vi.mocked(governanceRequest).mockResolvedValueOnce({state:'validated',reason_code:'direct_historical_verified',version:null,can_verify:false});
 render(<DirectCompletion turnId="original" expanded onState={()=>{}}/>);
 expect(await screen.findByText('历史成果已核验；当前动作以最新准入核验为准。')).toBeTruthy();
 expect(screen.queryByTestId('direct-completion-verify')).toBeNull();
 expect(governanceRequest).toHaveBeenCalledTimes(1);
});
it('explains uncovered successor inputs without suggesting replay',async()=>{
 vi.mocked(governanceRequest).mockResolvedValueOnce({state:'needs_review',reason_code:'direct_successor_input_uncovered',version:4,can_verify:true,differences:[{path:'openspec/changes/sample/design.md',kind:'modified'}]});
 render(<DirectCompletion turnId="original" expanded onState={()=>{}}/>);
 expect(await screen.findByText('变化文件未被当前有效验收覆盖，保护已保留。')).toBeTruthy();
 expect(screen.getByText('修改：openspec/changes/sample/design.md')).toBeTruthy();
 expect(screen.getByTestId('direct-completion-verify')).toBeTruthy();
});

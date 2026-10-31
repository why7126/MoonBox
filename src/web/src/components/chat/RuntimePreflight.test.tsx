import {render,screen,fireEvent,cleanup,waitFor} from '@testing-library/react';
import {it,expect,vi,afterEach} from 'vitest';
import {RuntimePreflight} from './RuntimePreflight';
import {governanceRequest} from '../workbench/governanceApi';
vi.mock('../workbench/governanceApi',()=>({governanceRequest:vi.fn()}));
afterEach(()=>{cleanup();vi.resetAllMocks();});
it('配置不会显示验收通过，手动重试失败保持未知',async()=>{
 vi.mocked(governanceRequest).mockResolvedValueOnce({checks:[{name:'python',status:'configured',reason_code:'runtime_probe_required'}]}).mockRejectedValueOnce(new Error('private'));
 render(<RuntimePreflight conversationId="chat"/>);
 await screen.findByText(/已配置，待实际运行验证/);
 fireEvent.click(screen.getByTestId('runtime-preflight-refresh'));
 await screen.findByRole('alert');
 expect(screen.queryByText(/已配置，待实际运行验证/)).toBeNull();
 expect(screen.queryByText('private')).toBeNull();
 expect(governanceRequest).toHaveBeenCalledTimes(2);
});
it('切换会话后拒绝旧响应，不轮询',async()=>{
 let finish:(value:unknown)=>void=()=>{};
 vi.mocked(governanceRequest).mockImplementationOnce(()=>new Promise(resolve=>{finish=resolve;})).mockResolvedValueOnce({checks:[{name:'worker',status:'unavailable',reason_code:'verification_worker_unavailable'}]});
 const view=render(<RuntimePreflight conversationId="old"/>);view.rerender(<RuntimePreflight conversationId="new"/>);
 await screen.findByText(/未检测到在线验证服务/);finish({checks:[{name:'python',status:'ready'}]});
 await waitFor(()=>expect(screen.queryByText(/Python 测试/)).toBeNull());
 expect(governanceRequest).toHaveBeenCalledTimes(2);
});

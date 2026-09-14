import { cleanup, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { TurnActivity } from './components/chat/TurnActivity';
afterEach(()=>{cleanup();vi.unstubAllGlobals();localStorage.clear();});
it('shows a failed turn beside its partial history, without inventing success',async()=>{
 localStorage.setItem('moonbox.session',JSON.stringify({access_token:'synthetic'}));
 vi.stubGlobal('fetch',vi.fn(async(url:string)=>url.includes('/events')?new Response('id: 1\nevent: execution.tool\ndata: {"item_id":"x","phase":"completed"}\n\n',{headers:{'Content-Type':'text/event-stream'}}):new Response(JSON.stringify({code:0,data:{id:'t',status:'failed'}}))));
 render(<TurnActivity turnId="t" onTrace={()=>{}}/>);await screen.findByRole('alert');expect(screen.getByRole('button').textContent).toContain('本轮运行失败');expect(screen.queryByText('已完成')).toBeNull();
});
it('clears details when authorization fails',async()=>{
 localStorage.setItem('moonbox.session',JSON.stringify({access_token:'synthetic'}));vi.stubGlobal('fetch',vi.fn(async()=>new Response('',{status:403})));
 render(<TurnActivity turnId="t" onTrace={()=>{}}/>);await waitFor(()=>expect(screen.getByRole('alert').textContent).toContain('不可访问'));expect(screen.queryByText(/次工具调用/)).toBeNull();
});

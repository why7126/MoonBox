import { afterEach, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { FullOutput } from './components/chat/FullOutput';
import { projectRunStatus } from './components/chat/turnStatus';
import { chatRequest, ChatApiError } from './components/chat/chatApi';
vi.mock('./components/chat/chatApi',()=>({chatRequest:vi.fn(),normalizeChatError:(e:unknown)=>e,ChatApiError:class extends Error {constructor(public status:number,message:string){super(message);}}}));
afterEach(()=>{cleanup();vi.clearAllMocks();});
const page=(text:string,next:string|null=null,final=false)=>({items:[{sequence:1,text}],next_cursor:next,resume_cursor:'resume',has_final:final,completeness:'unknown_tail'});
it('distinguishes display bounds, real gaps and normal streaming',()=>{
 expect(projectRunStatus({status:'running',partial:true}).notes).toEqual([]);
 expect(projectRunStatus({status:'running',truncated:true,truncationReason:'preview_limit'}).notes).toEqual(['仅展示部分输出']);
 expect(projectRunStatus({status:'completed',truncated:true,truncationReason:'history_gap'}).notes).toEqual(['部分历史输出不可用']);
 expect(projectRunStatus({truncated:true}).notes).toEqual(['输出内容不完整']);
});
it('loads a single page, navigates backwards, and keeps content on retryable failure',async()=>{
 vi.mocked(chatRequest).mockResolvedValueOnce(page('第一段','next')).mockRejectedValueOnce(new Error('读取失败')).mockResolvedValueOnce(page('第二段')).mockResolvedValueOnce(page('第一段','next'));
 render(<FullOutput turnId="one" preferFinal={false} onClose={()=>{}}/>);
 await screen.findByText('第一段');fireEvent.click(screen.getByTestId('output-next-page'));
 await screen.findByText('读取失败');expect(screen.getByText('第一段')).toBeTruthy();
 fireEvent.click(screen.getByText('重试'));await screen.findByText('第二段');expect(screen.queryByText('第一段')).toBeNull();
 fireEvent.click(screen.getByTestId('output-prev-page'));await screen.findByText('第一段');
 expect(chatRequest).toHaveBeenCalledTimes(4);
});
it('ignores a late response after turn changes',async()=>{
 let resolve!:(v:unknown)=>void;
 vi.mocked(chatRequest).mockImplementationOnce(()=>new Promise(r=>resolve=r)).mockResolvedValueOnce(page('新轮次'));
 const {rerender}=render(<FullOutput turnId="old" preferFinal={false} onClose={()=>{}}/>);
 rerender(<FullOutput turnId="new" preferFinal={false} onClose={()=>{}}/>);
 await screen.findByText('新轮次');resolve(page('过期内容'));
 await waitFor(()=>expect(screen.queryByText('过期内容')).toBeNull());
});
it('switches to final without concatenating output and resets expired cursors',async()=>{
 vi.mocked(chatRequest).mockResolvedValueOnce(page('过程',null,true)).mockResolvedValueOnce(page('最终','next',true)).mockRejectedValueOnce(new ChatApiError(422,'游标失效')).mockResolvedValueOnce(page('新版本',null,true));
 render(<FullOutput turnId="one" preferFinal={false} onClose={()=>{}}/>);
 await screen.findByText('最终');expect(screen.queryByText('过程')).toBeNull();
 fireEvent.click(screen.getByTestId('output-next-page'));await screen.findByText('返回首页读取最新输出');
 fireEvent.click(screen.getByText('返回首页读取最新输出'));await screen.findByText('新版本');
});

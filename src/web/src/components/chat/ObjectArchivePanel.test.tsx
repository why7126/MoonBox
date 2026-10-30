import { act, fireEvent, render, screen, waitFor, cleanup } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ObjectArchivePanel } from './ObjectArchivePanel';
import { governanceRequest } from '../workbench/governanceApi';
import { chatRequest } from './chatApi';
vi.mock('../workbench/governanceApi', () => ({governanceRequest:vi.fn()}));
vi.mock('./chatApi', () => ({chatRequest:vi.fn()}));
const conversation = {id:'conversation',space_id:'space',repository_id:'repo'} as any;
const op = {operation_id:'original',operation_kind:'ordinary',target_id:'fix-sample',stage:'synced',revision:2,verification:{status:'blocked',checked_at:'now',input_fingerprint:'hash',findings:[{relative_path:'issues/test.md',line:2,message:'核对当前状态',requires_review:false}]},allowed_actions:['refresh','resume']};
const view = {object_id:'fix-sample',operations:[op],summary:'needs_attention',not_started_targets:[]};
beforeEach(() => {vi.clearAllMocks();vi.mocked(chatRequest).mockResolvedValue({primary:{id:'fix-sample'}});vi.mocked(governanceRequest).mockResolvedValue(view);});
afterEach(cleanup);
describe('对象归档状态', () => {
  it('查询只读，明确确认后沿用原操作，重复点击不重复提交', async () => {
    render(<ObjectArchivePanel conversation={conversation}/>);
    fireEvent.click(await screen.findByTestId('object-archive-resume'));
    expect(vi.mocked(governanceRequest).mock.calls.every(([, options]) => !options?.method)).toBe(true);
    let resolve!: (v:unknown) => void;
    vi.mocked(governanceRequest).mockImplementation((_url, options) => options?.method === 'POST' ? new Promise(r => {resolve=r;}) : Promise.resolve(view));
    const button = screen.getByTestId('object-archive-confirm-submit');fireEvent.click(button);fireEvent.click(button);
    const writes=vi.mocked(governanceRequest).mock.calls.filter(([,o])=>o?.method==='POST');
    expect(writes).toHaveLength(1);
    expect(JSON.parse(String(writes[0][1]?.body))).toMatchObject({operation_id:'original',object_id:'fix-sample',confirmed:true});
    await act(async()=>resolve({stage:'completed'}));
  });
  it('已完成但当前失败仍显示，不能续接', async () => {
    vi.mocked(governanceRequest).mockResolvedValue({...view,operations:[{...op,stage:'completed',allowed_actions:['refresh']}]});
    render(<ObjectArchivePanel conversation={conversation}/>);
    expect(await screen.findByText('原操作已完成 · 当前文档需要处理')).toBeTruthy();
    expect(screen.queryByTestId('object-archive-resume')).toBeNull();
  });
  it('旧会话迟到响应不覆盖新对象', async () => {
    let resolve!: (v:unknown) => void;
    vi.mocked(governanceRequest).mockImplementationOnce(()=>new Promise(r=>{resolve=r;}));
    const {rerender}=render(<ObjectArchivePanel conversation={conversation}/>);
    await waitFor(()=>expect(governanceRequest).toHaveBeenCalled());
    vi.mocked(governanceRequest).mockResolvedValue({...view,object_id:'new-object',operations:[]});
    rerender(<ObjectArchivePanel conversation={{...conversation,id:'new'}}/>);
    await screen.findByText('new-object');
    await act(async()=>resolve(view));
    expect(screen.queryByText('fix-sample')).toBeNull();
  });
  it('事件只触发查询，读失败清除续接资格，重连可恢复', async () => {
    const {rerender}=render(<ObjectArchivePanel conversation={conversation}/>);
    await screen.findByTestId('object-archive-resume');
    vi.mocked(governanceRequest).mockRejectedValue(new Error('无权访问'));
    rerender(<ObjectArchivePanel conversation={conversation} refreshKey="tool-result-changed"/>);
    await screen.findByText('无权访问');expect(screen.queryByTestId('object-archive-resume')).toBeNull();
    vi.mocked(governanceRequest).mockResolvedValue(view);
    fireEvent(window,new Event('online'));await screen.findByTestId('object-archive-resume');
  });
});

import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import { QuestionCard } from './QuestionPanel';
import type { QuestionRead } from '../../api/generated/chat';
const question: QuestionRead = { id:'q', turn_id:'t', status:'pending', version:1, expires_at:'2099-01-01', created_at:'2026-10-31', questions:[{id:'choice',header:'方式',question:'选择方式',options:[{id:'0',label:'测试（推荐）',description:'合成数据'}],allow_text:true}] };
afterEach(cleanup);
describe('原轮次回答卡片', () => {
 it('保留失败答案及重试幂等键，选择或补充后可提交', async () => {
  const submit=vi.fn().mockRejectedValueOnce(new Error('网络失败')).mockResolvedValueOnce(undefined);
  render(<QuestionCard question={question} onSubmit={submit}/>);
  expect((screen.getByText('提交回答') as HTMLButtonElement).disabled).toBe(true);
  fireEvent.click(screen.getByRole('radio'));
  fireEvent.change(screen.getByRole('textbox'),{target:{value:'补充'}});
  fireEvent.click(screen.getByText('提交回答'));
  await screen.findByRole('alert');
  expect((screen.getByRole('textbox') as HTMLTextAreaElement).value).toBe('补充');
  fireEvent.click(screen.getByText('提交回答'));
  await waitFor(()=>expect(submit).toHaveBeenCalledTimes(2));
  expect(submit.mock.calls[0][1]).toBe(submit.mock.calls[1][1]);
 });
 it('终止后不再显示提交动作', () => {
  const view=render(<QuestionCard question={question} onSubmit={vi.fn()}/>);
  view.rerender(<QuestionCard question={{...question,status:'expired'}} onSubmit={vi.fn()}/>);
  expect(screen.queryByText('提交回答')).toBeNull();
  expect((screen.getByRole('textbox') as HTMLTextAreaElement).closest('fieldset')?.disabled).toBe(true);
 });
});

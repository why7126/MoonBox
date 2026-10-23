import { fireEvent, render, screen, waitFor, cleanup } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ReplacementReview } from './ReplacementReview';
const request = vi.hoisted(() => vi.fn());
vi.mock('./chatApi', () => ({ chatRequest: request }));
afterEach(cleanup);
const sample = { change_id: 'fix-sample', capability: 'archive', requirement: '归档保护',
  before: '原规则', after: '增加明确允许条件', protected_changes: ['old-change'],
  affected_requirements: ['归档保护'], review_reason: null, state: 'blocked',
  acceptance_ready: false, acceptance_blockers: ['验收尚未签署'],
  archive_ready: false, archive_reason: '规则内容已修改，需检查后继续' };
beforeEach(() => { request.mockReset(); request.mockResolvedValue(sample); });
function open() {
  const view = render(<ReplacementReview spaceId="space" repositoryId="repo" changeId="fix-sample" openRequest={0} />);
  view.rerender(<ReplacementReview spaceId="space" repositoryId="repo" changeId="fix-sample" openRequest={1} />);
  return view;
}
describe('规则修改只读检查', () => {
  it('从阻断项打开，显示完整差异与独立验收缺口', async () => {
    const view = render(<ReplacementReview spaceId="space" repositoryId="repo" changeId="fix-sample" openRequest={0} />);
    expect(screen.queryByTestId('rule-change-drawer')).toBeNull();
    view.rerender(<ReplacementReview spaceId="space" repositoryId="repo" changeId="fix-sample" openRequest={1} />);
    expect(await screen.findByText('归档保护')).toBeTruthy();
    fireEvent.click(screen.getByText('查看原规则与修改后全文'));
    expect(screen.getAllByText('原规则')).toHaveLength(2);
    expect(screen.getByText('验收尚未签署')).toBeTruthy();
    expect(screen.queryByText(/兼容追加证明/)).toBeNull();
    expect(request.mock.calls[0][0]).toContain('change_id=fix-sample');
    expect(screen.queryByTestId('rule-change-confirm')).toBeNull();
    expect(screen.queryByTestId('rule-change-reject')).toBeNull();
    expect(screen.queryByTestId('rule-change-revoke')).toBeNull();
  });
  it('重新检查仅重新读取，不发送确认、聊天或归档请求', async () => {
    open(); await screen.findByText('归档保护');
    fireEvent.click(screen.getByTestId('rule-change-recheck'));
    await waitFor(() => expect(request).toHaveBeenCalledTimes(2));
    expect(screen.getByText('已重新读取当前规则与验收状态；归档仍须单独执行。')).toBeTruthy();
    expect(request.mock.calls.every(call => String(call[0]).startsWith('/rule-changes?') && !call[1]?.method)).toBe(true);
  });
  it('读取失败只显示错误，不显示可写动作', async () => {
    request.mockRejectedValueOnce(new Error('读取失败'));
    open();
    expect(await screen.findByText('读取失败')).toBeTruthy();
    expect(screen.queryByTestId('rule-change-recheck')).toBeNull();
    expect(request.mock.calls.every(call => !call[1]?.method)).toBe(true);
  });
});

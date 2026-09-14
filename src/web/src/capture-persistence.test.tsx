import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { RequirementCenterPage } from './pages/catalog/RequirementCenterPage';

const workspace = { workspace_id: 'space', name: 'Capture Test', organization_name: 'Test', slug: 'test', role: '管理员', status: 'ACTIVE', timezone: 'Asia/Shanghai', member_count: 1 };
const context = { workspaces: [workspace], issues: [], current_user: { name: 'Test', avatar_initial: 'T', can_access_admin: false, permissions: [] }, selected_workspace_id: 'space', stats: { total: 0, requirements: 0, bugs: 0, blocked: 0, drift: 0 }, sprint_options: [], snapshot_revision: 'initial' };
const response = (data: unknown, status = 200) => Promise.resolve({ ok: status < 400, status, json: async () => ({ data, message: status >= 400 ? '受控写入失败' : 'ok' }) });
let requests: Record<string, unknown>[];
let created: Record<string, unknown>[];
let fail = false;
let serviceReady = true;
let multiple = false;
let terminalState = 'applied';
let pending: (() => void) | null;

beforeEach(() => {
  requests = []; created = []; fail = false; multiple = false; serviceReady = true; terminalState = 'applied'; pending = null;
  localStorage.clear(); sessionStorage.clear();
  window.history.replaceState(null, '', '/requirements');
  localStorage.setItem('moonbox.session', JSON.stringify({ username: 'test', access_token: 'synthetic', user: { id: 'test', username: 'test', role: '前台用户' } }));
  vi.stubGlobal('scrollTo', vi.fn());
  vi.stubGlobal('fetch', vi.fn((url: string, init?: RequestInit) => {
    if (url.includes('/capture-readiness')) return response({ ready: serviceReady, reason: serviceReady ? '' : '写入服务未配置' });
    if (url.includes('/projects')) return response({ ...context, projects: [{ space_id: 'space', repository_id: 'repo', status: 'connected', readonly: false }, ...(multiple ? [{ space_id: 'space', repository_id: 'other', status: 'connected', readonly: false }] : [])] });
    if (url.includes('/captures?')) {
      const body = JSON.parse(String(init?.body)); requests.push(body);
      if (fail) return response(null, 503);
      created = [{ ...body, id: 'REQ-0042-server-id', stage: 'capture', documents: ['capture.md', 'trace.md'], updated_at: '刚刚' }];
      return response({ id: 'operation', state: 'pending' }, 202);
    }
    if (url.includes('/governance-applications/')) return new Promise((resolve, reject) => {
      init?.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')), { once: true });
      pending = () => resolve({ ok: true, json: async () => ({ data: { id: 'operation', state: terminalState } }) });
    });
    return response({ ...context, issues: url.includes('repository_id=other') ? [] : created, snapshot_revision: JSON.stringify(created) });
  }));
});
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
async function open() {
  render(<RequirementCenterPage />);
  await screen.findByText('Capture Test');
  fireEvent.click(screen.getByRole('button', { name: '新建 Capture' }));
  fireEvent.change(screen.getByLabelText('Capture 标题'), { target: { value: '持久化标题' } });
  fireEvent.change(screen.getByLabelText('一句话描述'), { target: { value: '描述必须保留' } });
  await waitFor(() => expect(screen.queryByText('正在检查Capture写入服务…')).toBeNull());
}
it('waits for final success and reads the server card, sending description once', async () => {
  await open();
  fireEvent.click(screen.getByRole('button', { name: '＋ 创建 Capture' }));
  await waitFor(() => expect(requests).toHaveLength(1));
  expect(requests[0].description).toBe('描述必须保留');
  expect(screen.queryByText('Capture 已创建并插入采集池')).toBeNull();
  expect(screen.getByRole('button', { name: '创建中…' }).hasAttribute('disabled')).toBe(true);
  await waitFor(() => expect(pending).toBeTypeOf('function')); pending!();
  await screen.findByText('Capture 已创建并插入采集池');
  expect(document.querySelector('[data-issue-id="REQ-0042-server-id"]')).toBeTruthy();
  expect(screen.queryByRole('dialog', { name: '新建 Capture' })).toBeNull();
});
it('retains inputs on failure and reuses the idempotency key on retry', async () => {
  fail = true; await open();
  fireEvent.click(screen.getByRole('button', { name: '＋ 创建 Capture' }));
  await screen.findByText('受控写入失败');
  expect((screen.getByLabelText('一句话描述') as HTMLTextAreaElement).value).toBe('描述必须保留');
  fail = false;
  fireEvent.click(screen.getByRole('button', { name: '＋ 创建 Capture' }));
  await waitFor(() => expect(requests).toHaveLength(2));
  expect(requests[0].idempotency_key).toBe(requests[1].idempotency_key);
  await waitFor(() => expect(pending).toBeTypeOf('function')); pending!();
  await screen.findByText('Capture 已创建并插入采集池');
});
it('closing a pending dialog preserves input and prevents stale success feedback', async () => {
  await open(); fireEvent.click(screen.getByRole('button', { name: '＋ 创建 Capture' }));
  await waitFor(() => expect(pending).toBeTypeOf('function'));
  fireEvent.click(within(screen.getByRole('dialog', { name: '新建 Capture' })).getByRole('button', { name: '取消' }));
  pending!();
  fireEvent.click(screen.getByRole('button', { name: '新建 Capture' }));
  expect((screen.getByLabelText('Capture 标题') as HTMLInputElement).value).toBe('持久化标题');
  expect(screen.queryByText('Capture 已创建并插入采集池')).toBeNull();
});

it('ignores the original project response after selecting another repository', async () => {
  multiple = true; await open();
  fireEvent.click(screen.getByRole('button', { name: '＋ 创建 Capture' }));
  await waitFor(() => expect(pending).toBeTypeOf('function'));
  fireEvent.change(screen.getByLabelText('本地项目'), { target: { value: 'other' } });
  await waitFor(() => expect((screen.getByLabelText('本地项目') as HTMLSelectElement).value).toBe('other'));
  pending!();
  await new Promise(resolve => setTimeout(resolve, 20));
  expect(screen.queryByText('Capture 已创建并插入采集池')).toBeNull();
  expect(document.querySelector('[data-issue-id="REQ-0042-server-id"]')).toBeNull();
});

it('keeps the same operation key after the wait timeout', async () => {
  await open();
  const original = window.setTimeout.bind(window);
  const timer = vi.spyOn(window, 'setTimeout').mockImplementation(((handler: TimerHandler, delay?: number, ...args: unknown[]) => original(handler, delay === 30000 ? 80 : delay, ...args)) as typeof window.setTimeout);
  fireEvent.click(screen.getByRole('button', { name: '＋ 创建 Capture' }));
  await screen.findByText('等待超时，输入已保留；再次提交将查询同一次创建结果');
  timer.mockRestore();
  expect((screen.getByLabelText('一句话描述') as HTMLTextAreaElement).value).toBe('描述必须保留');
  pending = null;
  fireEvent.click(screen.getByRole('button', { name: '＋ 创建 Capture' }));
  await waitFor(() => expect(requests).toHaveLength(2));
  expect(requests[0].idempotency_key).toBe(requests[1].idempotency_key);
  await waitFor(() => expect(pending).toBeTypeOf('function')); pending!();
  await screen.findByText('Capture 已创建并插入采集池');
});

it('starts a new operation after a definitive no-write conflict', async () => {
  terminalState = 'conflict'; await open();
  fireEvent.click(screen.getByRole('button', { name: '＋ 创建 Capture' }));
  await waitFor(() => expect(pending).toBeTypeOf('function')); pending!();
  await screen.findByText('创建未完成，请检查项目写入条件；输入已保留');
  terminalState = 'applied'; pending = null;
  fireEvent.click(screen.getByRole('button', { name: '＋ 创建 Capture' }));
  await waitFor(() => expect(requests).toHaveLength(2));
  expect(requests[0].idempotency_key).not.toBe(requests[1].idempotency_key);
  await waitFor(() => expect(pending).toBeTypeOf('function')); pending!();
  await screen.findByText('Capture 已创建并插入采集池');
});

it('disables creation when the writer is unavailable and refreshes without losing input', async () => {
  serviceReady = false; render(<RequirementCenterPage />);
  await screen.findByText('Capture Test');
  fireEvent.click(screen.getByRole('button', { name: '新建 Capture' }));
  fireEvent.change(screen.getByLabelText('Capture 标题'), { target: { value: '保留输入' } });
  await screen.findByText('写入服务未配置');
  expect((screen.getByRole('button', { name: '＋ 创建 Capture' }) as HTMLButtonElement).disabled).toBe(true);
  expect(requests).toHaveLength(0);
  serviceReady = true;fireEvent.click(screen.getByRole('button', { name: '刷新状态' }));
  await waitFor(() => expect(screen.queryByText('正在检查Capture写入服务…')).toBeNull());
  expect((screen.getByLabelText('Capture 标题') as HTMLInputElement).value).toBe('保留输入');
  expect((screen.getByRole('button', { name: '＋ 创建 Capture' }) as HTMLButtonElement).disabled).toBe(false);
});

it('switches grading by type and submits only the selected type field', async () => {
  fail = true; await open();
  expect(within(screen.getByRole('group', { name: 'Capture 优先级' })).getAllByRole('button')).toHaveLength(4);
  fireEvent.click(screen.getByRole('button', { name: '◈ Bug' }));
  const grading = screen.getByRole('group', { name: 'Capture 严重性' });
  expect(within(grading).getAllByRole('button')).toHaveLength(5);
  fireEvent.click(within(grading).getByRole('button', { name: '严重' }));
  fireEvent.click(screen.getByRole('button', { name: '◆ 需求' }));
  fireEvent.click(screen.getByRole('button', { name: '◈ Bug' }));
  expect(screen.getByRole('button', { name: '严重' }).className).toBe('selected');
  fireEvent.click(screen.getByRole('button', { name: '＋ 创建 Capture' }));
  await screen.findByText('受控写入失败');
  expect(requests[0].severity).toBe('critical');
  expect(requests[0]).not.toHaveProperty('priority');
  fireEvent.click(screen.getByRole('button', { name: '◆ 需求' }));
  fireEvent.click(screen.getByRole('button', { name: '＋ 创建 Capture' }));
  await waitFor(() => expect(requests).toHaveLength(2));
  expect(requests[1].priority).toBe('P1');
  expect(requests[1]).not.toHaveProperty('severity');
});

it('shows only selected grading explanation, hides ready status and preserves P3', async () => {
  await open();
  const p3 = screen.getByRole('button', { name: 'P3' });
  fireEvent.mouseEnter(p3.parentElement!);
  expect(screen.queryByRole('tooltip')).toBeNull();
  fireEvent.focus(p3);
  expect(screen.queryByRole('tooltip')).toBeNull();
  expect(screen.queryByText('写入服务已就绪')).toBeNull();
  expect(document.querySelector('.rc-capture-readiness')).toBeNull();
  fireEvent.click(p3);
  expect(screen.getByText('P3：低优先级：体验优化或探索项，资源允许时安排')).toBeTruthy();
  fireEvent.click(screen.getByRole('button', { name: '＋ 创建 Capture' }));
  await waitFor(() => expect(requests).toHaveLength(1));
  expect(requests[0].priority).toBe('P3');
  await waitFor(() => expect(pending).toBeTypeOf('function')); pending!();
  await screen.findByText('Capture 已创建并插入采集池');
});

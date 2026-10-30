import React from 'react';
import { render, screen, fireEvent, cleanup, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { AcceptanceOperations } from './components/chat/AcceptanceOperations';
import { governanceRequest } from './components/workbench/governanceApi';
vi.mock('./components/workbench/governanceApi', () => ({ governanceRequest: vi.fn() }));
afterEach(() => { cleanup(); vi.resetAllMocks(); });
const item = { id: 'operation', source_turn_id: 'turn', change_id: 'add-test', status: 'running', version: 3,
  cleanup_state: 'active', cancel_requested: false, ready: false, reason_code: null, expires_at: null,
  allowed_actions: ['verify', 'stop'], checks: [{ ac_id: 'AC-001', status: 'pending', reason_code: null, evidence_available: false }] };
it('refresh is read-only and Escape cancels the stop dialog', async () => {
  vi.mocked(governanceRequest).mockResolvedValue({ items: [item] });
  render(<AcceptanceOperations conversationId="chat" />);
  fireEvent.click(await screen.findByRole('button', { name: '停止' }));
  expect(screen.getByRole('dialog')).toBeTruthy();
  fireEvent.keyDown(document, { key: 'Escape' });
  expect(screen.queryByRole('dialog')).toBeNull();
  expect(governanceRequest).toHaveBeenCalledTimes(1);
  expect(vi.mocked(governanceRequest).mock.calls[0][1]?.method).toBeUndefined();
});
it('explicit stop sends the current version once even with duplicate clicks', async () => {
  let complete: (value: unknown) => void = () => {};
  vi.mocked(governanceRequest).mockResolvedValueOnce({ items: [item] }).mockImplementationOnce(() => new Promise(resolve => { complete = resolve; }));
  render(<AcceptanceOperations conversationId="chat" />);
  fireEvent.click(await screen.findByRole('button', { name: '停止' }));
  const button = screen.getByRole('button', { name: '确认停止' });
  fireEvent.click(button); fireEvent.click(button);
  expect(governanceRequest).toHaveBeenCalledTimes(2);
  expect(vi.mocked(governanceRequest).mock.calls[1][1]?.body).toBe(JSON.stringify({ version: 3 }));
  complete({ ...item, status: 'cancelled', cancel_requested: true, allowed_actions: ['verify'] });
  await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull());
  expect(screen.queryByRole('button', { name: '停止' })).toBeNull();
});
it('read-only projection does not display a write action', async () => {
  vi.mocked(governanceRequest).mockResolvedValue({ items: [{ ...item, allowed_actions: ['verify'] }] });
  render(<AcceptanceOperations conversationId="chat" />);
  await screen.findByTestId('acceptance-operation');
  expect(screen.queryByRole('button', { name: '停止' })).toBeNull();
});
it('explicit verify and evidence remain read-only', async () => {
  vi.mocked(governanceRequest).mockResolvedValueOnce({ items: [{ ...item, allowed_actions: ['verify', 'evidence'] }] })
    .mockResolvedValueOnce({ ...item, allowed_actions: ['verify', 'evidence'] })
    .mockResolvedValueOnce({ checks: [{ ac_id: 'AC-001', status: 'passed', evidence: { kind: 'command', digest: 'd'.repeat(64) } }] });
  render(<AcceptanceOperations conversationId="chat" />);
  fireEvent.click(await screen.findByRole('button', { name: '重新核验' }));
  expect(vi.mocked(governanceRequest).mock.calls[1][1]).toEqual({ headers: { 'X-Acceptance-Action': 'verify' } });
  await waitFor(() => expect((screen.getByRole('button', { name: '查看证据' }) as HTMLButtonElement).disabled).toBe(false));
  fireEvent.click(screen.getByRole('button', { name: '查看证据' }));
  await screen.findByRole('dialog');
  expect(vi.mocked(governanceRequest).mock.calls[2][0]).toContain('/evidence');
  expect(vi.mocked(governanceRequest).mock.calls[2][1]).toBeUndefined();
});
it('resume uses the current version and hides the action on success', async () => {
  vi.mocked(governanceRequest).mockResolvedValueOnce({ items: [{ ...item, status: 'blocked', allowed_actions: ['verify', 'resume'] }] })
    .mockResolvedValueOnce({ ...item, status: 'queued', version: 4, allowed_actions: ['verify', 'stop'] });
  render(<AcceptanceOperations conversationId="chat" />);
  fireEvent.click(await screen.findByRole('button', { name: '继续' }));
  await waitFor(() => expect(screen.queryByRole('button', { name: '继续' })).toBeNull());
  expect(vi.mocked(governanceRequest).mock.calls[1][0]).toContain('/resume');
  expect(vi.mocked(governanceRequest).mock.calls[1][1]).toEqual({ method: 'POST', body: JSON.stringify({ version: 3 }) });
});
it('long-term summaries remain separately readable without an online evidence action', async () => {
  vi.mocked(governanceRequest).mockResolvedValueOnce({ items: [{ ...item, allowed_actions: ['verify', 'archive-evidence'] }] })
    .mockResolvedValueOnce({ items: [{ summary: { checks: [{ ac_id: 'AC-001', status: 'passed', evidence: { kind: 'command', digest: 'd'.repeat(64) } }] } }] });
  render(<AcceptanceOperations conversationId="chat" />);
  fireEvent.click(await screen.findByRole('button', { name: '长期摘要' }));
  await screen.findByRole('dialog');
  expect(vi.mocked(governanceRequest).mock.calls[1][0]).toContain('/evidence/archive');
  expect(vi.mocked(governanceRequest).mock.calls[1][1]).toBeUndefined();
  expect(screen.queryByRole('button', { name: '查看证据' })).toBeNull();
});

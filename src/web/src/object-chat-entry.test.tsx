import { act, cleanup, fireEvent, render, renderHook, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { chatRequest, listSessions } from './components/chat/chatApi';
import { ChatWorkbenchPage } from './pages/catalog/ChatWorkbenchPage';
import { openObjectChat, readObjectChatIntent } from './pages/catalog/objectChatIntent';
import { useObjectChatEntry } from './pages/catalog/useObjectChatEntry';
vi.mock('./components/chat/chatApi', async original => ({ ...await original<typeof import('./components/chat/chatApi')>(), chatRequest: vi.fn(), listSessions: vi.fn() }));
const intent = { id: 'entry-1', spaceId: 'space', repositoryId: 'repo', objectId: 'BUG-0200', title: '测试对象', text: '/bug-generate BUG-0200' };
const conversation = { id: 'chat-1', space_id: 'space', repository_id: 'repo', title: '测试会话', archived: false, active_turn_id: null };
afterEach(() => { cleanup(); vi.resetAllMocks(); vi.unstubAllGlobals(); sessionStorage.clear(); localStorage.clear(); history.replaceState(null, '', '/'); });
function seed() {
  openObjectChat(intent);
  vi.stubGlobal('matchMedia', vi.fn(() => ({ matches: true })));
  vi.mocked(listSessions).mockResolvedValue({ items: [], total: 0 } as never);
  vi.mocked(chatRequest).mockImplementation(async path => {
    if (path === '/spaces') return [{ id: 'space', name: '测试空间' }] as never;
    if (path.startsWith('/capabilities')) return { execution_ready: true, repositories: [{ id: 'repo' }] } as never;
    if (path === '/conversations/chat-1') return conversation as never;
    return { items: [] } as never;
  });
}
it('opens immediately without requests and preserves scoped intent across refresh', () => {
  openObjectChat(intent);
  expect(location.pathname).toBe('/chat'); expect(readObjectChatIntent()).toEqual(intent);
  expect(chatRequest).not.toHaveBeenCalled();
  history.replaceState(null, '', '/chat?space_id=other&object_entry=entry-1');
  expect(readObjectChatIntent()).toBeNull();
});
it('keeps the draft editable while opening and never submits or prepares a candidate', async () => {
  seed(); let complete!: (value: unknown) => void;
  const fallback = vi.mocked(chatRequest).getMockImplementation()!;
  vi.mocked(chatRequest).mockImplementation((path, options) => path === '/object-sessions'
    ? new Promise(resolve => { complete = resolve; }) : fallback(path, options));
  render(<ChatWorkbenchPage />);
  await waitFor(() => expect(complete).toBeTruthy());
  const editor = screen.getByTestId('chat-prompt');
  expect(editor.textContent).toBe(intent.text);
  expect(editor.getAttribute('contenteditable')).toBe('true');
  editor.textContent = '用户修改后的草稿'; fireEvent.input(editor);
  expect((screen.getByTestId('chat-send') as HTMLButtonElement).disabled).toBe(true);
  await act(async () => complete({ conversation_id: conversation.id }));
  await waitFor(() => expect(screen.getByTestId('chat-title-edit').textContent).toContain(conversation.title));
  expect(screen.getByTestId('chat-prompt').textContent).toBe('用户修改后的草稿');
  expect(readObjectChatIntent()?.text).toBe('用户修改后的草稿');
  expect(vi.mocked(chatRequest).mock.calls.some(([p, o]) => p.endsWith('/turns') && o?.method === 'POST')).toBe(false);
  expect(vi.mocked(chatRequest).mock.calls.some(([p]) => p.includes('governance-preparations'))).toBe(false);
});
it('retains both drafts until explicit selection', async () => {
  seed(); sessionStorage.setItem('moonbox.governance.prompt:chat-1', '已有草稿');
  const fallback = vi.mocked(chatRequest).getMockImplementation()!;
  vi.mocked(chatRequest).mockImplementation((p, o) => p === '/object-sessions' ? Promise.resolve({ conversation_id: 'chat-1' }) as never : fallback(p, o));
  render(<ChatWorkbenchPage />);
  await screen.findByRole('button', { name: '保留原会话草稿' });
  expect((screen.getByTestId('chat-send') as HTMLButtonElement).disabled).toBe(true);
  expect(sessionStorage.getItem('moonbox.governance.prompt:chat-1')).toBe('已有草稿');
  fireEvent.click(screen.getByRole('button', { name: '保留原会话草稿' }));
  expect(screen.getByTestId('chat-prompt').textContent).toBe('已有草稿');
});
it('retries a failed opening with the same identity and ignores abandoned responses', async () => {
  seed(); const selected = vi.fn(); let complete!: (value: unknown) => void; let signal: AbortSignal | undefined;
  vi.mocked(chatRequest).mockRejectedValueOnce(new Error('连接中断')).mockImplementation((_p, options) => {
    signal = options?.signal as AbortSignal; return new Promise(resolve => { complete = resolve; });
  });
  const view = renderHook(() => useObjectChatEntry('space', selected));
  await waitFor(() => expect(view.result.current.error).toBe('连接中断'));
  act(() => view.result.current.retry());
  await waitFor(() => expect(complete).toBeTruthy());
  const calls = vi.mocked(chatRequest).mock.calls;
  expect(calls[0][1]?.body).toBe(calls[1][1]?.body);
  view.unmount(); expect(signal?.aborted).toBe(true);
  await act(async () => complete({ conversation_id: 'late-chat' }));
  expect(selected).not.toHaveBeenCalled(); expect(readObjectChatIntent()?.text).toBe(intent.text);
});

it('rejects a delivery response for a sibling before loading its conversation', async () => {
  openObjectChat({...intent,objectId:'first-delivery',text:'/opsx-apply REQ-0001-source'});
  const selected=vi.fn();
  vi.mocked(chatRequest).mockResolvedValue({object_id:'second-delivery',conversation_id:'wrong-chat'} as never);
  const view=renderHook(()=>useObjectChatEntry('space',selected));
  await waitFor(()=>expect(view.result.current.error).toContain('交付会话目标不匹配'));
  expect(selected).not.toHaveBeenCalled();
  expect(chatRequest).toHaveBeenCalledTimes(1);
  expect(readObjectChatIntent()?.objectId).toBe('first-delivery');
});

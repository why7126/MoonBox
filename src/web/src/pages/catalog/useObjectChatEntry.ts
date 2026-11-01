import { useEffect, useState } from 'react';
import { chatRequest, type ConversationRead } from '../../components/chat/chatApi';
import { readObjectChatIntent } from './objectChatIntent';
import type { GovernanceSessionResult } from './governanceSession';

export function useObjectChatEntry(space: string, select: (row: ConversationRead | null) => void) {
  const [intent, setIntent] = useState(readObjectChatIntent);
  const [error, setError] = useState('');
  const [opening, setOpening] = useState(Boolean(intent));
  const [retry, setRetry] = useState(0);
  const [resolved, setResolved] = useState('');
  useEffect(() => {
    if (!intent || !space) return;
    if (space !== intent.spaceId) { setIntent(null); setOpening(false); return; }
    const controller = new AbortController();
    setOpening(true); setError('');
    void (async () => {
      try {
        const result = await chatRequest<GovernanceSessionResult>('/object-sessions', {
          method: 'POST', signal: controller.signal,
          body: JSON.stringify({ space_id: intent.spaceId, repository_id: intent.repositoryId,
            object_id: intent.objectId, action: 'open-chat', idempotency_key: intent.id }),
        });
        if (controller.signal.aborted) return;
        if (!/^(REQ-|BUG-|sprint-)/.test(intent.objectId) && result.object_id !== intent.objectId) throw new Error('交付会话目标不匹配，草稿已保留，请刷新后重试');
        const cid = result.conversation_id || result.view_conversation_id;
        if (!cid) throw new Error('对象暂不可打开，草稿已保留，请稍后重试');
        const row = await chatRequest<ConversationRead>(`/conversations/${encodeURIComponent(cid)}`, { signal: controller.signal });
        if (controller.signal.aborted) return;
        if (row.space_id !== intent.spaceId || row.repository_id !== intent.repositoryId) throw new Error('会话所属项目已变化，草稿已保留');
        setResolved(row.id); select(row); setOpening(false);
      } catch (e) {
        if (!controller.signal.aborted) { setError(e instanceof Error ? e.message : '打开会话失败，草稿已保留'); setOpening(false); }
      }
    })();
    return () => controller.abort();
  }, [intent?.id, space, retry]);
  return { intent, opening, error, resolved, retry: () => setRetry(v => v + 1), clear: () => {
    setIntent(null); setOpening(false); setError('');
    const url = new URL(location.href); url.searchParams.delete('object_entry');
    history.replaceState(null, '', url.pathname + url.search);
  } };
}

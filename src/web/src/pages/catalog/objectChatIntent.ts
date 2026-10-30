/** Per-tab navigation draft; never an authorization or an instruction to send. */
export type ObjectChatIntent = {
  id: string; spaceId: string; repositoryId: string; objectId: string; title: string; text: string;
};
const prefix = 'moonbox.objectChat.intent:';
export function saveObjectChatIntent(intent: ObjectChatIntent) {
  sessionStorage.setItem(prefix + intent.id, JSON.stringify(intent));
}
export function readObjectChatIntent(): ObjectChatIntent | null {
  const id = new URLSearchParams(location.search).get('object_entry');
  if (!id || !/^[A-Za-z0-9_-]{1,64}$/.test(id)) return null;
  try {
    const row = JSON.parse(sessionStorage.getItem(prefix + id) || 'null');
    const space = new URLSearchParams(location.search).get('space_id');
    if (!row || row.id !== id || row.spaceId !== space || typeof row.repositoryId !== 'string' ||
        typeof row.objectId !== 'string' || typeof row.title !== 'string' || typeof row.text !== 'string') return null;
    return row;
  } catch { return null; }
}
export function openObjectChat(intent: ObjectChatIntent) {
  saveObjectChatIntent(intent);
  window.history.pushState(null, '', `/chat?space_id=${encodeURIComponent(intent.spaceId)}&object_entry=${encodeURIComponent(intent.id)}`);
  window.dispatchEvent(new PopStateEvent('popstate'));
}

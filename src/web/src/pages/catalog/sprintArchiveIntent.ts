/** One-shot navigation data, never an authorization token or an instruction to send. */
export type SprintArchiveIntent = {
  version: 1; id: string; spaceId: string; repositoryId: string; conversationId: string; sprintId: string;
};
type Store = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>;
const key = (id: string) => `moonbox.sprintArchive.intent:${id}`;
export function storeSprintArchiveIntent(storage: Store, intent: SprintArchiveIntent) {
  storage.setItem(key(intent.conversationId), JSON.stringify(intent));
}
export function takeSprintArchiveIntent(storage: Store, target: { id: string; space_id: string; repository_id: string; active_turn_id: string | null; archived: boolean }): SprintArchiveIntent | null {
  const value = storage.getItem(key(target.id));
  if (!value) return null;
  storage.removeItem(key(target.id));
  try {
    const intent = JSON.parse(value) as SprintArchiveIntent;
    if (intent.version !== 1 || !intent.id || intent.conversationId !== target.id || intent.spaceId !== target.space_id || intent.repositoryId !== target.repository_id || !/^sprint-\d{3}$/.test(intent.sprintId) || target.active_turn_id || target.archived) return null;
    return intent;
  } catch { return null; }
}
export function sprintArchiveDraftDecision(text: string, sprintId: string): 'fill' | 'same' | 'conflict' {
  if (!text.trim()) return 'fill';
  return text.trim() === `/sprint-archive ${sprintId}` ? 'same' : 'conflict';
}

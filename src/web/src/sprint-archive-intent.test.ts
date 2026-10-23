import { describe, it, expect } from 'vitest';
import { takeSprintArchiveIntent, storeSprintArchiveIntent, sprintArchiveDraftDecision, type SprintArchiveIntent } from './pages/catalog/sprintArchiveIntent';
const intent: SprintArchiveIntent = { version: 1, id: 'click-1', spaceId: 'space-a', repositoryId: 'repo-a', conversationId: 'conv-a', sprintId: 'sprint-099' };
const target = { id: 'conv-a', space_id: 'space-a', repository_id: 'repo-a', active_turn_id: null, archived: false };
function storage() { const data = new Map<string,string>(); return { getItem: (k:string) => data.get(k) ?? null, setItem: (k:string,v:string) => { data.set(k,v); }, removeItem: (k:string) => { data.delete(k); } }; }
describe('Sprint archive navigation intent', () => {
  it('consumes only once; reload cannot replace a subsequently edited draft', () => { const s=storage(); storeSprintArchiveIntent(s,intent); expect(takeSprintArchiveIntent(s,target)).toEqual(intent); expect(takeSprintArchiveIntent(s,target)).toBeNull(); });
  it.each([{ space_id:'other' }, { repository_id:'other' }, { active_turn_id:'running' }, { archived:true }])('rejects stale identity or non-idle session %s', patch => { const s=storage(); storeSprintArchiveIntent(s,intent); expect(takeSprintArchiveIntent(s,{...target,...patch})).toBeNull(); });
  it('does not consume another conversation intent', () => { const s=storage(); storeSprintArchiveIntent(s,intent); expect(takeSprintArchiveIntent(s,{...target,id:'other'})).toBeNull(); expect(takeSprintArchiveIntent(s,target)).toEqual(intent); });
  it('preserves different draft, avoids duplicate same command', () => { expect(sprintArchiveDraftDecision('my draft','sprint-099')).toBe('conflict'); expect(sprintArchiveDraftDecision('/sprint-archive sprint-099','sprint-099')).toBe('same'); expect(sprintArchiveDraftDecision('  ','sprint-099')).toBe('fill'); });
});

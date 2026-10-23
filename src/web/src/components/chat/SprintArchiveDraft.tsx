import { Button } from "../ui/Button";
/** Inline choice: this component never sends or changes attachment/skill state. */
export function SprintArchiveDraft({ sprintId, disabled = false, onKeep, onReplace }: {
  sprintId: string; disabled?: boolean; onKeep: () => void; onReplace: () => void;
}) {
  return <section className="sprint-archive-draft" data-testid="sprint-archive-draft-conflict" aria-label="归档命令与当前草稿" onKeyDown={event => { if (event.key === 'Escape') onKeep(); }}>
    <div><strong>已保留当前草稿</strong><p>可继续编辑，或填入 <code>/sprint-archive {sprintId}</code>，确认后再发送。</p></div>
    <div className="sprint-archive-draft-actions">
      <Button variant="ghost" type="button" data-testid="sprint-archive-draft-keep" onClick={onKeep}>保留当前草稿</Button>
      <Button variant="ghost" type="button" data-testid="sprint-archive-draft-replace" disabled={disabled} onClick={onReplace}>填入归档命令</Button>
    </div>
  </section>;
}

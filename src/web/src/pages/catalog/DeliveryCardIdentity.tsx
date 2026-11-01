import type { ReactNode } from "react";

export type DeliverySource = { id: string; type: string; title: string };

/** Identity stays separate from title and never selects an execution source. */
export function DeliveryCardIdentity({ id, changeId, sources = [], sprintId, onSource, children }: {
  id: string; changeId?: string | null; sources?: DeliverySource[]; sprintId?: string;
  onSource?: (source: DeliverySource) => void;
  children?: ReactNode;
}) {
  return <>
    <div className="rc-card-top">
      <div className="rc-card-sources" data-testid="rc-source">
        {sources.length ? sources.map(source => <button key={source.id} type="button"
          title={`${source.id} · ${source.title}`} aria-label={`查看来源 ${source.id}`} disabled={!onSource}
          onClick={() => onSource?.(source)}><strong>{source.id.match(/^(?:REQ|BUG)-\d+/)?.[0] || source.id}</strong></button>) : <strong>{id}</strong>}
      </div>
      {sprintId && <span className="rc-sprint-tag" data-testid="rc-sprint">{sprintId}</span>}
    </div>
    {children}
    {changeId && sources.length > 0 && <div className="rc-change-id-row" data-testid="rc-change-id"><strong>{changeId}</strong></div>}
  </>;
}

export type CardInfoFacts = {
  type: string;
  estimated_person_days?: number | null;
  estimate_status?: "available" | "missing" | "conflict" | "invalid";
  root_cause_state?: "absent" | "pending" | "confirmed";
  root_cause_reason?: "missing" | "conflict" | "invalid" | null;
};

export function CardInfoTags({ facts, onRootCause, disabled = false }: {
  facts: CardInfoFacts; onRootCause: () => void; disabled?: boolean;
}) {
  const days = facts.estimated_person_days;
  const showDays = facts.estimate_status === "available" && typeof days === "number" && Number.isFinite(days) && days >= 0;
  const showRoot = facts.type === "bug" && (facts.root_cause_state === "pending" || facts.root_cause_state === "confirmed");
  const size = typeof days === "number" ? (days <= 1 ? "S" : days <= 3 ? "M" : days <= 5 ? "L" : days <= 10 ? "XL" : "XXL") : null;
  return <>
    {showRoot && <button type="button" className={`rc-tag rc-root-cause-tag ${facts.root_cause_state}`}
      data-testid="root-cause-tag" disabled={disabled}
      title={facts.root_cause_reason ? "根因状态需核对，点击查看根因文档" : "查看根因文档"}
      onClick={event => { event.stopPropagation(); onRootCause(); }}>
      {facts.root_cause_state === "confirmed" ? "根因已确认" : "根因待确认"}
    </button>}
    {showDays && <span className={`rc-tag rc-person-days-tag rc-effort-${size?.toLowerCase()}`} data-testid="person-days-tag" title={`${size} · 预估开发${days}人天`}>
      {size}<span className="rc-effort-separator">·</span>{days}人天
    </span>}
  </>;
}

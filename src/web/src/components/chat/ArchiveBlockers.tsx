import type { RequirementCenterArchiveReadinessBlocker } from "../../api/generated/governance";

export type ArchiveBlocker = RequirementCenterArchiveReadinessBlocker;
const labels: Record<string, string> = {
  archive_requirement_conflict: "规则内容已修改，需检查后继续", missing_signoff: "验收尚未签署",
  archive_spec_baseline_changed: "归档证明链待核验", archive_proof_inputs_changed: "输入已变化，请重新核验",
};
export function ArchiveBlockers({ items, onReviewReplacement }: { items: ArchiveBlocker[]; onReviewReplacement?: (changeId: string) => void }) {
  if (!items.length) return null;
  return <section role="alert" className="chat-archive-blockers" data-testid="archive-blockers">
    <strong>归档暂未就绪 · {items.length} 项需要处理</strong>
    {items.map((item, index) => <article key={`${item.type}:${item.id}:${index}`} data-testid="archive-blocker-item">
      <strong>{item.id || "归档条件"} · {labels[item.status || ""] || "需要核验"}</strong>
      <p>{item.message}</p>
      {item.status === "archive_requirement_conflict" && item.id && onReviewReplacement && <button type="button" data-testid="archive-review-replacement" onClick={() => onReviewReplacement(item.id!)}>查看修改</button>}
      {item.action_hint && <details><summary>查看处理步骤</summary><p>{item.action_hint}</p></details>}
    </article>)}
  </section>;
}

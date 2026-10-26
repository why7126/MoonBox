import { useEffect, useRef, useState } from "react";
import { chatRequest, normalizeChatError } from "./chatApi";
import { StoragePanel } from "./StoragePanel";

type Page = { items: { sequence: number; text: string }[]; next_cursor: string | null; resume_cursor: string; committed_sequence: number; completeness: string; has_final: boolean };
const reasons: Record<string, string> = {
  container_memory_exhausted: "执行容器达到部署内存保护，已被停止。已保存内容保留，请调整任务或部署资源后核验原运行。",
  container_terminated: "执行容器已被终止，尚未确认具体原因。已保存内容保留，请先核验原运行。",
  result_backpressure_timeout: "结果保存持续跟不上执行输出，已停止本次连接。已保存内容保留，请恢复存储性能后核验原运行。",
  workspace_resource_exhausted: "工作区或保存位置的资源不足。已保存内容保留，请释放空间或扩容后核验是否可以继续。",
  result_persistence_failed: "结果保存暂时失败。已提交内容保留，尚未确认保存的末尾内容可能不完整。请恢复存储服务后核验原运行。",
  operating_quota_exceeded: "已达到管理员配置的运营额度。已保存内容保留，请调整额度后核验。",
  protocol_resource_limit: "执行端消息超过当前部署的处理能力。已保存内容保留，请检查执行器兼容性或部署配置。",
  executor_disconnected: "与执行端的连接中断，尚不能确认原运行是否结束。请先核验状态，避免重复执行。",
};

/** Keep at most four response pages; navigation never downloads the whole run. */
export function SavedResults({ turnId, status, reason }: { turnId: string; status: string; reason?: string | null }) {
  const [pages, setPages] = useState<Page[]>([]), [stream, setStream] = useState("output");
  const [busy, setBusy] = useState(false), [error, setError] = useState("");
  const request = useRef<AbortController | null>(null);
  const recoveryRequest = useRef<string | null>(null);
  const [recovery, setRecovery] = useState<{ eligibility: boolean; state: string; reason: string | null } | null>(null);
  useEffect(() => {
    request.current?.abort(); setPages([]); setBusy(false); setError(""); setRecovery(null); recoveryRequest.current = null;
    return () => request.current?.abort();
  }, [turnId, stream]);
  async function load(cursor?: string) {
    request.current?.abort(); const controller = new AbortController(); request.current = controller;
    setBusy(true); setError("");
    try {
      const query = new URLSearchParams({ stream_id: stream }); if (cursor) query.set("cursor", cursor);
      const page = await chatRequest<Page>(`/turns/${turnId}/results?${query}`, { signal: controller.signal });
      if (!controller.signal.aborted) setPages(current => cursor ? [...current, page].slice(-4) : [page]);
    } catch (cause) {
      if (!controller.signal.aborted) {
        const normalized = normalizeChatError(cause, "已保存内容暂时无法读取，请重试");
        setError(normalized instanceof Error ? normalized.message : "已保存内容暂时无法读取，请重试");
      }
    } finally { if (!controller.signal.aborted) setBusy(false); }
  }
  const last = pages[pages.length - 1];
  async function recover() {
    if (busy) return;
    const mode = recovery?.eligibility ? "resume_prepare" : "check";
    if (!recoveryRequest.current) recoveryRequest.current = crypto.randomUUID();
    request.current?.abort(); const controller = new AbortController(); request.current = controller;
    setBusy(true); setError("");
    try {
      const result = await chatRequest<{ eligibility: boolean; state: string; reason: string | null }>(`/turns/${turnId}/recovery`, {
        signal: controller.signal, method: "POST", body: JSON.stringify({ mode, idempotency_key: recoveryRequest.current }),
      });
      if (controller.signal.aborted) return;
      setRecovery(result);
      if (mode === "check") recoveryRequest.current = null;
    } catch (cause) { if (!controller.signal.aborted) setError(cause instanceof Error ? cause.message : "状态核验失败，请重试"); }
    finally { if (!controller.signal.aborted) setBusy(false); }
  }
  const stage = status === "unknown" ? "执行状态待核验" : status === "connecting" ? "正在准备工作区" : status === "running" ? "执行中，结果持续保存" : status === "completed" ? "执行已结束" : status === "queued" ? "等待执行" : status === "failed" && reason?.startsWith("workspace_") ? "工作区准备失败" : "执行已中断";
  return <StoragePanel stage={stage} summary={last ? `已确认保存至第 ${last.committed_sequence} 段；当前只加载最近四页。${last.completeness === "complete" ? "结果已完成保存。" : "末尾完整性尚未确认。"}` : "可按需读取已经保存的内容。执行中断不会清空已保存结果。"}
    reason={reason ? `${reasons[reason] || "请结合执行轨迹核验原因；状态未知时请勿重复发起执行。"} 诊断标识：${reason}` : undefined}
    onRead={() => void load()} busy={busy}
    recoveryLabel={["failed", "unknown"].includes(status) ? recovery?.eligibility ? "继续准备工作区" : "核验执行状态" : undefined}
    onRecover={() => void recover()}>
    {recovery && <p role="status">{recovery.eligibility ? "已确认执行尚未开始，可以继续准备工作区。" : recovery.state === "queued" ? "续接已排队，尚未完成执行。" : "暂不可原地续接。请保留已保存结果并结合轨迹核验；已确认结束的运行可使用重试操作。"}</p>}
    <label>读取内容 <select aria-label="读取内容" value={stream} onChange={event => setStream(event.target.value)}><option value="output">执行输出</option><option value="final">最终答复</option></select></label>
    {error && <p role="alert">{error}</p>}
    {pages.map((page, index) => <div key={`${stream}:${index}`}>{page.items.map(item => <pre key={item.sequence}>{item.text}</pre>)}</div>)}
    {last && !pages.some(page => page.items.length) && <p>此内容流暂无已保存文字。</p>}
    {last && <button type="button" data-testid="chat-result-load-more" disabled={busy} onClick={() => void load(last.next_cursor || last.resume_cursor)}>{busy ? "正在读取…" : last.next_cursor ? "读取下一页" : "检查新保存内容"}</button>}
  </StoragePanel>;
}

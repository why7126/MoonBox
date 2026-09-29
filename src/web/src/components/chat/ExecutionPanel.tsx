import { useEffect, useRef, useState } from "react";
import { DiffView, type DiffData } from "./DiffView";
import { ChatDialog } from "./ChatDialog";
import { ChevronDown, Square } from "lucide-react";
import { chatRequest, type ConversationRead, type TurnRead } from "./chatApi";
import { readChatEvents, type ChatEvent } from "./chatEvents";
import { TrajectoryView } from "./TrajectoryView";
type ContextItem = { object_id: string; version: string; title: string; content: string; truncated: boolean };
const labels: Record<string, string> = { queued: "排队中", connecting: "连接中", running: "执行中", stopping: "停止中", unknown: "状态未知", completed: "已完成", failed: "失败", stopped: "已停止" };
export function ExecutionPanel({ conversation, executionReady = false, focusTurn, focusVersion }: { conversation: ConversationRead | null; executionReady?: boolean; focusTurn?: string; focusVersion?: number }) {
  const [turns, setTurns] = useState<TurnRead[]>([]), [selected, setSelected] = useState("");
  const [eventAfter, setEventAfter] = useState(0), [moreEvents, setMoreEvents] = useState(false);
  const [events, setEvents] = useState<ChatEvent[]>([]), [diff, setDiff] = useState<DiffData | null>(null);
  const [error, setError] = useState(""), [busy, setBusy] = useState(false), [retry, setRetry] = useState(0);
  const [context, setContext] = useState<ContextItem[]>([]);
  const stopping = useRef(false);
  const retrying = useRef(false), retryRequest = useRef<{ turn: string; id: string } | null>(null);
  const [confirmStop, setConfirmStop] = useState<string | null>(null);
  const active = turns.find(t => ["queued", "connecting", "running", "stopping", "unknown"].includes(t.status));
  useEffect(() => { if (focusTurn) { setEventAfter(0); setSelected(focusTurn); } }, [focusTurn, focusVersion]);
  useEffect(() => {
    setTurns([]); setSelected(""); setError("");
    if (!conversation) return;
    const controller = new AbortController(); let timer: ReturnType<typeof setTimeout>;
    const poll = async () => {
      try {
        const data = await chatRequest<{ items: TurnRead[] }>(`/conversations/${conversation.id}/turns`, { signal: controller.signal });
        if (controller.signal.aborted) return;
        setTurns(data.items); setSelected(current => data.items.some(t => t.id === current) ? current : data.items[0]?.id || "");
        timer = setTimeout(poll, 3000);
      } catch (e) { if (!controller.signal.aborted) { setTurns([]); setSelected(""); setEvents([]); setDiff(null); setContext([]); setError(e instanceof Error ? e.message : "读取失败"); } }
    };
    void poll(); return () => { controller.abort(); clearTimeout(timer); };
  }, [conversation?.id, retry]);
  useEffect(() => {
    setEvents([]); setDiff(null); setContext([]); setMoreEvents(false);
    if (!selected) return;
    const controller = new AbortController(); let timer: ReturnType<typeof setTimeout>, cursor = eventAfter, loaded = 0;
    const poll = async () => {
      try {
        const batch = await readChatEvents(selected, cursor, controller.signal);
        const snapshot = await chatRequest<DiffData>(`/turns/${selected}/diff`, { signal: controller.signal });
        const references = await chatRequest<ContextItem[]>(`/turns/${selected}/context`, { signal: controller.signal });
        if (controller.signal.aborted) return;
        setContext(Array.isArray(references) ? references : []);
        if (batch.length) { cursor = batch[batch.length - 1].sequence; loaded += batch.length; setEvents(current => [...current, ...batch]); }
        setDiff(snapshot); if (loaded >= 1000) { setMoreEvents(true); return; } timer = setTimeout(poll, batch.length === 200 ? 0 : 3000);
      } catch (e) { if (!controller.signal.aborted) { setEvents([]); setDiff(null); setContext([]); setError(e instanceof Error ? e.message : "事件读取失败"); } }
    };
    void poll(); return () => { controller.abort(); clearTimeout(timer); };
  }, [selected, retry, eventAfter]);
  const stop = async () => {
    if (!active || active.id !== confirmStop || stopping.current) return;
    stopping.current = true; setBusy(true); setError("");
    try {
      const result = await chatRequest<TurnRead>(`/turns/${active.id}/interrupt`, { method: "POST" });
      setTurns(current => current.map(t => t.id === result.id ? result : t)); setConfirmStop(null);
    } catch (e) { setError(e instanceof Error ? e.message : "停止请求失败"); }
    finally { stopping.current = false; setBusy(false); }
  };
  const selectedTurn = turns.find(turn => turn.id === selected);
  async function retryTurn() {
    if (!executionReady || active || retrying.current || !selectedTurn || !["failed", "stopped"].includes(selectedTurn.status)) return;
    if (!retryRequest.current || retryRequest.current.turn !== selected) retryRequest.current = { turn: selected, id: crypto.randomUUID() };
    retrying.current = true; setBusy(true); setError("");
    try {
      const row = await chatRequest<TurnRead>(`/turns/${selected}/retries`, { method: "POST", body: JSON.stringify({ client_request_id: retryRequest.current.id }) });
      setTurns(current => [row, ...current.filter(turn => turn.id !== row.id)]); setSelected(row.id); retryRequest.current = null;
    } catch (e) { setError(e instanceof Error ? e.message : "重试失败"); }
    finally { retrying.current = false; setBusy(false); }
  }
  return <>
    {active?.status === "unknown" && <p className="chat-error">原运行状态尚未确认，暂不能发起新运行。</p>}
    {error && <div role="alert" className="chat-error">{error}<button onClick={() => setRetry(value => value + 1)}>重新连接</button></div>}
    {selectedTurn?.error_code && <p className="chat-error">{selectedTurn.error_code === "result_or_token_limit" ? "本轮达到输出或Token预留上限，已记录内容保留，后续输出可能截断。" : selectedTurn.error_code === "reconciled_usage_pending" || selectedTurn.error_code === "usage_unavailable" ? "执行已结束，用量尚待核实，额度预留暂未释放。" : "本轮存在执行或结果异常，请结合事件和差异记录检查。"}</p>}
    <section className="chat-panel-section" data-testid="chat-execution-events"><h3>执行事件</h3>
      <div className="trace-wrap">
        <div className="trace-toolbar">
          <div className="run-state"><span className="dot" />{active ? labels[active.status] : "暂无活动运行"}</div>
          <div className="toolbar-right">
            <button className="stop-toggle" type="button" data-testid="chat-stop-current" disabled={busy || !active || ["unknown", "stopping"].includes(active.status)} onClick={() => setConfirmStop(active?.id || null)}><Square size={12} />停止当前运行</button>
            <label className="round-select"><span className="lbl">执行轮次</span><select data-testid="chat-turn-select" disabled={!turns.length} value={selected} onChange={event => { setEventAfter(0); setSelected(event.target.value); }}>{turns.length ? turns.map(turn => <option key={turn.id} value={turn.id}>{labels[turn.status] || turn.status} · {new Date(turn.created_at).toLocaleString()}</option>) : <option value="">暂无执行轮次</option>}</select><ChevronDown size={15} /></label>
          </div>
        </div>
        {selectedTurn && ["failed", "stopped"].includes(selectedTurn.status) && <div className="chat-run-control"><span>重试将复用原轮次的引用快照</span><button data-testid="chat-retry" disabled={!executionReady || !!active || busy} onClick={() => void retryTurn()}>重试原轮次</button></div>}
        <div className="trace-status">
          {selectedTurn && <p className="line1" data-testid="chat-turn-status">所选轮次当前状态：<b>{labels[selectedTurn.status] || selectedTurn.status}</b></p>}
          {events.length ? <p className="line2">当前窗口 {events.length} 条已读取事件（每窗口最多 1000 条），连续文字已合并；历史状态不代表当前状态。</p> : <p className="line2">暂无已持久化事件。</p>}
        </div>
        {events.length ? <>
          <div className="chat-event-pages">{eventAfter > 0 && <button onClick={() => setEventAfter(0)}>从头查看轨迹</button>}{moreEvents && <button onClick={() => setEventAfter(events[events.length - 1]?.sequence || 0)}>读取后续事件</button>}</div>
          <TrajectoryView key={selected} events={events} withinTraceWrap />
        </> : <p>暂无已持久化事件。</p>}
        <section className="section-block" data-testid="chat-context-snapshots"><h3 className="section-title">本轮引用快照</h3>{!context.length ? <p>此轮没有引用快照。</p> : context.map(item => <details className="disclosure" key={item.object_id}><summary className="disclosure-header"><span className="ref-id">{item.object_id}</span> · {item.title}</summary><div className="disclosure-body snapshot-detail"><div className="row"><span className="k">版本</span><span className="v">{item.version.slice(0, 12)}</span></div>{item.truncated && <div className="row"><span className="k">截断</span><span className="v">原文超过上下文边界，本轮使用截断快照。</span></div>}<pre>{item.content}</pre></div></details>)}</section>
        <DiffView key={selected} diff={diff} />
      </div>
    </section>
    {confirmStop && <ChatDialog title="停止当前运行" testId="chat-stop-confirm" busy={busy} onClose={() => setConfirmStop(null)} footer={<><button disabled={busy} data-testid="chat-modal-cancel" onClick={() => setConfirmStop(null)}>取消</button><button disabled={busy || !active || active.id !== confirmStop || ["stopping", "unknown"].includes(active.status)} data-testid="chat-modal-submit" onClick={() => void stop()}>确认停止</button></>}><p>将向当前活动运行发送停止请求。已产生的代码变更会保留；收到执行端确认后才解除运行锁。</p>{error && <p role="alert">{error}</p>}</ChatDialog>}
  </>;
}

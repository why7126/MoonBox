import { useMemo, useState } from "react";
import { Search } from "lucide-react";
import type { ChatEvent } from "./chatEvents";
import { groupChatEvents } from "./eventGroups";
export type TraceNode = { id: string; sequence: number; endSequence: number; type: string; payload: Record<string, unknown> };
export function traceNodes(events: ChatEvent[]): TraceNode[] {
  const rows: TraceNode[] = [], tools = new Map<string, TraceNode>();
  for (const event of groupChatEvents(events)) {
    const p = event.payload as Record<string, unknown>;
    const key = p.item_id ? `${p.executor_turn_id || ""}:${p.item_id}` : "";
    const previous = event.type === "execution.tool" && key ? tools.get(key) : undefined;
    if (previous) { previous.payload = { ...previous.payload, ...p }; previous.endSequence = event.endSequence; }
    else { const node = { ...event, id: String(event.sequence), payload: p }; rows.push(node); if (event.type === "execution.tool" && key) tools.set(key, node); }
  }
  return rows;
}
const stateLabels: Record<string,string> = { queued:"排队中", connecting:"连接中", running:"执行中", stopping:"停止中", unknown:"状态未知", completed:"已完成", failed:"失败", stopped:"已停止", inProgress:"执行中", declined:"已拒绝" };
export function traceText(node: TraceNode) {
  const p = node.payload;
  if (node.type === "execution.output") return String(p.text || "");
  if (node.type === "execution.state") return `历史状态：${stateLabels[String(p.status)] || "待确认"}`;
  if (node.type === "execution.usage") return `已记录 Token：${p.total_tokens ?? "未采集"}`;
  return `${p.tool_name || (p.type === "fileChange" ? "文件变更" : "命令执行")} · ${stateLabels[String(p.status)] || (p.phase === "completed" ? "已结束" : "已开始")}`;
}
const kind = (type: string) => type === "execution.tool" ? "工具" : type === "execution.output" ? "助手" : type === "execution.usage" ? "用量" : "状态";
const traceTone = (node: TraceNode) => {
  if (node.type === "execution.usage") return "usage";
  if (node.type === "execution.output") return "assistant";
  if (node.type === "execution.tool") return node.payload.status === "failed" ? "tool-err" : "tool-ok";
  return "status";
};
const formatDuration = (value: unknown) => typeof value === "number" ? `${value} ms` : "";
function RawEvents({ nodes }: { nodes: TraceNode[] }) {
  return <details className="disclosure" data-testid="chat-raw-events">
    <summary className="disclosure-header">查看原始事件（{nodes.length} 条）</summary>
    <pre className="raw-events-box">{nodes.map(node => JSON.stringify({ sequence: node.sequence, endSequence: node.endSequence, type: node.type, payload: node.payload }, null, 2)).join("\n")}</pre>
  </details>;
}
export function TrajectoryView({ events, withinTraceWrap = false }: { events: ChatEvent[]; withinTraceWrap?: boolean }) {
  const nodes = useMemo(() => traceNodes(events), [events]);
  const [detailWidth,setDetailWidth] = useState(45);
  const [search, setSearch] = useState(""), [selected, setSelected] = useState<string | null>(null), [tab, setTab] = useState("概述"), [compact, setCompact] = useState(false), [timed, setTimed] = useState(false);
  const visible = nodes.filter(n => `${traceText(n)} ${JSON.stringify(n.payload)}`.toLowerCase().includes(search.toLowerCase()));
  const node = nodes.find(n => n.id === selected);
  const select = (id: string) => { setSelected(id); setTab("概述"); };
  const body = <>
    <div className="trace-card">
      <div className="trace-controls chat-trajectory-toolbar" role="toolbar" aria-label="轨迹工具栏">
      <div className="trace-controls-left">
        <button className={`ghost-btn ${compact ? "on" : ""}`} aria-pressed={compact} onClick={() => setCompact(!compact)}>{compact ? "展开内容" : "收起内容"}</button>
        <button className={`ghost-btn ${timed ? "on" : ""}`} aria-pressed={timed} onClick={() => setTimed(!timed)}>{timed ? "实际耗时" : "事件顺序"}</button>
      </div>
      <label className="trace-search"><Search size={13} aria-hidden="true" /><input aria-label="搜索轨迹" placeholder="搜索轨迹" value={search} onChange={e => setSearch(e.target.value)} /></label>
      </div>
      <div className="chat-timeline-overview scrub" aria-label="轨迹概览">{visible.map(n => <button key={n.id} title={`${kind(n.type)} · ${traceText(n).slice(0,80)}`} aria-label={`定位事件 ${n.sequence}`} className={`trace-${kind(n.type)} ${traceTone(n)}`} style={{ flexGrow: timed && typeof n.payload.duration_ms === "number" ? Math.max(1,Math.log1p(n.payload.duration_ms)) : 1 }} onClick={() => select(n.id)} />)}</div>
      {timed && <small className="trace-hint">宽度按已采集耗时对数缩放；未采集事件等宽，不代表请求耗时。</small>}
      <div className="chat-event-timeline event-list" role="list" aria-label="轨迹事件">
        {!visible.length && <p>没有匹配的轨迹。</p>}
        {visible.map(n => <article role="listitem" className={`chat-event-group chat-trajectory-row event-row ${selected === n.id ? "is-selected" : ""}`} key={n.id}>
          <button className={`chat-trace-select ev-tag ${traceTone(n)}`} aria-label={`查看事件 ${n.sequence} 详情`} onClick={() => select(n.id)}><span className="dot" /><small>{kind(n.type)} · {n.sequence}{n.endSequence !== n.sequence ? `–${n.endSequence}` : ""}</small></button>
          <pre className={`ev-content ${compact ? "is-compact" : ""}`}>{traceText(n)}</pre>
          <small className="ev-meta">{formatDuration(n.payload.duration_ms)}</small>
        </article>)}
      </div>
      <RawEvents nodes={nodes} />
    </div>
    {node && <div className="chat-trajectory-split has-detail">
      <aside className="chat-event-detail" aria-label="事件详情" style={{width:`${detailWidth}%`}}><input className="chat-detail-resize" type="range" min="30" max="65" aria-label="调整事件详情宽度" value={detailWidth} onChange={e=>setDetailWidth(Number(e.target.value))}/>
        <header><strong>{kind(node.type)} · 事件 {node.sequence}</strong><button aria-label="关闭事件详情" onClick={() => setSelected(null)}>×</button></header>
        <div role="tablist" aria-label="事件详情标签">{["概述","参数","结果","Schema","计时"].map(name => <button key={name} role="tab" aria-selected={tab===name} onClick={() => setTab(name)}>{name}</button>)}</div>
        <div role="tabpanel" aria-label={tab}>
          {tab === "概述" && <><p>{traceText(node)}</p><p>记录范围：{node.sequence}–{node.endSequence}</p>{node.type === "execution.tool" && !node.payload.detail_version && <p>历史记录未采集工具详情。</p>}{node.payload.truncated === true && <p role="status">内容过长，已截断；这里不是完整执行输出。</p>}</>}
          {tab === "参数" && <pre>{node.payload.arguments ? JSON.stringify(node.payload.arguments,null,2) : "未采集参数"}</pre>}
          {tab === "结果" && <><pre>{node.payload.result !== undefined ? String(node.payload.result) : node.type === "execution.output" ? String(node.payload.text || "") : "未采集输出；文件差异请查看本轮 Diff"}</pre>{node.payload.exit_code !== undefined && <p>退出码：{String(node.payload.exit_code)}</p>}</>}
          {tab === "Schema" && <p>当前执行接口未采集工具 Schema。</p>}
          {tab === "计时" && <><p>记录时间：{typeof node.payload.recorded_at_ms === "number" ? new Date(node.payload.recorded_at_ms).toLocaleString() : "未采集"}</p><p>耗时：{typeof node.payload.duration_ms === "number" ? `${node.payload.duration_ms} ms` : "未采集"}</p><p>来源：{node.payload.timing_source === "executor" ? "执行端" : node.payload.timing_source === "worker_observed" ? "Worker 观测（含传输延迟）" : "未采集"}</p></>}
        </div>
      </aside>
    </div>
    }
  </>;
  return withinTraceWrap ? body : <div className="chat-trajectory trace-wrap">{body}</div>;
}

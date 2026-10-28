import { useEffect, useRef, useState } from "react";
import { ChatDialog } from "./ChatDialog";
import { chatRequest, ChatApiError, normalizeChatError } from "./chatApi";
import type { ResultPageRead } from "../../api/generated/chat";

/** One response page in memory. Cursor history contains no reply text. */
export function FullOutput({turnId, preferFinal, onClose}: {turnId: string; preferFinal: boolean; onClose: () => void}) {
  const [stream, setStream] = useState(preferFinal ? "final" : "output");
  const [cursors, setCursors] = useState<(string | null)[]>([null]);
  const [index, setIndex] = useState(0), [retry, setRetry] = useState(0);
  const [page, setPage] = useState<ResultPageRead | null>(null);
  const [busy, setBusy] = useState(true), [error, setError] = useState("");
  const [invalidCursor, setInvalidCursor] = useState(false);
  const generation = useRef(0);
  useEffect(() => {
    generation.current++; setStream(preferFinal ? "final" : "output");
    setCursors([null]); setIndex(0); setPage(null);
  }, [turnId, preferFinal]);
  const cursor = cursors[index] ?? null;
  useEffect(() => {
    const controller = new AbortController(), id = ++generation.current;
    setBusy(true); setError(""); setInvalidCursor(false);
    const query = new URLSearchParams({stream_id: stream}); if(cursor) query.set("cursor", cursor);
    void chatRequest<ResultPageRead>(`/turns/${turnId}/results?${query}`, {signal: controller.signal}).then(value => {
      if(controller.signal.aborted || id !== generation.current) return;
      if(stream === "output" && value.has_final) {
        setPage(null); setCursors([null]); setIndex(0); setStream("final"); return;
      }
      setPage(value);
    }).catch(cause => {
      if(controller.signal.aborted || id !== generation.current) return;
      setInvalidCursor(cause instanceof ChatApiError && cause.status === 422);
      if(cause instanceof ChatApiError && [401,403,404].includes(cause.status)) setPage(null);
      const normalized = normalizeChatError(cause, "输出暂时无法读取，请重试");
      setError(normalized instanceof Error ? normalized.message : "输出暂时无法读取，请重试");
    }).finally(() => {if(!controller.signal.aborted && id === generation.current) setBusy(false);});
    return () => {controller.abort();};
  }, [turnId, stream, cursor, retry]);
  function restart() {setPage(null); setCursors([null]); setIndex(0); setRetry(v=>v+1);}
  return <ChatDialog title="完整输出" testId="turn-full-output" onClose={onClose} footer={<>
    <button type="button" data-testid="output-prev-page" disabled={busy || index === 0 || !!error} onClick={()=>setIndex(i=>i-1)}>上一页</button>
    <button type="button" data-testid="output-next-page" disabled={busy || !page?.next_cursor || !!error} onClick={()=>{setCursors(old=>[...old.slice(0,index+1),page!.next_cursor!]);setIndex(i=>i+1);}}>下一页</button>
    <button type="button" disabled={busy} onClick={restart}>重新读取</button>
  </>}>
    <p role="status">{busy ? "正在读取…" : `${stream === "final" ? "最终答复" : "执行输出"} · 第 ${index+1} 页`}</p>
    {error && <div role="alert"><p>{error}</p><button type="button" onClick={()=>invalidCursor ? restart() : setRetry(v=>v+1)}>{invalidCursor ? "返回首页读取最新输出" : "重试"}</button></div>}
    {page && <pre className="chat-full-output-text" data-testid="output-page-text">{page.items.map(item=>item.text).join("") || "暂无已保存文字"}</pre>}
    {!busy && !error && page && !page.next_cursor && <p>已到当前保存内容末尾{page.completeness === "complete" ? "。" : "，执行结果仍以本轮状态为准。"}</p>}
  </ChatDialog>;
}

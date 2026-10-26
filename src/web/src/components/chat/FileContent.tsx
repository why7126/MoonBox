import { useEffect, useRef, useState } from "react";
import { chatRequest } from "./chatApi";
type ContentPage = { status: string; text: string | null; next_cursor: string | null };
type BlockPage = { status: string; items: { block: number; before_bytes: number; after_bytes: number }[]; next_cursor: string | null };
export function FileContent({ turnId, fileId, beforeFileId, scope }: { turnId: string; fileId: string; beforeFileId?: string; scope: string }) {
  const [side, setSide] = useState("after"), [page, setPage] = useState<ContentPage | null>(null);
  const [busy, setBusy] = useState(false), [error, setError] = useState("");
  const [blocks, setBlocks] = useState<BlockPage | null>(null);
  const controller = useRef<AbortController | null>(null);
  useEffect(() => { controller.current?.abort(); setPage(null); setBlocks(null); setBusy(false); setError(""); return () => controller.current?.abort(); }, [turnId, fileId, side, scope, beforeFileId]);
  async function compare(cursor?: string) {
    controller.current?.abort(); const current = new AbortController(); controller.current = current;
    setBusy(true); setError("");
    const query = new URLSearchParams({ scope });
    if (beforeFileId) query.set("before_file_id", beforeFileId);
    if (cursor) query.set("cursor", cursor);
    try {
      const result = await chatRequest<BlockPage>(`/turns/${turnId}/files/${fileId}/blocks?${query}`, { signal: current.signal });
      if (!current.signal.aborted) setBlocks(result);
    } catch (cause) { if (!current.signal.aborted) setError(cause instanceof Error ? cause.message : "比较失败"); }
    finally { if (!current.signal.aborted) setBusy(false); }
  }
  async function read(cursor?: string) {
    controller.current?.abort(); const current = new AbortController(); controller.current = current;
    setBusy(true); setError("");
    try {
      const query = new URLSearchParams({ side, scope }); if (cursor) query.set("cursor", cursor);
      const result = await chatRequest<ContentPage>(`/turns/${turnId}/files/${side === "before" ? beforeFileId || fileId : fileId}/content?${query}`, { signal: current.signal });
      if (!current.signal.aborted) setPage(result);
    } catch (cause) { if (!current.signal.aborted) setError(cause instanceof Error ? cause.message : "读取失败"); }
    finally { if (!current.signal.aborted) setBusy(false); }
  }
  return <div className="chat-file-content" data-testid="chat-file-content" data-file-id={fileId}><label>快照内容 <select aria-label="快照内容" value={side} onChange={event => setSide(event.target.value)}><option value="after">执行后</option><option value="before">执行前</option></select></label>
    <button data-testid="chat-file-read" disabled={busy} onClick={() => void read()}>读取文件内容</button>
    <button data-testid="chat-file-compare" disabled={busy} onClick={() => void compare()}>比较内容块</button>
    {blocks && <div><p>{blocks.status === "legacy_unavailable" ? "历史正文缺失，无法比较内容块。" : "按保存块精确比较；块编号从 1 开始，不代表行号。"}</p>
      {blocks.items.map(item => <p key={item.block}>第 {item.block + 1} 块有变化：{item.before_bytes} → {item.after_bytes} 字节</p>)}
      {blocks.status === "compared" && !blocks.items.length && <p>当前窗口内容块相同，文件属性仍可能不同。</p>}
      {blocks.next_cursor && <button disabled={busy} onClick={() => void compare(blocks.next_cursor!)}>比较下一页内容块</button>}
    </div>}
    {error && <p role="alert">{error}</p>}
    {page?.text !== null && page?.text !== undefined && <pre>{page.text}</pre>}
    {page && page.status !== "available" && <p>{page.status === "binary" ? "二进制内容，仅展示元数据。" : page.status === "legacy_unavailable" ? "历史版本未保存全文。" : "此快照侧没有可读取的正文。"}</p>}
    {page?.next_cursor && <button disabled={busy} onClick={() => void read(page.next_cursor!)}>读取下一段</button>}
  </div>;
}

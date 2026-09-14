import { useEffect, useRef, useState } from "react";
import { chatRequest, listSessions, patchSession, type Capabilities, type ConversationRead, type Space, type TurnRead } from "./chatApi";

export function useChatWorkbench() {
  const [spaces, setSpaces] = useState<Space[]>([]), [space, setSpace] = useState("");
  const [capabilitySpace, setCapabilitySpace] = useState("");
  const [capabilities, setCapabilities] = useState<Capabilities | null>(null);
  const [sessions, setSessions] = useState<ConversationRead[]>([]), [selected, setSelected] = useState<ConversationRead | null>(null);
  const [turns, setTurns] = useState<TurnRead[]>([]);
  const [query, setQuery] = useState(""), [archived, setArchived] = useState<boolean | "all" | "pinned">(false), [page, setPage] = useState(1), [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true), [busy, setBusy] = useState(false), [error, setError] = useState(""), [toast, setToast] = useState("");
  const [refresh, setRefresh] = useState(0), [boot, setBoot] = useState(0);
  const [sending, setSending] = useState(false);
  const mutation = useRef(false), scope = useRef(space); scope.current = space;
  useEffect(() => {
    const controller = new AbortController(); setLoading(true); setError("");
    chatRequest<Space[]>("/spaces", { signal: controller.signal }).then(rows => {
      if (controller.signal.aborted) return;
      const hint = new URLSearchParams(window.location.search).get("space_id");
      let storedId = "";
      try { storedId = JSON.parse(window.localStorage.getItem("moonbox.workspace") || "null")?.workspaceId || ""; } catch { /* 忽略无效偏好，使用授权目录。 */ }
      setSpaces(rows); setSpace(rows.find(row => row.id === hint)?.id || rows.find(row => row.id === storedId)?.id || rows[0]?.id || ""); setLoading(false);
    }).catch(e => { if (!controller.signal.aborted) { setError(e.message); setLoading(false); } });
    return () => controller.abort();
  }, [boot]);
  useEffect(() => {
    if (!space) return;
    const controller = new AbortController(); setCapabilities(null); setSelected(null); setSessions([]); setTurns([]); setError("");
    chatRequest<Capabilities>(`/capabilities?space_id=${encodeURIComponent(space)}`, { signal: controller.signal }).then(data => {
      if (!controller.signal.aborted) { setCapabilities(data); setCapabilitySpace(space); }
    }).catch(e => { if (!controller.signal.aborted) setError(e.message); });
    return () => controller.abort();
  }, [space, boot]);
  useEffect(() => {
    if (!space) { setSessions([]); return; }
    const controller = new AbortController(); setLoading(true);
    const timer = setTimeout(() => {
      listSessions(space, query, archived, page, controller.signal).then(data => {
        if (controller.signal.aborted) return;
        setSessions(data.items); setTotal(data.total); setLoading(false);
      }).catch(e => { if (!controller.signal.aborted) { setError(e.message); setLoading(false); setSessions([]); } });
    }, 150);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [space, query, archived, page, refresh, boot]);
  useEffect(() => {
    if (!space) return;
    const cid = new URLSearchParams(window.location.search).get("conversation_id");
    if (!cid || !/^[A-Za-z0-9_-]{1,64}$/.test(cid)) return;
    const controller = new AbortController();
    chatRequest<ConversationRead>(`/conversations/${encodeURIComponent(cid)}`, { signal: controller.signal }).then(row => {
      if (!controller.signal.aborted && row.space_id === space) setSelected(row);
    }).catch(() => { /* 不信任地址栏标识；无权或已删除会话不恢复。 */ });
    return () => controller.abort();
  }, [space, boot]);
  useEffect(() => {
    if (!selected) return;
    const url = new URL(window.location.href);
    url.searchParams.set("conversation_id", selected.id);
    url.searchParams.set("space_id", selected.space_id);
    window.history.replaceState(null, "", url.pathname + url.search + url.hash);
  }, [selected?.id, selected?.space_id]);
  useEffect(() => {
    if (!selected?.active_turn_id) return;
    const controller = new AbortController(); let timer: ReturnType<typeof setTimeout>;
    const cid = selected.id;
    const poll = async () => {
      try {
        const row = await chatRequest<ConversationRead>(`/conversations/${cid}`, { signal: controller.signal });
        if (controller.signal.aborted) return;
        setSelected(current => current?.id === cid ? row : current);
        if (row.active_turn_id) timer = setTimeout(poll, 1500);
      } catch { if (!controller.signal.aborted) timer = setTimeout(poll, 3000); }
    };
    timer = setTimeout(poll, 1500);
    return () => { controller.abort(); clearTimeout(timer); };
  }, [selected?.id, selected?.active_turn_id]);
  useEffect(() => {
    if (!selected) { setTurns([]); return; }
    const controller = new AbortController();
    chatRequest<{ items: TurnRead[] }>(`/conversations/${selected.id}/turns`, { signal: controller.signal }).then(data => {
      if (!controller.signal.aborted) setTurns(data.items);
    }).catch(e => { if (!controller.signal.aborted) { setTurns([]); setError(e.message); } });
    return () => controller.abort();
  }, [selected?.id, refresh]);
  useEffect(() => { if (!toast) return; const timer = setTimeout(() => setToast(""), 3500); return () => clearTimeout(timer); }, [toast]);
  async function mutate(action: () => Promise<unknown>, success: string) {
    if (mutation.current) return false;
    mutation.current = true; setBusy(true); setError("");
    try { await action(); setRefresh(x => x + 1); setToast(success); return true; }
    catch (e) { setError(e instanceof Error ? e.message : "操作失败"); return false; }
    finally { mutation.current = false; setBusy(false); }
  }
  const create = (repository: string) => mutate(async () => {
    const original = space;
    const row = await chatRequest<ConversationRead>("/conversations", { method: "POST", body: JSON.stringify({ space_id: space, repository_id: repository, title: "新会话" }) });
    if (scope.current === original) { setSelected(row); setArchived(false); setQuery(""); setPage(1); }
  }, "会话已创建");
  const patch = (row: ConversationRead, data: { title?: string; archived?: boolean; pinned?: boolean }) => mutate(async () => {
    const updated = await patchSession(row.id, data);
    setSelected(current => current?.id === row.id ? updated : current);
  }, "会话已更新");
  const remove = (row: ConversationRead, workspaceHash?: string | null) => mutate(async () => {
    await chatRequest(`/conversations/${row.id}${workspaceHash ? `?expected_hash=${encodeURIComponent(workspaceHash)}` : ""}`, { method: "DELETE" });
    setSelected(current => current?.id === row.id ? null : current);
  }, "会话已删除");
  const refreshSelected = () => {
    setRefresh(value => value + 1);
    if (selected) chatRequest<ConversationRead>(`/conversations/${selected.id}`).then(row => setSelected(current => current?.id === row.id ? row : current)).catch(e => setError(e.message));
  };
  return { notify: setToast, refreshSelected, spaces, space, setSpace, capabilities: capabilitySpace === space ? capabilities : null, sessions, selected: selected?.space_id === space ? selected : null, setSelected, turns, query, setQuery, archived, setArchived, page, setPage, total, loading, busy: busy || sending, setSending, error, setError, toast, create, patch, remove, retry: () => setBoot(x => x + 1) };
}

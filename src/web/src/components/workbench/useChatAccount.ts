import { useCallback, useEffect, useState } from "react";
import { readFrontendSession } from "../../pages/home/frontendSession";
import { emptyWorkspace, fallbackUserFromSession, normalizeWorkbenchContext, readAccessToken, type WorkbenchContext } from "./workbenchAccount";

/** 复用需求中心的授权账号/空间目录；执行授权仍以 Chat API 为准。 */
export function useChatAccount() {
  const [context, setContext] = useState<WorkbenchContext>({ currentUser: fallbackUserFromSession(), workspaces: [], selectedWorkspaceId: "" });
  const [loading, setLoading] = useState(true), [error, setError] = useState("");
  const [refresh, setRefresh] = useState(0);
  useEffect(() => {
    const token = readAccessToken();
    if (!token) { setLoading(false); return; }
    const controller = new AbortController(); setLoading(true); setError("");
    void fetch("/api/v1/requirement-center/projects", { headers: { accept: "application/json", authorization: `Bearer ${token}` }, signal: controller.signal })
      .then(async response => {
        if (!response.ok) throw new Error("账号与空间信息暂不可用");
        const envelope = await response.json();
        if (!controller.signal.aborted) setContext(normalizeWorkbenchContext(envelope.data, readFrontendSession()?.username));
      }).catch(() => { if (!controller.signal.aborted) { setError("账号与空间信息暂不可用"); setContext({ currentUser: { ...fallbackUserFromSession(), canAccessAdmin: false }, workspaces: [], selectedWorkspaceId: "" }); } })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [refresh]);
  return { context, setContext, loading, error, refresh: useCallback(() => setRefresh(n => n + 1), []), emptyWorkspace };
}

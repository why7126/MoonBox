import "../../styles/project-governance.css";
export type ProjectState = "loading" | "connected" | "unbound" | "unavailable" | "readonly";
export function ProjectBinding({ name = "本地项目", state = "loading", sync = "正在读取项目连接", onRefresh }: { name?: string; state?: ProjectState; sync?: string; onRefresh?: () => void }) {
  const labels = { loading: "连接中", connected: "已连接", unbound: "未绑定", unavailable: "连接不可用", readonly: "只读" };
  return <section className="pg-binding" data-testid="project-binding" data-state={state} aria-label="项目连接">
    <div><strong>{name}</strong><span className="pg-badge">{labels[state]}</span></div>
    <div><span data-testid="project-sync-status" role="status">{sync}</span><button type="button" data-testid="project-sync-refresh" disabled={!onRefresh || state === "loading"} onClick={onRefresh}>刷新</button></div>
  </section>;
}

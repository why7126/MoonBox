import { governanceRequest, type Project } from "../../components/workbench/governanceApi";
import { GovernanceResult, type GovernanceCandidate } from "../../components/chat/GovernanceResult";
import { History,Pencil,MessageCircle,PanelRight,Plus,Terminal,X } from "lucide-react";
import { useEffect,useRef,useState } from "react";
import { ChatStatus } from "../../components/chat/ChatStatus";
import { Composer, type DraftState } from "../../components/chat/Composer";
import { ConversationMessages } from "../../components/chat/ConversationMessages";
import { ExecutionPanel } from "../../components/chat/ExecutionPanel";
import { RelationsBar } from "../../components/chat/RelationsBar";
import { SessionDialogs,type SessionDialog } from "../../components/chat/SessionDialogs";
import { useChatWorkbench } from "../../components/chat/useChatWorkbench";
import { WorkbenchSidebar } from "../../components/workbench/WorkbenchSidebar";
import { useChatAccount } from "../../components/workbench/useChatAccount";
import { useWorkbenchTheme } from "../../components/workbench/useWorkbenchTheme";
import type { Workspace } from "../../components/workbench/workbenchAccount";
import "../../styles/chat-workbench.css";

/** 会话来自鉴权API；执行按钮遵循服务端能力门禁。 */
export function ChatWorkbenchPage({ skeletonCandidate }: { skeletonCandidate?: GovernanceCandidate } = {}) {
  const model = useChatWorkbench();
  const [project, setProject] = useState<Project | null>(null);
  const [candidate, setCandidate] = useState<GovernanceCandidate | undefined>();
  const [governanceError, setGovernanceError] = useState("");
  const [bindingRefresh, setBindingRefresh] = useState(0);
  useEffect(() => {
    setProject(null); setCandidate(undefined); setGovernanceError("");
    if (!model.space) return;
    const controller = new AbortController(); let timer: ReturnType<typeof setTimeout>;
    const poll = async () => {
      if (!document.hidden) try {
        const data = await governanceRequest<{ projects: Project[] }>("/api/v1/requirement-center/projects", { signal: controller.signal });
        if (controller.signal.aborted) return;
        setProject(data.projects.find(p => p.space_id === model.space && (!model.selected || p.repository_id === model.selected.repository_id)) || null);
        if (model.selected) {
          const result = await governanceRequest<{ items: GovernanceCandidate[] }>(`/api/v1/chat/conversations/${model.selected.id}/governance-candidates`, { signal: controller.signal });
          if (controller.signal.aborted) return;
          setCandidate(result.items[0]);
        }
        setGovernanceError("");
      } catch (e) { if (!controller.signal.aborted) { setProject(null); setCandidate(undefined); setGovernanceError(e instanceof Error ? e.message : "项目连接暂不可用"); } }
      if (!controller.signal.aborted) timer = setTimeout(poll, 3000);
    };
    void poll(); return () => { controller.abort(); clearTimeout(timer); };
  }, [model.space, model.selected?.id, bindingRefresh]);
  const drafts = useRef<Record<string, DraftState>>({});
  const [draftVersion, setDraftVersion] = useState(0);
  const draftKey = model.selected?.id || `${model.space}:draft:${draftVersion}`;
  const draftState = drafts.current[draftKey] ||= { text: model.selected ? sessionStorage.getItem(`moonbox.governance.prompt:${model.selected.id}`) || "" : "" };
  const [focusVersion, setFocusVersion] = useState(0);
  const [focusTurn, setFocusTurn] = useState("");
  const [dialog, setDialog] = useState<SessionDialog>(null);
  const [theme] = useWorkbenchTheme();
  const account = useChatAccount();
  const currentWorkspace = account.context.workspaces.find(item => item.workspaceId === model.space) || { ...account.emptyWorkspace, workspaceId: model.space, name: model.spaces.find(item => item.id === model.space)?.name || "暂无空间" };
  const selectWorkspace = (workspace: Workspace) => {
    if (model.busy || !model.spaces.some(item => item.id === workspace.workspaceId)) return;
    window.localStorage.setItem("moonbox.workspace", JSON.stringify(workspace));
    model.setSpace(workspace.workspaceId); model.setQuery(""); model.setPage(1);
  };
  const [panelOpen, setPanelOpen] = useState(false);
  return (
    <main className={`requirement-center theme-${theme} chat-shell ${panelOpen ? "chat-panel-open" : ""}`} data-theme={theme} data-testid="chat-shell">
      <WorkbenchSidebar activePage="chat" activeUser={account.context.currentUser} workspace={currentWorkspace} availableWorkspaces={account.context.workspaces.filter(item => model.spaces.some(space => space.id === item.workspaceId))} isLoadingContext={account.loading} contextError={account.error} spaceSwitchDisabled={model.busy} onWorkspaceChange={selectWorkspace} onUserChange={currentUser => account.setContext(current => ({ ...current, currentUser }))} onRefresh={account.refresh} />
      <section className="chat-main" aria-label="Chat 工作台">
        <div className="chat-session-bar">
          <button type="button" disabled={!model.selected || model.busy} onClick={() => { if (model.selected) setDialog({ kind: "rename", row: model.selected }); }} aria-label={model.selected ? "重命名当前会话" : "新会话"} data-testid="chat-title-edit"><MessageCircle size={16} /><strong>{model.selected?.title || "新会话"}</strong>{model.selected && <Pencil size={14} />}</button>
          <div><button type="button" disabled={!model.space || model.busy} onClick={() => setDialog({ kind: "history" })} aria-label="历史" data-testid="chat-history-trigger"><History size={15} /><span>历史</span></button><button type="button" disabled={!model.capabilities?.repositories.length || model.busy} onClick={() => { model.setSelected(null); setDraftVersion(value => value + 1); setPanelOpen(false); const url = new URL(window.location.href); url.searchParams.delete("conversation_id"); window.history.replaceState(null, "", url.pathname + url.search); }} aria-label="新建会话" data-testid="chat-new-session"><Plus size={15} /><span>新建会话</span></button><button className="chat-icon-button" type="button" data-testid="chat-panel-toggle" aria-label={panelOpen ? "收起执行详情" : "展开执行详情"} aria-expanded={panelOpen} aria-controls="chat-execution-panel" onClick={() => setPanelOpen(!panelOpen)}><PanelRight size={17} /></button></div>
        </div>
        <div className="chat-view-tabs" role="tablist" aria-label="会话视图"><button role="tab" aria-selected={!panelOpen} onClick={() => setPanelOpen(false)}>对话</button><button role="tab" aria-selected={panelOpen} onClick={() => setPanelOpen(true)}>轨迹</button></div>
        <RelationsBar projectStatus={<button className="pg-chat-project" data-testid="chat-project-status" title={governanceError || "与需求中心使用同一本地项目；点击刷新连接"} onClick={() => setBindingRefresh(n => n + 1)}>{project?.repository_id || "本地项目"} · {governanceError ? "连接不可用" : !model.space ? "连接中" : !project ? "未连接" : project.readonly ? "只读" : "已连接"}</button>} conversation={model.selected} onSaved={() => model.notify("关联已保存，将用于下一轮")} />
        <section hidden={panelOpen} className="chat-conversation" data-testid="chat-conversation" aria-label="会话内容">{model.error && !dialog ? <><p role="alert" className="chat-error">{model.error}</p><button onClick={model.retry}>重新连接</button></> : model.loading ? <ChatStatus availability="loading" /> : !model.spaces.length ? <div className="chat-status"><h2>暂无可用空间</h2><p>加入有效空间后即可管理个人会话。</p></div> : !model.selected ? <div className="chat-status"><h2>有什么需要帮忙？</h2><p>{model.capabilities?.reason || "直接输入内容，发送后自动开始会话。"}</p>{!model.capabilities?.repositories.length && <p>当前空间尚未配置仓库，请联系空间管理员。</p>}</div> : null}{model.selected && <ConversationMessages key={model.selected.id} conversationId={model.selected.id} onTrace={id => { setFocusTurn(id); setFocusVersion(value => value+1); setPanelOpen(true); }} />}</section>
      {<aside hidden={!panelOpen} className="chat-execution-panel" id="chat-execution-panel" data-testid="chat-execution-panel" aria-label="执行详情">
        <header><div><Terminal size={16} /><h2>轨迹</h2></div><button className="chat-icon-button" type="button" aria-label="关闭执行详情" onClick={() => setPanelOpen(false)}><X size={16} /></button></header>
        <ExecutionPanel key={model.selected?.id || "empty"} conversation={model.selected} executionReady={model.capabilities?.execution_ready} focusTurn={focusTurn} focusVersion={focusVersion} />
        <footer>仅展示实际执行产生的事件与文件变更</footer>
      </aside>}
        <GovernanceResult candidate={skeletonCandidate || candidate} previewOnly={Boolean(skeletonCandidate)} />
        <Composer spaceId={model.space} unavailableReason={model.error} key={draftKey} conversation={model.selected} capabilities={model.capabilities} draftState={draftState} initialDraft={draftState.text} onDraft={value => { draftState.text = value; }} onBusyChange={model.setSending} onCreated={model.setSelected} onSubmitted={() => { if (model.selected) sessionStorage.removeItem(`moonbox.governance.prompt:${model.selected.id}`); model.refreshSelected(); }} />
      </section>
      {dialog && <SessionDialogs key={dialog.kind + ("row" in dialog ? dialog.row.id : "")} model={model} dialog={dialog} setDialog={setDialog} />}
      {model.toast && <div className="chat-toast" data-testid="chat-toast" role="status">{model.toast}</div>}
    </main>
  );
}

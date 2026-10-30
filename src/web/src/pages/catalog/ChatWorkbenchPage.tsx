import { SprintArchiveDraft } from "../../components/chat/SprintArchiveDraft";
import { AcceptanceOperations } from "../../components/chat/AcceptanceOperations";
import { WorkspacePanel } from "../../components/workspaces/WorkspacePanel";
import { takeSprintArchiveIntent, sprintArchiveDraftDecision, type SprintArchiveIntent } from "./sprintArchiveIntent";
import "../../components/chat/sprint-archive-draft.css";
import { governanceRequest, type Project } from "../../components/workbench/governanceApi";
import { GovernanceResult, activeGovernanceCandidate, type GovernanceCandidate } from "../../components/chat/GovernanceResult";
import { History,Pencil,MessageCircle,PanelRight,Plus,Terminal,X } from "lucide-react";
import { useEffect,useRef,useState } from "react";
import { ChatStatus } from "../../components/chat/ChatStatus";
import { Composer, type DraftState } from "../../components/chat/Composer";
import { ReplacementReview } from "../../components/chat/ReplacementReview";
import { ConversationMessages } from "../../components/chat/ConversationMessages";
import { ExecutionPanel } from "../../components/chat/ExecutionPanel";
import { RelationsBar } from "../../components/chat/RelationsBar";
import { SessionDialogs,type SessionDialog } from "../../components/chat/SessionDialogs";
import { useChatWorkbench } from "../../components/chat/useChatWorkbench";
import { removeLegacyGovernancePanels } from "../../runtimeBuild";
import { WorkbenchSidebar } from "../../components/workbench/WorkbenchSidebar";
import { useChatAccount } from "../../components/workbench/useChatAccount";
import { useWorkbenchRootBackground } from "../../components/workbench/useWorkbenchRootBackground";
import { useWorkbenchTheme } from "../../components/workbench/useWorkbenchTheme";
import type { Workspace } from "../../components/workbench/workbenchAccount";
import "../../styles/chat-workbench.css";

/** 会话来自鉴权API；执行按钮遵循服务端能力门禁。 */
export function ChatWorkbenchPage({ skeletonCandidate }: { skeletonCandidate?: GovernanceCandidate } = {}) {
  const model = useChatWorkbench();
  const [project, setProject] = useState<Project | null>(null);
  const [candidates, setCandidates] = useState<GovernanceCandidate[]>([]);
  const [candidate, setCandidate] = useState<GovernanceCandidate | undefined>();
  const [rejectedGovernanceTurns, setRejectedGovernanceTurns] = useState<string[]>([]);
  const [governanceError, setGovernanceError] = useState("");
  const [bindingRefresh, setBindingRefresh] = useState(0);
  const [replacementOpenRequest, setReplacementOpenRequest] = useState(0);
  const [reviewChangeId, setReviewChangeId] = useState('');
  const [workspaceOpen, setWorkspaceOpen] = useState(false);
  useEffect(() => {
    setProject(null); setCandidate(undefined); setCandidates([]); setRejectedGovernanceTurns([]); setGovernanceError("");
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
          setCandidates(result.items); setCandidate(activeGovernanceCandidate(result.items));
          setRejectedGovernanceTurns(result.items.filter(item => item.state === "rejected").map(item => item.turn_id || item.prepared_turn_id || "").filter(Boolean));
        }
        setGovernanceError("");
      } catch (e) { if (!controller.signal.aborted) { setProject(null); setCandidate(undefined); setGovernanceError(e instanceof Error ? e.message : "项目连接暂不可用，请稍后重试"); } }
      if (!controller.signal.aborted) timer = setTimeout(poll, 3000);
    };
    void poll(); return () => { controller.abort(); clearTimeout(timer); };
  }, [model.space, model.selected?.id, bindingRefresh]);
  const drafts = useRef<Record<string, DraftState>>({});
  const [draftVersion, setDraftVersion] = useState(0);
  const [recoveryDraftVersion, setRecoveryDraftVersion] = useState(0);
  const draftKey = model.selected?.id || `${model.space}:draft:${draftVersion}`;
  const draftState = drafts.current[draftKey] ||= {
    text: model.selected ? sessionStorage.getItem(`moonbox.governance.prompt:${model.selected.id}`) || "" : "",
    hiddenPrompt: model.selected ? sessionStorage.getItem(`moonbox.governance.executionPrompt:${model.selected.id}`) || undefined : undefined,
  };
  const [archiveIntent, setArchiveIntent] = useState<SprintArchiveIntent | null>(null);
  const fillArchiveDraft = (intent: SprintArchiveIntent) => {
    if (model.selected?.id !== intent.conversationId || model.space !== intent.spaceId || model.selected.repository_id !== intent.repositoryId || model.selected.active_turn_id || model.selected.archived) return;
    draftState.text = `/sprint-archive ${intent.sprintId}`;
    draftState.hiddenPrompt = undefined;
    draftState.request = undefined;
    sessionStorage.setItem(`moonbox.governance.prompt:${intent.conversationId}`, draftState.text);
    sessionStorage.removeItem(`moonbox.governance.executionPrompt:${intent.conversationId}`);
    setRecoveryDraftVersion(v => v + 1);
    setArchiveIntent(null);
  };
  useEffect(() => {
    setArchiveIntent(previous => previous && previous.conversationId === model.selected?.id && previous.spaceId === model.space ? previous : null);
    if (!model.selected || model.selected.space_id !== model.space) return;
    const intent = takeSprintArchiveIntent(sessionStorage, model.selected);
    if (!intent) return;
    const decision = sprintArchiveDraftDecision(draftState.text, intent.sprintId);
    if (decision === 'conflict') setArchiveIntent(intent);
    else fillArchiveDraft(intent);
  }, [model.selected?.id, model.space]);
  const [focusVersion, setFocusVersion] = useState(0);
  const [focusTurn, setFocusTurn] = useState(new URLSearchParams(window.location.search).get("turn_id")||"");
  const [dialog, setDialog] = useState<SessionDialog>(null);
  const [theme] = useWorkbenchTheme();
  useWorkbenchRootBackground(theme);
  const account = useChatAccount();
  const blockingWorkbenchError = model.selected ? "" : model.error;
  const reviewRepository = model.selected?.repository_id || project?.repository_id || model.capabilities?.repositories[0]?.id;
  const currentWorkspace = account.context.workspaces.find(item => item.workspaceId === model.space) || { ...account.emptyWorkspace, workspaceId: model.space, name: model.spaces.find(item => item.id === model.space)?.name || "暂无空间" };
  const selectWorkspace = (workspace: Workspace) => {
    if (model.busy || !model.spaces.some(item => item.id === workspace.workspaceId)) return;
    window.localStorage.setItem("moonbox.workspace", JSON.stringify(workspace));
    model.setSpace(workspace.workspaceId); model.setQuery(""); model.setPage(1);
  };
  const [panelOpen, setPanelOpen] = useState(Boolean(new URLSearchParams(window.location.search).get("turn_id")));
  useEffect(() => {
    removeLegacyGovernancePanels();
  }, [model.selected?.id, candidate?.id, skeletonCandidate?.id]);
  return (
    <main className={`requirement-center theme-${theme} chat-shell ${panelOpen ? "chat-panel-open" : ""}`} data-theme={theme} data-testid="chat-shell">
      <WorkbenchSidebar activePage="chat" activeUser={account.context.currentUser} workspace={currentWorkspace} availableWorkspaces={account.context.workspaces.filter(item => model.spaces.some(space => space.id === item.workspaceId))} isLoadingContext={account.loading} contextError={account.error} spaceSwitchDisabled={model.busy} onWorkspaceChange={selectWorkspace} onUserChange={currentUser => account.setContext(current => ({ ...current, currentUser }))} onRefresh={account.refresh} />
      <section className="chat-main" aria-label="Chat 工作台">
        <div className="chat-session-bar">
          <button type="button" disabled={!model.selected || model.busy} onClick={() => { if (model.selected) setDialog({ kind: "rename", row: model.selected }); }} aria-label={model.selected ? "重命名当前会话" : "新会话"} data-testid="chat-title-edit"><MessageCircle size={16} /><strong>{model.selected?.title || "新会话"}</strong>{model.selected && <Pencil size={14} />}</button>
          <div><button type="button" disabled={!model.space || model.busy} onClick={() => setDialog({ kind: "history" })} aria-label="历史" data-testid="chat-history-trigger"><History size={15} /><span>历史</span></button><button type="button" disabled={!model.capabilities?.repositories.length || model.busy} onClick={() => { model.setSelected(null); setDraftVersion(value => value + 1); setPanelOpen(false); const url = new URL(window.location.href); url.searchParams.delete("conversation_id"); window.history.replaceState(null, "", url.pathname + url.search); }} aria-label="新建会话" data-testid="chat-new-session"><Plus size={15} /><span>新建会话</span></button><button className="chat-icon-button" type="button" data-testid="chat-panel-toggle" aria-label={panelOpen ? "收起执行详情" : "展开执行详情"} aria-expanded={panelOpen} aria-controls="chat-execution-panel" onClick={() => setPanelOpen(!panelOpen)}><PanelRight size={17} /></button></div>
        </div>
        <div className="chat-subbar">
          <button type="button" data-testid="workspace-details-open" disabled={!model.space || !reviewRepository} onClick={() => setWorkspaceOpen(true)}>工作区</button>
          <div className="chat-view-tabs" role="tablist" aria-label="会话视图"><button role="tab" aria-selected={!panelOpen} onClick={() => setPanelOpen(false)}>对话</button><button role="tab" aria-selected={panelOpen} onClick={() => setPanelOpen(true)}>轨迹</button></div>
          <RelationsBar projectStatus={<button className="pg-chat-project" data-testid="chat-project-status" title={governanceError || "与需求中心使用同一本地项目；点击刷新连接"} onClick={() => setBindingRefresh(n => n + 1)}>{project?.repository_id || "本地项目"} · {governanceError ? "连接不可用" : !model.space ? "连接中" : !project ? "未连接" : project.readonly ? "只读" : "已连接"}</button>} conversation={model.selected} onSaved={() => { model.refreshSelected(); model.notify("关联已保存，写权限已刷新；已有运行保持原权限，下一轮使用最新范围"); }} />
        </div>
        <section hidden={panelOpen} className="chat-conversation" data-testid="chat-conversation" aria-label="会话内容">{blockingWorkbenchError && !dialog ? <><p role="alert" className="chat-error">{blockingWorkbenchError}</p><button onClick={model.retry}>重新连接</button></> : model.loading && !model.selected ? <ChatStatus availability="loading" /> : !model.spaces.length ? <div className="chat-status"><h2>暂无可用空间</h2><p>加入有效空间后即可管理个人会话。</p></div> : !model.selected ? <div className="chat-status"><h2>有什么需要帮忙？</h2><p>{model.capabilities?.reason || "直接输入内容，发送后自动开始会话。"}</p>{!model.capabilities?.repositories.length && <p>当前空间尚未配置仓库，请联系空间管理员。</p>}</div> : null}{model.selected && <ConversationMessages key={model.selected.id} conversationId={model.selected.id} candidates={candidates} draftText={draftState.text} onDraft={text => { draftState.text = text; draftState.hiddenPrompt = undefined; draftState.request = undefined; setRecoveryDraftVersion(v => v + 1); if (model.selected) sessionStorage.setItem(`moonbox.governance.prompt:${model.selected.id}`, text); model.notify('已填入评审草稿，请确认后发送'); model.refreshSelected(); }} rejectedGovernanceTurnIds={rejectedGovernanceTurns} onTrace={id => { setFocusTurn(id); setFocusVersion(value => value+1); setPanelOpen(true); }} />}{model.selected && <AcceptanceOperations key={`acceptance:${model.selected.id}`} conversationId={model.selected.id} />}</section>
      {<aside hidden={!panelOpen} className="chat-execution-panel" id="chat-execution-panel" data-testid="chat-execution-panel" aria-label="执行详情">
        <header><div><Terminal size={16} /><h2>轨迹</h2></div><button className="chat-icon-button" type="button" aria-label="关闭执行详情" onClick={() => setPanelOpen(false)}><X size={16} /></button></header>
        <ExecutionPanel key={model.selected?.id || "empty"} conversation={model.selected} executionReady={model.capabilities?.execution_ready} focusTurn={focusTurn} focusVersion={focusVersion} />
      </aside>}
        <GovernanceResult candidate={skeletonCandidate || candidate} previewOnly={Boolean(skeletonCandidate)} onApplied={model.refreshSelected} onNotice={model.notify} />
        {archiveIntent && archiveIntent.conversationId === model.selected?.id && archiveIntent.spaceId === model.space && <SprintArchiveDraft sprintId={archiveIntent.sprintId} disabled={Boolean(model.selected?.active_turn_id || model.selected?.archived || model.busy)} onKeep={() => setArchiveIntent(null)} onReplace={() => fillArchiveDraft(archiveIntent)} />}
        <Composer spaceId={model.space} unavailableReason={blockingWorkbenchError} key={`${draftKey}:${recoveryDraftVersion}`} conversation={model.selected} capabilities={model.capabilities} draftState={draftState} initialDraft={draftState.text} onDraft={value => { draftState.text = value; if (model.selected) { sessionStorage.setItem(`moonbox.governance.prompt:${model.selected.id}`, value); sessionStorage.removeItem(`moonbox.governance.executionPrompt:${model.selected.id}`); } }} onReviewReplacement={changeId => { setReviewChangeId(changeId); setReplacementOpenRequest(n => n + 1); }} onBusyChange={model.setSending} onCreated={model.setSelected} onSubmitted={() => { if (model.selected) { sessionStorage.removeItem(`moonbox.governance.prompt:${model.selected.id}`); sessionStorage.removeItem(`moonbox.governance.executionPrompt:${model.selected.id}`); } model.refreshSelected(); }} />
        {model.space && reviewRepository && reviewChangeId && <ReplacementReview key={`${model.space}:${reviewRepository}:${reviewChangeId}`} spaceId={model.space} repositoryId={reviewRepository} changeId={reviewChangeId} openRequest={replacementOpenRequest} />}
      </section>
      {dialog && <SessionDialogs key={dialog.kind + ("row" in dialog ? dialog.row.id : "")} model={model} dialog={dialog} setDialog={setDialog} />}
      {workspaceOpen && model.space && reviewRepository && <WorkspacePanel key={`${model.space}:${reviewRepository}`} spaceId={model.space} repositoryId={reviewRepository} conversationId={model.selected?.id} initialWorkspaceId={model.selected?.execution_workspace_id || undefined} onClose={() => setWorkspaceOpen(false)} />}
      {model.toast && <div className="chat-toast" data-testid="chat-toast" role="status">{model.toast}</div>}
    </main>
  );
}

import { useEffect, useRef, useState } from "react";
import type { ClipboardEvent, KeyboardEvent } from "react";
import { ChevronDown, FileText, Paperclip, Send, Sparkles, X } from "lucide-react";
import { chatRequest, uploadChatMaterial, type Capabilities, type ConversationRead, type ExecutionConfig, type ExecutionOption, type SkillCandidate, type TurnRead } from "./chatApi";
import { agentDisplayName, modelDisplayName, reasoningDisplayName } from "./executionLabels";

/** 内存草稿同时保留不确定请求的标识，切换历史后重试仍复用原请求。 */
type MaterialDraft = { id: string; ref_id?: string; kind: "image" | "file"; name: string; mime_type: string; size_bytes: number; status: "uploading" | "done" | "failed"; error?: string };
export type DraftState = { text: string; repository?: string; branch?: string; creationId?: string; conversation?: ConversationRead; images?: MaterialDraft[]; skills?: SkillCandidate[]; executionConfig?: ExecutionConfig; request?: { prompt: string; id: string; signature: string } };

const fallbackExecution: ExecutionConfig = { agent: "codex", model: "gpt-6-astra", reasoning: "high" };
const emptyOptions: ExecutionOption[] = [];
function executionDefaults(capabilities: Capabilities | null): ExecutionConfig {
  return capabilities?.execution?.defaults || fallbackExecution;
}
function executionOptionLabel(mode: "agent" | "model" | "reasoning", options: ExecutionOption[] | undefined, value: string) {
  if (mode === "agent") return agentDisplayName(value, options);
  if (mode === "model") return modelDisplayName(value, options);
  return reasoningDisplayName(value, options);
}
function availableOption(options: ExecutionOption[] | undefined, value: string) {
  const option = options?.find(item => item.value === value);
  return !!option?.available;
}
function skillDisplayName(value: string) {
  return value.split("-").filter(Boolean).map(part => part.charAt(0).toUpperCase() + part.slice(1)).join(" ") || value;
}
function skillSearchText(item: SkillCandidate) {
  return `${item.id} ${item.name} ${item.summary || ""}`.toLowerCase();
}
function writeScopeLabel(conversation: ConversationRead | null) {
  if (!conversation) return "";
  if (conversation.write_scope === "implementation_write") return "实现可写";
  if (conversation.write_scope === "governance_write") return "治理可写";
  return "完全只读";
}
function writeScopeReason(conversation: ConversationRead | null) {
  const code = conversation?.write_reason_code || "";
  const labels: Record<string, string> = {
    actor_not_writer: "当前账号在空间内不是所有者、管理员或编辑者，无法写入。",
    default_read_only: "当前会话未获得写入权限。",
    governance_candidate_forbidden: "治理候选对象权限校验失败，无法写入。",
    governance_candidate_invalid: "治理候选对象已失效，无法写入。",
    governance_candidate_running: "治理候选对象生成中，仅允许受控治理写入。",
    governance_facts_invalid: "主对象治理事实读取失败，无法确认可写范围。",
    governance_object_read_only: "主对象已归档、关闭或完成，无法继续写入。",
    governance_object_writable: "当前主对象允许治理文档写入；产品实现文件仍受 Sprint 和 Change 门禁限制。",
    implementation_change_in_sprint: "当前主对象已纳入 Sprint 与活动 Change，允许实现写入。",
    primary_object_required: "请先在管理关联中设置主对象；保存后刷新为下一轮可用的写权限。",
    space_forbidden: "当前账号无权访问该空间。",
  };
  return labels[code] || code || "写权限由主对象、空间角色和执行门禁自动判定。";
}
export function Composer({ conversation, capabilities, onSubmitted, initialDraft, onDraft, unavailableReason, draftState, onCreated, onBusyChange, spaceId }: { spaceId?: string; unavailableReason?: string; initialDraft: string; onDraft: (value: string) => void; conversation: ConversationRead | null; capabilities: Capabilities | null; onSubmitted: () => void; draftState?: DraftState; onCreated?: (row: ConversationRead) => void; onBusyChange?: (busy: boolean) => void }) {
  const fallback = useRef<DraftState>({ text: initialDraft });
  const attempt = draftState || fallback.current;
  const [draft, setDraft] = useState(attempt.text), [busy, setBusy] = useState(false), [error, setError] = useState("");
  const [materials, setMaterials] = useState<MaterialDraft[]>(attempt.images || []), [skills, setSkills] = useState<SkillCandidate[]>(attempt.skills || []);
  const [skillMenu, setSkillMenu] = useState(false), [skillRows, setSkillRows] = useState<SkillCandidate[]>([]), [skillLoading, setSkillLoading] = useState(false), [skillQuery, setSkillQuery] = useState("");
  const [skillMenuTrigger, setSkillMenuTrigger] = useState<"button" | "slash" | null>(null);
  const [activeSkillIndex, setActiveSkillIndex] = useState(0);
  const [configMenu, setConfigMenu] = useState<"model" | "reasoning" | null>(null);
  const [executionConfig, setExecutionConfig] = useState<ExecutionConfig>(attempt.executionConfig || executionDefaults(capabilities));
  const [chosen, setChosen] = useState(attempt.repository || ""), [branch, setBranch] = useState(attempt.branch || "");
  const input = useRef<HTMLSpanElement | null>(null), pending = useRef(false), composerRoot = useRef<HTMLDivElement>(null);
  const repositories = capabilities?.repositories || [];
  const repository = repositories.some(row => row.id === chosen) ? chosen : repositories[0]?.id || "";
  const repositoryRow = repositories.find(row => row.id === repository);
  const branchRows = repositoryRow?.branches?.items || [];
  const defaultBranch = repositoryRow?.branches?.default || branchRows.find(row => row.is_default)?.name || "main";
  const branchName = branchRows.some(row => row.name === branch) ? branch : defaultBranch;
  const disabled = !!conversation?.archived || !!conversation?.active_turn_id || !capabilities?.execution_ready || (!conversation && (!repository || !onCreated || !spaceId));
  const readyMaterials = materials.filter(item => item.status === "done");
  const hasUploading = materials.some(item => item.status === "uploading");
  const hasContent = !!draft.trim() || readyMaterials.length > 0;
  const hint = unavailableReason || (!capabilities?.execution_ready ? capabilities?.reason || "执行服务未就绪 · 可先编写草稿" : conversation?.archived ? "已归档 · 只读" : conversation?.active_turn_id ? "原运行尚未终止 · 可先编写草稿" : !conversation && !repository ? "请选择本次对话使用的仓库" : hasUploading ? "文件上传中，完成后可发送" : "");
  const scopeLabel = writeScopeLabel(conversation);
  useEffect(() => {
    const defaults = executionDefaults(capabilities);
    setExecutionConfig(current => {
      const next = availableOption(capabilities?.execution?.models, current.model) && availableOption(capabilities?.execution?.reasoning, current.reasoning) ? current : defaults;
      attempt.executionConfig = next;
      return next;
    });
  }, [capabilities?.execution?.policy_version]);
  useEffect(() => {
    const close = (event: MouseEvent) => {
      const target = event.target instanceof Element ? event.target : null;
      if (target?.closest(".chat-composer-popover,[data-testid='chat-skill-button'],[data-testid='chat-model-selector'],[data-testid='chat-reasoning-selector']")) return;
      closeAllPopovers();
    };
    const closeOnEscape = (event: globalThis.KeyboardEvent) => {
      if (event.key === "Escape") closeAllPopovers();
    };
    document.addEventListener("mousedown", close);
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.removeEventListener("mousedown", close);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, []);
  useEffect(() => {
    if (input.current && input.current.textContent !== draft) input.current.textContent = draft;
  }, [draft]);
  function remember(nextMaterials = materials, nextSkills = skills) { attempt.images = nextMaterials; attempt.skills = nextSkills; }
  function counts(nextMaterials = materials, nextSkills = skills) {
    return { image_count: nextMaterials.filter(item => item.status === "done" && item.kind === "image").length,
      file_count: nextMaterials.filter(item => item.status === "done" && item.kind === "file").length,
      skill_count: nextSkills.length };
  }
  function logMaterialEvent(event_name: "chat.image_add" | "chat.image_remove" | "chat.file_add" | "chat.file_remove" | "chat.skill_select" | "chat.skill_remove", nextMaterials = materials, nextSkills = skills) {
    void chatRequest("/behavior-events", { method: "POST", body: JSON.stringify({ event_name, ...counts(nextMaterials, nextSkills) }) }).catch(() => {});
  }
  function requestSignature() {
    return JSON.stringify({ prompt: draft, attachments: readyMaterials.map(({ ref_id, kind, name, mime_type, size_bytes }) => ({ ref_id, kind, name, mime_type, size_bytes })), skills: skills.map(({ id, digest }) => ({ id, digest })), execution_config: executionConfig });
  }
  function setMaterialDraft(next: MaterialDraft[]) { setMaterials(next); remember(next, skills); }
  function setSkillDraft(next: SkillCandidate[]) { setSkills(next); remember(materials, next); }
  function setExecution(partial: Partial<ExecutionConfig>) {
    const next = { ...executionConfig, ...partial };
    setExecutionConfig(next);
    attempt.executionConfig = next;
    setConfigMenu(null);
    void chatRequest("/behavior-events", { method: "POST", body: JSON.stringify({ event_name: "chat.config_select", ...counts(materials, skills), ...next }) }).catch(() => {});
  }
  function closeAllPopovers() {
    closeSkillMenu();
    setConfigMenu(null);
  }
  function focusPromptEnd() {
    const node = input.current;
    if (!node) return;
    node.focus();
    const range = document.createRange();
    range.selectNodeContents(node);
    range.collapse(false);
    const selection = window.getSelection();
    selection?.removeAllRanges();
    selection?.addRange(range);
  }
  function isPromptCaretAtStart() {
    const node = input.current, selection = window.getSelection();
    if (!node || !selection?.rangeCount || !selection.isCollapsed) return false;
    const range = selection.getRangeAt(0);
    if (!node.contains(range.startContainer)) return false;
    const before = document.createRange();
    before.selectNodeContents(node);
    before.setEnd(range.startContainer, range.startOffset);
    return before.toString().length === 0;
  }
  function removeSkill(id: string) {
    const next = skills.filter(row => row.id !== id);
    if (next.length === skills.length) return;
    setSkillDraft(next);
    logMaterialEvent("chat.skill_remove", materials, next);
    window.setTimeout(focusPromptEnd, 0);
  }
  function chooseExecution(mode: "model" | "reasoning", value: string) {
    setExecution(mode === "model" ? { model: value } : { reasoning: value });
  }
  async function addFiles(files: FileList | File[] | null) {
    const limits = capabilities?.materials;
    const repositoryId = conversation?.repository_id || repository;
    const targetSpace = conversation?.space_id || spaceId;
    if (!files || !limits || !targetSpace || !repositoryId) return;
    const accepted = limits.allowed_file_mime_types || limits.allowed_image_mime_types;
    const maxFiles = limits.max_files || limits.max_images;
    const maxFileBytes = limits.max_file_bytes || limits.max_image_bytes;
    const maxTotalBytes = limits.max_total_file_bytes || limits.max_total_image_bytes;
    let total = materials.filter(item => item.status === "done").reduce((sum, item) => sum + item.size_bytes, 0);
    const incoming = Array.from(files);
    const queued: MaterialDraft[] = [];
    let readyCount = materials.filter(item => item.status !== "failed").length;
    for (const file of incoming) {
      const kind = file.type.startsWith("image/") ? "image" : "file";
      const failed = readyCount >= maxFiles ? "文件数量超过限制" : !accepted.includes(file.type) ? "文件格式不受支持" : file.size > maxFileBytes ? "文件过大" : total + file.size > maxTotalBytes ? "文件总大小超过限制" : "";
      if (!failed) { total += file.size; readyCount += 1; }
      queued.push({ id: crypto.randomUUID(), kind, name: file.name, mime_type: file.type, size_bytes: file.size, status: failed ? "failed" : "uploading", error: failed || undefined });
    }
    const optimistic = [...materials, ...queued];
    setMaterialDraft(optimistic);
    for (let i = 0; i < incoming.length; i += 1) {
      const file = incoming[i], item = queued[i];
      if (item.status === "failed") continue;
      try {
        const uploaded = await uploadChatMaterial(targetSpace, repositoryId, file);
        let updatedMaterials: MaterialDraft[] = [];
        setMaterials(current => {
          const next = current.map(row => row.id === item.id ? { ...row, ...uploaded, id: item.id, status: "done" as const } : row);
          updatedMaterials = next;
          remember(next, skills);
          return next;
        });
        logMaterialEvent(uploaded.kind === "image" ? "chat.image_add" : "chat.file_add", updatedMaterials.length ? updatedMaterials : materials, skills);
      } catch (e) {
        setMaterials(current => {
          const next = current.map(row => row.id === item.id ? { ...row, status: "failed" as const, error: e instanceof Error ? e.message : "上传失败" } : row);
          remember(next, skills);
          return next;
        });
      }
    }
  }
  function closeSkillMenu() {
    setSkillMenu(false);
    setSkillMenuTrigger(null);
  }
  async function openSkillMenu(options: { forceOpen?: boolean; query?: string; trigger?: "button" | "slash" } = {}) {
    if (options.query !== undefined) setSkillQuery(options.query);
    if (options.trigger) setSkillMenuTrigger(options.trigger);
    setConfigMenu(null);
    setSkillMenu(value => options.forceOpen ? true : !value);
    if (skillRows.length || skillLoading || (!conversation && !repository)) return;
    setSkillLoading(true); setError("");
    try {
      const path = conversation ? `/conversations/${conversation.id}/skills` : `/skills?${new URLSearchParams({ space_id: spaceId || "", repository_id: repository })}`;
      const data = await chatRequest<{ items: SkillCandidate[] }>(path);
      setSkillRows(data.items);
    } catch (e) { setError(e instanceof Error ? e.message : "读取 Skill 候选失败"); }
    finally { setSkillLoading(false); }
  }
  async function send() {
    if (pending.current || disabled || hasUploading || !hasContent) return;
    const signature = requestSignature();
    if (!attempt.request || attempt.request.signature !== signature) attempt.request = { prompt: draft, id: crypto.randomUUID(), signature };
    pending.current = true; setBusy(true); onBusyChange?.(true); setError("");
    try {
      let target = conversation || attempt.conversation;
      if (!target) {
        attempt.creationId ||= crypto.randomUUID(); attempt.repository = repository; attempt.branch = branchName; setChosen(repository); setBranch(branchName);
        target = await chatRequest<ConversationRead>("/conversations", { method: "POST", body: JSON.stringify({ space_id: spaceId, repository_id: repository, branch_name: branchName, title: (draft.trim() || readyMaterials[0]?.name || "新会话").slice(0,80), client_request_id: attempt.creationId }) });
        attempt.conversation = target;
      }
      const turn = await chatRequest<TurnRead>(`/conversations/${target.id}/turns`, { method: "POST", body: JSON.stringify({ prompt: attempt.request.prompt, client_request_id: attempt.request.id,
        attachments: readyMaterials.map(item => ({ ref_id: item.ref_id, kind: item.kind, name: item.name, mime_type: item.mime_type, size_bytes: item.size_bytes })),
        skills: skills.map(item => ({ id: item.id, name: item.name, summary: item.summary, source: item.source, digest: item.digest })),
        execution_config: executionConfig }) });
      attempt.text = ""; attempt.request = undefined; attempt.creationId = undefined; attempt.conversation = undefined; attempt.images = []; attempt.skills = []; attempt.executionConfig = executionConfig;
      setDraft(""); setMaterials([]); setSkills([]); onDraft("");
      if (!conversation) onCreated?.({ ...target, active_turn_id: turn.id });
      onSubmitted();
    } catch (e) { setError(e instanceof Error ? e.message : "发送失败，草稿已保留"); }
    finally { pending.current = false; setBusy(false); onBusyChange?.(false); }
  }
  function selectSkill(item: SkillCandidate) {
    const next = [...skills, item];
    setSkillDraft(next);
    setDraft(current => {
      const updated = current.replace(/\/[A-Za-z0-9_-]*$/, "").trimStart();
      attempt.text = updated; onDraft(updated);
      return updated;
    });
    closeSkillMenu();
    setSkillQuery("");
    logMaterialEvent("chat.skill_select", materials, next);
    window.setTimeout(focusPromptEnd, 0);
  }
  function onPromptChange(value: string) {
    const nextValue = value.slice(0, 32000);
    setDraft(nextValue); attempt.text = nextValue; onDraft(nextValue);
    const match = nextValue.match(/\/([A-Za-z0-9_-]*)$/);
    if (match) void openSkillMenu({ forceOpen: true, query: match[1], trigger: "slash" });
    else {
      setSkillQuery("");
      if (skillMenuTrigger === "slash") closeSkillMenu();
    }
  }
  function onPaste(event: ClipboardEvent<HTMLElement>) {
    const files = Array.from(event.clipboardData.files || []);
    if (files.length) {
      event.preventDefault();
      void addFiles(files);
    }
  }
  function handlePromptKeyDown(event: KeyboardEvent<HTMLElement>) {
    if (skillMenu && (event.key === "ArrowDown" || event.key === "ArrowUp" || event.key === "Enter" || event.key === "Escape")) {
      const available = filteredSkillRows.filter(item => !skillDisabled(item));
      if (event.key === "Escape") {
        event.preventDefault();
        closeSkillMenu();
        return;
      }
      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        event.preventDefault();
        if (!available.length) return;
        setActiveSkillIndex(index => (index + (event.key === "ArrowDown" ? 1 : -1) + available.length) % available.length);
        return;
      }
      if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing && event.keyCode !== 229 && available[activeSkillIndex]) {
        event.preventDefault();
        selectSkill(available[activeSkillIndex]);
        return;
      }
    }
    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing && event.keyCode !== 229) {
      event.preventDefault();
      void send();
      return;
    }
    if ((event.key === "Delete" || event.key === "Backspace") && skills.length && isPromptCaretAtStart()) {
      event.preventDefault();
      removeSkill(skills[skills.length - 1].id);
    }
  }
  function bindPrompt(node: HTMLSpanElement | null) {
    input.current = node;
    if (!node || Object.prototype.hasOwnProperty.call(node, "value")) return;
    Object.defineProperty(node, "value", { configurable: true, get: () => node.textContent || "", set: value => { node.textContent = String(value ?? ""); } });
    Object.defineProperty(node, "disabled", { configurable: true, get: () => false });
    node.addEventListener("change", event => onPromptChange((event.currentTarget as HTMLSpanElement).textContent || ""));
  }
  const normalizedSkillQuery = skillQuery.trim().toLowerCase();
  const filteredSkillRows = normalizedSkillQuery ? skillRows.filter(item => skillSearchText(item).includes(normalizedSkillQuery)) : skillRows;
  const skillDisabled = (item: SkillCandidate) => skills.some(row => row.id === item.id) || (capabilities?.materials?.max_skills || 0) <= skills.length;
  useEffect(() => { setActiveSkillIndex(0); }, [skillMenu, normalizedSkillQuery, filteredSkillRows.length]);
  function toggleConfigMenu(next: "model" | "reasoning") {
    closeSkillMenu();
    setConfigMenu(configMenu === next ? null : next);
  }
  return <div className="chat-composer" data-testid="chat-composer" data-repository={repository} ref={composerRoot}>
    {!conversation && <div className="chat-draft-repository">
      <label>分支 <select aria-label="会话分支" data-testid="chat-draft-branch" value={branchName} disabled={busy || !!attempt.creationId || !repositories.length} onChange={e => { setBranch(e.target.value); attempt.branch = e.target.value; }}>{branchRows.length ? branchRows.map(row => <option key={row.name} value={row.name}>{row.name}</option>) : <option value="main">main</option>}</select></label>
    </div>}
    <label className="chat-input-label" htmlFor="chat-prompt">消息</label>
    {materials.length > 0 && <div className="chat-material-strip" data-testid="chat-attachment-strip">
      {materials.map(item => <span key={item.id} className={`chat-material-token ${item.status === "failed" ? "is-failed" : ""}`} data-testid={item.kind === "image" ? "chat-image-attachment" : "chat-file-attachment"} title={item.error || item.name}><FileText size={14}/><b>{item.name}</b><small>{item.status === "uploading" ? "上传中" : item.status === "failed" ? item.error : `${Math.ceil(item.size_bytes / 1024)}KB`}</small><button type="button" aria-label={`移除文件 ${item.name}`} onClick={() => { const next = materials.filter(row => row.id !== item.id); setMaterialDraft(next); logMaterialEvent(item.kind === "image" ? "chat.image_remove" : "chat.file_remove", next, skills); }}><X size={12}/></button></span>)}
    </div>}
    <div className="chat-input-row" data-testid="chat-input-row" onClick={focusPromptEnd}>
      <div className="chat-rich-composer" data-testid="chat-rich-composer">
      {skills.map(item => <span key={item.id} className="chat-skill-token-inline" data-testid="chat-skill-token" title={item.source} tabIndex={0} onKeyDown={e => { if (e.key === "Delete" || e.key === "Backspace") { e.preventDefault(); removeSkill(item.id); } }}><Sparkles size={14}/><b>{skillDisplayName(item.name)}</b><button type="button" aria-label={`移除 Skill ${item.name}`} onClick={() => removeSkill(item.id)}><X size={12}/></button></span>)}
      <span ref={bindPrompt} id="chat-prompt" data-testid="chat-prompt" role="textbox" aria-multiline="true" aria-disabled={!!conversation?.archived || busy} aria-describedby={hint ? "chat-composer-hint" : undefined} className="chat-prompt-editor" data-placeholder="发消息，或输入 / 引用 Skill…" contentEditable={!conversation?.archived && !busy} suppressContentEditableWarning onPaste={onPaste} onKeyDown={handlePromptKeyDown} onInput={e => onPromptChange(e.currentTarget.textContent || "")} />
      </div>
    </div>
    {error && <p role="alert" className="chat-error">{error}</p>}
    {skillMenu && <div className="chat-composer-popover chat-skill-menu" data-testid="chat-skill-menu" role="listbox" aria-label="Skill 候选">
      {skillLoading && <span>正在读取 Skill…</span>}
      {!skillLoading && !skillRows.length && <span>当前仓库暂无可引用 Skill</span>}
      {!skillLoading && !!skillRows.length && !filteredSkillRows.length && <span>未找到匹配 Skill</span>}
      {filteredSkillRows.map(item => {
        const availableRows = filteredSkillRows.filter(row => !skillDisabled(row));
        const availableIndex = availableRows.findIndex(row => row.id === item.id);
        const active = availableIndex >= 0 && availableIndex === activeSkillIndex;
        return <button type="button" role="option" aria-selected={active} className={`chat-composer-option ${active ? "is-active" : ""}`} key={item.id} disabled={skillDisabled(item)} onClick={() => selectSkill(item)}><Sparkles size={14}/><span className="chat-skill-copy"><b>{skillDisplayName(item.name)}</b><small>{item.summary}</small></span></button>;
      })}
    </div>}
    <div className="chat-composer-actions">
      <div className="chat-material-actions">
        <label className="chat-tool-button" title="上传文件"><Paperclip size={14}/><input data-testid="chat-file-input" type="file" accept={(capabilities?.materials?.allowed_file_mime_types || capabilities?.materials?.allowed_image_mime_types || []).join(",")} multiple hidden disabled={disabled || busy} onChange={e => { void addFiles(e.currentTarget.files); e.currentTarget.value = ""; }}/></label>
        <button type="button" data-testid="chat-skill-button" title="引用 Skill" disabled={disabled || busy} onClick={() => void openSkillMenu({ query: "", trigger: "button" })}><Sparkles size={14}/></button>
        {scopeLabel && <span className={`chat-write-scope is-${conversation?.write_scope || "read_only"}`} data-testid="chat-write-scope" role="status" aria-label={`${scopeLabel}：${writeScopeReason(conversation)}`} title={writeScopeReason(conversation)}>{scopeLabel}</span>}
      </div>
      {hint && <span id="chat-composer-hint">{hint}</span>}
      <div className="chat-composer-right" data-testid="chat-execution-config-bar">
        <button type="button" className="chat-config-chip" data-testid="chat-agent-selector" disabled title="当前 Agent"><span>Agent</span><b>{executionOptionLabel("agent", capabilities?.execution?.agents, executionConfig.agent)}</b></button>
        <button type="button" className="chat-config-chip" data-testid="chat-model-selector" disabled={disabled || busy} aria-expanded={configMenu === "model"} onClick={() => toggleConfigMenu("model")}><span>模型</span><b>{executionOptionLabel("model", capabilities?.execution?.models, executionConfig.model)}</b><ChevronDown size={14}/></button>
        <button type="button" className="chat-config-chip" data-testid="chat-reasoning-selector" disabled={disabled || busy} aria-expanded={configMenu === "reasoning"} onClick={() => toggleConfigMenu("reasoning")}><span>推理</span><b>{executionOptionLabel("reasoning", capabilities?.execution?.reasoning, executionConfig.reasoning)}</b><ChevronDown size={14}/></button>
        {configMenu && <div className="chat-composer-popover chat-config-menu" data-testid="chat-execution-config-menu" role="menu">
          {(configMenu === "model" ? capabilities?.execution?.models || emptyOptions : capabilities?.execution?.reasoning || emptyOptions).map(item => <button type="button" className="chat-composer-option" role="menuitemradio" aria-checked={executionConfig[configMenu] === item.value} key={item.value} disabled={!item.available} title={item.disabled_reason || item.display_name} onClick={() => chooseExecution(configMenu, item.value)}><span>{item.display_name}</span>{!item.available && item.disabled_reason && <small>{item.disabled_reason}</small>}</button>)}
        </div>}
        <button type="button" aria-label={busy ? "发送中" : "发送"} title={busy ? "发送中" : "发送"} className="chat-send" data-testid="chat-send" disabled={disabled || busy || hasUploading || !hasContent} onClick={() => void send()}><Send size={14} /></button>
      </div></div>
  </div>;
}

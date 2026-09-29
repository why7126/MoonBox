import { RequirementCenterError, RequirementCenterErrorDetails, readFailure, type ReadFailure } from "./RequirementCenterError";
import "../../styles/project-governance.css";
import { clearAdminSession } from "../admin/adminAuth";
import { clearFrontendSession } from "../home/frontendSession";
import { governanceRequest, governanceTextRequest, GovernanceError, scopedUrl, waitApplication, type Project, type Application } from "../../components/workbench/governanceApi";
import {
Archive,
Check,
CircleDot,
Code2,
Command,
Copy,
ImageIcon,
Info,
Loader2,
Maximize2,
Minimize2,
RefreshCw,
Search,
Send,
Sigma,
Table2,
Wrench,
X
} from "lucide-react";
import { CSSProperties,FormEvent,KeyboardEvent,MouseEvent,RefObject,useCallback,useEffect,useMemo,useRef,useState } from "react";
import { WorkbenchSidebar } from "../../components/workbench/WorkbenchSidebar";
import { useWorkbenchTheme } from "../../components/workbench/useWorkbenchTheme";
import { avatarInitial,emptyUser,emptyWorkspace,fallbackUserFromSession,getStoredWorkspace,readAccessToken,type FrontendUser,type Workspace } from "../../components/workbench/workbenchAccount";
import { CaptureDialog, type CaptureExistingIssue } from "../../components/requirement-center/capture/CaptureDialog";
import { readFrontendSession } from "../home/frontendSession";

const stages: Stage[] = [
  { id: "capture", title: "采集池", subtitle: "Capture / req-capture / bug-capture", emptyTitle: "暂无采集", emptyHint: "从新建 Capture 开始", emptyDetail: "需求或缺陷会先进入这里", requiredDocs: ["capture.md", "trace.md"] },
  { id: "planning", title: "规划中", subtitle: "req-generate / bug-generate", emptyTitle: "暂无需求", emptyHint: "从采集池生成需求", emptyDetail: "后会显示在这里", requiredDocs: ["requirement.md", "trace.md"] },
  { id: "review-ready", title: "待评审", subtitle: "req-complete / bug-complete", emptyTitle: "暂无待评审项", emptyHint: "规划完成的需求", emptyDetail: "将流转至此", requiredDocs: ["acceptance.md", "trace.md"] },
  { id: "approved", title: "已评审", subtitle: "review.md 已生成", emptyTitle: "暂无已评审项", emptyHint: "通过评审后", emptyDetail: "自动归档于此", requiredDocs: ["review.md", "trace.md"] },
  { id: "sprint-planning", title: "迭代规划", subtitle: "sprint-propose", emptyTitle: "暂无迭代项", emptyHint: "评审通过的对象", emptyDetail: "可加入 Sprint", requiredDocs: ["sprint.md", "trace.md"] },
  { id: "ready-dev", title: "待开发", subtitle: "req-opsx / bug-opsx", emptyTitle: "暂无待开发项", emptyHint: "生成 OpenSpec 后", emptyDetail: "会进入开发队列", requiredDocs: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"] },
  { id: "development", title: "研发中", subtitle: "opsx-apply / sprint-apply", emptyTitle: "暂无研发中任务", emptyHint: "开始 apply 后", emptyDetail: "进度会显示在这里", requiredDocs: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"] },
  { id: "acceptance", title: "验收中", subtitle: "测试与人工验收", emptyTitle: "暂无验收项", emptyHint: "研发完成后", emptyDetail: "等待测试与人工确认", requiredDocs: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"] },
  { id: "done", title: "已完成", subtitle: "全链路留痕", emptyTitle: "暂无完成项", emptyHint: "归档完成后", emptyDetail: "会保留最终证据", requiredDocs: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md", "archive.md"] },
];


type IssueType = "requirement" | "bug";
type CardType = IssueType | "change";
type Theme = "dark" | "light";
type MarkdownUploadState = "idle" | "uploading" | "done" | "failed";
type MarkdownViewMode = "preview" | "edit" | "split";
type ProgressFocus = "development" | "test" | "manual";
type MarkdownParts = { frontmatter: Array<[string, string]>; frontmatterRaw: string; body: string };
type DrawerState =
  | { type: "none" }
  | { type: "markdown"; issue: IssueCard; document: IssueDocument; content: string; draft: string; loading: boolean; saving: boolean; error: string; failure?: ReadFailure; readBlocked?: boolean; mode: MarkdownViewMode; dirty: boolean; savedAt?: string; version?: string; focus?: ProgressFocus }
  | { type: "ai"; issue?: IssueCard };
type ChoiceDialog =
  | { type: "none" }
  | { type: "generation" | "completion" | "sprint" | "review"; issue: IssueCard; error: string };
type ActionDialogKind = "analysis" | "command" | "complete" | "sprint" | "opsx" | "apply" | "progress";
type ActionDialog =
  | { type: "none" }
  | { type: ActionDialogKind; issue: IssueCard; tab: "ai" | "import" | "existing" | "new"; ready: boolean; running: boolean; fileName: string; sprintId: string; newSprintId: string; sprintEstimate: number; error: string; adoptedPointIndexes: number[] };
type ArchiveDialog =
  | { type: "none" }
  | { type: "current_iteration_archive"; item: CurrentIterationCapacity };

type Stage = {
  id: string;
  title: string;
  subtitle: string;
  emptyTitle: string;
  emptyHint: string;
  emptyDetail: string;
  requiredDocs: string[];
};

type ChangeSummary = { id: string; title: string | null; stage: string; source_kind: string; task_progress?: [number, number] | null; document_entries?: IssueDocument[]; warnings?: string[] };

type IssueCard = {
  display_title?: string | null;
  title_source?: string | null;
  title_warning?: string | null;
  id: string;
  current_change?: ChangeSummary | null;
  related_changes?: ChangeSummary[];
  change_warning?: string | null;
  drift_warnings?: string[];
  type: CardType;
  title: string;
  priority?: "P0" | "P1" | "P2" | "P3" | "";
  severity?: "blocker" | "critical" | "high" | "medium" | "low" | "";
  owner: string;
  source: string;
  stage: string;
  documents: string[];
  documentEntries?: IssueDocument[];
  detailUrl?: string;
  archiveUrl?: string;
  action?: IssueAction;
  tasks?: IssueTasks;
  updatedAt: string;
  blocked?: string;
  sprintId?: string;
  taskProgress?: [number, number];
  testProgress?: [number, number];
  manualAcceptanceProgress?: [number, number];
  manualAcceptanceCount?: number;
};

type IssueDocument = {
  name: string;
  type: "markdown" | "html" | string;
  openMode?: "drawer" | "new-tab" | string;
  open_mode?: "drawer" | "new-tab" | string;
  status?: string;
  label?: string;
  url?: string | null;
  editable?: boolean;
  capability?: DocumentCapability;
  content?: string;
  htmlContent?: string;
};

type DocumentCapability = {
  readable?: boolean;
  human_editable?: boolean;
  humanEditable?: boolean;
  ai_mutable?: boolean;
  aiMutable?: boolean;
  task_toggle_only?: boolean;
  taskToggleOnly?: boolean;
  reason?: string;
};

type IssueAction = {
  command: string;
  label: string;
  requiresChoice?: "generation" | "completion" | "sprint" | string | null;
  requires_choice?: "generation" | "completion" | "sprint" | string | null;
  disabledReason?: string | null;
  disabled_reason?: string | null;
};

type AuxiliaryAction = {
  command: string;
  label: string;
};

type IssueTasks = {
  done: number;
  total: number;
  blocked?: string[];
  source?: string | null;
};

type RequirementCenterContext = {
  issues: IssueCard[];
  workspaces: Workspace[];
  currentUser: FrontendUser;
  selectedWorkspaceId: string;
  stats: {
    total: number;
    requirements: number;
    bugs: number;
    blocked: number;
    drift: number;
  };
  sprintMetrics?: SprintMetrics;
  sprint_metrics?: SprintMetrics;
  currentIterationCapacity?: CurrentIterationCapacity[];
  current_iteration_capacity?: CurrentIterationCapacity[];
  sprintOptions?: string[];
  sprint_options?: string[];
  sprintOptionDetails?: SprintFilterOption[];
  sprint_option_details?: SprintFilterOption[];
};

type CurrentIterationCapacity = {
  sprintId?: string;
  sprint_id?: string;
  usedCapacity?: number | null;
  used_capacity?: number | null;
  totalCapacity?: number | null;
  total_capacity?: number | null;
  capacityUnit?: "person_day" | string;
  capacity_unit?: "person_day" | string;
  capacitySource?: "explicit" | "default" | "unknown" | string;
  capacity_source?: "explicit" | "default" | "unknown" | string;
  status?: "normal" | "near_limit" | "over_limit" | "unknown" | string;
  message?: string | null;
  archiveReadiness?: ArchiveReadiness | null;
  archive_readiness?: ArchiveReadiness | null;
};

type ArchiveReadiness = {
  canEnterConfirmation?: boolean;
  can_enter_confirmation?: boolean;
  displayMode?: "hidden" | "disabled" | "enabled" | string;
  display_mode?: "hidden" | "disabled" | "enabled" | string;
  reasonCode?: string;
  reason_code?: string;
  safeSummary?: string | null;
  safe_summary?: string | null;
  blockers?: ArchiveReadinessBlocker[];
};

type ArchiveReadinessBlocker = {
  type?: string;
  id?: string | null;
  status?: string | null;
  message?: string | null;
  actionHint?: string | null;
  action_hint?: string | null;
  visible?: boolean;
};

type SprintMetrics = {
  completed_count?: number;
  total_count?: number;
  completedCount?: number;
  totalCount?: number;
  source?: string;
  warning?: string | null;
  refreshed_at?: string | null;
  refreshedAt?: string | null;
};

type SprintOptionModel = {
  id: string;
  status: SprintStatusLabel;
  used: number;
  total: number;
  disabled: boolean;
};
type MetricStatValue = number | { completed: number; total: number };
type MetricStat = {
  label: string;
  value: MetricStatValue;
  description: string;
  testId?: string;
};
type SprintStatusKey = "planning" | "in_progress" | "completed" | "archived" | "unknown";
type SprintStatusLabel = "规划中" | "进行中" | "已完成" | "已归档" | "状态待核实";
type SprintFilterStatusLabel = "进行中" | "已归档";
type SprintFilterOption = {
  sprint_id?: string;
  sprintId?: string;
  id?: string;
  label?: string;
  lifecycle_stage?: string;
  lifecycleStage?: string;
  status?: string;
  status_label?: string;
  statusLabel?: string;
  warning?: string | null;
};
type MultiFilterKey = "stage" | "owner" | "level" | "sprint";
type MultiFilterOption = {
  value: string;
  label: string;
  meta?: string;
  group?: string;
  searchAliases?: string;
  statusLabel?: SprintFilterStatusLabel;
  warning?: string | null;
  disabled?: boolean;
};

const UNASSIGNED_SPRINT_FILTER_VALUE = "__unassigned_sprint__";

type ApiEnvelope<T> = {
  data: T;
};

type VditorEditorShellProps = {
  value: string;
  sourceContent: string;
  documentName: string;
  mode: Exclude<MarkdownViewMode, "preview">;
  uploadState: MarkdownUploadState;
  uploadError: string;
  metadataOpen: boolean;
  onToggleMetadata: () => void;
  onChange: (value: string) => void;
  editorRef: RefObject<HTMLTextAreaElement>;
};

const markdownToolbarSnippets = {
  table: {
    text: "| 列 1 | 列 2 |\n| --- | --- |\n| 内容 | 内容 |\n",
    selectionStart: 22,
    selectionEnd: 24,
  },
  code: {
    before: "```ts\n",
    placeholder: "// code",
    after: "\n```\n",
  },
  formula: {
    before: "$$\n",
    placeholder: "E = mc^2",
    after: "\n$$\n",
  },
};

const parseMarkdownFrontmatter = (content: string): MarkdownParts => {
  const match = content.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!match) return { frontmatter: [], frontmatterRaw: "", body: content };
  const frontmatter = match[1]
    .split("\n")
    .map((line) => line.match(/^([^:#][^:]*):\s*(.*)$/))
    .filter((line): line is RegExpMatchArray => Boolean(line))
    .slice(0, 6)
    .map((line) => [line[1].trim(), line[2].trim()] as [string, string]);
  return { frontmatter, frontmatterRaw: match[0], body: content.slice(match[0].length).trimStart() };
};

const composeMarkdownContent = (sourceContent: string, body: string) => {
  const parsed = parseMarkdownFrontmatter(sourceContent);
  if (!parsed.frontmatterRaw) return body;
  return `${parsed.frontmatterRaw}${body.trimStart()}`;
};

const issueSprintEstimate = (issue: IssueCard) => issue.priority === "P0" ? 5 : issue.priority === "P1" ? 3 : 2;

const nextSprintId = (options: string[]) => {
  const maxNumber = options.reduce((max, option) => {
    const match = option.match(/^sprint-(\d+)$/);
    return match ? Math.max(max, Number(match[1])) : max;
  }, 4);
  return `sprint-${String(maxNumber + 1).padStart(3, "0")}`;
};

const sprintOptionModels = (options: string[], estimate: number, details: SprintFilterOption[] = []): SprintOptionModel[] => {
  const baseOptions = options.length ? options : ["sprint-004"];
  const ids = baseOptions.length > 1 ? baseOptions : [...baseOptions, nextSprintId(baseOptions)];
  const statusById = new Map<string, SprintFilterOption>();
  details.forEach((option) => {
    const id = option.sprint_id || option.sprintId || option.id;
    if (id) statusById.set(id, option);
  });
  return ids.map((id, index) => {
    const total = 12;
    const used = index === 0 ? 8 : 11;
    const detail = statusById.get(id);
    return {
      id,
      status: detail ? normalizeSprintStatus(detail.status, detail.status_label || detail.statusLabel) : (index === 0 ? "进行中" : "规划中"),
      used,
      total,
      disabled: estimate > total - used,
    };
  });
};

const firstSelectableSprintId = (options: SprintOptionModel[]) => options.find((option) => !option.disabled)?.id || "";

const sprintStatusLabels: Record<SprintStatusKey, SprintStatusLabel> = {
  planning: "规划中",
  in_progress: "进行中",
  completed: "已完成",
  archived: "已归档",
  unknown: "状态待核实",
};

const normalizeSprintStatus = (value?: string | null, label?: string | null): SprintStatusLabel => {
  const normalized = String(value || "").toLowerCase();
  if (normalized === "archive") return sprintStatusLabels.archived;
  if (normalized in sprintStatusLabels) return sprintStatusLabels[normalized as SprintStatusKey];
  if (label === "规划中" || label === "进行中" || label === "已完成" || label === "已归档" || label === "状态待核实") return label;
  return sprintStatusLabels.unknown;
};

const sprintStatusClass = (label: SprintStatusLabel) => {
  if (label === "进行中") return "active";
  if (label === "规划中") return "planned";
  if (label === "已完成") return "completed";
  if (label === "已归档") return "archived";
  return "unknown";
};

const sprintFilterStatusLabel = (option?: SprintFilterOption): SprintFilterStatusLabel => {
  const lifecycle = option?.lifecycle_stage || option?.lifecycleStage;
  const status = String(option?.status || "").toLowerCase();
  const label = option?.status_label || option?.statusLabel;
  if (lifecycle === "archive" || status === "archived" || status === "archive" || status === "completed" || label === "已归档" || label === "已完成") return "已归档";
  return "进行中";
};

const issueLevelFilterValue = (issue: IssueCard) => {
  if (issue.type === "requirement" && issue.priority) return `requirement:${issue.priority}`;
  if (issue.type === "bug" && issue.severity) return `bug:${issue.severity}`;
  return "";
};

const isRatioStatValue = (value: MetricStatValue): value is { completed: number; total: number } => typeof value === "object";

const MetricLabel = ({ id, label, description }: { id: string; label: string; description: string }) => (
  <span className="rc-stat-label">
    <span>{label}</span>
    <span id={id} className="rc-stat-info" tabIndex={0} aria-label={`${label}说明：${description}`} data-tooltip={description}>
      <Info size={13} aria-hidden="true" />
    </span>
  </span>
);

const normalizeSprintOptionId = (option: SprintFilterOption) => option.sprint_id || option.sprintId || option.id || "";

const isCurrentSprintOption = (option: SprintFilterOption) => {
  const lifecycle = option.lifecycle_stage || option.lifecycleStage;
  const status = String(option.status || "").toLowerCase();
  return lifecycle === "change" && (status === "planning" || status === "in_progress");
};

const markdownInlineParts = (text: string) => text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g).map((part, index) => {
  if (part.startsWith("`") && part.endsWith("`")) return <code key={index}>{part.slice(1, -1)}</code>;
  if (part.startsWith("**") && part.endsWith("**")) return <strong key={index}>{part.slice(2, -2)}</strong>;
  return part;
});

function RenderedMarkdown({ content, onTaskToggle }: { content: string; onTaskToggle?: (taskIndex: number, checked: boolean) => void }) {
  const [copyState, setCopyState] = useState<{ key: number; status: "copied" | "failed" } | null>(null);
  const blocks: JSX.Element[] = [];
  const lines = content.trim().split("\n");
  let index = 0;
  let taskIndex = 0;
  const copyCodeBlock = async (code: string, key: number) => {
    try {
      if (!navigator.clipboard?.writeText) throw new Error("clipboard unavailable");
      await navigator.clipboard.writeText(code);
      setCopyState({ key, status: "copied" });
    } catch {
      setCopyState({ key, status: "failed" });
    }
    window.setTimeout(() => setCopyState((current) => current?.key === key ? null : current), 1600);
  };
  while (index < lines.length) {
    const blockStart = index;
    const line = lines[index];
    if (!line.trim()) {
      index += 1;
      continue;
    }
    const heading = line.match(/^(#{1,6})\s+(.+)$/);
    if (heading) {
      const level = heading[1].length;
      const className = `level-${level}`;
      blocks.push(<h3 key={blockStart} data-task-heading="true" className={className}>{heading[2]}</h3>);
      index += 1;
      continue;
    }
    if (/^```/.test(line)) {
      const codeLines: string[] = [];
      const blockKey = index;
      index += 1;
      while (index < lines.length && !/^```/.test(lines[index])) {
        codeLines.push(lines[index]);
        index += 1;
      }
      const code = codeLines.join("\n");
      const currentCopyState = copyState?.key === blockKey ? copyState.status : null;
      blocks.push(
        <div key={blockStart} className="code-block">
          <button type="button" className={`copy-code ${currentCopyState ?? ""}`} aria-label="复制代码块" onClick={() => void copyCodeBlock(code, blockKey)}>
            {currentCopyState === "copied" ? <Check size={13} aria-hidden="true" /> : <Copy size={13} aria-hidden="true" />}
            <span>{currentCopyState === "copied" ? "已复制" : currentCopyState === "failed" ? "复制失败" : "复制"}</span>
          </button>
          <pre className="code"><code>{code}</code></pre>
        </div>,
      );
      index += 1;
      continue;
    }
    if (/^\|.+\|$/.test(line)) {
      const rows: string[][] = [];
      while (index < lines.length && /^\|.+\|$/.test(lines[index])) {
        const cells = lines[index].split("|").slice(1, -1).map((cell) => cell.trim());
        if (!cells.every((cell) => /^-+$/.test(cell.replace(/\s/g, "")))) rows.push(cells);
        index += 1;
      }
      blocks.push(
        <div key={blockStart} className="table-scroll">
          <table>
            <tbody>
              {rows.map((row, rowIndex) => <tr key={rowIndex}>{row.map((cell, cellIndex) => <td key={cellIndex}>{markdownInlineParts(cell)}</td>)}</tr>)}
            </tbody>
          </table>
        </div>,
      );
      continue;
    }
    if (/^[-*]\s+/.test(line)) {
      const items: Array<{ content: string; checked?: boolean; taskIndex?: number }> = [];
      while (index < lines.length && /^[-*]\s+/.test(lines[index])) {
        const task = lines[index].match(/^[-*]\s+\[( |x|X)\]\s+(.+)$/);
        if (task) {
          items.push({ content: task[2], checked: task[1].toLowerCase() === "x", taskIndex });
          taskIndex += 1;
        } else {
          items.push({ content: lines[index].replace(/^[-*]\s+/, "") });
        }
        index += 1;
      }
      blocks.push(
        <ul key={blockStart}>
          {items.map((item, itemIndex) => (
            <li key={itemIndex} data-task-item={item.taskIndex === undefined ? undefined : "true"} className={item.taskIndex === undefined ? undefined : "task-list-item"}>
              {item.taskIndex === undefined ? markdownInlineParts(item.content) : (
                <label>
                  <input
                    type="checkbox"
                    checked={item.checked}
                    disabled={!onTaskToggle}
                    onChange={(event) => onTaskToggle?.(item.taskIndex as number, event.target.checked)}
                  />
                  <span>{markdownInlineParts(item.content)}</span>
                </label>
              )}
            </li>
          ))}
        </ul>,
      );
      continue;
    }
    const paragraph = [line.trim()];
    index += 1;
    while (index < lines.length && lines[index].trim() && !/^(#{1,6})\s+/.test(lines[index]) && !/^[-*]\s+/.test(lines[index]) && !/^```/.test(lines[index]) && !/^\|.+\|$/.test(lines[index])) {
      paragraph.push(lines[index].trim());
      index += 1;
    }
    blocks.push(<p key={blockStart}>{markdownInlineParts(paragraph.join(" "))}</p>);
  }
  return <>{blocks.length ? blocks : <p>暂无内容</p>}</>;
}

function MarkdownMetadataPanel({ parts, open, onToggle, compact = false }: { parts: MarkdownParts; open: boolean; onToggle: () => void; compact?: boolean }) {
  if (!parts.frontmatter.length) return null;
  return (
    <section className={`rc-markdown-frontmatter-panel${compact ? " compact" : ""}`}>
      <button
        type="button"
        className="rc-markdown-frontmatter-toggle"
        aria-expanded={open}
        aria-controls="markdown-frontmatter-summary"
        onClick={onToggle}
      >
        <span>文档属性</span>
        <b>{open ? "收起" : "展开"}</b>
      </button>
      {open && (
        <div id="markdown-frontmatter-summary" className="rc-markdown-frontmatter-summary" aria-label="Frontmatter 摘要">
          {parts.frontmatter.map(([key, value]) => <span key={key}><b>{key}</b>{value || "—"}</span>)}
        </div>
      )}
    </section>
  );
}

function MarkdownPreviewPane({ content, compact = false, metadataOpen, onToggleMetadata, showMetadata = true, onTaskToggle, focus }: { focus?: ProgressFocus; content: string; compact?: boolean; metadataOpen: boolean; onToggleMetadata: () => void; showMetadata?: boolean; onTaskToggle?: (taskIndex: number, checked: boolean) => void }) {
  const parsed = parseMarkdownFrontmatter(content);
  const previewRef = useRef<HTMLDivElement>(null);
  const [navigation, setNavigation] = useState("");
  useEffect(() => {
    if (!focus || !previewRef.current) return;
    const patterns: Record<ProgressFocus, RegExp> = {
      development: /研发|开发|实现|implementation|development/i,
      test: /测试|回归|\btest(?:ing|s)?\b/i,
      manual: /人工验收|人工确认|人工签收|manual(?: acceptance)?|human acceptance/i,
    };
    const candidates: HTMLElement[] = [];
    for (const node of previewRef.current.querySelectorAll<HTMLElement>("[data-task-heading], [data-task-item]")) {
      if (node.hasAttribute("data-task-heading") && /历史|返修记录/.test(node.textContent || "")) break;
      candidates.push(node);
    }
    const target = candidates.find(node => node.hasAttribute("data-task-heading") && patterns[focus].test(node.textContent || ""))
      || candidates.find(node => node.hasAttribute("data-task-item") && patterns[focus].test(node.textContent || ""));
    if (!target) {
      setNavigation(`tasks.md 中未找到${progressFocusLabel[focus]}章节或任务，已展示完整文档。`);
      return;
    }
    setNavigation(`已定位${progressFocusLabel[focus]}：${target.textContent}`);
    target.classList.add("rc-task-navigation-target");
    target.setAttribute("tabindex", "-1");
    const frame = requestAnimationFrame(() => {
      target.scrollIntoView?.({ block: "center", behavior: "instant" });
      target.focus({ preventScroll: true });
    });
    return () => { cancelAnimationFrame(frame); target.classList.remove("rc-task-navigation-target"); target.removeAttribute("tabindex"); };
  }, [focus, content]);
  return (
    <div ref={previewRef} className={`rc-markdown-prototype-preview${compact ? " compact" : ""}`}  aria-label="Markdown 安全预览">
      {focus && <p role="status" data-task-navigation="true">{navigation}</p>}
      {showMetadata && <MarkdownMetadataPanel parts={parsed} open={metadataOpen} onToggle={onToggleMetadata} compact={compact} />}
      <div className="rc-markdown-preview-section">
        <div className="rc-rendered-markdown" data-testid="markdown-rendered-preview">
          <RenderedMarkdown content={parsed.body} onTaskToggle={onTaskToggle} />
        </div>
      </div>
    </div>
  );
}

function VditorEditorShell({ value, sourceContent, documentName, mode, uploadState, uploadError, metadataOpen, onToggleMetadata, onChange, editorRef }: VditorEditorShellProps) {
  const sourceParts = parseMarkdownFrontmatter(sourceContent);
  return (
    <div className={`rc-vditor-shell ${mode}`} data-testid="vditor-editor-shell">
      <MarkdownMetadataPanel parts={sourceParts} open={metadataOpen} onToggle={onToggleMetadata} />
      {(uploadState !== "idle" || uploadError) && (
        <div className={`rc-vditor-upload-state ${uploadState}`} data-testid="vditor-upload-state" role={uploadState === "failed" ? "alert" : "status"}>
          图片上传：{uploadState === "uploading" ? "上传中" : uploadState === "done" ? "已插入" : "暂不可用"}
          {uploadError && <span>{uploadError}</span>}
        </div>
      )}
      <div className="rc-vditor-workspace">
        <div className="rc-vditor-pane editor">
          <textarea
            ref={editorRef}
            aria-label={`编辑 ${documentName}`}
            data-testid="markdown-source-fallback"
            value={value}
            onChange={(event) => onChange(event.target.value)}
          />
        </div>
        {mode === "split" && (
          <div className="rc-vditor-pane preview">
            <MarkdownPreviewPane content={composeMarkdownContent(sourceContent, value)} compact metadataOpen={metadataOpen} onToggleMetadata={onToggleMetadata} showMetadata={false} />
          </div>
        )}
      </div>
    </div>
  );
}


const stageTitleById = new Map(stages.map((stage) => [stage.id, stage.title]));

const stageVisibleDocs: Record<string, string[]> = {
  capture: ["capture.md", "trace.md"],
  planning: ["requirement.md", "bug.md", "prototype.html", "trace.md"],
  "review-ready": ["requirement.md", "bug.md", "acceptance.md", "business-flow.md", "user-stories.md", "root-cause.md", "workaround.md", "trace.md"],
  approved: ["requirement.md", "bug.md", "acceptance.md", "business-flow.md", "user-stories.md", "root-cause.md", "workaround.md", "review.md", "trace.md"],
  "sprint-planning": ["sprint.md", "trace.md"],
  "ready-dev": ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"],
  development: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"],
  acceptance: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"],
  done: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md", "archive.md"],
};

const stageAction: Record<string, Partial<Record<CardType, string>>> = {
  capture: { requirement: "/req-generate", bug: "/bug-generate" },
  planning: { requirement: "/req-complete", bug: "/bug-complete" },
  "review-ready": { requirement: "/req-review", bug: "/bug-review" },
  approved: { requirement: "/sprint-propose", bug: "/sprint-propose" },
  "sprint-planning": { requirement: "/req-opsx", bug: "/bug-opsx" },
  "ready-dev": { requirement: "/opsx-apply", bug: "/opsx-apply" },
  development: { requirement: "/opsx-apply", bug: "/opsx-apply" },
  acceptance: { requirement: "/opsx-archive", bug: "/opsx-archive" },
  done: { requirement: "只读", bug: "只读" },
};

const stageActionLabel: Record<string, Partial<Record<CardType, string>>> = {
  capture: { requirement: "生成需求 →", bug: "生成 Bug →" },
  planning: { requirement: "完善需求 →", bug: "完善 Bug →" },
  "review-ready": { requirement: "发起评审 →", bug: "确认修复 →" },
  approved: { requirement: "加入迭代 →", bug: "加入迭代 →" },
  "sprint-planning": { requirement: "生成 Opsx →", bug: "生成 Opsx →" },
  "ready-dev": { requirement: "开始开发 →", bug: "开始修复 →" },
  development: { requirement: "查看进度 →", bug: "查看进度 →" },
  acceptance: { requirement: "完成 / 归档 →", bug: "完成 / 归档 →" },
  done: { requirement: "查看归档 →", bug: "查看归档 →" },
};

const nextStage: Record<string, string> = {
  capture: "planning",
  planning: "review-ready",
  "review-ready": "approved",
  approved: "sprint-planning",
  "sprint-planning": "ready-dev",
  "ready-dev": "development",
  development: "acceptance",
  acceptance: "done",
};
const sprintVisibleStages = new Set(["sprint-planning", "ready-dev", "development", "acceptance", "done"]);

const sanitizeFeedback = (value: string) =>
  value
    .replace(/\/Users\/[^ \n)]+/g, "[local-path]")
    .replace(/CodeSpaces\/Projects\/[^ \n)]+/g, "[workspace-path]")
    .replace(/token[^ \n]*/gi, "token=[redacted]")
    .slice(0, 420);

const documentCapability = (document: IssueDocument): Required<Pick<DocumentCapability, "readable" | "human_editable" | "task_toggle_only" | "reason">> => {
  const capability = document.capability || {};
  const humanEditable = capability.human_editable ?? capability.humanEditable ?? document.editable ?? false;
  const taskToggleOnly = capability.task_toggle_only ?? capability.taskToggleOnly ?? false;
  return {
    readable: capability.readable ?? true,
    human_editable: Boolean(humanEditable),
    task_toggle_only: Boolean(taskToggleOnly),
    reason: capability.reason || (humanEditable ? "当前阶段可编辑" : taskToggleOnly ? "仅允许勾选任务" : "当前阶段只读"),
  };
};

const canEditDocument = (document: IssueDocument) => documentCapability(document).human_editable;

const canToggleTaskDocument = (document: IssueDocument) => documentCapability(document).task_toggle_only;

const canMutateMarkdownDocument = (document: IssueDocument) => canEditDocument(document) || canToggleTaskDocument(document);

const capabilityForStage = (issueType: CardType, stage: string, name: string): DocumentCapability => {
  if (issueType === "change") return { readable: true, human_editable: false, task_toggle_only: false, ai_mutable: false, reason: "独立 Change 只读" };
  if (name === "trace.md") {
    return { readable: true, human_editable: false, ai_mutable: true, task_toggle_only: false, reason: "trace.md 仅允许系统治理链路更新，人工始终只读" };
  }
  if (stage === "capture" && name === "capture.md") {
    return { readable: true, human_editable: true, ai_mutable: true, task_toggle_only: false, reason: "采集池阶段允许编辑 capture.md" };
  }
  if (stage === "planning") {
    const allowed = issueType === "requirement" ? "requirement.md" : "bug.md";
    if (name === allowed) {
      return { readable: true, human_editable: true, ai_mutable: true, task_toggle_only: false, reason: "规划中阶段允许编辑主文档" };
    }
  }
  if (stage === "review-ready") {
    const allowed = new Set(issueType === "requirement" ? ["requirement.md", "business-flow.md", "user-stories.md", "acceptance.md"] : ["bug.md", "root-cause.md", "workaround.md", "acceptance.md"]);
    if (allowed.has(name)) {
      return { readable: true, human_editable: true, ai_mutable: true, task_toggle_only: false, reason: "待评审阶段允许完善类文档编辑" };
    }
  }
  if (stage === "approved") {
    const allowed = new Set(issueType === "requirement" ? ["requirement.md", "business-flow.md", "user-stories.md", "acceptance.md", "review.md"] : ["bug.md", "root-cause.md", "workaround.md", "acceptance.md", "review.md"]);
    if (allowed.has(name)) {
      return { readable: true, human_editable: true, ai_mutable: true, task_toggle_only: false, reason: "已评审阶段允许已评审材料编辑" };
    }
  }
  if (stage === "ready-dev" && ["proposal.md", "spec.md", "design.md", "tasks.md"].includes(name)) {
    return { readable: true, human_editable: true, ai_mutable: true, task_toggle_only: false, reason: "待开发阶段允许编辑当前 OpenSpec Change 计划类文档" };
  }
  if (stage === "acceptance" && name === "tasks.md") {
    return { readable: true, human_editable: false, ai_mutable: true, task_toggle_only: true, reason: "验收中 tasks.md 仅允许勾选或取消勾选任务" };
  }
  return { readable: true, human_editable: false, ai_mutable: true, task_toggle_only: false, reason: "当前治理阶段不允许人工编辑" };
};

const issueDocumentEntries = (issue: IssueCard): IssueDocument[] =>
  issue.documentEntries?.length
    ? issue.documentEntries
    : issue.documents.map((name) => {
        const suffix = name.toLowerCase().endsWith(".html") ? "html" : "markdown";
        const capability = capabilityForStage(issue.type, issue.stage, name);
        const editable = Boolean(capability.human_editable);
        return {
          name,
          label: name,
          type: suffix,
          openMode: suffix === "html" ? "new-tab" : "drawer",
          editable,
          capability,
        };
      });


const documentSemanticKey = (document: IssueDocument, source: "issue" | "change", changeId?: string) => {
  const name = (document.name || document.label || "").trim().toLowerCase();
  if (source === "change" && name === "trace.md") return `change:${changeId || "current"}:trace.md`;
  return name;
};

const relatedChangeDocumentGroups = (issue: IssueCard, issueDocuments: IssueDocument[] = []): { change: ChangeSummary; documents: IssueDocument[] }[] => {
  if (issue.type === "change") return [];
  const seenDocumentKeys = new Set(issueDocuments.map((document) => documentSemanticKey(document, "issue")));
  const changes = issue.related_changes?.length ? issue.related_changes : issue.current_change ? [issue.current_change] : [];
  return changes
    .map((change) => {
      const documents = (change.document_entries || []).filter((document) => {
        const key = documentSemanticKey(document, "change", change.id);
        if (seenDocumentKeys.has(key)) return false;
        seenDocumentKeys.add(key);
        return true;
      });
      return { change, documents };
    })
    .filter((group) => group.documents.length > 0);
};

const changeDocumentShortLabel = (index: number, total: number) => (total > 1 ? `Change ${index + 1}` : "Change");

const changeDocumentButtonLabel = (document: IssueDocument, index: number, total: number) => {
  const name = document.label || document.name;
  const documentName = document.name === "trace.md" ? "Change trace.md" : name;
  return total > 1 ? `${changeDocumentShortLabel(index, total)} ${documentName}` : documentName;
};

const visibleIssueDocuments = (stage: Stage, issue: IssueCard) => {
  if (issue.type === "change" || stage.id === "unknown") return issueDocumentEntries(issue);
  const allowed = new Set(stageVisibleDocs[stage.id] || stage.requiredDocs);
  const mainDocument = issue.type === "requirement" ? "requirement.md" : "bug.md";
  allowed.add(mainDocument);
  allowed.add("sprint.md");
  const stageOrder = stage.id === "done" ? ["archive.md", "tasks.md", "spec.md", "design.md", "proposal.md"]
    : ["development", "acceptance"].includes(stage.id) ? ["tasks.md", "spec.md", "design.md", "proposal.md"]
    : stage.id === "approved" ? ["review.md", "acceptance.md", "business-flow.md", "user-stories.md", "root-cause.md", "workaround.md"]
    : (stageVisibleDocs[stage.id] || stage.requiredDocs);
  const order = [...new Set([mainDocument, "sprint.md", "trace.md", ...stageOrder])];
  const prototypes = issue.type === "requirement" ? issueDocumentEntries(issue).filter(doc => doc.name === "prototype.html" || (doc.name.startsWith("prototype/") && doc.name.endsWith(".html"))).map(doc => doc.name).sort() : [];
  prototypes.forEach(name => allowed.add(name));
  order.splice(1, 0, ...prototypes);
  return issueDocumentEntries(issue)
    .filter((document) => allowed.has(document.name) && (!["requirement.md", "bug.md"].includes(document.name) || document.name === mainDocument))
    .sort((a, b) => order.indexOf(a.name) - order.indexOf(b.name));
};

const issueDetailUrl = (issue: IssueCard) => issue.detailUrl || `/requirements/${issue.id}`;

const issueCommandTarget = (issue: IssueCard) => (issue.type === "requirement" ? "--req" : "--bug");

const choiceForStage = (stageId: string): IssueAction["requiresChoice"] | "review" | undefined => {
  if (stageId === "capture") return "generation";
  if (stageId === "planning") return "completion";
  if (stageId === "review-ready") return "review";
  if (stageId === "approved") return "sprint";
  return undefined;
};

const actionCommandForStage = (issue: IssueCard, stageId: string) => {
  if (issue.type === "change") return "只读";
  if (stageId === "approved") return `/sprint-propose ${issueCommandTarget(issue)} ${issue.id}`;
  return `${stageAction[stageId]?.[issue.type] || "只读"} ${issue.id}`.trim();
};

const actionForStage = (issue: IssueCard, stageId: string): IssueAction | undefined => {
  if (issue.type === "change") {
    const action = {
      "ready-dev": { label: "开始开发", command: `/opsx-apply ${issue.id}` },
      development: { label: "查看进度", command: `查看进度 ${issue.id}` },
      acceptance: { label: "完成 / 归档", command: `/opsx-archive ${issue.id}` },
    }[stageId];
    return action;
  }
  const label = stageActionLabel[stageId]?.[issue.type]?.replace(" →", "") || "只读";
  if (label === "只读") return undefined;
  return {
    command: actionCommandForStage(issue, stageId),
    label,
    requiresChoice: choiceForStage(stageId),
  };
};

const actionChoice = (action: IssueAction | undefined, issue?: IssueCard) => action?.requiresChoice || action?.requires_choice || (issue ? choiceForStage(issue.stage) : null) || null;

const actionDisabledReason = (action: IssueAction | undefined) => action?.disabledReason || action?.disabled_reason || "";

const issueAction = (issue: IssueCard): IssueAction => {
  const fallback = actionForStage(issue, issue.stage);
  if (issue.type === "change") return {
    ...(fallback || { command: "只读", label: "只读" }),
    disabledReason: actionDisabledReason(issue.action) || fallback?.disabledReason,
  };
  return issue.action || fallback || { command: "只读", label: "只读" };
};

const actionDialogType = (issue: IssueCard, action?: AuxiliaryAction | IssueAction): ActionDialogKind => {
  if (action?.label.includes("分析")) return "analysis";
  if (issue.stage === "planning") return "complete";
  if (issue.stage === "approved") return "sprint";
  if (issue.stage === "sprint-planning") return "opsx";
  if (issue.stage === "ready-dev") return "apply";
  if (issue.stage === "development") return "progress";
  return "command";
};

const commandDocsForAction = (issue: IssueCard, type: ActionDialogKind) => {
  if (type === "command" && issue.stage === "capture") return [issue.type === "requirement" ? "requirement.md" : "bug.md"];
  if (type === "command" && issue.stage === "review-ready") return ["review.md"];
  if (type === "command" && issue.stage === "acceptance") return ["archive.md"];
  if (type === "complete") {
    return issue.type === "requirement"
      ? ["acceptance.md", "business-flow.md", "user-stories.md", "prototype.html", "prototype-context.md"]
      : ["root-cause.md", "workaround.md", "acceptance.md", "prototype.html", "prototype-context.md"];
  }
  if (type === "opsx") return ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"];
  if (type === "apply") return ["同步 Change 分支到工作区", `初始化任务列表 · 共 ${issue.taskProgress?.[1] || 8} 项`, "执行环境依赖检查"];
  return [];
};

const actionModalCopy = (issue: IssueCard, type: ActionDialogKind) => {
  const action = issueAction(issue);
  const isReq = issue.type === "requirement";
  if (type === "analysis") {
    return {
      eyebrow: isReq ? "req-explore" : "bug-explore",
      title: isReq ? "需求分析" : "Bug 分析",
      sub: `AI 分析 ${issue.id} 的上下文并给出建议方案`,
      command: `${isReq ? "/req-explore" : "/bug-explore"} ${issue.id}`,
      confirm: "采纳 3/3 项并保留分析 →",
      running: "保存中…",
    };
  }
  if (type === "complete") {
    return {
      eyebrow: isReq ? "req-complete" : "bug-complete",
      title: isReq ? "完善需求" : "完善 Bug",
      sub: `为 ${issue.id} 补齐必需文档`,
      command: `${isReq ? "/req-complete" : "/bug-complete"} ${issue.id}`,
      confirm: "生成完善文档 →",
      running: "处理中…",
    };
  }
  if (type === "sprint") {
    return {
      eyebrow: "sprint-propose · 加入迭代",
      title: "加入迭代",
      sub: `将 ${issue.id} 纳入即将开始的迭代排期`,
      command: action.command,
      confirm: "加入迭代",
      running: "加入中…",
    };
  }
  if (type === "opsx") {
    return {
      eyebrow: isReq ? "req-opsx" : "bug-opsx",
      title: "生成 Opsx",
      sub: `为 ${issue.id} 生成 OpenSpec Change 与配套文档`,
      command: `${isReq ? "/req-opsx" : "/bug-opsx"} ${issue.id}`,
      confirm: "完成生成，进入待开发 →",
      running: "处理中…",
    };
  }
  if (type === "apply") {
    return {
      eyebrow: "opsx-apply",
      title: isReq ? "开始开发" : "开始修复",
      sub: `将 ${issue.id} 的 Change 应用到工作区并启动研发`,
      command: `/opsx-apply ${issue.id}`,
      confirm: "应用变更，进入研发中 →",
      running: "应用中…",
    };
  }
  if (type === "progress") {
    return {
      eyebrow: "opsx-apply · 研发进度",
      title: "查看进度",
      sub: `${issue.id} 正在由 Codex 自动执行任务`,
      command: `/opsx-apply ${issue.id}`,
      confirm: "关闭",
      running: "关闭",
    };
  }
  if (issue.stage === "review-ready") {
    return {
      eyebrow: isReq ? "req-review" : "bug-review",
      title: isReq ? "发起评审" : "确认修复",
      sub: `AI 将为 ${issue.id} 生成评审文档`,
      command: action.command,
      confirm: isReq ? "发起评审，进入已评审 →" : "确认修复，进入已评审 →",
      running: "AI 生成评审中…",
    };
  }
  if (issue.stage === "acceptance") {
    return {
      eyebrow: "opsx-archive",
      title: "完成 / 归档",
      sub: `归档 ${issue.id} 并沉淀全链路记录`,
      command: action.command,
      confirm: "确认归档 →",
      running: "归档中…",
    };
  }
  return {
    eyebrow: isReq ? "req-generate" : "bug-generate",
    title: isReq ? "生成需求" : "生成 Bug",
    sub: `AI 将基于采集内容为 ${issue.id} 生成正式文档`,
    command: action.command,
    confirm: isReq ? "生成需求，进入规划中 →" : "生成 Bug，进入规划中 →",
    running: "AI 生成中…",
  };
};

const transitionDocumentsForStage = (issue: IssueCard, stageId: string) => {
  if (stageId === "planning") return [issue.type === "requirement" ? "requirement.md" : "bug.md"];
  if (stageId === "review-ready") {
    return issue.type === "requirement"
      ? ["acceptance.md", "business-flow.md", "user-stories.md"]
      : ["root-cause.md", "workaround.md", "acceptance.md"];
  }
  if (stageId === "approved") return ["review.md"];
  if (stageId === "sprint-planning") return ["sprint.md"];
  return [];
};

const transitionDocumentEntry = (issue: IssueCard, name: string): IssueDocument => {
  const suffix = name.toLowerCase().endsWith(".html") ? "html" : "markdown";
  const targetStage = nextStage[issue.stage] || issue.stage;
  const capability = capabilityForStage(issue.type, targetStage, name);
  const editable = Boolean(capability.human_editable);
  return {
    name,
    label: name,
    type: suffix,
    openMode: suffix === "html" ? "new-tab" : "drawer",
    editable,
    capability,
  };
};

const appendTransitionDocuments = (issue: IssueCard, stageId: string) => {
  const extraDocs = transitionDocumentsForStage(issue, stageId).filter((name) => !issue.documents.includes(name));
  if (!extraDocs.length) return { documents: issue.documents, documentEntries: issue.documentEntries };
  const existingEntries = issueDocumentEntries(issue);
  return {
    documents: [...issue.documents, ...extraDocs],
    documentEntries: [...existingEntries, ...extraDocs.map((name) => transitionDocumentEntry(issue, name))],
  };
};

const drawerTitle = (drawer: DrawerState) => {
  if (drawer.type === "markdown") return `${drawer.issue.id} · ${drawer.document.label || drawer.document.name}`;
  if (drawer.type === "ai") return "AI Chat";
  return "";
};

const drawerIssueSubtitle = (drawer: Extract<DrawerState, { type: "markdown" }>) => (
  `${drawer.issue.priority} · ${drawer.issue.owner}负责 · ${stageTitleById.get(drawer.issue.stage) || drawer.issue.stage}`
);

const visibleSprintId = (issue: IssueCard) => (sprintVisibleStages.has(issue.stage) ? issue.sprintId : undefined);

const visibleTaskProgress = (issue: IssueCard) => (["ready-dev", "development", "acceptance"].includes(issue.stage) ? issue.taskProgress : undefined);

const visibleManualAcceptanceProgress = (issue: IssueCard): [number, number] | undefined => {
  if (issue.stage !== "acceptance" || !issue.testProgress) return undefined;
  if (issue.manualAcceptanceProgress) return issue.manualAcceptanceProgress;
  const pendingCount = issue.manualAcceptanceCount ?? 0;
  return pendingCount > 0 ? [0, pendingCount] : undefined;
};

const progressFocusLabel: Record<ProgressFocus, string> = {
  development: "研发任务",
  test: "自动化测试",
  manual: "人工验收",
};



const auxiliaryActions = (issue: IssueCard): AuxiliaryAction[] => {
  if (issue.type === "change" || issue.stage === "unknown") return [];
  if (issue.stage !== "capture") return [];
  if (issue.type === "bug") return [{ command: `/bug-explore ${issue.id}`, label: "Bug 分析" }];
  return [{ command: `/req-explore ${issue.id}`, label: "需求分析" }];
};

const workflowDemoIssue = (issue: IssueCard): IssueCard => issue;

const workflowDemoDocumentContent = (issueId: string, name: string) => {
  const title = issueId.replace("DEMO-", "Demo ");
  const templates: Record<string, string> = {
    "capture.md": `---
source: workflow-demo
issue: ${issueId}
---

# ${title} Capture

## 背景
- 这是一份用于需求中心受控 demo 模式的采集记录。
- 用来验证 Markdown 抽屉、预览态、编辑入口和阶段卡片文档入口。

## 待澄清
- 目标用户、影响范围和下一步命令由卡片阶段动作承接。
`,
    "trace.md": `---
source: workflow-demo
issue: ${issueId}
status: demo
---

# ${title} Trace

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-30 22:50:41 | demo | 受控 demo 文档内容已加载。 |
`,
    "bug.md": `# ${title} Bug

## 现象
- 生成文档后 trace 时间未刷新。

## 影响
- 影响用户判断卡片是否完成阶段流转。

## 期望
- 完善后自动补齐验收、复现和 trace 证据。
`,
    "requirement.md": `# ${title} Requirement

## 目标
- 让需求中心在 demo 模式下呈现完整阶段文档。

## 范围
- 展示文档正文、阶段动作和只读/可编辑边界。
`,
    "acceptance.md": `# ${title} Acceptance

- [ ] 阶段动作映射正确。
- [ ] 文档入口可打开并展示正文。
- [ ] 异常分支不触发阶段流转。
`,
    "business-flow.md": `# ${title} Business Flow

采集 -> 生成 -> 完善 -> 评审 -> 纳入迭代 -> 开发 -> 验收 -> 归档。
`,
    "user-stories.md": `# ${title} User Stories

- 作为产品团队，我希望看到阶段文档内容，便于判断下一步动作。
- 作为测试团队，我希望 demo 数据覆盖每个阶段，便于做视觉验收。
`,
    "review.md": `# ${title} Review

评审结论：已评审，等待纳入迭代。
`,
    "sprint.md": `# ${title} Sprint

目标迭代：sprint-004

## 范围
- 承接已评审对象。
- 准备生成对应 OpenSpec Change。
`,
    "proposal.md": `# ${title} Proposal

## Why
- 当前阶段已经进入 OpenSpec 开发链路，需要展示提案摘要。

## What
- 补齐卡片动作、文档入口和验收证据。
`,
    "design.md": `# ${title} Design

## 决策
- 默认真实数据不变。
- demo 模式只使用前端内置脱敏样例。
`,
    "tasks.md": `# ${title} Tasks

- [x] 建立卡片壳。
- [x] 补充文档入口。
- [ ] 完成视觉验收。
`,
    "test-plan.md": `# ${title} Test Plan

## 自动化
- 前端聚焦测试。
- 1440px 视觉证据。

## 人工验收
- 检查卡片文案、间距和抽屉内容。
`,
    "archive.md": `# ${title} Archive

## 结果
- 已完成并保留全链路留痕。

## 证据
- demo 归档卡片用于验证已完成阶段展示。
`,
  };
  return templates[name] || `# ${title} ${name}\n\n这是 ${issueId} 的受控 demo 文档内容。`;
};

const workflowDemoHtmlContent = (issueId: string, name: string) => `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>${issueId} ${name}</title>
  <style>
    body { margin: 0; padding: 32px; background: var(--preview-bg, #0A0D14); color: var(--preview-text, #ECEAE4); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    h1 { color: var(--preview-accent, #D8AC55); }
    section { max-width: 760px; line-height: 1.7; }
  </style>
</head>
<body>
  <section>
    <h1>${issueId} Demo HTML Preview</h1>
    <p>${name} 来自受控 workflow demo 模式，用于验证 HTML 文档新 Tab 打开体验。</p>
  </section>
</body>
</html>`;

const workflowDemoStage = (issueId: string): string => {
  if (issueId.includes("-CAPTURE-")) return "capture";
  if (issueId.includes("-PLANNING-")) return "planning";
  if (issueId.includes("-REVIEW-")) return "review-ready";
  if (issueId.includes("-APPROVED-")) return "approved";
  if (issueId.includes("-SPRINT-")) return "sprint-planning";
  if (issueId.includes("-READY-DEV")) return "ready-dev";
  if (issueId.includes("-DEVELOPMENT")) return "development";
  if (issueId.includes("-ACCEPTANCE-")) return "acceptance";
  if (issueId.includes("-DONE")) return "done";
  return "capture";
};

const workflowDemoDocuments = (issueId: string, names: string[], editableCapture = false): IssueDocument[] => {
  const issueType: IssueType = issueId.includes("-BUG-") ? "bug" : "requirement";
  const stage = workflowDemoStage(issueId);
  return (
  names.map((name) => {
    const capability = editableCapture && name === "capture.md" ? capabilityForStage(issueType, "capture", name) : capabilityForStage(issueType, stage, name);
    const isHtml = name.endsWith(".html");
    return {
      name,
      label: name,
      type: isHtml ? "html" : "markdown",
      openMode: isHtml ? "new-tab" : "drawer",
      url: isHtml
        ? `/api/v1/requirement-center/issues/${issueId}/documents/${name}/preview`
        : `/api/v1/requirement-center/issues/${issueId}/documents/${name}`,
      editable: Boolean(capability.human_editable),
      capability,
      content: isHtml ? undefined : workflowDemoDocumentContent(issueId, name),
      htmlContent: isHtml ? workflowDemoHtmlContent(issueId, name) : undefined,
    };
  })
  );
};

function isWorkflowDemoMode() {
  const params = new URLSearchParams(window.location.search);
  return params.get("mock") === "workflow" || params.get("demo") === "workflow";
}

function buildWorkflowDemoContext(frontendUsername?: string): RequirementCenterContext {
  const issues = [
    workflowDemoIssue({
      id: "DEMO-REQ-CAPTURE-READY",
      type: "requirement",
      title: "采集客户访谈中的空间权限诉求",
      priority: "P1",
      owner: "产品团队",
      source: "demo",
      stage: "capture",
      documents: ["capture.md", "trace.md"],
      documentEntries: workflowDemoDocuments("DEMO-REQ-CAPTURE-READY", ["capture.md", "trace.md"], true),
      detailUrl: "/requirements/DEMO-REQ-CAPTURE-READY",
      action: { command: "/req-generate DEMO-REQ-CAPTURE-READY", label: "生成需求", requiresChoice: "generation" },
      updatedAt: "09:12",
    }),
    workflowDemoIssue({
      id: "DEMO-REQ-CAPTURE-MISSING-TRACE",
      type: "requirement",
      title: "采集语音纪要缺少追踪记录",
      priority: "P2",
      owner: "产品团队",
      source: "demo",
      stage: "capture",
      documents: ["capture.md"],
      documentEntries: workflowDemoDocuments("DEMO-REQ-CAPTURE-MISSING-TRACE", ["capture.md"], true),
      detailUrl: "/requirements/DEMO-REQ-CAPTURE-MISSING-TRACE",
      action: { command: "/req-generate DEMO-REQ-CAPTURE-MISSING-TRACE", label: "生成需求", requiresChoice: "generation", disabledReason: "缺少 trace.md" },
      updatedAt: "09:18",
    }),
    workflowDemoIssue({
      id: "DEMO-BUG-CAPTURE-READY",
      type: "bug",
      title: "采集用户反馈中的按钮状态异常",
      severity: "medium",
      owner: "前端体验",
      source: "demo",
      stage: "capture",
      documents: ["capture.md", "trace.md"],
      documentEntries: workflowDemoDocuments("DEMO-BUG-CAPTURE-READY", ["capture.md", "trace.md"], true),
      detailUrl: "/requirements/DEMO-BUG-CAPTURE-READY",
      action: { command: "/bug-generate DEMO-BUG-CAPTURE-READY", label: "生成 Bug", requiresChoice: "generation" },
      updatedAt: "09:36",
    }),
    workflowDemoIssue({
      id: "DEMO-BUG-CAPTURE-EMPTY-CAPTURE",
      type: "bug",
      title: "采集缺陷描述为空待补充",
      severity: "high",
      owner: "测试团队",
      source: "demo",
      stage: "capture",
      documents: ["capture.md", "trace.md"],
      documentEntries: workflowDemoDocuments("DEMO-BUG-CAPTURE-EMPTY-CAPTURE", ["capture.md", "trace.md"], true),
      detailUrl: "/requirements/DEMO-BUG-CAPTURE-EMPTY-CAPTURE",
      action: { command: "/bug-generate DEMO-BUG-CAPTURE-EMPTY-CAPTURE", label: "生成 Bug", requiresChoice: "generation", disabledReason: "文档内容为空：capture.md" },
      updatedAt: "09:44",
    }),
    workflowDemoIssue({
      id: "DEMO-REQ-PLANNING-READY",
      type: "requirement",
      title: "空间成员权限矩阵完善中",
      priority: "P1",
      owner: "产品团队",
      source: "demo",
      stage: "planning",
      documents: ["capture.md", "trace.md", "requirement.md", "prototype.html"],
      documentEntries: workflowDemoDocuments("DEMO-REQ-PLANNING-READY", ["capture.md", "trace.md", "requirement.md", "prototype.html"]),
      detailUrl: "/requirements/DEMO-REQ-PLANNING-READY",
      action: { command: "/req-complete DEMO-REQ-PLANNING-READY", label: "完善需求", requiresChoice: "completion" },
      updatedAt: "10:00",
    }),
    workflowDemoIssue({
      id: "DEMO-REQ-PLANNING-MISSING-REQ",
      type: "requirement",
      title: "规划中需求缺少 PRD",
      priority: "P2",
      owner: "产品团队",
      source: "demo",
      stage: "planning",
      documents: ["capture.md", "trace.md"],
      documentEntries: workflowDemoDocuments("DEMO-REQ-PLANNING-MISSING-REQ", ["capture.md", "trace.md"]),
      detailUrl: "/requirements/DEMO-REQ-PLANNING-MISSING-REQ",
      action: { command: "/req-complete DEMO-REQ-PLANNING-MISSING-REQ", label: "完善需求", requiresChoice: "completion", disabledReason: "缺少 requirement.md" },
      updatedAt: "10:03",
    }),
    workflowDemoIssue({
      id: "DEMO-BUG-PLANNING-READY",
      type: "bug",
      title: "生成文档后 trace 时间未刷新",
      severity: "critical",
      owner: "平台工程",
      source: "demo",
      stage: "planning",
      documents: ["capture.md", "trace.md", "bug.md", "prototype.html"],
      documentEntries: workflowDemoDocuments("DEMO-BUG-PLANNING-READY", ["capture.md", "trace.md", "bug.md", "prototype.html"]),
      detailUrl: "/requirements/DEMO-BUG-PLANNING-READY",
      action: { command: "/bug-complete DEMO-BUG-PLANNING-READY", label: "完善 Bug", requiresChoice: "completion" },
      updatedAt: "10:06",
    }),
    workflowDemoIssue({
      id: "DEMO-BUG-PLANNING-EMPTY-BUG",
      type: "bug",
      title: "规划中 Bug 正文为空",
      severity: "high",
      owner: "平台工程",
      source: "demo",
      stage: "planning",
      documents: ["capture.md", "trace.md", "bug.md"],
      documentEntries: workflowDemoDocuments("DEMO-BUG-PLANNING-EMPTY-BUG", ["capture.md", "trace.md", "bug.md"]),
      detailUrl: "/requirements/DEMO-BUG-PLANNING-EMPTY-BUG",
      action: { command: "/bug-complete DEMO-BUG-PLANNING-EMPTY-BUG", label: "完善 Bug", requiresChoice: "completion", disabledReason: "文档内容为空：bug.md" },
      updatedAt: "10:10",
    }),
    workflowDemoIssue({
      id: "DEMO-REQ-REVIEW-READY",
      type: "requirement",
      title: "补齐需求验收标准与用户故事",
      priority: "P1",
      owner: "产品团队",
      source: "demo",
      stage: "review-ready",
      documents: ["capture.md", "trace.md", "requirement.md", "acceptance.md", "business-flow.md", "user-stories.md"],
      documentEntries: workflowDemoDocuments("DEMO-REQ-REVIEW-READY", ["capture.md", "trace.md", "requirement.md", "acceptance.md", "business-flow.md", "user-stories.md"]),
      detailUrl: "/requirements/DEMO-REQ-REVIEW-READY",
      action: { command: "/req-review DEMO-REQ-REVIEW-READY", label: "发起评审" },
      updatedAt: "10:24",
    }),
    workflowDemoIssue({
      id: "DEMO-REQ-REVIEW-MISSING-STORIES",
      type: "requirement",
      title: "待评审需求缺少用户故事",
      priority: "P2",
      owner: "产品团队",
      source: "demo",
      stage: "review-ready",
      documents: ["capture.md", "trace.md", "requirement.md", "acceptance.md", "business-flow.md"],
      documentEntries: workflowDemoDocuments("DEMO-REQ-REVIEW-MISSING-STORIES", ["capture.md", "trace.md", "requirement.md", "acceptance.md", "business-flow.md"]),
      detailUrl: "/requirements/DEMO-REQ-REVIEW-MISSING-STORIES",
      action: { command: "/req-review DEMO-REQ-REVIEW-MISSING-STORIES", label: "发起评审", disabledReason: "缺少 user-stories.md" },
      updatedAt: "10:28",
    }),
    workflowDemoIssue({
      id: "DEMO-BUG-REVIEW-READY",
      type: "bug",
      title: "禁用态二次点击保护待确认",
      severity: "medium",
      owner: "前端体验",
      source: "demo",
      stage: "review-ready",
      documents: ["capture.md", "trace.md", "bug.md", "root-cause.md", "workaround.md", "acceptance.md"],
      documentEntries: workflowDemoDocuments("DEMO-BUG-REVIEW-READY", ["capture.md", "trace.md", "bug.md", "root-cause.md", "workaround.md", "acceptance.md"]),
      detailUrl: "/requirements/DEMO-BUG-REVIEW-READY",
      action: { command: "/bug-review DEMO-BUG-REVIEW-READY", label: "确认修复" },
      updatedAt: "10:36",
    }),
    workflowDemoIssue({
      id: "DEMO-BUG-REVIEW-EMPTY-ROOT-CAUSE",
      type: "bug",
      title: "待评审 Bug 根因文档为空",
      severity: "critical",
      owner: "平台工程",
      source: "demo",
      stage: "review-ready",
      documents: ["capture.md", "trace.md", "bug.md", "root-cause.md", "workaround.md", "acceptance.md"],
      documentEntries: workflowDemoDocuments("DEMO-BUG-REVIEW-EMPTY-ROOT-CAUSE", ["capture.md", "trace.md", "bug.md", "root-cause.md", "workaround.md", "acceptance.md"]),
      detailUrl: "/requirements/DEMO-BUG-REVIEW-EMPTY-ROOT-CAUSE",
      action: { command: "/bug-review DEMO-BUG-REVIEW-EMPTY-ROOT-CAUSE", label: "确认修复", disabledReason: "文档内容为空：root-cause.md" },
      updatedAt: "10:40",
    }),
    workflowDemoIssue({
      id: "DEMO-REQ-APPROVED-READY",
      type: "requirement",
      title: "已评审需求等待纳入迭代",
      priority: "P1",
      owner: "产品团队",
      source: "demo",
      stage: "approved",
      documents: ["capture.md", "trace.md", "requirement.md", "acceptance.md", "business-flow.md", "user-stories.md", "review.md"],
      documentEntries: workflowDemoDocuments("DEMO-REQ-APPROVED-READY", ["capture.md", "trace.md", "requirement.md", "acceptance.md", "business-flow.md", "user-stories.md", "review.md"]),
      detailUrl: "/requirements/DEMO-REQ-APPROVED-READY",
      action: { command: "/sprint-propose --req DEMO-REQ-APPROVED-READY", label: "加入迭代", requiresChoice: "sprint" },
      updatedAt: "10:48",
    }),
    workflowDemoIssue({
      id: "DEMO-REQ-APPROVED-MISSING-REVIEW",
      type: "requirement",
      title: "已评审需求缺少评审记录",
      priority: "P2",
      owner: "产品团队",
      source: "demo",
      stage: "approved",
      documents: ["capture.md", "trace.md", "requirement.md", "acceptance.md", "business-flow.md", "user-stories.md"],
      documentEntries: workflowDemoDocuments("DEMO-REQ-APPROVED-MISSING-REVIEW", ["capture.md", "trace.md", "requirement.md", "acceptance.md", "business-flow.md", "user-stories.md"]),
      detailUrl: "/requirements/DEMO-REQ-APPROVED-MISSING-REVIEW",
      action: { command: "/sprint-propose --req DEMO-REQ-APPROVED-MISSING-REVIEW", label: "加入迭代", requiresChoice: "sprint", disabledReason: "缺少 review.md" },
      updatedAt: "10:52",
    }),
    workflowDemoIssue({
      id: "DEMO-BUG-APPROVED-READY",
      type: "bug",
      title: "按钮禁用态缺少二次点击保护",
      severity: "medium",
      owner: "前端体验",
      source: "demo",
      stage: "approved",
      documents: ["capture.md", "trace.md", "bug.md", "root-cause.md", "workaround.md", "acceptance.md", "review.md"],
      documentEntries: workflowDemoDocuments("DEMO-BUG-APPROVED-READY", ["capture.md", "trace.md", "bug.md", "root-cause.md", "workaround.md", "acceptance.md", "review.md"]),
      detailUrl: "/requirements/DEMO-BUG-APPROVED-READY",
      action: { command: "/sprint-propose --bug DEMO-BUG-APPROVED-READY", label: "加入迭代", requiresChoice: "sprint" },
      updatedAt: "10:56",
    }),
    workflowDemoIssue({
      id: "DEMO-BUG-APPROVED-DRIFT",
      type: "bug",
      title: "已评审 Bug 存在数据漂移",
      severity: "high",
      owner: "平台工程",
      source: "demo",
      stage: "approved",
      documents: ["capture.md", "trace.md", "bug.md", "root-cause.md", "workaround.md", "acceptance.md", "review.md"],
      documentEntries: workflowDemoDocuments("DEMO-BUG-APPROVED-DRIFT", ["capture.md", "trace.md", "bug.md", "root-cause.md", "workaround.md", "acceptance.md", "review.md"]),
      detailUrl: "/requirements/DEMO-BUG-APPROVED-DRIFT",
      action: { command: "/sprint-propose --bug DEMO-BUG-APPROVED-DRIFT", label: "加入迭代", requiresChoice: "sprint", disabledReason: "存在数据漂移" },
      updatedAt: "11:00",
    }),
    workflowDemoIssue({
      id: "DEMO-REQ-SPRINT-READY",
      type: "requirement",
      title: "选择 sprint-004 承接 AI 聊天反馈",
      priority: "P1",
      owner: "产品团队",
      source: "demo",
      stage: "sprint-planning",
      documents: ["sprint.md", "trace.md"],
      documentEntries: workflowDemoDocuments("DEMO-REQ-SPRINT-READY", ["sprint.md", "trace.md"]),
      detailUrl: "/requirements/DEMO-REQ-SPRINT-READY",
      action: { command: "/req-opsx DEMO-REQ-SPRINT-READY", label: "生成 Opsx" },
      sprintId: "sprint-004",
      updatedAt: "11:08",
    }),
    workflowDemoIssue({
      id: "DEMO-BUG-SPRINT-READY",
      type: "bug",
      title: "迭代规划中的 Bug 待生成 Opsx",
      severity: "medium",
      owner: "平台工程",
      source: "demo",
      stage: "sprint-planning",
      documents: ["sprint.md", "trace.md"],
      documentEntries: workflowDemoDocuments("DEMO-BUG-SPRINT-READY", ["sprint.md", "trace.md"]),
      detailUrl: "/requirements/DEMO-BUG-SPRINT-READY",
      action: { command: "/bug-opsx DEMO-BUG-SPRINT-READY", label: "生成 Opsx" },
      sprintId: "sprint-004",
      updatedAt: "11:14",
    }),
    workflowDemoIssue({
      id: "DEMO-REQ-READY-DEV",
      type: "requirement",
      title: "待开发需求已生成 OpenSpec",
      priority: "P2",
      owner: "产品团队",
      source: "demo",
      stage: "ready-dev",
      documents: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"],
      documentEntries: workflowDemoDocuments("DEMO-REQ-READY-DEV", ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"]),
      detailUrl: "/requirements/DEMO-REQ-READY-DEV",
      action: { command: "/opsx-apply DEMO-REQ-READY-DEV", label: "开始开发" },
      sprintId: "sprint-004",
      taskProgress: [0, 10],
      tasks: { done: 0, total: 10, blocked: [], source: "tasks.md" },
      updatedAt: "11:22",
    }),
    workflowDemoIssue({
      id: "DEMO-BUG-READY-DEV",
      type: "bug",
      title: "归档详情页新 Tab 打开状态异常",
      severity: "medium",
      owner: "平台工程",
      source: "demo",
      stage: "ready-dev",
      documents: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"],
      documentEntries: workflowDemoDocuments("DEMO-BUG-READY-DEV", ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"]),
      detailUrl: "/requirements/DEMO-BUG-READY-DEV",
      action: { command: "/opsx-apply DEMO-BUG-READY-DEV", label: "开始修复" },
      sprintId: "sprint-004",
      taskProgress: [0, 8],
      tasks: { done: 0, total: 8, blocked: ["等待复现截图"], source: "tasks.md" },
      updatedAt: "11:30",
    }),
    workflowDemoIssue({
      id: "DEMO-REQ-DEVELOPMENT",
      type: "requirement",
      title: "实现 Markdown 抽屉编辑与保存回显",
      priority: "P0",
      owner: "前端体验",
      source: "demo",
      stage: "development",
      documents: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"],
      documentEntries: workflowDemoDocuments("DEMO-REQ-DEVELOPMENT", ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"]),
      detailUrl: "/requirements/DEMO-REQ-DEVELOPMENT",
      action: { command: "/opsx-apply DEMO-REQ-DEVELOPMENT", label: "查看进度" },
      sprintId: "sprint-004",
      taskProgress: [5, 8],
      tasks: { done: 5, total: 8, blocked: ["视觉证据待补"], source: "tasks.md" },
      updatedAt: "12:10",
    }),
    workflowDemoIssue({
      id: "DEMO-BUG-DEVELOPMENT",
      type: "bug",
      title: "修复任务流转后状态未刷新",
      severity: "high",
      owner: "平台工程",
      source: "demo",
      stage: "development",
      documents: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"],
      documentEntries: workflowDemoDocuments("DEMO-BUG-DEVELOPMENT", ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"]),
      detailUrl: "/requirements/DEMO-BUG-DEVELOPMENT",
      action: { command: "/opsx-apply DEMO-BUG-DEVELOPMENT", label: "查看进度" },
      sprintId: "sprint-004",
      taskProgress: [3, 6],
      tasks: { done: 3, total: 6, blocked: [], source: "tasks.md" },
      updatedAt: "12:18",
    }),
    workflowDemoIssue({
      id: "DEMO-REQ-ACCEPTANCE-READY",
      type: "requirement",
      title: "验收完成的需求等待归档",
      priority: "P1",
      owner: "测试团队",
      source: "demo",
      stage: "acceptance",
      documents: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"],
      documentEntries: workflowDemoDocuments("DEMO-REQ-ACCEPTANCE-READY", ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"]),
      detailUrl: "/requirements/DEMO-REQ-ACCEPTANCE-READY",
      action: { command: "/opsx-archive DEMO-REQ-ACCEPTANCE-READY", label: "完成 / 归档" },
      sprintId: "sprint-004",
      taskProgress: [7, 7],
      testProgress: [3, 3],
      manualAcceptanceProgress: [1, 1],
      manualAcceptanceCount: 0,
      tasks: { done: 7, total: 7, blocked: [], source: "tasks.md" },
      updatedAt: "12:34",
    }),
    workflowDemoIssue({
      id: "DEMO-BUG-ACCEPTANCE-BLOCKED",
      type: "bug",
      title: "验收报告缺少 computed style 证据",
      severity: "medium",
      owner: "测试团队",
      source: "demo",
      stage: "acceptance",
      documents: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"],
      documentEntries: workflowDemoDocuments("DEMO-BUG-ACCEPTANCE-BLOCKED", ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"]),
      detailUrl: "/requirements/DEMO-BUG-ACCEPTANCE-BLOCKED",
      action: { command: "/opsx-archive DEMO-BUG-ACCEPTANCE-BLOCKED", label: "完成 / 归档" },
      sprintId: "sprint-004",
      taskProgress: [8, 8],
      testProgress: [2, 3],
      manualAcceptanceProgress: [0, 1],
      manualAcceptanceCount: 1,
      tasks: { done: 8, total: 8, blocked: ["等待人工验收"], source: "tasks.md" },
      updatedAt: "12:42",
    }),
    workflowDemoIssue({
      id: "DEMO-REQ-DONE",
      type: "requirement",
      title: "沉淀需求中心卡片工作流经验",
      priority: "P2",
      owner: "产品团队",
      source: "demo",
      stage: "done",
      documents: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md", "archive.md"],
      documentEntries: workflowDemoDocuments("DEMO-REQ-DONE", ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md", "archive.md"]),
      detailUrl: "/requirements/DEMO-REQ-DONE",
      archiveUrl: "/requirements/DEMO-REQ-DONE",
      action: { command: "只读 DEMO-REQ-DONE", label: "查看归档" },
      sprintId: "sprint-004",
      taskProgress: [6, 6],
      tasks: { done: 6, total: 6, blocked: [], source: "tasks.md" },
      updatedAt: "13:05",
    }),
    workflowDemoIssue({
      id: "DEMO-BUG-DONE",
      type: "bug",
      title: "归档缺陷保留最终追踪证据",
      severity: "low",
      owner: "平台工程",
      source: "demo",
      stage: "done",
      documents: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md", "archive.md"],
      documentEntries: workflowDemoDocuments("DEMO-BUG-DONE", ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md", "archive.md"]),
      detailUrl: "/requirements/DEMO-BUG-DONE",
      archiveUrl: "/requirements/DEMO-BUG-DONE",
      action: { command: "只读 DEMO-BUG-DONE", label: "查看归档" },
      sprintId: "sprint-004",
      taskProgress: [4, 4],
      tasks: { done: 4, total: 4, blocked: [], source: "tasks.md" },
      updatedAt: "13:12",
    }),
  ];
  return {
    issues,
    workspaces: [{
      organizationName: "MoonBox",
      workspaceId: "workflow-demo",
      name: "需求中心演示空间",
      slug: "workflow-demo",
      description: "用于需求研发流转看板 9 阶段视觉验收的受控 demo 数据。",
      timezone: "Asia/Shanghai",
      memberCount: 9,
      role: "拥有者",
      status: "ACTIVE",
      readonly: true,
    }],
    currentUser: {
      name: frontendUsername?.trim() || "Demo 用户",
      avatarInitial: avatarInitial(frontendUsername || "Demo 用户"),
      avatarUrl: null,
      canAccessAdmin: false,
      permissions: ["requirement:read", "bug:read", "sprint:read", "openspec:read"],
    },
    selectedWorkspaceId: "workflow-demo",
    stats: {
      total: issues.length,
      requirements: issues.filter((issue) => issue.type === "requirement").length,
      bugs: issues.filter((issue) => issue.type === "bug").length,
      blocked: issues.filter((issue) => issue.blocked).length,
      drift: 0,
    },
    sprintMetrics: { completed_count: 1, total_count: 2, source: "sprint_lifecycle" },
    currentIterationCapacity: [
      {
        sprintId: "sprint-004",
        usedCapacity: 28,
        totalCapacity: 30,
        capacityUnit: "person_day",
        capacitySource: "explicit",
        status: "near_limit",
        message: "接近容量上限",
        archiveReadiness: {
          canEnterConfirmation: false,
          displayMode: "disabled",
          reasonCode: "unarchived_scope",
          safeSummary: "Sprint archive readiness 未通过：REQ 1 项、BUG 1 项、Change 1 项 未闭环。",
          blockers: [
            { type: "requirement", id: "DEMO-REQ-ACCEPTANCE-READY", status: "applied", message: "范围内需求尚未归档闭环" },
            { type: "bug", id: "DEMO-BUG-ACCEPTANCE-BLOCKED", status: "applied", message: "范围内 BUG 尚未归档闭环" },
            { type: "change", id: "demo-change", status: "applied", message: "范围内 Change 尚未归档闭环" },
          ],
        },
      },
      {
        sprintId: "sprint-003",
        usedCapacity: 18,
        totalCapacity: 30,
        capacityUnit: "person_day",
        capacitySource: "explicit",
        status: "normal",
        message: "归档 readiness 已通过",
        archiveReadiness: {
          canEnterConfirmation: true,
          displayMode: "enabled",
          reasonCode: "ready",
          safeSummary: "范围内 REQ、BUG 与独立 Change 均已归档闭环，验收 sign-off、权限与 Workflow Sync 将在 Sprint archive 确认流程中继续复核。",
          blockers: [],
        },
      },
    ],
    sprintOptions: ["sprint-004"],
    sprintOptionDetails: [
      { sprint_id: "sprint-004", label: "sprint-004", lifecycle_stage: "change", status: "in_progress", status_label: "进行中" },
    ],
  };
}

function normalizeContext(payload: RequirementCenterContext, frontendUsername?: string): RequirementCenterContext {
  const rawContext = payload as RequirementCenterContext & {
    current_user?: FrontendUser;
    selected_workspace_id?: string;
  };
  const rawUser = rawContext.current_user || payload.currentUser;
  const frontendDisplayName = frontendUsername?.trim();
  const rawUserName = rawUser?.name?.trim();
  const isAnonymousUser = !rawUser || !rawUserName || rawUserName === "未登录";
  const normalizedUser = isAnonymousUser && frontendDisplayName
      ? {
        name: frontendDisplayName,
        avatarInitial: avatarInitial(frontendDisplayName),
        avatarUrl: null,
        canAccessAdmin: false,
        permissions: ["requirement:read"],
      }
    : {
        ...(rawUser || emptyUser),
        avatarInitial: avatarInitial(rawUserName, rawUser?.avatarInitial || (rawUser as FrontendUser & { avatar_initial?: string } | undefined)?.avatar_initial),
        avatarUrl:
          (rawUser as FrontendUser & { avatar_url?: string | null } | undefined)?.avatar_url ?? rawUser?.avatarUrl ?? null,
        canAccessAdmin:
          (rawUser as FrontendUser & { can_access_admin?: boolean } | undefined)?.can_access_admin ?? rawUser?.canAccessAdmin ?? false,
      };
  return {
    ...payload,
    issues: payload.issues.map((issue) => ({
      ...issue,
      documentEntries:
        (issue as IssueCard & { document_entries?: IssueDocument[] }).document_entries || issue.documentEntries || [],
      detailUrl: (issue as IssueCard & { detail_url?: string }).detail_url || issue.detailUrl,
      archiveUrl: (issue as IssueCard & { archive_url?: string }).archive_url || issue.archiveUrl,
      action: issue.action
        ? {
            ...issue.action,
            requiresChoice: issue.action.requires_choice || issue.action.requiresChoice,
            disabledReason: issue.action.disabled_reason || issue.action.disabledReason,
          }
        : undefined,
      updatedAt: (issue as IssueCard & { updated_at?: string }).updated_at || issue.updatedAt,
      sprintId: (issue as IssueCard & { sprint_id?: string }).sprint_id || issue.sprintId,
      taskProgress: (issue as IssueCard & { task_progress?: [number, number] }).task_progress || issue.taskProgress,
      testProgress: (issue as IssueCard & { test_progress?: [number, number] }).test_progress || issue.testProgress,
      manualAcceptanceProgress:
        (issue as IssueCard & { manual_acceptance_progress?: [number, number] }).manual_acceptance_progress ??
        issue.manualAcceptanceProgress,
      manualAcceptanceCount:
        (issue as IssueCard & { manual_acceptance_count?: number }).manual_acceptance_count ?? issue.manualAcceptanceCount,
    })),
    workspaces: payload.workspaces.map((workspace) => ({
      ...workspace,
      organizationName: (workspace as Workspace & { organization_name?: string }).organization_name || workspace.organizationName,
      workspaceId: (workspace as Workspace & { workspace_id?: string }).workspace_id || workspace.workspaceId,
      memberCount: (workspace as Workspace & { member_count?: number }).member_count ?? workspace.memberCount,
      readonly: (workspace as Workspace & { readonly?: boolean }).readonly ?? false,
    })),
    currentUser: normalizedUser,
    selectedWorkspaceId: rawContext.selected_workspace_id || payload.selectedWorkspaceId,
    sprintMetrics: rawContext.sprint_metrics || payload.sprintMetrics || { completed_count: 0, total_count: 0, source: "sprint_lifecycle" },
    currentIterationCapacity: (rawContext.current_iteration_capacity || payload.currentIterationCapacity || []).map(normalizeCapacityItem),
    sprintOptions: rawContext.sprint_options || payload.sprintOptions || [],
    sprintOptionDetails: rawContext.sprint_option_details || payload.sprintOptionDetails || [],
  };
}

function normalizeCapacityItem(item: CurrentIterationCapacity): CurrentIterationCapacity {
  return {
    sprintId: item.sprint_id || item.sprintId,
    usedCapacity: item.used_capacity ?? item.usedCapacity ?? null,
    totalCapacity: item.total_capacity ?? item.totalCapacity ?? null,
    capacityUnit: item.capacity_unit || item.capacityUnit || "person_day",
    capacitySource: item.capacity_source || item.capacitySource || "unknown",
    status: item.status || "unknown",
    message: item.message || null,
    archiveReadiness: normalizeArchiveReadiness(item.archive_readiness || item.archiveReadiness || null),
  };
}

function normalizeArchiveReadiness(readiness: ArchiveReadiness | null): ArchiveReadiness | null {
  if (!readiness) return null;
  return {
    canEnterConfirmation: readiness.can_enter_confirmation ?? readiness.canEnterConfirmation ?? false,
    displayMode: readiness.display_mode || readiness.displayMode || "hidden",
    reasonCode: readiness.reason_code || readiness.reasonCode || "unknown",
    safeSummary: readiness.safe_summary ?? readiness.safeSummary ?? null,
    blockers: (readiness.blockers || []).map((blocker) => ({
      type: blocker.type,
      id: blocker.id ?? null,
      status: blocker.status ?? null,
      message: blocker.message ?? null,
      actionHint: blocker.action_hint ?? blocker.actionHint ?? null,
      visible: blocker.visible ?? true,
    })),
  };
}

function issueLevelTag(issue: IssueCard) {
  if (issue.type === "bug") {
    return issue.severity ? { value: issue.severity, className: `rc-severity-tag ${issue.severity}` } : null;
  }
  if (issue.type === "requirement") {
    return issue.priority ? { value: issue.priority, className: `rc-priority-tag ${issue.priority.toLowerCase()}` } : null;
  }
  return null;
}

const capacityStatusLabel = (status?: string) => {
  if (status === "near_limit") return "接近上限";
  if (status === "over_limit") return "已超量";
  if (status === "unknown") return "待核实";
  return "正常";
};

const capacityUnitLabel = (unit?: string) => unit === "person_day" ? "人天" : unit || "人天";

const capacitySourceLabel = (source?: string) => {
  if (source === "explicit") return "显式容量";
  if (source === "default") return "默认容量";
  return "待核实";
};

const formatCapacityValue = (item: CurrentIterationCapacity) => {
  const used = item.usedCapacity;
  const total = item.totalCapacity;
  if (typeof used !== "number" || typeof total !== "number") return "待核实";
  return `${Number.isInteger(used) ? used : used.toFixed(1)} / ${Number.isInteger(total) ? total : total.toFixed(1)} ${capacityUnitLabel(item.capacityUnit)}`;
};

const capacityProgressPercent = (item: CurrentIterationCapacity) => {
  const used = item.usedCapacity;
  const total = item.totalCapacity;
  if (typeof used !== "number" || typeof total !== "number" || total <= 0) return 0;
  return Math.max(0, Math.min(100, (used / total) * 100));
};

const archiveReadinessSummary = (readiness?: ArchiveReadiness | null) => readiness?.safeSummary || "Sprint archive readiness 待核实";

const archiveActionHint = (readiness: ArchiveReadiness | null | undefined, archiveEnabled: boolean) => {
  const summary = archiveReadinessSummary(readiness);
  return archiveEnabled ? `归档当前迭代：${summary}` : `无法归档当前迭代：${summary}`;
};

const capacityStatusHint = (item: CurrentIterationCapacity) => {
  const source = capacitySourceLabel(item.capacitySource);
  const message = item.message || `${source}，容量状态${capacityStatusLabel(item.status)}`;
  return `容量来源：${source}；说明：${message}`;
};

function CurrentIterationCapacityStrip({
  items,
  loading,
  stale,
  onArchive,
}: {
  items: CurrentIterationCapacity[];
  loading: boolean;
  stale: boolean;
  onArchive: (item: CurrentIterationCapacity) => void;
}) {
  if (!loading && items.length === 0) return null;
  return (
    <section
      className={`rc-current-capacity${stale ? " stale" : ""}`}
      data-testid="current-iteration-capacity"
      data-state={loading ? "loading" : stale ? "refresh_failed" : "ready"}
      aria-label="当前迭代容量"
    >
      {stale && <div className="rc-current-capacity-notice">刷新失败，保留上次成功数据</div>}
      <div className="rc-current-capacity-items">
        {loading && items.length === 0 ? (
          <article className="rc-capacity-item loading" data-testid="capacity-metric-item" data-state="loading">
            <div className="rc-capacity-meta">
              <span className="rc-loading-number" aria-hidden="true" />
              <small>读取中</small>
            </div>
            <div className="rc-capacity-track">
              <strong>正在读取容量</strong>
              <span className="rc-capacity-bar" aria-hidden="true"><span /></span>
            </div>
            <span className="rc-capacity-status"><i aria-hidden="true" />待同步</span>
          </article>
        ) : items.map((item) => {
          const status = item.status || "unknown";
          const sprintId = item.sprintId || "sprint-unknown";
          const readiness = item.archiveReadiness;
          const archiveMode = readiness?.displayMode || "hidden";
          const showArchiveEntry = archiveMode !== "hidden";
          const archiveEnabled = archiveMode === "enabled" && Boolean(readiness?.canEnterConfirmation);
          const archiveHint = archiveActionHint(readiness, archiveEnabled);
          const progressStyle = { "--capacity-progress": `${capacityProgressPercent(item)}%` } as CSSProperties;
          return (
            <article className={`rc-capacity-item ${status}`} key={sprintId} data-testid="capacity-metric-item" data-state={status}>
              <div className="rc-capacity-main">
                <div className="rc-capacity-meta">
                  <b>{sprintId}</b>
                  <span className="rc-capacity-status" data-testid="current-iteration-capacity-status" title={capacityStatusHint(item)}><i aria-hidden="true" />{capacityStatusLabel(status)}</span>
                </div>
                <div className="rc-capacity-track">
                  <strong>{formatCapacityValue(item)}</strong>
                  <span className="rc-capacity-bar" style={progressStyle} aria-hidden="true"><span /></span>
                </div>
              </div>
              {showArchiveEntry && (
                <div className="rc-capacity-archive">
                  <span
                    className="rc-capacity-archive-tip"
                    data-testid="current-iteration-archive-summary"
                    title={archiveHint}
                  >
                    <button
                      type="button"
                      aria-label={archiveEnabled ? `归档当前迭代 ${sprintId}` : `无法归档当前迭代 ${sprintId}`}
                      data-testid="current-iteration-archive-action"
                      disabled={!archiveEnabled}
                      title={archiveHint}
                      onClick={() => onArchive(item)}
                    >
                      <Archive size={15} aria-hidden="true" />
                    </button>
                  </span>
                </div>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}

function requiredDocsForIssue(stageId: string, issueType: CardType) {
  const requirementReviewDocs = ["capture.md", "trace.md", "requirement.md", "acceptance.md", "business-flow.md", "user-stories.md"];
  const bugReviewDocs = ["capture.md", "trace.md", "bug.md", "root-cause.md", "workaround.md", "acceptance.md"];
  if (stageId === "capture") return ["capture.md", "trace.md"];
  if (stageId === "planning") return issueType === "requirement" ? ["capture.md", "trace.md", "requirement.md"] : ["capture.md", "trace.md", "bug.md"];
  if (stageId === "review-ready") return issueType === "requirement" ? requirementReviewDocs : bugReviewDocs;
  if (stageId === "approved") return issueType === "requirement" ? [...requirementReviewDocs, "review.md"] : [...bugReviewDocs, "review.md"];
  return stages.find((stage) => stage.id === stageId)?.requiredDocs || [];
}

function missingDocs(stageId: string, issue: IssueCard) {
  return requiredDocsForIssue(stageId, issue.type).filter((doc) => !issue.documents.includes(doc));
}

function blockedTip(stageId: string, issue: IssueCard, action: IssueAction | undefined) {
  // Terminal cards have no pending action; archive.md is not a required artifact.
  if (stageId === "done" || stageId === "unknown") return "";
  if (issue.type === "change") return actionDisabledReason(action) || issue.blocked || "";
  const reason = actionDisabledReason(action) || issue.blocked || "";
  if (reason) return reason;
  const missing = missingDocs(stageId, issue);
  return missing.length ? `缺少 ${missing.join("、")}` : "";
}

function canArchive(issue: IssueCard) {
  if (issue.stage !== "acceptance") return true;
  const testsDone = !issue.testProgress || issue.testProgress[0] >= issue.testProgress[1];
  return testsDone && (issue.manualAcceptanceCount || 0) === 0;
}

export function RequirementCenterPage() {
  const [context, setContext] = useState<RequirementCenterContext | null>(null);
  const [isLoadingContext, setIsLoadingContext] = useState(true);
  const [isRefreshingContext, setIsRefreshingContext] = useState(false);
  const [contextError, setContextError] = useState("");
  const [contextFailure, setContextFailure] = useState<ReadFailure | null>(null);
  const [errorDetails, setErrorDetails] = useState<ReadFailure | null>(null);
  const [lastSuccess, setLastSuccess] = useState("");
  const documentFlight = useRef<string | null>(null);
  const [theme] = useWorkbenchTheme();
  const [typeFilter, setTypeFilter] = useState<"all" | CardType>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedStages, setSelectedStages] = useState<string[]>([]);
  const [selectedOwners, setSelectedOwners] = useState<string[]>([]);
  const [selectedLevels, setSelectedLevels] = useState<string[]>([]);
  const [selectedSprints, setSelectedSprints] = useState<string[]>([]);
  const [openFilter, setOpenFilter] = useState<MultiFilterKey | null>(null);
  const [filterSearch, setFilterSearch] = useState<Record<MultiFilterKey, string>>({ stage: "", owner: "", level: "", sprint: "" });
  const [toast, setToast] = useState("");
  const [project, setProject] = useState<Project | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [syncLabel, setSyncLabel] = useState("正在读取项目连接");
  const projectRef = useRef<Project | null>(null);
  const requestedSpace = useRef("");
  const requestEpoch = useRef(0);
  const contextController = useRef<AbortController | null>(null);
  const contextFlight = useRef<{ key: string; promise: Promise<void> } | null>(null);
  const revisionRef = useRef("");
  const documentEpoch = useRef(0);
  const pollFailures = useRef(0);
  const pollPaused = useRef(false);
  const [workspace, setWorkspace] = useState<Workspace>(emptyWorkspace);
  const [captureOpen, setCaptureOpen] = useState(false);
  const [agentOpen, setAgentOpen] = useState(false);
  const [captureForm, setCaptureForm] = useState({
    type: "requirement" as IssueType,
    title: "",
    priority: "P1" as "P0" | "P1" | "P2" | "P3",
    severity: "medium",
    description: "",
    owner: "产品团队",
    source: "explore",
  });
  const [captureError, setCaptureError] = useState("");
  const [captureBusy, setCaptureBusy] = useState(false);
  const [captureReady, setCaptureReady] = useState<{ ready: boolean; reason: string } | null>(null);
  const [captureCheck, setCaptureCheck] = useState(0);
  const captureController = useRef<AbortController | null>(null);
  const captureAttempt = useRef<{ fingerprint: string; key: string } | null>(null);
  const closeCapture = () => {
    captureController.current?.abort(); captureController.current = null;
    setCaptureBusy(false); setCaptureOpen(false);
  };
  useEffect(() => () => captureController.current?.abort(), []);
  const [drawer, setDrawer] = useState<DrawerState>({ type: "none" });
  const drawerRef = useRef(drawer); drawerRef.current = drawer;
  const [drawerWidth, setDrawerWidth] = useState(760);
  const [isDrawerFullscreen, setIsDrawerFullscreen] = useState(false);
  const [markdownUploadState, setMarkdownUploadState] = useState<MarkdownUploadState>("idle");
  const [markdownUploadError, setMarkdownUploadError] = useState("");
  const [markdownMetadataOpen, setMarkdownMetadataOpen] = useState(false);
  const [choiceDialog, setChoiceDialog] = useState<ChoiceDialog>({ type: "none" });
  const [actionDialog, setActionDialog] = useState<ActionDialog>({ type: "none" });
  const [archiveDialog, setArchiveDialog] = useState<ArchiveDialog>({ type: "none" });
  const [lockedActionId, setLockedActionId] = useState("");
  const [aiMessages, setAiMessages] = useState<Array<{ role: "ai" | "user"; content: string }>>([
    { role: "ai", content: "我会在这里汇总卡片动作、命令上下文和失败原因。" },
  ]);
  const [aiDraft, setAiDraft] = useState("");
  const captureTitleRef = useRef<HTMLInputElement | null>(null);
  const drawerResizeRef = useRef({ active: false, startX: 0, startWidth: 760 });
  const markdownEditorRef = useRef<HTMLTextAreaElement | null>(null);
  const activeFilterRef = useRef<HTMLDivElement | null>(null);
  const filterDetailsRef = useRef<HTMLDetailsElement | null>(null);
  const defaultSprintSelectionKey = useRef("");
  const pendingMarkdownSelectionRef = useRef<{ start: number; end: number } | null>(null);
  const issues = context?.issues ?? [];
  const availableWorkspaces = context?.workspaces ?? [];
  const [sessionFallbackUser, setSessionFallbackUser] = useState<FrontendUser>(() => fallbackUserFromSession());
  const activeUser = context?.currentUser ?? sessionFallbackUser;
  const sprintOptions = context?.sprintOptions || context?.sprint_options || [];
  const sprintOptionDetails = context?.sprintOptionDetails || context?.sprint_option_details || [];
  const sprintMetrics = context?.sprintMetrics || context?.sprint_metrics;
  const currentIterationCapacity = context?.currentIterationCapacity || context?.current_iteration_capacity || [];

  const isEditableDocument = (state: DrawerState): state is Extract<DrawerState, { type: "markdown" }> => (
    state.type === "markdown" && !project?.readonly && canEditDocument(state.document)
  );

  const isTaskToggleDocument = (state: DrawerState): state is Extract<DrawerState, { type: "markdown" }> => (
    state.type === "markdown" && !project?.readonly && canToggleTaskDocument(state.document)
  );

  const isMutableMarkdownDrawer = (state: DrawerState): state is Extract<DrawerState, { type: "markdown" }> => (
    state.type === "markdown" && !project?.readonly && canMutateMarkdownDocument(state.document)
  );

  const isDirtyMarkdownDrawer = useCallback((state: DrawerState = drawer) => (
    isMutableMarkdownDrawer(state) && state.dirty && composeMarkdownContent(state.content, state.draft) !== state.content
  ), [drawer, project?.readonly]);
  const isCurrentMarkdownDirty = isDirtyMarkdownDrawer(drawer);

  useEffect(() => {
    const pendingSelection = pendingMarkdownSelectionRef.current;
    if (!pendingSelection || drawer.type !== "markdown" || drawer.mode === "preview") return;
    pendingMarkdownSelectionRef.current = null;
    requestAnimationFrame(() => {
      const editor = markdownEditorRef.current;
      if (!editor) return;
      editor.focus();
      editor.setSelectionRange(pendingSelection.start, pendingSelection.end);
    });
  }, [drawer]);

  const closeDrawer = useCallback(() => {
    const dirtyName = drawer.type === "markdown" ? drawer.document.name : "文档";
    if (isDirtyMarkdownDrawer() && !window.confirm(`${dirtyName} 有未保存修改，确认关闭？`)) return;
    setIsDrawerFullscreen(false);
    documentEpoch.current++; documentFlight.current = null;
    setDrawer({ type: "none" });
  }, [drawer, isDirtyMarkdownDrawer]);

  const beginDrawerResize = (event: MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    if (isDrawerFullscreen) return;
    drawerResizeRef.current = { active: true, startX: event.clientX, startWidth: drawerWidth };
    document.body.classList.add("rc-resizing-drawer");
  };

  const loadContext = useCallback((mode: "initial" | "refresh" = "initial"): Promise<void> => {
    const key = JSON.stringify([requestedSpace.current || projectRef.current?.space_id || "initial", projectRef.current?.repository_id || ""]);
    if (contextFlight.current?.key === key && !contextController.current?.signal.aborted) return contextFlight.current.promise;
    const run = async () => {
    const epoch = ++requestEpoch.current;
    contextController.current?.abort();
    const controller = new AbortController(); contextController.current = controller;
    const current = () => epoch === requestEpoch.current && !controller.signal.aborted;
    if (mode === "initial") setIsLoadingContext(true); else setIsRefreshingContext(true);
    try {
      const username = readFrontendSession()?.username;
      if (isWorkflowDemoMode()) {
        const next = buildWorkflowDemoContext(username);
        setContext(next); setWorkspace(getStoredWorkspace(next.workspaces, next.selectedWorkspaceId));
        setSessionFallbackUser(next.currentUser); return;
      }
      const directory = await governanceRequest<{ projects: Project[]; workspaces: Workspace[]; current_user: FrontendUser }>("/api/v1/requirement-center/projects", { signal: controller.signal });
      if (!current()) return;
      if (!Array.isArray(directory.projects)) throw new Error("项目目录响应不兼容，请刷新或联系管理员完成协同升级");
      setProjects(directory.projects);
      const directoryContext = normalizeContext({ ...directory, issues: [] } as unknown as RequirementCenterContext, username);
      const preferred = requestedSpace.current || new URLSearchParams(window.location.search).get("space_id") || getStoredWorkspace(directoryContext.workspaces, "").workspaceId;
      const repository = projectRef.current?.repository_id || new URLSearchParams(window.location.search).get("repository_id");
      const selected = directory.projects.find(p => p.space_id === preferred && p.repository_id === repository)
        || directory.projects.find(p => p.space_id === preferred) || (!requestedSpace.current ? directory.projects[0] : undefined);
      setSessionFallbackUser(directoryContext.currentUser);
      setWorkspace(directoryContext.workspaces.find(w => w.workspaceId === (selected?.space_id || preferred)) || emptyWorkspace);
      if (projectRef.current && (selected?.space_id !== projectRef.current.space_id || selected?.repository_id !== projectRef.current.repository_id)) {
        documentEpoch.current++; documentFlight.current = null; revisionRef.current = "";
        setContext(null); setDrawer({ type: "none" }); setErrorDetails(null); setLastSuccess("");
      }
      setProject(selected || null); projectRef.current = selected || null;
      if (contextFlight.current) contextFlight.current.key = JSON.stringify([requestedSpace.current || selected?.space_id || "initial", selected?.repository_id || ""]);
      if (!selected) { setContext(directoryContext); setSyncLabel("当前空间尚未绑定本地项目"); setContextError(""); return; }
      const data = await governanceRequest<RequirementCenterContext & { snapshot_revision: string }>(scopedUrl("/api/v1/requirement-center/context", selected), { signal: controller.signal });
      if (!current()) return;
      const next = normalizeContext(data, username);
      setWorkspace(next.workspaces.find(w => w.workspaceId === selected.space_id) || emptyWorkspace);
      if (!next.workspaces.length) window.localStorage.removeItem("moonbox.workspace");
      next.selectedWorkspaceId = selected.space_id;
      setContext(next); // Visibility can change without a file revision change.
      const opened = drawerRef.current;
      if (opened.type === "markdown" && !next.issues.some(issue => issue.id === opened.issue.id)) {
        documentEpoch.current++; documentFlight.current = null; setDrawer({ type: "none" }); setErrorDetails(null);
      }
      if (opened.type === "markdown" && next.issues.some(issue => issue.id === opened.issue.id) && (revisionRef.current !== data.snapshot_revision || opened.error) && !opened.loading && !opened.saving) {
        const docEpoch = documentEpoch.current;
        try {
          const latest = await governanceRequest<{ content: string; version: string }>(scopedUrl(opened.document.url || `/api/v1/requirement-center/issues/${opened.issue.id}/documents/${opened.document.name}`, selected), { signal: controller.signal });
          if (!current()) return;
          if (docEpoch === documentEpoch.current) setDrawer(value => {
            if (value.type !== "markdown" || value.document !== opened.document || value.saving) return value;
            if (latest.version === value.version) return { ...value, error: "", failure: undefined, readBlocked: false };
            if (value.dirty) return { ...value, readBlocked: true, error: "项目文档已有新版本；当前草稿已保留，旧基准保存将被拒绝。请复制草稿后重新打开核对。" };
            return { ...value, content: latest.content, draft: parseMarkdownFrontmatter(latest.content).body, version: latest.version, error: "", readBlocked: false, failure: undefined };
          });
        } catch (error) {
          if (!current()) return;
          if (docEpoch === documentEpoch.current) setDrawer(value => value.type === "markdown" && value.document === opened.document ? { ...value, ...(error instanceof GovernanceError && [401,403].includes(error.status) ? {content: "", draft: "", dirty: false} : {}), error: "文档暂时无法加载", readBlocked: true, failure: readFailure(error) } : value);
        }
      }
      revisionRef.current = data.snapshot_revision;
      setContextError(""); setContextFailure(null); setLastSuccess(new Date().toLocaleTimeString()); setSyncLabel("已同步 · " + new Date().toLocaleTimeString()); pollFailures.current = 0; pollPaused.current = false;
    } catch (error) {
      if (!current()) return;
      pollFailures.current++;
      const denied = error instanceof GovernanceError && [401, 403].includes(error.status);
      if (denied || mode === "initial") setContext(null);
      if (denied) { setProject(null); projectRef.current = null; documentEpoch.current++; setDrawer({ type: "none" }); setErrorDetails(null); revisionRef.current = ""; }
      setSyncLabel(denied ? "项目访问权限已失效" : "同步失败，将自动重试");
      if (error instanceof GovernanceError && error.status === 401) {
        clearFrontendSession(); clearAdminSession(); setSessionFallbackUser(emptyUser);
        window.history.replaceState(null, "", "/login"); window.dispatchEvent(new PopStateEvent("popstate"));
      }
      if (denied || mode === "initial") setContextError("需求中心数据暂时不可用：" + (error instanceof Error ? error.message : "项目暂不可用"));
      setContextFailure(readFailure(error)); pollPaused.current = readFailure(error).kind === "source_invalid";
    } finally {
      if (current()) { setIsLoadingContext(false); setIsRefreshingContext(false); }
    }
    };
    const flight = { key, promise: Promise.resolve() };
    contextFlight.current = flight;
    flight.promise = run().finally(() => { if (contextFlight.current === flight) contextFlight.current = null; });
    return flight.promise;
  }, []);

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    let stopped = false;
    const poll = async () => {
      if (!document.hidden && !pollPaused.current) await loadContext("refresh");
      if (!stopped) timer = setTimeout(poll, Math.min(30000, 3000 * 2 ** Math.min(pollFailures.current, 3)));
    };
    void loadContext().then(() => { if (!stopped) timer = setTimeout(poll, 3000); });
    const focus = () => { if (!document.hidden && !pollPaused.current) void loadContext("refresh"); };
    window.addEventListener("focus", focus); document.addEventListener("visibilitychange", focus);
    return () => { stopped = true; clearTimeout(timer); contextController.current?.abort(); window.removeEventListener("focus", focus); document.removeEventListener("visibilitychange", focus); };
  }, [loadContext]);


  useEffect(() => {
    const closeOnEscape = (event: globalThis.KeyboardEvent) => {
      if (event.key !== "Escape" || document.querySelector('[data-testid="rc-error-details-dialog"]')) return;
      if (openFilter) {
        setOpenFilter(null);
        filterDetailsRef.current?.removeAttribute("open");
        return;
      }
      captureController.current?.abort(); captureController.current = null;
      setCaptureBusy(false); setCaptureOpen(false);
      setAgentOpen(false);
      setChoiceDialog({ type: "none" });
      setActionDialog({ type: "none" });
      setArchiveDialog({ type: "none" });
      closeDrawer();
    };
    document.addEventListener("keydown", closeOnEscape);
    return () => document.removeEventListener("keydown", closeOnEscape);
  }, [closeDrawer, openFilter]);

  useEffect(() => {
    if (!openFilter) return;
    const closeOnOutsidePointer = (event: globalThis.MouseEvent) => {
      const target = event.target;
      if (target instanceof Node && (activeFilterRef.current?.contains(target) || filterDetailsRef.current?.contains(target))) return;
      setOpenFilter(null);
      filterDetailsRef.current?.removeAttribute("open");
    };
    document.addEventListener("mousedown", closeOnOutsidePointer, true);
    return () => document.removeEventListener("mousedown", closeOnOutsidePointer, true);
  }, [openFilter]);

  useEffect(() => {
    if (actionDialog.type === "none" || actionDialog.ready) return;
    if (!["analysis", "sprint", "opsx"].includes(actionDialog.type)) {
      setActionDialog((current) => current.type === actionDialog.type ? { ...current, ready: true } : current);
      return;
    }
    const timer = window.setTimeout(() => {
      setActionDialog((current) => current.type === actionDialog.type ? { ...current, ready: true } : current);
    }, actionDialog.type === "sprint" ? 650 : 900);
    return () => window.clearTimeout(timer);
  }, [actionDialog]);

  useEffect(() => {
    const handleResizeMove = (event: globalThis.MouseEvent) => {
      if (!drawerResizeRef.current.active) return;
      const delta = drawerResizeRef.current.startX - event.clientX;
      setDrawerWidth(Math.min(760, Math.max(420, drawerResizeRef.current.startWidth + delta)));
    };
    const stopResize = () => {
      drawerResizeRef.current.active = false;
      document.body.classList.remove("rc-resizing-drawer");
    };
    document.addEventListener("mousemove", handleResizeMove);
    document.addEventListener("mouseup", stopResize);
    return () => {
      document.removeEventListener("mousemove", handleResizeMove);
      document.removeEventListener("mouseup", stopResize);
      document.body.classList.remove("rc-resizing-drawer");
    };
  }, []);



  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(""), 2200);
    return () => window.clearTimeout(timer);
  }, [toast]);

  useEffect(() => {
    if (!captureOpen) return;
    window.setTimeout(() => captureTitleRef.current?.focus(), 0);
  }, [captureOpen]);

  useEffect(() => {
    if (!captureOpen) return;
    const target = projectRef.current;
    setCaptureReady(null);
    if (!target) { setCaptureReady({ ready: false, reason: "当前项目未连接" }); return; }
    const controller = new AbortController();
    let disposed = false;
    const timer = window.setTimeout(() => controller.abort(), 10000);
    governanceRequest<{ ready: boolean; reason: string }>(scopedUrl("/api/v1/requirement-center/capture-readiness", target), { signal: controller.signal })
      .then(result => { if (!controller.signal.aborted) setCaptureReady(result); })
      .catch(() => { if (!controller.signal.aborted) setCaptureReady({ ready: false, reason: "暂时无法检查写入服务，请刷新状态" }); })
      .finally(() => window.clearTimeout(timer));
    controller.signal.addEventListener("abort", () => { if (!disposed) setCaptureReady({ ready: false, reason: "写入服务检查超时，请刷新状态" }); }, { once: true });
    return () => { disposed = true; window.clearTimeout(timer); controller.abort(); };
  }, [captureOpen, captureCheck, project?.space_id, project?.repository_id]);

  const stageOptions: MultiFilterOption[] = useMemo(() => stages.map((stage) => ({
    value: stage.id,
    label: stage.title,
    meta: stage.subtitle,
  })), []);
  const owners = useMemo(() => {
    const names = Array.from(new Set(issues.map((issue) => issue.owner).filter(Boolean)));
    return names.sort((a, b) => {
      if (a === activeUser.name) return -1;
      if (b === activeUser.name) return 1;
      return a.localeCompare(b, "zh-Hans-CN");
    });
  }, [issues, activeUser.name]);
  const ownerOptions: MultiFilterOption[] = useMemo(() => owners.map((owner) => ({
    value: owner,
    label: owner,
    meta: owner === activeUser.name ? "当前用户" : undefined,
  })), [owners, activeUser.name]);
  const levelOptions: MultiFilterOption[] = useMemo(() => [
    ...(["P0", "P1", "P2", "P3"] as const).map((priority) => ({
      value: `requirement:${priority}`,
      label: `${priority} ${{ P0: "最高", P1: "高", P2: "中", P3: "低" }[priority]}`,
      group: "需求优先级",
    })),
    ...(["blocker", "critical", "high", "medium", "low"] as const).map((severity) => ({
      value: `bug:${severity}`,
      label: `${severity} ${{ blocker: "阻断", critical: "严重", high: "高", medium: "中", low: "低" }[severity]}`,
      group: "缺陷严重性",
    })),
  ], []);
  const captureOwners = ["产品团队", "研发团队", "设计团队", "未分配"];
  const captureSources = [
    { value: "explore", label: "explore · 前置探索" },
    { value: "user-feedback", label: "user-feedback · 用户反馈" },
    { value: "internal", label: "internal · 内部提出" },
    { value: "incident", label: "incident · 故障复盘" },
  ];
  const sprints = useMemo(() => {
    const sprintSet = new Set([...sprintOptions, ...issues.map((issue) => visibleSprintId(issue)).filter((value): value is string => Boolean(value))]);
    return Array.from(sprintSet).sort((a, b) => {
      const aNumber = Number(a.match(/^sprint-(\d+)$/)?.[1] || "-1");
      const bNumber = Number(b.match(/^sprint-(\d+)$/)?.[1] || "-1");
      if (aNumber !== bNumber) return bNumber - aNumber;
      return a.localeCompare(b);
    });
  }, [issues, sprintOptions]);
  const sprintStatusById = useMemo(() => {
    const entries = new Map<string, SprintFilterOption>();
    sprintOptionDetails.forEach((option) => {
      const id = normalizeSprintOptionId(option);
      if (id) entries.set(id, option);
    });
    return entries;
  }, [sprintOptionDetails]);
  const currentSprintIds = useMemo(() => sprintOptionDetails
    .filter(isCurrentSprintOption)
    .map(normalizeSprintOptionId)
    .filter((value): value is string => Boolean(value)),
    [sprintOptionDetails],
  );
  const currentSprintSet = useMemo(() => new Set(currentSprintIds), [currentSprintIds]);
  const sprintOptionsForFilter: MultiFilterOption[] = useMemo(() => [
    ...sprints.map((sprint) => ({
      value: sprint,
      label: sprint,
      meta: currentSprintSet.has(sprint) ? "当前迭代" : undefined,
      statusLabel: sprintFilterStatusLabel(sprintStatusById.get(sprint)),
      warning: sprintStatusById.get(sprint)?.warning || null,
    })),
    {
      value: UNASSIGNED_SPRINT_FILTER_VALUE,
      label: "未纳入 Sprint",
      meta: "未纳入迭代范围",
      searchAliases: "no sprint none unassigned",
    },
  ], [sprints, sprintStatusById, currentSprintSet]);
  const effectiveSprintId = useCallback((issue: IssueCard) => {
    if (issue.sprintId) return issue.sprintId;
    const sprintId = visibleSprintId(issue);
    if (sprintId) return sprintId;
    return currentSprintIds.length === 1 && sprintVisibleStages.has(issue.stage) ? currentSprintIds[0] : "";
  }, [currentSprintIds]);
  const defaultSelectedSprints = useMemo(
    () => isWorkflowDemoMode() ? [] : [...currentSprintIds, UNASSIGNED_SPRINT_FILTER_VALUE],
    [currentSprintIds],
  );

  useEffect(() => {
    if (!context || isWorkflowDemoMode()) return;
    const key = [
      context.selectedWorkspaceId || projectRef.current?.space_id || "",
      projectRef.current?.repository_id || "",
      defaultSelectedSprints.join(","),
    ].join("|");
    if (defaultSprintSelectionKey.current === key) return;
    defaultSprintSelectionKey.current = key;
    setSelectedSprints(defaultSelectedSprints);
  }, [context, defaultSelectedSprints]);

  const selectedForFilter = (key: MultiFilterKey) => {
    if (key === "stage") return selectedStages;
    if (key === "owner") return selectedOwners;
    if (key === "level") return selectedLevels;
    return selectedSprints;
  };

  const setSelectedForFilter = (key: MultiFilterKey, values: string[]) => {
    if (key === "stage") setSelectedStages(values);
    else if (key === "owner") setSelectedOwners(values);
    else if (key === "level") setSelectedLevels(values);
    else setSelectedSprints(values);
  };

  const clearAllFilters = () => {
    setSearchQuery("");
    setTypeFilter("all");
    setSelectedStages([]);
    setSelectedOwners([]);
    setSelectedLevels([]);
    setSelectedSprints(defaultSelectedSprints);
    setFilterSearch({ stage: "", owner: "", level: "", sprint: "" });
    setOpenFilter(null);
    filterDetailsRef.current?.removeAttribute("open");
  };

  const sprintFilterIsDefault =
    selectedSprints.length === defaultSelectedSprints.length &&
    selectedSprints.every((sprint) => defaultSelectedSprints.includes(sprint));

  const filterSummary = (selected: string[], options: MultiFilterOption[], placeholder: string, defaultSummary?: string) => {
    if (!selected.length) return placeholder;
    if (defaultSummary) return defaultSummary;
    const labels = selected.map((value) => options.find((option) => option.value === value)?.label || value);
    if (labels.length <= 2 && labels.join("、").length <= 12) return labels.join("、");
    return `已选 ${labels.length} 项`;
  };

  const renderMultiFilter = (key: MultiFilterKey, label: string, placeholder: string, options: MultiFilterOption[]) => {
    const selected = selectedForFilter(key);
    const search = filterSearch[key].trim().toLowerCase();
    const visibleOptions = options.filter((option) => {
      const haystack = `${option.value} ${option.label} ${option.meta || ""} ${option.group || ""} ${option.searchAliases || ""}`.toLowerCase();
      return !search || haystack.includes(search);
    });
    const selectableVisibleOptions = visibleOptions.filter((option) => !option.disabled);
    const allVisibleSelected = selectableVisibleOptions.length > 0 && selectableVisibleOptions.every((option) => selected.includes(option.value));
    const groupedVisibleOptions = visibleOptions.reduce<Array<{ group?: string; options: MultiFilterOption[] }>>((groups, option) => {
      const last = groups[groups.length - 1];
      if (last && last.group === option.group) last.options.push(option);
      else groups.push({ group: option.group, options: [option] });
      return groups;
    }, []);
    const disabled = isLoadingContext || Boolean(contextError);
    return (
      <div className="rc-multi-filter" data-testid={`requirement-filter-${key}`} ref={openFilter === key ? activeFilterRef : undefined}>
        <button
          className={`rc-multi-filter-trigger ${openFilter === key ? "open" : ""} ${selected.length ? "selected" : ""}`}
          type="button"
          data-testid={`requirement-filter-trigger-${key}`}
          aria-expanded={openFilter === key}
          aria-controls={`requirement-filter-popover-${key}`}
          disabled={disabled}
          onClick={() => setOpenFilter(openFilter === key ? null : key)}
        >
          <span>{label}</span>
          <strong>{filterSummary(selected, options, placeholder, key === "sprint" && sprintFilterIsDefault ? "默认 Sprint 范围" : undefined)}</strong>
          <em aria-hidden="true">⌄</em>
        </button>
        {openFilter === key && (
          <div
            className="rc-multi-filter-popover"
            id={`requirement-filter-popover-${key}`}
            data-testid={`requirement-filter-popover-${key}`}
            role="group"
            aria-label={`${label}筛选选项`}
          >
            <label className="rc-multi-filter-search">
              <Search size={14} aria-hidden="true" />
              <input
                data-testid={`requirement-filter-search-${key}`}
                aria-label={`${label}候选项搜索`}
                value={filterSearch[key]}
                onChange={(event) => setFilterSearch({ ...filterSearch, [key]: event.target.value })}
                placeholder={`搜索${label}`}
              />
            </label>
            <div className="rc-multi-filter-options" data-testid={`requirement-filter-options-${key}`}>
              {groupedVisibleOptions.length ? groupedVisibleOptions.map((group) => (
                <div className="rc-multi-filter-group" key={group.group || "default"}>
                  {group.group && <p className="rc-multi-filter-group-label">{group.group}</p>}
                  {group.options.map((option) => {
                    const checked = selected.includes(option.value);
                    return (
                      <label
                        className={`rc-multi-filter-option ${checked ? "checked" : ""} ${option.disabled ? "disabled" : ""}`}
                        data-testid={`requirement-filter-option-${key}-${option.value}`}
                        key={option.value}
                      >
                        <input
                          type="checkbox"
                          checked={checked}
                          disabled={option.disabled}
                          onChange={() => {
                            const next = checked ? selected.filter((value) => value !== option.value) : [...selected, option.value];
                            setSelectedForFilter(key, next);
                          }}
                        />
                        <span>
                          <strong>
                            {option.label}
                            {key === "sprint" && option.statusLabel && (
                              <em className={`rc-sprint-status-pill ${sprintStatusClass(option.statusLabel)}`}>
                                {option.statusLabel}
                              </em>
                            )}
                            {option.meta && <small className="rc-multi-filter-inline-meta">{option.meta}</small>}
                          </strong>
                          {key === "sprint" && option.warning && <small>状态来源待核实</small>}
                        </span>
                      </label>
                    );
                  })}
                </div>
              )) : (
                <p className="rc-multi-filter-empty">没有匹配的候选项</p>
              )}
            </div>
            <footer className="rc-multi-filter-footer">
              <span>{selected.length ? `已选 ${selected.length} 项` : "未选择"}</span>
              <button
                type="button"
                data-testid={`requirement-filter-select-all-${key}`}
                disabled={!selectableVisibleOptions.length || allVisibleSelected}
                onClick={() => {
                  const next = Array.from(new Set([...selected, ...selectableVisibleOptions.map((option) => option.value)]));
                  setSelectedForFilter(key, next);
                }}
              >
                {search ? "全选当前结果" : "全选"}
              </button>
              <button
                type="button"
                data-testid={`requirement-filter-clear-${key}`}
                disabled={!selected.length}
                onClick={() => setSelectedForFilter(key, [])}
              >
                清空
              </button>
            </footer>
          </div>
        )}
      </div>
    );
  };

  const filteredCandidates = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    return issues.filter((issue) => {
      const sprintId = effectiveSprintId(issue);
      const explicitSprintId = issue.sprintId || visibleSprintId(issue) || "";
      const matchesType = typeFilter === "all" || issue.type === typeFilter;
      const matchesSearch =
        !query ||
        issue.id.toLowerCase().includes(query) ||
        issue.title.toLowerCase().includes(query) ||
        (issue.display_title ?? "").toLowerCase().includes(query) ||
        issue.related_changes?.some(change => change.id.toLowerCase().includes(query) || change.title?.toLowerCase().includes(query)) ||
        issue.owner.toLowerCase().includes(query) ||
        (stageTitleById.get(issue.stage) || issue.stage).toLowerCase().includes(query) ||
        issue.source.toLowerCase().includes(query) ||
        issue.documents.some((doc) => doc.toLowerCase().includes(query));
      const matchesStage = selectedStages.length === 0 || selectedStages.includes(issue.stage);
      const matchesOwner = selectedOwners.length === 0 || selectedOwners.includes(issue.owner);
      const levelValue = issueLevelFilterValue(issue);
      const matchesLevel = selectedLevels.length === 0 || selectedLevels.includes(levelValue);
      const matchesUnassignedSprint = !explicitSprintId && selectedSprints.includes(UNASSIGNED_SPRINT_FILTER_VALUE);
      const matchesDefaultCurrentSprint = !explicitSprintId && sprintFilterIsDefault && selectedSprints.includes(sprintId);
      const matchesSprint = issue.stage === "unknown" || selectedSprints.length === 0 || selectedSprints.includes(explicitSprintId) || matchesUnassignedSprint || matchesDefaultCurrentSprint;
      return matchesType && matchesSearch && matchesStage && matchesOwner && matchesLevel && matchesSprint;
    });
  }, [effectiveSprintId, issues, selectedLevels, selectedOwners, selectedSprints, selectedStages, searchQuery, sprintFilterIsDefault, typeFilter]);


  const filteredIssues = filteredCandidates.filter(issue => issue.stage !== "unknown");
  const diagnosticIssues = filteredCandidates.filter(issue => issue.stage === "unknown");

  const completionValue = (cardType: CardType) => {
    const scoped = filteredIssues.filter((issue) => issue.type === cardType);
    return {
      completed: scoped.filter((issue) => issue.stage === "done").length,
      total: scoped.length,
    };
  };
  const stats: MetricStat[] = [
    { label: "全部对象", value: filteredIssues.length, description: "当前筛选条件下可见的需求、Bug 和独立 Change 总数。" },
    { label: "需求", value: completionValue("requirement"), description: "当前筛选条件下，已完成需求数 / 需求总数。", testId: "requirement-completion-metric" },
    { label: "Bug", value: completionValue("bug"), description: "当前筛选条件下，已完成 Bug 数 / Bug 总数。", testId: "bug-completion-metric" },
    { label: "独立 Change", value: completionValue("change"), description: "当前筛选条件下，已完成独立 Change 数 / 独立 Change 总数。", testId: "change-completion-metric" },
    { label: "当前阻塞", value: filteredIssues.filter((issue) => issue.blocked).length, description: "当前筛选条件下存在阻塞提示的对象数量。" },
  ];
  const sprintMetricValue = {
    completed: sprintMetrics?.completed_count ?? sprintMetrics?.completedCount ?? 0,
    total: sprintMetrics?.total_count ?? sprintMetrics?.totalCount ?? 0,
    warning: sprintMetrics?.warning || "",
  };
  const sprintMetricState = isLoadingContext ? "loading" : contextError && !context ? "error" : sprintMetricValue.total === 0 ? "empty" : "ready";
  const activeFilterCount = [
    searchQuery.trim(),
    typeFilter !== "all",
    selectedStages.length,
    selectedOwners.length,
    selectedLevels.length,
    !sprintFilterIsDefault,
  ].filter(Boolean).length;



  const openIssueDetail = (issue: IssueCard) => {
    if (issue.type === "change") {
      const document = issueDocumentEntries(issue)[0];
      if (document) void openDocument(issue, document);
      else setToast("Change 文档缺失或归档版本待核实");
      return;
    }
    window.open(issueDetailUrl(issue), "_blank", "noopener,noreferrer");
  };

  const openDocument = async (issue: IssueCard, document: IssueDocument, focus?: ProgressFocus) => {
    if (isDirtyMarkdownDrawer() && !window.confirm("文档有未保存修改，确认打开另一份文档？")) return;
    const selectedProject = projectRef.current;
    const flightKey = JSON.stringify([selectedProject?.space_id, selectedProject?.repository_id, issue.id, document.url || document.name]);
    if (documentFlight.current === flightKey) return;
    const epoch = ++documentEpoch.current;
    const mode = document.openMode || document.open_mode;
    if (document.status && document.status !== "available") {
      setToast(`${document.name} 暂不可用，未触发卡片流转`);
      return;
    }
    if (document.type === "html" || mode === "new-tab") {
      if (document.htmlContent) {
        const demoUrl = URL.createObjectURL(new Blob([document.htmlContent], { type: "text/html" }));
        window.open(demoUrl, "_blank", "noopener,noreferrer");
        window.setTimeout(() => URL.revokeObjectURL(demoUrl), 30_000);
        return;
      }
      try {
        documentFlight.current = flightKey;
        if (!selectedProject) throw new Error("项目未连接，无法预览 HTML 文档");
        if (!document.url) throw new Error("HTML 预览地址缺失");
        const html = await governanceTextRequest(scopedUrl(document.url, selectedProject));
        if (epoch !== documentEpoch.current || selectedProject.space_id !== projectRef.current?.space_id || selectedProject.repository_id !== projectRef.current?.repository_id) return;
        const previewUrl = URL.createObjectURL(new Blob([html], { type: "text/html" }));
        const opened = window.open(previewUrl, "_blank", "noopener,noreferrer");
        if (!opened) {
          URL.revokeObjectURL(previewUrl);
          setToast("浏览器拦截了 HTML 预览窗口，请允许弹出窗口后重试");
          return;
        }
        window.setTimeout(() => URL.revokeObjectURL(previewUrl), 30_000);
      } catch (error) {
        if (epoch !== documentEpoch.current) return;
        setToast(error instanceof GovernanceError ? `HTML 预览失败：${error.message}` : error instanceof Error ? `HTML 预览失败：${error.message}` : "HTML 预览失败");
      } finally {
        if (epoch === documentEpoch.current && documentFlight.current === flightKey) documentFlight.current = null;
      }
      return;
    }
    setMarkdownUploadState("idle");
    setMarkdownUploadError("");
    setMarkdownMetadataOpen(false);
    setIsDrawerFullscreen(false);
    setDrawer({ type: "markdown", issue, document, focus, content: "", draft: "", loading: true, saving: false, error: "", mode: "preview", dirty: false });
    if (document.content) {
      setDrawer({
        type: "markdown",
        issue,
        document,
        focus,
        content: document.content,
        draft: parseMarkdownFrontmatter(document.content).body,
        loading: false,
        saving: false,
        error: "",
        mode: "preview",
        dirty: false,
      });
      return;
    }
    try {
      documentFlight.current = flightKey;
      if (!selectedProject) throw new Error("项目未连接");
      const data = await governanceRequest<{ content: string; version: string }>(scopedUrl(document.url || `/api/v1/requirement-center/issues/${issue.id}/documents/${document.name}`, selectedProject));
      if (epoch !== documentEpoch.current || selectedProject.space_id !== projectRef.current?.space_id || selectedProject.repository_id !== projectRef.current?.repository_id) return;
      setDrawer({ type: "markdown", issue, document, focus, version: data.version, content: data.content, draft: parseMarkdownFrontmatter(data.content).body, loading: false, saving: false, error: "", mode: "preview", dirty: false });
    } catch (error) {
      if (epoch !== documentEpoch.current) return;
      setDrawer({ type: "markdown", issue, document, focus, content: "", draft: "", loading: false, saving: false, error: "文档暂时无法加载", readBlocked: true, failure: readFailure(error), mode: "preview", dirty: false });
    } finally {
      if (epoch === documentEpoch.current && documentFlight.current === flightKey) documentFlight.current = null;
    }
  };

  const openTasksAt = (issue: IssueCard, focus: ProgressFocus) => {
    const document = issueDocumentEntries(issue).find(entry => entry.name === "tasks.md");
    if (!document) { setToast(`${issue.id} 未关联 tasks.md，无法打开${progressFocusLabel[focus]}。`); return; }
    void openDocument(issue, document, focus);
  };

  const saveMarkdownDocument = async () => {
    if (drawer.type !== "markdown" || !isMutableMarkdownDrawer(drawer) || drawer.saving || contextFailure || drawer.readBlocked) return;
    const currentDrawer = drawer;
    const saveProject = projectRef.current!;
    setDrawer({ ...currentDrawer, saving: true, error: "" });
    try {
      const contentToSave = composeMarkdownContent(currentDrawer.content, currentDrawer.draft);
      if (currentDrawer.issue.id.startsWith("DEMO-") && typeof currentDrawer.document.content === "string") {
        setDrawer({
          ...currentDrawer,
          content: contentToSave,
          draft: parseMarkdownFrontmatter(contentToSave).body,
          saving: false,
          error: "",
          mode: "preview",
          dirty: false,
          savedAt: "刚刚保存",
        });
        setToast(`${currentDrawer.document.name} 已保存`);
        return;
      }
      const token = readAccessToken();
      const baseUrl = currentDrawer.document.url || `/api/v1/requirement-center/issues/${currentDrawer.issue.id}/documents/${currentDrawer.document.name}`;
      const response = await fetch(scopedUrl(baseUrl, saveProject, isTaskToggleDocument(currentDrawer) ? "/tasks" : ""), {
        method: "PUT",
        headers: {
          accept: "application/json",
          "content-type": "application/json",
          ...(token ? { authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ content: contentToSave, expected_version: currentDrawer.version, idempotency_key: crypto.randomUUID() }),
      });
      if (!response.ok) {
        if (response.status === 403) {
          let detail = "";
          try {
            const errorEnvelope = (await response.json()) as { detail?: unknown };
            detail = typeof errorEnvelope.detail === "string" ? errorEnvelope.detail : "";
          } catch {
            detail = "";
          }
          throw new Error(detail || documentCapability(currentDrawer.document).reason);
        }
        if (response.status === 404) throw new Error("文档不存在或已移动");
        if (response.status === 422) throw new Error("文档内容为空或超过长度限制，内容已保留");
        let detail = "";
        try {
          const errorEnvelope = (await response.json()) as { detail?: unknown };
          detail = typeof errorEnvelope.detail === "string" ? errorEnvelope.detail : "";
        } catch {
          detail = "";
        }
        throw new Error(detail || "文档保存失败，内容已保留");
      }
      const queued = (await response.json()) as ApiEnvelope<Application>;
      const result = await waitApplication(queued.data.id);
      if (result.state === "conflict") captureAttempt.current = null;
      if (result.state !== "applied") throw new Error(result.state === "recovery_blocked" ? "应用已暂停，需要管理员处理恢复；草稿已保留" : "文件版本冲突或维护窗口不可用；草稿已保留");
      const saved = await governanceRequest<{ content: string; version: string }>(scopedUrl(baseUrl, saveProject));
      setDrawer(latest => latest.type === "markdown" && latest.document === currentDrawer.document ? { ...latest, content: saved.content, version: saved.version, draft: latest.draft === currentDrawer.draft ? parseMarkdownFrontmatter(saved.content).body : latest.draft, saving: false, error: "", mode: latest.draft === currentDrawer.draft ? "preview" : latest.mode, dirty: latest.draft !== currentDrawer.draft, savedAt: "刚刚保存" } : latest);
      setToast(`${currentDrawer.document.name} 已保存`);
    } catch (error) {
      const message = sanitizeFeedback(error instanceof Error ? error.message : "文档保存失败，内容已保留");
      setDrawer((latest) => (latest.type === "markdown" && latest.document === currentDrawer.document ? { ...latest, saving: false, error: message } : latest));
      setToast(message);
    }
  };

  const updateMarkdownDraft = (value: string) => {
    setDrawer((current) => isEditableDocument(current) ? { ...current, draft: value, dirty: true, savedAt: undefined } : current);
  };

  const toggleMarkdownTask = (taskToToggle: number, checked: boolean) => {
    setDrawer((current) => {
      if (!isMutableMarkdownDrawer(current)) return current;
      const lines = current.draft.split("\n");
      let taskIndex = 0;
      const draft = lines.map((line) => {
        if (!/^[-*]\s+\[( |x|X)\]\s+/.test(line)) return line;
        if (taskIndex !== taskToToggle) {
          taskIndex += 1;
          return line;
        }
        taskIndex += 1;
        return line.replace(/^([-*]\s+\[)( |x|X)(\]\s+.*)$/, `$1${checked ? "x" : " "}$3`);
      }).join("\n");
      return { ...current, draft, dirty: true, savedAt: undefined };
    });
  };

  const setMarkdownMode = (mode: MarkdownViewMode) => {
    if (drawer.type !== "markdown") return;
    if (mode !== "preview" && !isEditableDocument(drawer)) return;
    setMarkdownUploadState("idle");
    setMarkdownUploadError("");
    setDrawer({ ...drawer, draft: mode === "preview" ? drawer.draft : drawer.draft || parseMarkdownFrontmatter(drawer.content).body, mode, savedAt: mode === "preview" ? drawer.savedAt : undefined });
  };

  const attemptMarkdownImageUpload = () => {
    setMarkdownUploadState("failed");
    setMarkdownUploadError("文档图片上传接口暂未启用；本次不会写入本机路径或私有对象地址。");
  };

  const insertMarkdownSnippet = (kind: keyof typeof markdownToolbarSnippets) => {
    if (drawer.type !== "markdown" || !isEditableDocument(drawer)) return;
    const currentDraft = drawer.mode === "preview" ? parseMarkdownFrontmatter(drawer.content).body : drawer.draft;
    const editor = markdownEditorRef.current;
    const start = editor ? editor.selectionStart : currentDraft.length;
    const end = editor ? editor.selectionEnd : currentDraft.length;
    const boundedStart = Math.max(0, Math.min(start, currentDraft.length));
    const boundedEnd = Math.max(boundedStart, Math.min(end, currentDraft.length));
    const beforeSelection = currentDraft.slice(0, boundedStart);
    const selection = currentDraft.slice(boundedStart, boundedEnd);
    const afterSelection = currentDraft.slice(boundedEnd);
    const prefix = beforeSelection && !beforeSelection.endsWith("\n") ? "\n" : "";
    const suffix = afterSelection && !afterSelection.startsWith("\n") ? "\n" : "";
    let inserted = "";
    let nextSelectionStart = 0;
    let nextSelectionEnd = 0;
    if (kind === "table") {
      inserted = `${prefix}${markdownToolbarSnippets.table.text}${suffix}`;
      nextSelectionStart = boundedStart + prefix.length + markdownToolbarSnippets.table.selectionStart;
      nextSelectionEnd = boundedStart + prefix.length + markdownToolbarSnippets.table.selectionEnd;
    } else {
      const snippet = markdownToolbarSnippets[kind];
      const body = selection || snippet.placeholder;
      inserted = `${prefix}${snippet.before}${body}${snippet.after}${suffix}`;
      nextSelectionStart = boundedStart + prefix.length + snippet.before.length;
      nextSelectionEnd = nextSelectionStart + body.length;
    }
    setMarkdownUploadError("");
    pendingMarkdownSelectionRef.current = { start: nextSelectionStart, end: nextSelectionEnd };
    setDrawer({ ...drawer, draft: `${beforeSelection}${inserted}${afterSelection}`, mode: drawer.mode === "preview" ? "split" : drawer.mode, dirty: true, savedAt: undefined });
  };

  const cancelMarkdownDraft = () => {
    if (drawer.type !== "markdown") return;
    setMarkdownUploadState("idle");
    setMarkdownUploadError("");
    setDrawer({ ...drawer, draft: parseMarkdownFrontmatter(drawer.content).body, mode: "preview", dirty: false, savedAt: undefined });
  };

  const submitCapture = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (captureController.current || !captureReady?.ready || contextFailure) return;
    const title = captureForm.title.trim();
    if (!title) { setCaptureError("标题不能为空"); return; }
    const target = projectRef.current;
    if (!target || target.readonly || target.status !== "connected") {
      setCaptureError("当前项目未连接或没有写入权限"); return;
    }
    const { priority, severity, ...captureFields } = captureForm;
    const payload = { ...captureFields, title, ...(captureForm.type === "bug" ? { severity } : { priority }) };
    const fingerprint = JSON.stringify([target.space_id, target.repository_id, payload]);
    if (captureAttempt.current?.fingerprint !== fingerprint) {
      captureAttempt.current = { fingerprint, key: crypto.randomUUID() };
    }
    const controller = new AbortController(); captureController.current = controller;
    const timer = window.setTimeout(() => controller.abort(), 30000);
    const active = () => captureController.current === controller &&
      projectRef.current?.space_id === target.space_id && projectRef.current?.repository_id === target.repository_id;
    setCaptureBusy(true); setCaptureError("");
    try {
      const queued = await governanceRequest<Application>(scopedUrl("/api/v1/requirement-center/captures", target), {
        method: "POST", body: JSON.stringify({ ...payload, idempotency_key: captureAttempt.current.key }), signal: controller.signal,
      });
      const result = await waitApplication(queued.id, controller.signal);
      if (!active()) return;
      if (result.state === "conflict") captureAttempt.current = null;
      if (result.state !== "applied") throw new Error(result.state === "recovery_blocked"
        ? "创建需要恢复，请联系项目管理员；输入已保留" : "创建未完成，请检查项目写入条件；输入已保留");
      const data = await governanceRequest<RequirementCenterContext & { snapshot_revision: string }>(
        scopedUrl("/api/v1/requirement-center/context", target), { signal: controller.signal });
      if (!active()) return;
      setContext(normalizeContext(data, readFrontendSession()?.username));
      revisionRef.current = data.snapshot_revision;
      captureAttempt.current = null;
      setCaptureForm({ type: "requirement", title: "", priority: "P1", severity: "medium", description: "", owner: "产品团队", source: "explore" });
      setCaptureOpen(false); setToast("Capture 已创建并插入采集池");
    } catch (error) {
      if (active()) setCaptureError(controller.signal.aborted ? "等待超时，输入已保留；再次提交将查询同一次创建结果" : error instanceof Error ? error.message : "创建失败，输入已保留");
    } finally {
      window.clearTimeout(timer);
      if (captureController.current === controller) { captureController.current = null; setCaptureBusy(false); }
    }
  };

  const handleCaptureKeyDown = (event: KeyboardEvent<HTMLFormElement>) => {
    if (!(event.metaKey || event.ctrlKey) || event.key !== "Enter") return;
    event.preventDefault();
    if (typeof event.currentTarget.requestSubmit === "function") {
      event.currentTarget.requestSubmit();
    }
  };

  const appendAiMessage = (content: string, role: "ai" | "user" = "ai") => {
    setAiMessages((current) => [...current, { role, content: sanitizeFeedback(content) }]);
  };

  const sendAiMessage = () => {
    const content = aiDraft.trim();
    if (!content) return;
    appendAiMessage(content, "user");
    setAiDraft("");
    appendAiMessage("已收到，我会结合当前看板上下文给出下一步建议。");
  };

  const handleAiKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key !== "Enter" || event.shiftKey) return;
    event.preventDefault();
    sendAiMessage();
  };

  const validateImportedFile = (file: File | undefined, dialog: ChoiceDialog) => {
    if (!file || dialog.type === "none") return "";
    const name = file.name.toLowerCase();
    if (dialog.type === "generation") {
      const expected = dialog.issue.type === "requirement" ? "requirement.md" : "bug.md";
      return name === expected ? "" : `仅允许导入单个 ${expected}`;
    }
    if (dialog.type === "completion") {
      return name.endsWith(".zip") || name.endsWith(".md") ? "" : "仅允许 ZIP 或约定 Markdown 文件";
    }
    return "";
  };

  const openIssueActionDialog = (issue: IssueCard, auxAction?: AuxiliaryAction) => {
    if (contextFailure) { setToast("请先重新加载项目数据"); return; }
    if (issue.stage === "unknown") return;
    const blocked = blockedTip(issue.stage, issue, issueAction(issue));
    if (!auxAction && blocked) { setToast(blocked); return; }
    if (issue.stage === "development" && !auxAction) { openTasksAt(issue, "development"); return; }
    if (!isWorkflowDemoMode()) {
      if (issue.type !== "requirement" || issue.stage !== "capture" || auxAction) { setToast("当前仅支持采集需求的生成动作"); return; }
      const target = projectRef.current;
      if (!target || target.readonly || lockedActionId) { setToast("项目不可写或正在准备会话"); return; }
      setLockedActionId(issue.id);
      void governanceRequest<{ conversation_id: string; prompt: string }>("/api/v1/chat/governance-preparations", { method: "POST", body: JSON.stringify({ space_id: target.space_id, repository_id: target.repository_id, object_id: issue.id, action: "req-generate" }) }).then(result => {
        sessionStorage.setItem(`moonbox.governance.prompt:${result.conversation_id}`, result.prompt);
        window.history.pushState(null, "", `/chat?space_id=${encodeURIComponent(target.space_id)}&conversation_id=${encodeURIComponent(result.conversation_id)}`);
        window.dispatchEvent(new PopStateEvent("popstate"));
      }).catch(error => setToast(error.message)).finally(() => setLockedActionId(""));
      return;
    }
    const action = auxAction || issueAction(issue);
    if (actionDisabledReason(action as IssueAction)) {
      appendAiMessage(`${issue.id} 前置条件不满足：${actionDisabledReason(action as IssueAction)}`);
      setDrawer({ type: "ai", issue });
      return;
    }
    const type = actionDialogType(issue, action);
    const sprintEstimate = issueSprintEstimate(issue);
    const sprintModels = sprintOptionModels(sprintOptions, sprintEstimate, sprintOptionDetails);
    const defaultSprintId = firstSelectableSprintId(sprintModels) || sprintModels[0]?.id || "sprint-auto";
    setAgentOpen(false);
    setChoiceDialog({ type: "none" });
    setActionDialog({
      type,
      issue,
      tab: type === "sprint" ? "existing" : "ai",
      ready: !["analysis", "sprint", "opsx"].includes(type),
      running: false,
      fileName: "",
      sprintId: type === "sprint" ? defaultSprintId : sprintOptions[0] || "sprint-auto",
      newSprintId: type === "sprint" ? nextSprintId(sprintOptions) : "",
      sprintEstimate,
      error: "",
      adoptedPointIndexes: type === "analysis" ? [0, 1, 2] : [],
    });
  };

  const closeActionDialog = () => {
    setActionDialog({ type: "none" });
  };

  const runIssueAction = async (issue: IssueCard, options?: { sprintId?: string; importedFile?: File; confirmed?: boolean }) => {
    const action = issueAction(issue);
    if (lockedActionId || contextFailure) return;
    const blocked = blockedTip(issue.stage, issue, action);
    if (blocked) {
      appendAiMessage(`${issue.id} 前置条件不满足：${blocked}`);
      setDrawer({ type: "ai", issue });
      return;
    }
    const choice = actionChoice(action, issue);
    if (choice && !options) {
      setChoiceDialog({ type: choice as ChoiceDialog["type"], issue, error: "" });
      return;
    }
    if (issue.stage === "development") {
      openTasksAt(issue, "development");
      return;
    }
    setLockedActionId(issue.id);
    appendAiMessage(`准备执行：${action.command}；上下文：${issue.id} / ${issue.title} / ${issue.type} / ${issue.stage}`);
    await new Promise((resolve) => window.setTimeout(resolve, 260));
    const targetStage = nextStage[issue.stage] || issue.stage;
    setContext((current) => current ? {
      ...current,
      issues: current.issues.map((item) => {
        if (item.id !== issue.id) return item;
        const documentPatch = appendTransitionDocuments(item, targetStage);
        const nextIssue = {
          ...item,
          ...documentPatch,
          stage: targetStage,
          sprintId: options?.sprintId || item.sprintId,
          updatedAt: "刚刚",
          blocked: undefined,
        };
        return {
          ...nextIssue,
          action: actionForStage(nextIssue, targetStage),
        };
      }),
    } : current);
    setLockedActionId("");
    setChoiceDialog({ type: "none" });
    setToast(`${issue.id} 已流转到 ${stages.find((stage) => stage.id === targetStage)?.title || targetStage}`);
    appendAiMessage(`执行成功：${action.command}，卡片已流转。`);
  };

  const saveAnalysisResult = (issue: IssueCard, adoptedCount: number) => {
    setContext((current) => current ? {
      ...current,
      issues: current.issues.map((item) => item.id === issue.id ? {
        ...item,
        documents: item.documents.includes("explore.md") ? item.documents : [...item.documents, "explore.md"],
        documentEntries: [
          ...issueDocumentEntries(item),
          ...(item.documents.includes("explore.md") ? [] : [transitionDocumentEntry(item, "explore.md")]),
        ],
        updatedAt: "刚刚",
      } : item),
    } : current);
    appendAiMessage(`${issue.id} 已保存分析结论，采纳 ${adoptedCount}/3 项建议。`);
    setToast(`${issue.id} 已保存分析结论，采纳 ${adoptedCount}/3 项建议`);
  };

  const confirmActionDialog = async () => {
    if (actionDialog.type === "none" || actionDialog.running || contextFailure) return;
    const { issue, type } = actionDialog;
    if (type === "progress") {
      appendAiMessage(`${issue.id} 当前研发进度：${issue.taskProgress?.[0] || 0}/${issue.taskProgress?.[1] || 0}`);
      closeActionDialog();
      return;
    }
    if (type === "complete" && actionDialog.tab === "import" && !actionDialog.fileName) {
      setActionDialog({ ...actionDialog, error: "请先导入文件" });
      return;
    }
    if (type === "analysis" && actionDialog.adoptedPointIndexes.length === 0) return;
    setActionDialog({ ...actionDialog, running: true, error: "" });
    await new Promise((resolve) => window.setTimeout(resolve, 520));
    closeActionDialog();
    if (type === "analysis") {
      saveAnalysisResult(issue, actionDialog.adoptedPointIndexes.length);
      return;
    }
    if (type === "sprint") {
      await runIssueAction(issue, { sprintId: actionDialog.tab === "new" ? actionDialog.newSprintId.trim() || "sprint-auto" : actionDialog.sprintId || sprintOptions[0] || "sprint-auto" });
      return;
    }
    await runIssueAction(issue, { confirmed: true });
  };

  const selectWorkspace = (item: Workspace) => {
    if (isDirtyMarkdownDrawer() && !window.confirm("文档有未保存修改，确认切换项目并放弃草稿？")) return;
    documentEpoch.current++; documentFlight.current = null; pollPaused.current = false; requestedSpace.current = item.workspaceId; projectRef.current = null; revisionRef.current = "";
    setDrawer({ type: "none" }); setContext(null); setProject(null); setContextFailure(null); setErrorDetails(null); setLastSuccess("");
    setWorkspace(item); void loadContext();
    setContext(current => current ? { ...current, selectedWorkspaceId: item.workspaceId } : current);
    defaultSprintSelectionKey.current = "";
    setTypeFilter("all");
    setSearchQuery("");
    setSelectedStages([]);
    setSelectedOwners([]);
    setSelectedLevels([]);
    setSelectedSprints([]);
    setFilterSearch({ stage: "", owner: "", level: "", sprint: "" });
    setOpenFilter(null);
    filterDetailsRef.current?.removeAttribute("open");
  };

  const stageColumns = stages.map((stage) => ({
    stage,
    items: filteredIssues.filter((issue) => issue.stage === stage.id),
  }));

  const runAgentStageAction = (stage: Stage, issue: IssueCard) => {
    if (issue.type === "change") {
      if (stage.id === "done") openIssueDetail(issue);
      else openIssueActionDialog(issue);
      return;
    }
    setAgentOpen(false);
    if (stage.id === "done") {
      window.open(issue.archiveUrl || issueDetailUrl(issue), "_blank", "noopener,noreferrer");
      return;
    }
    openIssueActionDialog(issue);
  };

  const renderIssueCard = (stage: Stage, issue: IssueCard) => {
    const action = issueAction(issue);
    const tip = blockedTip(stage.id, issue, action);
    const actionLabel = action.label || stageActionLabel[stage.id]?.[issue.type];
    const isDoneStage = stage.id === "done";
    const showArchive = issue.type === "change"
      ? ["ready-dev", "development", "acceptance"].includes(stage.id) && (stage.id !== "acceptance" || canArchive(issue))
      : stage.id !== "unknown" && !isDoneStage && (stage.id !== "acceptance" || canArchive(issue));
    const isLocked = lockedActionId === issue.id;
    const documents = visibleIssueDocuments(stage, issue);
    const persistentNames = ["requirement.md", "bug.md", "sprint.md", "trace.md"];
    if (issue.type === "requirement") persistentNames.push(...documents.filter(doc => doc.name === "prototype.html" || doc.name.startsWith("prototype/") && doc.name.endsWith(".html")).map(doc => doc.name));
    const documentGroups = [documents.filter(doc => persistentNames.includes(doc.name)), documents.filter(doc => !persistentNames.includes(doc.name))];
    const relatedChangeDocuments = relatedChangeDocumentGroups(issue, documentGroups.flat());
    const taskProgress = visibleTaskProgress(issue);
    const manualProgress = visibleManualAcceptanceProgress(issue);
    const auxActions = auxiliaryActions(issue);
    const levelTag = issueLevelTag(issue);

    return (
      <article className={`rc-card ${issue.type}`} data-issue-id={issue.id} key={issue.id}>
        <div className="rc-card-top">
          <strong>{issue.id}</strong>
          {visibleSprintId(issue) && <span className="rc-sprint-tag">{visibleSprintId(issue)}</span>}
        </div>
        <button className="rc-card-title" title={issue.title_warning || undefined} type="button" onClick={() => openIssueDetail(issue)}>{issue.display_title || issue.title}</button>
        <div className="rc-card-meta rc-card-tags">
          {levelTag && <span className={`${levelTag.className} rc-tag ${levelTag.value.toLowerCase()}`}>{levelTag.value}</span>}
          <span className="rc-owner-tag rc-tag">{issue.owner}</span>
        </div>
        <div className="rc-docs" aria-label={`${issue.id} 关联文档`}>
          {documentGroups.map((group, groupIndex) => group.length > 0 && (
            <div className="rc-doc-group" role="group" aria-label={groupIndex === 0 ? "常驻文档" : "阶段文档"} key={groupIndex}>
              {group.map(document => (
                <span className="rc-doc-item" key={document.url || document.name}>
                  <button type="button" onClick={(event) => { event.stopPropagation(); void openDocument(issue, document); }}>
                    {document.label || document.name}
                  </button>
                </span>
              ))}
            </div>
          ))}
          {relatedChangeDocuments.map(({ change, documents }, changeIndex, groups) => (
            <div className="rc-doc-group" role="group" aria-label={`${changeDocumentShortLabel(changeIndex, groups.length)} Change 文档`} key={change.id}>
              {documents.map(document => {
                const label = changeDocumentButtonLabel(document, changeIndex, groups.length);
                return (
                  <span className="rc-doc-item" key={`${change.id}:${document.url || document.name}`}>
                    <button
                      type="button"
                      title={`${change.id} / ${document.name}`}
                      onClick={(event) => { event.stopPropagation(); void openDocument(issue, { ...document, label }); }}
                    >
                      {label}
                    </button>
                  </span>
                );
              })}
            </div>
          ))}
        </div>
        {issue.type === "change" && !issue.taskProgress && <p className="rc-progress">任务进度未知</p>}
        {tip ? (
          <p className="rc-blocked"><CircleDot size={12} /> {tip}</p>
        ) : null}
        {!isDoneStage && (taskProgress || issue.testProgress) && (
          <div className="rc-progress" aria-label={`${issue.id} 进度`}>
            {taskProgress && (
              <button
                aria-label={`研发 ${taskProgress[0]}/${taskProgress[1]}`}
                className="rc-progress-action"
                type="button"
                onClick={() => openTasksAt(issue, "development")}
              >
                <span className="rc-progress-label">研发</span>
                <b className="rc-progress-value">{taskProgress[0]}/{taskProgress[1]}</b>
              </button>
            )}
            {issue.testProgress && (
              <button
                aria-label={`测试 ${issue.testProgress[0]}/${issue.testProgress[1]}`}
                className="rc-progress-action"
                type="button"
                onClick={() => openTasksAt(issue, "test")}
              >
                <span className="rc-progress-label">测试</span>
                <b className="rc-progress-value">{issue.testProgress[0]}/{issue.testProgress[1]}</b>
              </button>
            )}
            {manualProgress && (
              <button
                aria-label={`人工验收 ${manualProgress[0]}/${manualProgress[1]}`}
                className="rc-progress-action"
                type="button"
                onClick={() => openTasksAt(issue, "manual")}
              >
                <span className="rc-progress-label">人工验收</span>
                <b className="rc-progress-value">{manualProgress[0]}/{manualProgress[1]}</b>
              </button>
            )}
          </div>
        )}
        <footer>
          <span className="rc-updated">{/^\d{2}\/\d{2}\/\d{2} \d{2}:\d{2}$/.test(issue.updatedAt || "") ? `更新 ${issue.updatedAt}` : "更新时间未知"}</span>
          <span className="rc-card-actions" aria-label={`${issue.id} 卡片动作`}>
            {auxActions.map((auxAction) => (
              <button
                className="secondary"
                key={auxAction.command}
                type="button"
                title={auxAction.command}
                onClick={() => {
                  openIssueActionDialog(issue, auxAction);
                }}
              >
                {auxAction.label}
              </button>
            ))}
            {showArchive && (
              <button className="primary" type="button" title={tip || action.command} disabled={isLocked || Boolean(tip)} onClick={() => openIssueActionDialog(issue)}>
                {isLocked && <Loader2 size={13} aria-hidden="true" />} {actionLabel} →
              </button>
            )}
          </span>
        </footer>
      </article>
    );
  };

  const renderDocChecklist = (items: string[], done = false) => (
    <div className="rc-action-doc-list">
      {items.map((item) => (
        <div className={`rc-action-doc ${done ? "done" : ""}`} key={item}>
          <span />
          {item}
        </div>
      ))}
    </div>
  );

  const renderActionDialogBody = (dialog: Exclude<ActionDialog, { type: "none" }>) => {
    const copy = actionModalCopy(dialog.issue, dialog.type);
    const docs = commandDocsForAction(dialog.issue, dialog.type);
    const estimate = dialog.issue.priority === "P0" ? 5 : dialog.issue.priority === "P1" ? 3 : 2;
    const changeCount = dialog.issue.type === "requirement" && ["P0", "P1"].includes(dialog.issue.priority || "") ? 2 : 1;

    if (dialog.type === "analysis") {
      const points = [
        `补充「${dialog.issue.title}」涉及的关键角色与使用场景`,
        "明确验收标准边界，避免评审阶段返工",
        "识别与现有 Space / OpenSpec 治理链路的依赖关系",
      ];
      return (
        <>
          <div className="rc-action-command"><span>$</span>{copy.command}</div>
          <div className="rc-action-analysis">
            {!dialog.ready ? <><span className="rc-action-spinner" />AI 正在分析上下文...</> : `已扫描关联事实源，围绕「${dialog.issue.title}」输出以下分析结论与建议方案：`}
          </div>
          {dialog.ready && (
            <div className="rc-action-field">
              <label>解决方案要点（可选择采纳）</label>
              <div className="rc-action-adopt-list">
                {points.map((point, index) => {
                  const checked = dialog.adoptedPointIndexes.includes(index);
                  return (
                    <button
                      aria-pressed={checked}
                      className={checked ? "checked" : ""}
                      type="button"
                      key={point}
                      onClick={() => setActionDialog((current) => {
                        if (current.type !== "analysis" || current.issue.id !== dialog.issue.id) return current;
                        const nextIndexes = checked
                          ? current.adoptedPointIndexes.filter((item) => item !== index)
                          : [...current.adoptedPointIndexes, index].sort();
                        return { ...current, adoptedPointIndexes: nextIndexes };
                      })}
                    >
                      <span />
                      {point}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </>
      );
    }

    if (dialog.type === "complete") {
      return (
        <>
          <div className="rc-action-tabs" role="tablist" aria-label="完善方式">
            <button className={dialog.tab === "ai" ? "active" : ""} type="button" role="tab" aria-selected={dialog.tab === "ai"} onClick={() => setActionDialog({ ...dialog, tab: "ai", error: "" })}>AI 生成</button>
            <button className={dialog.tab === "import" ? "active" : ""} type="button" role="tab" aria-selected={dialog.tab === "import"} onClick={() => setActionDialog({ ...dialog, tab: "import", error: "" })}>导入文档</button>
          </div>
          {dialog.tab === "ai" ? (
            <div className="rc-action-panel active">
              <div className="rc-action-command"><span>$</span>{copy.command}</div>
              <p>AI 将基于当前上下文直接生成完善所需的文档。</p>
            </div>
          ) : (
            <div className="rc-action-panel active">
              <label className="rc-action-dropzone">
                <input
                  type="file"
                  aria-label="导入完善文档"
                  accept=".zip,.docx,.pdf,.md"
                  onChange={(event) => {
                    const file = event.target.files?.[0];
                    setActionDialog({ ...dialog, fileName: file?.name || "", error: "" });
                  }}
                />
                <span>📎</span>
                <strong>点击上传已设计的文档</strong>
                <small>支持 .zip / .docx / .pdf / .md，AI 将解析并补全缺失部分</small>
              </label>
              {dialog.fileName && <div className="rc-action-file-chip">📄 {dialog.fileName}<button type="button" aria-label="移除导入文件" onClick={() => setActionDialog({ ...dialog, fileName: "", error: "" })}>×</button></div>}
            </div>
          )}
          <div className="rc-action-field">
            <label>本次将生成 / 更新</label>
            {renderDocChecklist(docs, dialog.running)}
          </div>
        </>
      );
    }

    if (dialog.type === "sprint") {
      const options = sprintOptionModels(sprintOptions, dialog.sprintEstimate || estimate, sprintOptionDetails);
      const selectedOption = options.find((option) => option.id === dialog.sprintId && !option.disabled) || options.find((option) => !option.disabled);
      return (
        <>
          <div className="rc-action-field rc-sprint-context-field">
            <label>对象</label>
            <div className="rc-action-context rc-sprint-context-strip">
              <strong>{dialog.issue.id}</strong>
              <span>{dialog.issue.title}</span>
            </div>
          </div>
          <div className="rc-action-field">
            <label>AI 工作量评估</label>
            <div className="rc-action-estimate">
              {!dialog.ready ? <><span className="rc-action-spinner" />正在评估工作量...</> : <>预估工作量：<b>{estimate} 项容量点</b>（依据优先级 {dialog.issue.priority}）</>}
            </div>
          </div>
          {dialog.ready && (
            <>
              <div className="rc-action-tabs rc-sprint-mode-toggle" role="tablist" aria-label="迭代模式">
                <button className={dialog.tab === "existing" ? "active" : ""} type="button" role="tab" aria-selected={dialog.tab === "existing"} onClick={() => setActionDialog({ ...dialog, tab: "existing", sprintId: selectedOption?.id || dialog.sprintId })}>加入现有迭代</button>
                <button className={dialog.tab === "new" ? "active" : ""} type="button" role="tab" aria-selected={dialog.tab === "new"} onClick={() => setActionDialog({ ...dialog, tab: "new" })}>新建迭代</button>
              </div>
              {dialog.tab === "existing" ? (
                <div className="rc-sprint-options" role="radiogroup" aria-label="现有迭代">
                  {options.map((option) => {
                    const selected = selectedOption?.id === option.id;
                    const capacityPercent = Math.min(100, Math.round((option.used / option.total) * 100));
                    return (
                      <button
                        aria-checked={selected}
                        className={`${selected ? "selected" : ""} ${option.disabled ? "disabled" : ""}`}
                        disabled={option.disabled}
                        role="radio"
                        type="button"
                        key={option.id}
                        onClick={() => setActionDialog({ ...dialog, sprintId: option.id })}
                      >
                        <span className="rc-sprint-option-top">
                          <span className="rc-sprint-option-name">{option.id}<em className={`rc-sprint-status-pill ${sprintStatusClass(option.status)}`}>{option.status}</em>{option.disabled && <em className="rc-sprint-capacity-badge">容量不足</em>}</span>
                          <span className="rc-sprint-radio" />
                        </span>
                        <span className="rc-sprint-meta-row"><span>容量</span><span>{option.used}/{option.total} 项</span></span>
                        <span className="rc-sprint-capacity-bar"><span style={{ width: `${capacityPercent}%` }} /></span>
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div className="rc-action-grid rc-new-sprint-panel">
                  <label>迭代编号<input value={dialog.newSprintId} onChange={(event) => setActionDialog({ ...dialog, newSprintId: event.target.value })} /></label>
                </div>
              )}
              <div className="rc-action-field">
                <label>本次将生成 / 更新</label>
                {renderDocChecklist(["sprint.md", "sprint.yaml", "release-note.md", "acceptance-report.md"], true)}
              </div>
            </>
          )}
        </>
      );
    }

    if (dialog.type === "opsx") {
      const titles = Array.from({ length: changeCount }, (_, index) => `${dialog.issue.title}${changeCount > 1 ? (index === 0 ? " · 前端实现" : " · 后端与数据实现") : ""}`);
      return (
        <>
          <div className="rc-action-command"><span>$</span>{copy.command}</div>
          <div className="rc-action-analysis">{!dialog.ready ? <><span className="rc-action-spinner" />AI 正在拆解 Change 并生成配套文档...</> : `已完成拆解，共识别到 ${changeCount} 个 Change：`}</div>
          {dialog.ready && (
            <div className="rc-action-change-list">
              {titles.map((title, index) => (
                <div className="rc-action-change" key={title}>
                  <strong>CHG-{index + 1} · {title}</strong>
                  {renderDocChecklist(docs, dialog.running)}
                </div>
              ))}
            </div>
          )}
        </>
      );
    }

    if (dialog.type === "apply") {
      return (
        <>
          <div className="rc-action-command"><span>$</span>{copy.command}</div>
          <div className="rc-action-field">
            <label>执行步骤</label>
            {renderDocChecklist(docs, dialog.running)}
          </div>
        </>
      );
    }


    return (
      <>
        <div className="rc-action-command"><span>$</span>{copy.command}</div>
        <div className="rc-action-field">
          <label>本次将生成 / 更新</label>
          {renderDocChecklist(docs, dialog.running)}
        </div>
      </>
    );
  };

  const renderActionDialog = () => {
    if (actionDialog.type === "none") return null;
    const copy = actionModalCopy(actionDialog.issue, actionDialog.type);
    const adoptedCount = actionDialog.type === "analysis" ? actionDialog.adoptedPointIndexes.length : 0;
    const sprintConfirmLabel = actionDialog.type === "sprint"
      ? actionDialog.tab === "new"
        ? `创建 ${actionDialog.newSprintId.trim() || "新迭代"} 并加入`
        : `加入 ${actionDialog.sprintId || "现有迭代"}`
      : "";
    const confirmLabel = actionDialog.type === "analysis" ? `采纳 ${adoptedCount}/3 项并保留分析 →` : actionDialog.type === "sprint" ? sprintConfirmLabel : copy.confirm;
    const sprintConfirmDisabled = actionDialog.type === "sprint" && (actionDialog.tab === "new" ? !actionDialog.newSprintId.trim() : !actionDialog.sprintId);
    const confirmDisabled = actionDialog.running || !actionDialog.ready || (actionDialog.type === "complete" && actionDialog.tab === "import" && !actionDialog.fileName) || (actionDialog.type === "analysis" && adoptedCount === 0) || sprintConfirmDisabled;
    return (
      <div className="rc-settings-mask rc-action-mask" role="presentation" onMouseDown={closeActionDialog}>
        <section className={`rc-flow-dialog rc-action-dialog ${actionDialog.type === "sprint" ? "sprint" : ""}`} role="dialog" aria-modal="true" aria-label={copy.title} onMouseDown={(event) => event.stopPropagation()}>
          <header className="rc-dialog-head">
            <div>
              <p>{copy.eyebrow}</p>
              <h2>{copy.title}</h2>
              <span>{copy.sub}</span>
            </div>
            <button aria-label={`关闭${copy.title}`} type="button" onClick={closeActionDialog}><X size={17} /></button>
          </header>
          <div className="rc-action-body">
            {renderActionDialogBody(actionDialog)}
            {actionDialog.error && <p className="rc-application-alert" role="alert">{actionDialog.error}</p>}
          </div>
          <footer className="rc-dialog-actions">
            <p><kbd>Esc</kbd> 关闭</p>
            <div>
              <button className="rc-secondary-action" type="button" onClick={closeActionDialog}>取消</button>
              <button className="rc-primary-action" type="button" disabled={confirmDisabled} onClick={() => void confirmActionDialog()}>
                {actionDialog.running && <span className="rc-action-spinner" />} {actionDialog.running ? copy.running : confirmLabel}
              </button>
            </div>
          </footer>
        </section>
      </div>
    );
  };

  return (
    <main className={`requirement-center theme-${theme}`} data-theme={theme}>
      <WorkbenchSidebar activePage="requirements" activeUser={activeUser} workspace={workspace} availableWorkspaces={availableWorkspaces} isLoadingContext={isLoadingContext} contextError={contextError} onWorkspaceChange={selectWorkspace} onUserChange={(currentUser) => setContext(current => current ? { ...current, currentUser } : current)} onRefresh={() => loadContext("refresh")} />

      <section className="rc-content">
        <header className="rc-page-header">
          <div>
            <p>Requirement Operations</p>
            <h1>需求研发流转看板</h1>
          </div>
          <button className="rc-header-action" type="button" onClick={() => setCaptureOpen(true)}>
            <Command size={16} aria-hidden="true" /> 新建 Capture
          </button>
        </header>

        {projects.filter(p => p.space_id === workspace.workspaceId).length > 1 && <select aria-label="本地项目" value={project?.repository_id || ""} onChange={event => {
          if (isDirtyMarkdownDrawer() && !window.confirm("文档有未保存修改，确认切换项目并放弃草稿？")) return;
          documentEpoch.current++; projectRef.current = projects.find(p => p.space_id === workspace.workspaceId && p.repository_id === event.target.value) || null;
          contextController.current?.abort();
          defaultSprintSelectionKey.current = "";
          requestedSpace.current = workspace.workspaceId; revisionRef.current = ""; documentEpoch.current++; documentFlight.current = null; setContextFailure(null); setErrorDetails(null); setLastSuccess(""); setDrawer({ type: "none" }); setContext(null); void loadContext();
        }}>{projects.filter(p => p.space_id === workspace.workspaceId).map(p => <option key={p.repository_id} value={p.repository_id}>{p.repository_id}</option>)}</select>}

        <section className="rc-stats" aria-label="需求中心统计" data-state={isLoadingContext ? "loading" : contextError ? "error" : "ready"}>
          {stats.map((item, index) => (
            <article className="rc-stat" key={item.label} data-testid={item.testId}>
              <MetricLabel id={`rc-stat-tooltip-${index}`} label={item.label} description={item.description} />
              <strong aria-label={isRatioStatValue(item.value) ? `${item.label}已完成 ${item.value.completed} 个，总体 ${item.value.total} 个` : `${item.label}${item.value}`}>
                {isLoadingContext ? <span className="rc-loading-number" aria-hidden="true" /> : isRatioStatValue(item.value) ? (
                  <>
                    <b>{item.value.completed}</b>
                    <em aria-hidden="true">/</em>
                    <b>{item.value.total}</b>
                  </>
                ) : item.value}
              </strong>
            </article>
          ))}
          <article className="rc-stat rc-sprint-metric" data-testid="sprint-completion-metric" data-state={sprintMetricState}>
            <MetricLabel id="rc-stat-tooltip-sprint" label="Sprint" description="项目级 Sprint 总览：已完成 Sprint 数 / 累计 Sprint 数，不随当前筛选变化。" />
            <strong aria-label={`Sprint 已完成 ${sprintMetricValue.completed} 个，总体 ${sprintMetricValue.total} 个`}>
              {isLoadingContext && !context ? <span className="rc-loading-number" aria-hidden="true" /> : (
                <>
                  <b data-testid="sprint-completion-metric-completed">{sprintMetricValue.completed}</b>
                  <em aria-hidden="true">/</em>
                  <b data-testid="sprint-completion-metric-total">{sprintMetricValue.total}</b>
                </>
              )}
            </strong>
          </article>
        </section>

        <CurrentIterationCapacityStrip
          items={currentIterationCapacity}
          loading={isLoadingContext}
          stale={Boolean(contextFailure && context)}
          onArchive={(item) => setArchiveDialog({ type: "current_iteration_archive", item })}
        />

        <section className="rc-toolbar" aria-label="需求中心筛选" data-testid="requirement-filter-toolbar">
          <label className="rc-search">
            <Search size={15} aria-hidden="true" />
            <input
              aria-label="搜索治理对象"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="搜索 ID、标题、文档或负责人"
              disabled={isLoadingContext || Boolean(contextError)}
            />
          </label>
          <div className="rc-segmented" aria-label="对象类型筛选">
            {[
              ["all", "全部"],
              ["requirement", "需求"],
              ["bug", "Bug"],
              ["change", "Change"],
            ].map(([value, label]) => (
              <button
                className={typeFilter === value ? "selected" : ""}
                type="button"
                key={value}
                onClick={() => setTypeFilter(value as "all" | CardType)}
                disabled={isLoadingContext || Boolean(contextError)}
              >
                {label}
              </button>
            ))}
          </div>
          <details className="rc-filter-popover" ref={filterDetailsRef}>
            <summary aria-label="打开筛选条件">
              筛选
              <span className="rc-filter-badge" aria-label={`已启用 ${activeFilterCount} 个筛选`}>{activeFilterCount}</span>
            </summary>
            <div className="rc-filter-menu" role="group" aria-label="筛选条件">
              {renderMultiFilter("sprint", "Sprint", "全部 Sprint", sprintOptionsForFilter)}
              {renderMultiFilter("level", "分级", "全部分级", levelOptions)}
              {renderMultiFilter("owner", "负责人", "全部负责人", ownerOptions)}
              {renderMultiFilter("stage", "阶段", "全部阶段", stageOptions)}
              <button
                className="rc-filter-clear-all"
                type="button"
                data-testid="requirement-filter-clear-all"
                disabled={activeFilterCount === 0}
                onClick={clearAllFilters}
              >
                清空全部筛选
              </button>
            </div>
          </details>
          <button
            className={`rc-refresh-button ${isRefreshingContext ? "refreshing" : ""}`}
            type="button"
            aria-label="刷新需求中心"
            aria-busy={isRefreshingContext}
            title={`刷新 · ${syncLabel}`}
            disabled={isLoadingContext || isRefreshingContext}
            onClick={() => void loadContext("refresh")}
          >
            <RefreshCw size={15} aria-hidden="true" />
          </button>
        </section>

        {contextFailure && context && <section className="rc-stale-notice" aria-label="更新失败">
          <span>更新失败 · 上次成功同步 {lastSuccess || "时间未记录"}，当前结果可能不是最新，写入已暂停。</span>
          <button type="button" disabled={isRefreshingContext} onClick={() => void loadContext("refresh")}>{isRefreshingContext ? "正在加载…" : "重新加载"}</button>
          <button type="button" onClick={() => setErrorDetails(contextFailure)}>查看详情</button>
        </section>}
        {!isLoadingContext && !contextError && diagnosticIssues.length > 0 && (
          <details className="rc-data-diagnostics">
            <summary>数据异常 · {diagnosticIssues.length} 项</summary>
            <p>以下对象的状态或归档身份无法唯一确认，未计入看板统计。请核对项目治理记录。</p>
            <ul>{diagnosticIssues.map(issue => <li key={issue.id}><code>{issue.id}</code><span>状态或归档版本存在歧义</span></li>)}</ul>
          </details>
        )}
        <section className="rc-board-wrap" aria-busy={isLoadingContext} aria-label="9 阶段需求研发流转看板" data-state={isLoadingContext ? "loading" : contextError ? "error" : filteredIssues.length ? "ready" : "empty"}>
          {isLoadingContext && <span className="rc-loading-announcement" role="status">正在加载需求</span>}
          {!isLoadingContext && contextError && (
            <RequirementCenterError busy={isLoadingContext || isRefreshingContext} onRetry={() => void loadContext("refresh")} onDetails={() => setErrorDetails(contextFailure || {})} />
          )}
          {!isLoadingContext && !contextError && filteredIssues.length === 0 && (
            <div className="rc-state-panel" role="status">
              <strong>没有匹配的治理对象</strong>
              <p>调整搜索、负责人、优先级或 Sprint 筛选后再查看。</p>
            </div>
          )}
          <div className="rc-board">
            {stageColumns.map(({ stage, items }) => (
              <header className={`rc-column-head ${items.length > 0 ? "filled" : "empty"}`} data-stage-head={stage.id} key={`${stage.id}-head`}>
                <div>
                  <h2 id={`stage-${stage.id}`}>{stage.title}</h2>
                  <p>{stage.subtitle}</p>
                </div>
                <span aria-label={isLoadingContext ? `${stage.title}加载中` : `${stage.title} ${items.length} 个对象`}>{isLoadingContext ? <i className="rc-loading-count" aria-hidden="true" /> : String(items.length).padStart(2, "0")}</span>
              </header>
            ))}
            {stageColumns.map(({ stage, items }) => (
              <section className="rc-column" data-stage={stage.id} aria-labelledby={`stage-${stage.id}`} key={stage.id}>
                <div className={`rc-column-body ${!isLoadingContext && items.length === 0 ? "empty" : ""}`}>
                  {!isLoadingContext && items.length === 0 && (
                    <div className="rc-empty-stage" aria-label={`${stage.title}暂无对象`}>
                      <span className="rc-empty-stage-icon" aria-hidden="true">◌</span>
                      <strong>{stage.emptyTitle}</strong>
                      <p>{stage.emptyHint}<br />{stage.emptyDetail}</p>
                    </div>
                  )}
                  {isLoadingContext ? <div className="rc-loading-card" aria-hidden="true">
                    <span /><span /><span /><span />
                  </div> : items.map((issue) => renderIssueCard(stage, issue))}
                </div>
              </section>
            ))}
          </div>
        </section>

      </section>

      {captureOpen && <CaptureDialog project={project} contextFailure={Boolean(contextFailure)} existingIssues={issues as CaptureExistingIssue[]} onClose={closeCapture} onCreated={() => loadContext("refresh")} />}

      {renderActionDialog()}

      {choiceDialog.type !== "none" && (
        <div className="rc-settings-mask" role="presentation" onMouseDown={() => setChoiceDialog({ type: "none" })}>
          <section className="rc-flow-dialog" role="dialog" aria-modal="true" aria-label={choiceDialog.type === "review" ? "确认评审结果" : "选择执行方式"} onMouseDown={(event) => event.stopPropagation()}>
            <header className="rc-dialog-head">
              <h2>{choiceDialog.type === "review" ? "确认评审结果" : "选择执行方式"}</h2>
              <button aria-label={choiceDialog.type === "review" ? "关闭确认评审结果" : "关闭选择执行方式"} type="button" onClick={() => setChoiceDialog({ type: "none" })}><X size={17} /></button>
            </header>
            {choiceDialog.type === "sprint" ? (
              <div className="rc-choice-list">
                {[...sprintOptions, "新建下一迭代"].map((sprint) => (
                  <button key={sprint} type="button" onClick={() => void runIssueAction(choiceDialog.issue, { sprintId: sprint === "新建下一迭代" ? "sprint-auto" : sprint })}>{sprint}</button>
                ))}
              </div>
            ) : choiceDialog.type === "review" ? (
              <div className="rc-choice-list">
                <button type="button" onClick={() => void runIssueAction(choiceDialog.issue, { confirmed: true })}>
                  {choiceDialog.issue.type === "requirement" ? "确认评审通过" : "确认修复通过"}
                </button>
                <button type="button" onClick={() => setChoiceDialog({ type: "none" })}>暂不流转</button>
              </div>
            ) : (
              <div className="rc-choice-list">
                <button type="button" onClick={() => void runIssueAction(choiceDialog.issue)}>AI {choiceDialog.type === "generation" ? "生成" : "完善"}</button>
                <label className="rc-file-choice">
                  <input
                    type="file"
                    aria-label="导入文件"
                    accept={choiceDialog.type === "generation" ? ".md" : ".zip,.md"}
                    onChange={(event) => {
                      const file = event.target.files?.[0];
                      const error = validateImportedFile(file, choiceDialog);
                      if (error) {
                        setChoiceDialog({ ...choiceDialog, error });
                        event.target.value = "";
                        return;
                      }
                      void runIssueAction(choiceDialog.issue, { importedFile: file });
                    }}
                  />
                  导入文件
                </label>
              </div>
            )}
            {choiceDialog.error && <p className="rc-application-alert" role="alert">{choiceDialog.error}</p>}
          </section>
        </div>
      )}

      {agentOpen && (
        <div className="rc-settings-mask rc-agent-mask" role="presentation" onMouseDown={() => setAgentOpen(false)}>
          <section className="rc-flow-dialog rc-agent-dialog" role="dialog" aria-modal="true" aria-label="Agent 助手" onMouseDown={(event) => event.stopPropagation()}>
            <header className="rc-dialog-head">
              <div>
                <p>Requirement Operations</p>
                <h2>Agent 助手</h2>
                <span>选择一个阶段动作，沿用当前看板上下文继续流转。</span>
              </div>
              <button aria-label="关闭 Agent 助手" type="button" onClick={() => setAgentOpen(false)}><X size={17} /></button>
            </header>
            <div className="rc-agent-body">
              {stageColumns.map(({ stage, items }) => {
                const availableIssue = items.find((item) => stage.id === "done" || !actionDisabledReason(issueAction(item)));
                const fallbackIssue = items[0];
                const selectedIssue = availableIssue || fallbackIssue;
                const action = selectedIssue ? issueAction(selectedIssue) : null;
                const isDone = stage.id === "done";
                const disabledReason = selectedIssue && !isDone ? actionDisabledReason(action || undefined) : "";
                const buttonLabel = selectedIssue
                  ? (isDone ? "查看归档" : (action?.label || stageActionLabel[stage.id]?.[selectedIssue.type] || "只读").replace(" →", ""))
                  : "暂无对象";
                return (
                  <article className="rc-agent-stage" data-stage={stage.id} key={stage.id}>
                    <div>
                      <strong>{stage.title}</strong>
                      <p>{stage.subtitle}</p>
                    </div>
                    <span className="rc-agent-count">{String(items.length).padStart(2, "0")}</span>
                    <small>{selectedIssue ? `${selectedIssue.id} · ${selectedIssue.title}` : stage.emptyHint}</small>
                    <button
                      type="button"
                      disabled={!selectedIssue || Boolean(disabledReason)}
                      title={selectedIssue ? (disabledReason || action?.command || "查看归档") : stage.emptyDetail}
                      onClick={() => selectedIssue && runAgentStageAction(stage, selectedIssue)}
                    >
                      {buttonLabel} →
                    </button>
                  </article>
                );
              })}
            </div>
            <footer className="rc-dialog-actions">
              <p><kbd>Esc</kbd> 关闭</p>
              <div>
                <button className="rc-secondary-action" type="button" onClick={() => setAgentOpen(false)}>取消</button>
              </div>
            </footer>
          </section>
        </div>
      )}

      {archiveDialog.type === "current_iteration_archive" && (() => {
        const item = archiveDialog.item;
        const sprintId = item.sprintId || "当前迭代";
        const readiness = item.archiveReadiness;
        const blockers = readiness?.blockers?.filter((blocker) => blocker.visible !== false) || [];
        const canConfirm = Boolean(readiness?.canEnterConfirmation && readiness.displayMode === "enabled");
        return (
          <div className="rc-settings-mask rc-action-mask" role="presentation" onMouseDown={() => setArchiveDialog({ type: "none" })}>
            <section className="rc-flow-dialog rc-archive-dialog" role="dialog" aria-modal="true" aria-label="归档当前迭代" data-testid="archive-sprint-confirm-dialog" onMouseDown={(event) => event.stopPropagation()}>
              <header className="rc-dialog-head">
                <div>
                  <p>Sprint Archive</p>
                  <h2>归档当前迭代</h2>
                  <span>{sprintId} · {formatCapacityValue(item)}</span>
                </div>
                <button aria-label="关闭归档当前迭代确认" type="button" onClick={() => setArchiveDialog({ type: "none" })}><X size={17} /></button>
              </header>
              <div className="rc-archive-body">
                <div className={`rc-archive-readiness ${canConfirm ? "ready" : "blocked"}`} data-state={canConfirm ? "ready" : "blocked"}>
                  <strong>{canConfirm ? "Sprint archive readiness 已通过" : "Sprint archive readiness 未通过"}</strong>
                  <p>{readiness?.safeSummary || "归档门禁状态待核实，请刷新后重试。"}</p>
                </div>
                <dl className="rc-archive-facts">
                  <div><dt>Sprint</dt><dd>{sprintId}</dd></div>
                  <div><dt>容量</dt><dd>{formatCapacityValue(item)}</dd></div>
                  <div><dt>状态</dt><dd>{capacityStatusLabel(item.status)}</dd></div>
                  <div><dt>门禁</dt><dd>{readiness?.reasonCode || "unknown"}</dd></div>
                </dl>
                <div className="rc-archive-gates" data-testid="archive-gate-checklist" aria-label="归档门禁">
                  {["全部 REQ/BUG/独立 Change 已归档", "验收报告 sign-off", "归档权限复核", "Workflow Sync 校验"].map((gate) => (
                    <span key={gate} className={canConfirm ? "ready" : "blocked"}><Check size={13} aria-hidden="true" />{gate}</span>
                  ))}
                </div>
                {blockers.length > 0 && (
                  <div className="rc-archive-blockers">
                    <strong>安全摘要</strong>
                    <ul>
                      {blockers.slice(0, 6).map((blocker, index) => (
                        <li key={`${blocker.type}-${blocker.id || index}`}>
                          <span>{blocker.id || blocker.type}</span>
                          <em>{blocker.message || "尚未闭环"}{blocker.status ? ` · ${blocker.status}` : ""}</em>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              <footer className="rc-dialog-actions">
                <p><kbd>Esc</kbd> 关闭</p>
                <div>
                  <button className="rc-secondary-action" data-testid="archive-sprint-cancel" type="button" onClick={() => setArchiveDialog({ type: "none" })}>取消</button>
                  <button
                    className="rc-primary-action"
                    data-testid="archive-sprint-confirm"
                    type="button"
                    disabled={!canConfirm}
                    onClick={() => {
                      setArchiveDialog({ type: "none" });
                      setToast(`请继续执行 /sprint-archive ${sprintId} 完成最终归档`);
                    }}
                  >
                    进入归档确认流程
                  </button>
                </div>
              </footer>
            </section>
          </div>
        );
      })()}

      {drawer.type !== "none" && (
        <div className="rc-drawer-layer" role="presentation">
          <button className="rc-drawer-backdrop" type="button" aria-label="关闭右侧抽屉蒙层" onClick={closeDrawer} />
          <aside className={`rc-drawer${isDrawerFullscreen ? " fullscreen" : ""}`} style={isDrawerFullscreen ? undefined : { width: drawerWidth }} role="dialog" aria-modal="true" aria-label={drawerTitle(drawer)} onMouseDown={(event) => event.stopPropagation()}>
            {!isDrawerFullscreen && <button className="rc-drawer-resizer" type="button" aria-label="调整右侧抽屉宽度" onMouseDown={beginDrawerResize} />}
            <header className="rc-drawer-head">
              {drawer.type === "markdown" ? (
                <div className="rc-drawer-title-block">
                  <div className="rc-drawer-crumb">{drawer.issue.id}<span>·</span>{drawer.document.label || drawer.document.name}</div>
                  <h2>{drawer.issue.title}</h2>
                  <span>{drawerIssueSubtitle(drawer)}</span>
                </div>
              ) : (
                <div>
                  <h2>{drawerTitle(drawer)}</h2>
                </div>
              )}
              <div className="rc-drawer-head-actions">
                <button
                  aria-label={isDrawerFullscreen ? "恢复右侧抽屉" : "放大右侧抽屉"}
                  type="button"
                  onClick={() => setIsDrawerFullscreen((fullscreen) => !fullscreen)}
                >
                  {isDrawerFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
                </button>
                <button aria-label="关闭右侧抽屉" type="button" onClick={closeDrawer}><X size={17} /></button>
              </div>
            </header>
            {drawer.type === "markdown" && (
              <>
                {isEditableDocument(drawer) && !drawer.loading && (
                  <div className="rc-markdown-mode-bar">
                    <div className="rc-markdown-segmented" role="group" aria-label="Markdown 查看模式">
                      {(["preview", "edit", "split"] as const).map((mode) => (
                        <button
                          key={mode}
                          type="button"
                          className={drawer.mode === mode ? "active" : ""}
                          onClick={() => setMarkdownMode(mode)}
                        >
                          {mode === "preview" ? "预览" : mode === "edit" ? "编辑" : "分栏"}
                        </button>
                      ))}
                    </div>
                    {drawer.mode !== "preview" && (
                      <div className="rc-vditor-toolbar" role="toolbar" aria-label="Vditor Markdown 工具栏">
                        <button type="button" aria-label="插入图片" onClick={attemptMarkdownImageUpload}>
                          <ImageIcon size={14} aria-hidden="true" />
                        </button>
                        <button type="button" aria-label="插入表格" onClick={() => insertMarkdownSnippet("table")}>
                          <Table2 size={14} aria-hidden="true" />
                        </button>
                        <button type="button" aria-label="插入代码块" onClick={() => insertMarkdownSnippet("code")}>
                          <Code2 size={14} aria-hidden="true" />
                        </button>
                        <button type="button" aria-label="插入数学公式" onClick={() => insertMarkdownSnippet("formula")}>
                          <Sigma size={14} aria-hidden="true" />
                        </button>
                      </div>
                    )}
                  </div>
                )}
                <section className="rc-markdown-view" data-testid="markdown-drawer">
                  {drawer.loading && <p role="status"><Loader2 size={14} /> Markdown 加载中</p>}
                  {drawer.error && !drawer.readBlocked && <p role="alert">{drawer.error}</p>}
                  {drawer.error && drawer.readBlocked && <RequirementCenterError drawer busy={drawer.loading || isRefreshingContext} onRetry={() => drawer.dirty ? void loadContext("refresh") : void openDocument(drawer.issue, drawer.document, drawer.focus)} onDetails={() => setErrorDetails(drawer.failure || {})}>{drawer.dirty ? "项目文档已有新版本或暂不可读，当前草稿已保留。请复制草稿后核对新版本，保存暂时停用。" : undefined}</RequirementCenterError>}
                  {!drawer.loading && (!drawer.error || !!drawer.content || drawer.dirty) && (
                    isEditableDocument(drawer) && drawer.mode !== "preview" ? (
                      <VditorEditorShell
                        value={drawer.draft}
                        sourceContent={drawer.content}
                        documentName={drawer.document.name}
                        mode={drawer.mode}
                        uploadState={markdownUploadState}
                        uploadError={markdownUploadError}
                        metadataOpen={markdownMetadataOpen}
                        onToggleMetadata={() => setMarkdownMetadataOpen((open) => !open)}
                        onChange={updateMarkdownDraft}
                        editorRef={markdownEditorRef}
                      />
                    ) : (
                      <MarkdownPreviewPane
                        focus={drawer.error ? undefined : drawer.focus}
                        content={composeMarkdownContent(drawer.content, drawer.draft)}
                        metadataOpen={markdownMetadataOpen}
                        onToggleMetadata={() => setMarkdownMetadataOpen((open) => !open)}
                        onTaskToggle={isMutableMarkdownDrawer(drawer) ? toggleMarkdownTask : undefined}
                      />
                    )
                  )}
                </section>
                {!drawer.loading && (!drawer.error || !!drawer.content || drawer.dirty) && (
                  <footer className="rc-markdown-footer">
                    <div className="rc-markdown-footer-status">
                      <span className={isCurrentMarkdownDirty ? "dirty" : ""} />
                      {drawer.savedAt || (isCurrentMarkdownDirty ? "有未保存修改" : "已同步")}
                      {!canEditDocument(drawer.document) && !canToggleTaskDocument(drawer.document) && ` · ${documentCapability(drawer.document).reason}`}
                      {canToggleTaskDocument(drawer.document) && !isCurrentMarkdownDirty && " · 仅允许勾选任务"}
                    </div>
                    {isMutableMarkdownDrawer(drawer) && (
                      <div className="rc-markdown-footer-actions">
                        <button type="button" className="flow" disabled>{issueAction(drawer.issue).label}</button>
                        <button type="button" onClick={cancelMarkdownDraft}>取消</button>
                        <button type="button" className="primary" disabled={drawer.saving || !isCurrentMarkdownDirty || Boolean(contextFailure) || Boolean(drawer.readBlocked)} onClick={() => void saveMarkdownDocument()}>
                          {drawer.saving && <Loader2 size={13} aria-hidden="true" />} 保存
                        </button>
                      </div>
                    )}
                  </footer>
                )}
              </>
            )}
            {drawer.type === "ai" && (
              <section className="rc-ai-chat" data-testid="ai-chat-drawer">
                <a href={`/chat?${new URLSearchParams({ space_id: workspace.workspaceId, ...(drawer.issue ? { object_id: drawer.issue.id } : {}) })}`} className="rc-secondary-action">在Chat工作台继续</a>
                <div className="rc-ai-messages">
                  {aiMessages.map((message, index) => <p key={`${message.role}-${index}`} className={message.role}>{message.content}</p>)}
                </div>
                <div className="rc-ai-composer">
                  <textarea aria-label="AI 消息" value={aiDraft} onKeyDown={handleAiKeyDown} onChange={(event) => setAiDraft(event.target.value)} />
                  <button type="button" aria-label="发送 AI 消息" onClick={sendAiMessage}><Send size={15} /></button>
                </div>
              </section>
            )}
          </aside>
        </div>
      )}

      <button className="rc-ai-fab rc-agent-fab" type="button" aria-label="打开 Agent 助手" onClick={() => setAgentOpen(true)}>
        <Wrench size={17} aria-hidden="true" />
        <span>Agent 助手</span>
      </button>

      {errorDetails && <RequirementCenterErrorDetails failure={errorDetails} onClose={() => setErrorDetails(null)} />}
      {toast && (
        <div className="rc-toast" role="status">
          <Check size={15} aria-hidden="true" /><span>{toast}</span>
        </div>
      )}
    </main>
  );
}

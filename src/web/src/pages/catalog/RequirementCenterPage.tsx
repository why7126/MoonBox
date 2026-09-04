import {
  Bot,
  BookOpen,
  Calendar,
  Check,
  ChevronLeft,
  ChevronRight,
  CircleDot,
  ClipboardList,
  Code2,
  Command,
  Copy,
  FileCheck,
  GitBranch,
  ImageIcon,
  Loader2,
  KeyRound,
  LayoutDashboard,
  ListChecks,
  LogOut,
  Maximize2,
  MessageCircle,
  Minimize2,
  Plus,
  RefreshCw,
  Search,
  Send,
  Settings,
  Sigma,
  SunMoon,
  Table2,
  UserRound,
  Users,
  Wrench,
  X,
} from "lucide-react";
import { ChangeEvent, FormEvent, KeyboardEvent, MouseEvent, RefObject, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import type { LucideIcon } from "lucide-react";
import type { AdminSession } from "../admin/adminAuth";
import { PRODUCT_VERSION } from "../../../../shared/product-version";
import { ChangePasswordModal } from "../admin/AdminUserManagementPage";
import { canAccessAdmin, clearAdminSession, logoutAdmin, readAdminSession, updateAdminProfile } from "../admin/adminAuth";
import { clearFrontendSession, readFrontendSession, saveFrontendSession } from "../home/frontendSession";
import { readUiPreferences, saveUiTheme, UI_PREFERENCES_EVENT } from "../home/uiPreferences";

type IssueType = "requirement" | "bug";
type Theme = "dark" | "light";
type SettingsTab = "general" | "members" | "agents" | "skills" | "integrations" | "danger";
type ProfileUploadState = "idle" | "uploading" | "done" | "failed";
type MarkdownUploadState = "idle" | "uploading" | "done" | "failed";
type MarkdownViewMode = "preview" | "edit" | "split";
type ProgressFocus = "development" | "test" | "manual";
type MarkdownParts = { frontmatter: Array<[string, string]>; frontmatterRaw: string; body: string };
type DrawerState =
  | { type: "none" }
  | { type: "markdown"; issue: IssueCard; document: IssueDocument; content: string; draft: string; loading: boolean; saving: boolean; error: string; mode: MarkdownViewMode; dirty: boolean; savedAt?: string }
  | { type: "tasks"; issue: IssueCard; focus: ProgressFocus }
  | { type: "ai" };
type ChoiceDialog =
  | { type: "none" }
  | { type: "generation" | "completion" | "sprint" | "review"; issue: IssueCard; error: string };
type ActionDialogKind = "analysis" | "command" | "complete" | "sprint" | "opsx" | "apply" | "progress";
type ActionDialog =
  | { type: "none" }
  | { type: ActionDialogKind; issue: IssueCard; tab: "ai" | "import" | "existing" | "new"; ready: boolean; running: boolean; fileName: string; sprintId: string; newSprintId: string; sprintEstimate: number; error: string; adoptedPointIndexes: number[] };

type Stage = {
  id: string;
  title: string;
  subtitle: string;
  emptyTitle: string;
  emptyHint: string;
  emptyDetail: string;
  requiredDocs: string[];
};

type IssueCard = {
  id: string;
  type: IssueType;
  title: string;
  priority: "P0" | "P1" | "P2" | "P3";
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

type Workspace = {
  organizationName: string;
  workspaceId: string;
  name: string;
  slug: string;
  description: string;
  timezone: string;
  memberCount: number;
  role: string;
  status?: string;
  readonly?: boolean;
};

type FrontendUser = {
  name: string;
  avatarInitial: string;
  avatarUrl?: string | null;
  canAccessAdmin: boolean;
  permissions: string[];
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
  sprintOptions?: string[];
  sprint_options?: string[];
};

type SprintOptionModel = {
  id: string;
  status: "进行中" | "规划中";
  used: number;
  total: number;
  disabled: boolean;
};

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

const sprintOptionModels = (options: string[], estimate: number): SprintOptionModel[] => {
  const baseOptions = options.length ? options : ["sprint-004"];
  const ids = baseOptions.length > 1 ? baseOptions : [...baseOptions, nextSprintId(baseOptions)];
  return ids.map((id, index) => {
    const total = 12;
    const used = index === 0 ? 8 : 11;
    return {
      id,
      status: index === 0 ? "进行中" : "规划中",
      used,
      total,
      disabled: estimate > total - used,
    };
  });
};

const firstSelectableSprintId = (options: SprintOptionModel[]) => options.find((option) => !option.disabled)?.id || "";

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
    const line = lines[index];
    if (!line.trim()) {
      index += 1;
      continue;
    }
    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      const level = heading[1].length;
      const className = `level-${level}`;
      blocks.push(<h3 key={index} className={className}>{heading[2]}</h3>);
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
        <div key={index} className="code-block">
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
        <div key={index} className="table-scroll">
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
        <ul key={index}>
          {items.map((item, itemIndex) => (
            <li key={itemIndex} className={item.taskIndex === undefined ? undefined : "task-list-item"}>
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
    while (index < lines.length && lines[index].trim() && !/^(#{1,3})\s+/.test(lines[index]) && !/^[-*]\s+/.test(lines[index]) && !/^```/.test(lines[index]) && !/^\|.+\|$/.test(lines[index])) {
      paragraph.push(lines[index].trim());
      index += 1;
    }
    blocks.push(<p key={index}>{markdownInlineParts(paragraph.join(" "))}</p>);
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

function MarkdownPreviewPane({ content, compact = false, metadataOpen, onToggleMetadata, showMetadata = true, onTaskToggle }: { content: string; compact?: boolean; metadataOpen: boolean; onToggleMetadata: () => void; showMetadata?: boolean; onTaskToggle?: (taskIndex: number, checked: boolean) => void }) {
  const parsed = parseMarkdownFrontmatter(content);
  return (
    <div className={`rc-markdown-prototype-preview${compact ? " compact" : ""}`} aria-label="Markdown 安全预览">
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

type CreatedSpaceApplicationResult = {
  application: {
    id: string;
    name: string;
    code: string;
    status: string;
  };
};

const emptyWorkspace: Workspace = {
  organizationName: "MoonBox",
  workspaceId: "",
  name: "暂无空间",
  slug: "",
  description: "",
  timezone: "Asia/Shanghai",
  memberCount: 0,
  role: "只读",
  readonly: true,
};

const emptyUser: FrontendUser = {
  name: "未登录",
  avatarInitial: "未",
  avatarUrl: null,
  canAccessAdmin: false,
  permissions: [],
};

const frontendNavGroups: Array<{
  group: string;
  items: Array<{ label: string; title: string; icon: LucideIcon; active?: boolean }>;
}> = [
  {
    group: "WORKSPACE",
    items: [
      { label: "研发总览", title: "研发总览", icon: LayoutDashboard },
      { label: "Chat 工作台", title: "Chat 工作台", icon: MessageCircle },
      { label: "需求中心", title: "需求中心", icon: ClipboardList, active: true },
      { label: "Spec", title: "Spec", icon: GitBranch },
      { label: "任务中心", title: "任务中心", icon: ListChecks },
    ],
  },
  {
    group: "CAPABILITIES",
    items: [
      { label: "Skill Center", title: "Skill Center", icon: Command },
      { label: "Agent Center", title: "Agent Center", icon: Bot },
      { label: "知识中心", title: "知识中心", icon: BookOpen },
    ],
  },
] as const;

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

const stageAction: Record<string, Record<IssueType, string>> = {
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

const stageActionLabel: Record<string, Record<IssueType, string>> = {
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

const capabilityForStage = (issueType: IssueType, stage: string, name: string): DocumentCapability => {
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

const visibleIssueDocuments = (stage: Stage, issue: IssueCard) => {
  const allowed = new Set(stageVisibleDocs[stage.id] || stage.requiredDocs);
  return issueDocumentEntries(issue).filter((document) => allowed.has(document.name));
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
  if (stageId === "approved") return `/sprint-propose ${issueCommandTarget(issue)} ${issue.id}`;
  return `${stageAction[stageId]?.[issue.type] || "只读"} ${issue.id}`.trim();
};

const actionForStage = (issue: IssueCard, stageId: string): IssueAction | undefined => {
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

const issueAction = (issue: IssueCard) =>
  issue.action || actionForStage(issue, issue.stage) || {
    command: "只读",
    label: "只读",
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
  if (drawer.type === "markdown") return `${drawer.issue.id} · ${drawer.document.name}`;
  if (drawer.type === "tasks") return `${drawer.issue.id} · tasks.md`;
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
  if (pendingCount <= 0) return [1, 1];
  return [0, pendingCount];
};

const progressFocusLabel: Record<ProgressFocus, string> = {
  development: "研发任务",
  test: "自动化测试",
  manual: "人工验收",
};

const progressPercent = (done = 0, total = 0) => (total ? Math.round((done / total) * 100) : 0);

const auxiliaryActions = (issue: IssueCard): AuxiliaryAction[] => {
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
      priority: "P2",
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
      priority: "P1",
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
      priority: "P0",
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
      priority: "P1",
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
      priority: "P1",
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
      priority: "P0",
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
      priority: "P2",
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
      priority: "P1",
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
      priority: "P1",
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
      priority: "P1",
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
      priority: "P1",
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
      priority: "P1",
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
      priority: "P3",
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
    sprintOptions: ["sprint-004"],
  };
}

const settingsTabs: Array<{ id: SettingsTab; label: string }> = [
  { id: "general", label: "常规" },
  { id: "members", label: "成员与权限" },
  { id: "agents", label: "Agent" },
  { id: "skills", label: "Skill" },
  { id: "integrations", label: "集成" },
  { id: "danger", label: "高级设置" },
];

function getStoredWorkspace(workspaces: Workspace[], selectedWorkspaceId?: string) {
  try {
    const raw = window.localStorage.getItem("moonbox.workspace");
    const fallback = workspaces.find((workspace) => workspace.workspaceId === selectedWorkspaceId) || workspaces[0] || emptyWorkspace;
    if (!workspaces.length) {
      window.localStorage.removeItem("moonbox.workspace");
      return emptyWorkspace;
    }
    if (!raw) {
      window.localStorage.setItem("moonbox.workspace", JSON.stringify(fallback));
      return fallback;
    }
    const stored = JSON.parse(raw) as Partial<Workspace>;
    const matched = workspaces.find((workspace) => workspace.workspaceId === stored.workspaceId);
    if (matched) return matched;
    window.localStorage.setItem("moonbox.workspace", JSON.stringify(fallback));
    return fallback;
  } catch {
    const fallback = workspaces[0] || emptyWorkspace;
    if (workspaces.length) window.localStorage.setItem("moonbox.workspace", JSON.stringify(fallback));
    return fallback;
  }
}

const apiBase = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

const apiUrl = (path: string) => `${apiBase}${path}`;

const avatarImageSrc = (avatarUrl: string | null | undefined) => {
  const url = avatarUrl?.trim();
  if (!url) return null;
  if (/^(https?:|blob:|data:)/i.test(url)) return url;
  return url.startsWith("/") ? apiUrl(url) : url;
};

const authenticatedAvatarCache = new Map<string, Promise<string>>();

const readAuthenticatedAvatar = async (source: string, token: string) => {
  const cached = authenticatedAvatarCache.get(source);
  if (cached) return cached;
  const pending = fetch(source, { headers: { authorization: `Bearer ${token}` } })
    .then((response) => {
      if (!response.ok) throw new Error("头像读取失败");
      return response.blob();
    })
    .then((blob) => URL.createObjectURL(blob))
    .catch((error) => {
      authenticatedAvatarCache.delete(source);
      throw error;
    });
  authenticatedAvatarCache.set(source, pending);
  return pending;
};

async function readProfileApiError(response: Response, fallback = "头像上传失败，请重试。") {
  try {
    const payload = await response.json();
    return payload.detail || payload.message || fallback;
  } catch {
    return fallback;
  }
}

function AuthenticatedRequirementAvatar({
  avatarUrl,
  alt,
  fallback,
}: {
  avatarUrl: string | null | undefined;
  alt: string;
  fallback: string;
}) {
  const [objectUrl, setObjectUrl] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;
    setObjectUrl(null);
    const source = avatarImageSrc(avatarUrl);
    if (!source) return undefined;
    if (/^(blob:|data:)/i.test(source)) {
      setObjectUrl(source);
      return undefined;
    }
    const session = readFrontendSession();
    const adminSession = readAdminSession();
    const token = session?.access_token || adminSession?.access_token;
    if (!token) return undefined;
    void readAuthenticatedAvatar(source, token)
      .then((nextObjectUrl) => {
        if (isActive) setObjectUrl(nextObjectUrl);
      })
      .catch(() => {
        if (isActive) setObjectUrl(null);
      });
    return () => {
      isActive = false;
    };
  }, [avatarUrl]);

  return <span className="rc-avatar">{objectUrl ? <img src={objectUrl} alt={alt} /> : fallback}</span>;
}

function frontendUserFromAdmin(user: AdminSession["user"], fallback: FrontendUser): FrontendUser {
  const displayName = (user.nickname || user.username || fallback.name || emptyUser.name).trim();
  return {
    ...fallback,
    name: displayName,
    avatarInitial: avatarInitial(displayName, fallback.avatarInitial),
    avatarUrl: user.avatar_url ?? null,
  };
}

function avatarInitial(name: string | null | undefined, fallback = emptyUser.avatarInitial) {
  const displayName = name?.trim();
  return displayName ? displayName.slice(0, 2).toUpperCase() : fallback;
}

const sessionAvatarUrl = (avatarUrl: string | null | undefined) =>
  avatarUrl?.startsWith("/api/v1/admin/users/avatar/") ? null : avatarUrl ?? null;

function fallbackUserFromSession(): FrontendUser {
  const frontendSession = readFrontendSession();
  const adminSession = readAdminSession();
  const sessionUser = frontendSession?.user || adminSession?.user;
  const displayName = (
    frontendSession?.username ||
    adminSession?.user.nickname ||
    adminSession?.user.username ||
    ""
  ).trim();
  if (!displayName) return emptyUser;
  return {
    name: displayName,
    avatarInitial: avatarInitial(displayName),
    avatarUrl: sessionAvatarUrl(sessionUser?.avatar_url),
    canAccessAdmin: canAccessAdmin(sessionUser),
    permissions: ["requirement:read"],
  };
}

function FrontendProfileModal({
  user,
  onClose,
  onSaved,
}: {
  user: FrontendUser;
  onClose: () => void;
  onSaved: (nextUser: AdminSession["user"]) => void;
}) {
  const frontendSessionUser = readFrontendSession()?.user;
  const adminSessionUser = readAdminSession()?.user;
  const sessionUser = frontendSessionUser || adminSessionUser;
  const username = sessionUser?.username || user.name;
  const [nickname, setNickname] = useState(sessionUser?.nickname ?? user.name);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(user.avatarUrl ?? sessionUser?.avatar_url ?? null);
  const [avatarPreviewUrl, setAvatarPreviewUrl] = useState<string | null>(avatarImageSrc(user.avatarUrl ?? sessionUser?.avatar_url));
  const [uploadState, setUploadState] = useState<ProfileUploadState>("idle");
  const [uploadError, setUploadError] = useState("");
  const [saveError, setSaveError] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const avatarButtonText = uploadState === "uploading" ? "上传中" : avatarUrl ? "更换" : "上传";

  const uploadAvatar = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploadState("uploading");
    setUploadError("");
    const session = readAdminSession();
    try {
      if (!session?.access_token) throw new Error("登录已失效，请重新登录");
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(apiUrl("/api/v1/auth/avatar"), {
        method: "POST",
        headers: { authorization: `Bearer ${session.access_token}` },
        body: formData,
      });
      if (!response.ok) throw new Error(await readProfileApiError(response));
      const payload = await response.json();
      const persistentUrl = payload.data.url as string;
      const objectUrl = await readAuthenticatedAvatar(apiUrl(persistentUrl), session.access_token);
      setAvatarUrl(persistentUrl);
      setAvatarPreviewUrl(objectUrl);
      setUploadState("done");
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : "头像上传失败，请重试。");
      setUploadState("failed");
    } finally {
      event.target.value = "";
    }
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (isSaving || uploadState === "uploading") return;
    setIsSaving(true);
    setSaveError("");
    try {
      const nextUser = await updateAdminProfile(nickname.trim() || null, avatarUrl);
      onSaved(nextUser);
    } catch (error) {
      setSaveError(error instanceof Error ? error.message : "个人资料保存失败，请重试。");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="rc-profile-mask" role="presentation" onMouseDown={onClose}>
      <form
        className="rc-profile-modal"
        aria-label="个人资料"
        onSubmit={submit}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header className="rc-profile-head">
          <h2>个人资料</h2>
          <button aria-label="关闭个人资料" type="button" onClick={onClose}>
            <X size={17} />
          </button>
        </header>
        <p className="rc-profile-summary">{username}</p>
        <div className="rc-form-row">
          <label><span>头像</span></label>
          <div className="rc-profile-avatar-picker">
            <AuthenticatedRequirementAvatar avatarUrl={avatarPreviewUrl} alt="头像预览" fallback={avatarInitial(nickname || username || user.name)} />
            <span className="rc-profile-avatar-copy">
              <small>支持 JPG、PNG、WEBP，建议 1:1，最大 2MB</small>
              <button type="button" aria-label="上传或更换头像" disabled={uploadState === "uploading" || isSaving} onClick={() => fileInputRef.current?.click()}>
                {avatarButtonText}
              </button>
            </span>
            <input ref={fileInputRef} className="rc-profile-avatar-file" type="file" accept="image/jpeg,image/png,image/webp" aria-label="选择头像文件" onChange={uploadAvatar} />
          </div>
          {uploadState === "failed" && <div className="rc-profile-error" aria-live="polite">{uploadError}</div>}
        </div>
        <div className="rc-form-row">
          <label htmlFor="rc-profile-nickname">昵称</label>
          <input id="rc-profile-nickname" maxLength={128} value={nickname} onChange={(event) => setNickname(event.target.value)} />
        </div>
        {saveError && <div className="rc-profile-error" aria-live="polite">{saveError}</div>}
        <footer>
          <button type="button" onClick={onClose}>取消</button>
          <button className="primary" type="submit" disabled={uploadState === "uploading" || isSaving}>
            {isSaving ? "保存中" : "保存"}
          </button>
        </footer>
      </form>
    </div>
  );
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
    sprintOptions: rawContext.sprint_options || payload.sprintOptions || [],
  };
}

function canManageWorkspace(item: Workspace) {
  if (!item.workspaceId || item.readonly || item.status === "FROZEN") return false;
  return ["拥有者", "管理员"].includes(item.role);
}

function isReadonlyWorkspace(item: Workspace) {
  return Boolean(item.readonly || item.status === "FROZEN");
}

function requiredDocsForIssue(stageId: string, issueType: IssueType) {
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

function readAccessToken() {
  const adminSession = readAdminSession();
  const frontendSession = readFrontendSession();
  return frontendSession?.access_token || adminSession?.access_token || "";
}

function toLocalDateTimeInputValue(date: Date) {
  const pad = (value: number) => String(value).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function defaultExpiryAt() {
  const now = new Date();
  const quarterEndMonth = Math.floor(now.getMonth() / 3) * 3 + 2;
  const quarterEnd = new Date(now.getFullYear(), quarterEndMonth + 1, 0, 23, 59, 59);
  if (quarterEnd <= now) {
    quarterEnd.setMonth(quarterEnd.getMonth() + 3);
  }
  return `${toLocalDateTimeInputValue(quarterEnd)}Z`;
}

function datetimeLocalValue(value: string) {
  return (value || defaultExpiryAt()).replace("Z", "").slice(0, 19);
}

function toDateTimeDisplayValue(value: string) {
  return datetimeLocalValue(value).replace("T", " ");
}

function fromDateTimeDisplayValue(value: string) {
  const normalized = value.trim().replace(/\//g, "-").replace(/\s+/, "T");
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/.test(normalized)) return "";
  const parsed = new Date(`${normalized}Z`);
  if (!Number.isFinite(parsed.getTime())) return "";
  return `${normalized}Z`;
}

function daysInMonth(year: number, month: number) {
  return new Date(year, month + 1, 0).getDate();
}

function clampTimePart(value: string, max: number) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return "00";
  return String(Math.min(Math.max(parsed, 0), max)).padStart(2, "0");
}

function isFutureExpiry(value: string) {
  const parsed = new Date(value);
  return Number.isFinite(parsed.getTime()) && parsed > new Date();
}

function nextFixedExpiryValue(value: string) {
  return isFutureExpiry(value) ? value : defaultExpiryAt();
}

function validateCreateApplicationForm(form: {
  name: string;
  code: string;
  member_quota: string;
  storage_quota_gb: string;
  ai_quota_tokens: string;
  expiry_type: string;
  expires_at: string;
}) {
  const name = form.name.trim();
  const code = form.code.trim();
  const members = Number(form.member_quota);
  const storage = Number(form.storage_quota_gb);
  const aiTokens = Number(form.ai_quota_tokens);
  if (name.length < 2 || name.length > 80) return "空间名称需为 2-80 个字符";
  if (!/^[a-z][a-z0-9-]{1,31}$/.test(code)) return "空间标识需为 2-32 位，以小写字母开头，仅支持小写字母、数字和连字符";
  if (!Number.isInteger(members) || members < 1 || members > 100000) return "成员上限需为 1-100000 的整数";
  if (!Number.isFinite(storage) || storage <= 0) return "存储空间必须大于 0";
  if (!Number.isInteger(aiTokens) || aiTokens < 0) return "AI Tokens 需为不小于 0 的整数";
  if (form.expiry_type === "fixed_date" && !isFutureExpiry(form.expires_at)) return "到期时间必须晚于当前时间";
  return "";
}

function RequirementDateTimePicker({ ariaLabel, value, onChange }: { ariaLabel: string; value: string; onChange: (value: string) => void }) {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState(toDateTimeDisplayValue(value));
  const [panelRect, setPanelRect] = useState({ top: 0, left: 0, width: 0, maxHeight: 360, placement: "bottom" as "top" | "bottom" });
  const selectedLocalValue = datetimeLocalValue(value || defaultExpiryAt());
  const selectedDate = new Date(selectedLocalValue);
  const calendarDate = Number.isFinite(selectedDate.getTime()) ? selectedDate : new Date(datetimeLocalValue(defaultExpiryAt()));
  const year = calendarDate.getFullYear();
  const month = calendarDate.getMonth();
  const monthDays = daysInMonth(year, month);
  const leadingDays = (new Date(year, month, 1).getDay() + 6) % 7;
  const weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];
  const days = Array.from({ length: leadingDays + monthDays }, (_, index) => index < leadingDays ? 0 : index - leadingDays + 1);

  useEffect(() => {
    setDraft(toDateTimeDisplayValue(value));
  }, [value]);

  useEffect(() => {
    if (!open) return undefined;
    const updatePanelRect = () => {
      const rect = rootRef.current?.getBoundingClientRect();
      if (!rect) return;
      const width = Math.max(rect.width, 360);
      const left = Math.min(Math.max(12, rect.left), window.innerWidth - width - 12);
      const margin = 12;
      const gap = 4;
      const preferredHeight = 392;
      const belowSpace = window.innerHeight - rect.bottom - margin;
      const aboveSpace = rect.top - margin;
      const openUpward = belowSpace < preferredHeight && aboveSpace > belowSpace;
      const availableHeight = Math.max(320, Math.min(preferredHeight, openUpward ? aboveSpace - gap : belowSpace));
      const rawTop = openUpward ? rect.top - gap - availableHeight : rect.bottom + gap;
      const top = Math.min(Math.max(margin, rawTop), window.innerHeight - availableHeight - margin);
      setPanelRect({ top, left, width, maxHeight: availableHeight, placement: openUpward ? "top" : "bottom" });
    };
    const handlePointerDown = (event: globalThis.MouseEvent) => {
      const target = event.target as Node;
      const panel = document.querySelector(".admin-datetime-panel");
      if (rootRef.current?.contains(target) || panel?.contains(target)) return;
      setOpen(false);
    };
    updatePanelRect();
    window.addEventListener("resize", updatePanelRect);
    window.addEventListener("scroll", updatePanelRect, true);
    document.addEventListener("mousedown", handlePointerDown, true);
    return () => {
      window.removeEventListener("resize", updatePanelRect);
      window.removeEventListener("scroll", updatePanelRect, true);
      document.removeEventListener("mousedown", handlePointerDown, true);
    };
  }, [open]);

  const commitLocalValue = (nextLocalValue: string) => {
    onChange(`${nextLocalValue}Z`);
    setDraft(nextLocalValue.replace("T", " "));
  };
  const updateDatePart = (nextDate: Date) => {
    const current = datetimeLocalValue(value || defaultExpiryAt());
    const [, time = "23:59:59"] = current.split("T");
    commitLocalValue(`${toLocalDateTimeInputValue(nextDate).slice(0, 10)}T${time}`);
  };
  const updateTimePart = (part: "hour" | "minute" | "second", rawValue: string) => {
    const [datePart, timePart = "23:59:59"] = selectedLocalValue.split("T");
    const [hour = "23", minute = "59", second = "59"] = timePart.split(":");
    const nextHour = part === "hour" ? clampTimePart(rawValue, 23) : hour;
    const nextMinute = part === "minute" ? clampTimePart(rawValue, 59) : minute;
    const nextSecond = part === "second" ? clampTimePart(rawValue, 59) : second;
    commitLocalValue(`${datePart}T${nextHour}:${nextMinute}:${nextSecond}`);
  };
  const shiftMonth = (step: number) => {
    const next = new Date(year, month + step, Math.min(calendarDate.getDate(), 28), calendarDate.getHours(), calendarDate.getMinutes(), calendarDate.getSeconds());
    updateDatePart(next);
  };
  const applyShortcut = (mode: "today" | "quarter" | "year") => {
    const now = new Date();
    if (mode === "today") {
      commitLocalValue(`${toLocalDateTimeInputValue(now).slice(0, 10)}T23:59:59`);
      setOpen(false);
      return;
    }
    if (mode === "year") {
      commitLocalValue(`${now.getFullYear() + 1}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}T23:59:59`);
      setOpen(false);
      return;
    }
    commitLocalValue(datetimeLocalValue(defaultExpiryAt()));
    setOpen(false);
  };
  const commitDraft = () => {
    const parsed = fromDateTimeDisplayValue(draft);
    if (parsed) {
      onChange(parsed);
      setDraft(toDateTimeDisplayValue(parsed));
    } else {
      setDraft(toDateTimeDisplayValue(value));
    }
  };
  const panel = open && createPortal(
    <div className={`admin-datetime-panel ${themeClassFromBody()}`} data-placement={panelRect.placement} role="dialog" aria-label={`${ariaLabel}选择器`} style={{ top: panelRect.top, left: panelRect.left, width: panelRect.width, maxHeight: panelRect.maxHeight }}>
      <div className="admin-datetime-calendar-head">
        <button type="button" aria-label="上个月" onClick={() => shiftMonth(-1)}><ChevronLeft size={16} /></button>
        <strong>{year}年{month + 1}月</strong>
        <button type="button" aria-label="下个月" onClick={() => shiftMonth(1)}><ChevronRight size={16} /></button>
      </div>
      <div className="admin-datetime-weekdays">{weekdays.map((day) => <span key={day}>{day}</span>)}</div>
      <div className="admin-datetime-days">
        {days.map((day, index) => day === 0 ? <span key={`blank-${index}`} /> : (
          <button key={day} type="button" className={day === calendarDate.getDate() ? "active" : ""} onClick={() => updateDatePart(new Date(year, month, day, calendarDate.getHours(), calendarDate.getMinutes(), calendarDate.getSeconds()))}>{day}</button>
        ))}
      </div>
      <div className="admin-datetime-time" aria-label="时间选择">
        <label>时<input type="number" min="0" max="23" value={selectedLocalValue.slice(11, 13)} onChange={(event) => updateTimePart("hour", event.target.value)} /></label>
        <label>分<input type="number" min="0" max="59" value={selectedLocalValue.slice(14, 16)} onChange={(event) => updateTimePart("minute", event.target.value)} /></label>
        <label>秒<input type="number" min="0" max="59" value={selectedLocalValue.slice(17, 19)} onChange={(event) => updateTimePart("second", event.target.value)} /></label>
      </div>
      <div className="admin-datetime-shortcuts">
        <button type="button" onClick={() => applyShortcut("today")}>今天 23:59:59</button>
        <button type="button" onClick={() => applyShortcut("quarter")}>本季度末</button>
        <button type="button" onClick={() => applyShortcut("year")}>一年后</button>
      </div>
    </div>,
    document.body,
  );

  return (
    <div className="admin-datetime-picker" ref={rootRef} data-testid="catalog-datetime-picker">
      <input ref={inputRef} aria-label={ariaLabel} type="text" required value={draft} onBlur={commitDraft} onChange={(event) => setDraft(event.target.value)} onFocus={() => setOpen(true)} placeholder="yyyy-mm-dd hh:mm:ss" />
      <button
        type="button"
        aria-label={`选择${ariaLabel}`}
        onClick={() => {
          if (open) {
            setOpen(false);
            return;
          }
          setOpen(true);
          inputRef.current?.focus();
        }}
      >
        <Calendar size={16} />
      </button>
      {panel}
    </div>
  );
}

function themeClassFromBody() {
  if (typeof document === "undefined") return "dark";
  return document.querySelector(".requirement-center.theme-light") ? "light" : "dark";
}

export function RequirementCenterPage() {
  const [context, setContext] = useState<RequirementCenterContext | null>(null);
  const [isLoadingContext, setIsLoadingContext] = useState(true);
  const [isRefreshingContext, setIsRefreshingContext] = useState(false);
  const [contextError, setContextError] = useState("");
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [theme, setTheme] = useState<Theme>(() => readUiPreferences().theme);
  const [typeFilter, setTypeFilter] = useState<"all" | IssueType>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [ownerFilter, setOwnerFilter] = useState("全部负责人");
  const [priorityFilter, setPriorityFilter] = useState("全部优先级");
  const [sprintFilter, setSprintFilter] = useState("全部 Sprint");
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isSpacePopoverOpen, setIsSpacePopoverOpen] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [workspace, setWorkspace] = useState<Workspace>(emptyWorkspace);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isApplicationOpen, setIsApplicationOpen] = useState(false);
  const [applicationError, setApplicationError] = useState("");
  const [isSubmittingApplication, setIsSubmittingApplication] = useState(false);
  const [createdSpaceResult, setCreatedSpaceResult] = useState<CreatedSpaceApplicationResult | null>(null);
  const [isCodeManuallyEdited, setIsCodeManuallyEdited] = useState(false);
  const [createApplicationForm, setCreateApplicationForm] = useState({
    name: "",
    code: "",
    description: "",
    member_quota: "20",
    storage_quota_gb: "100",
    ai_quota_tokens: "1000000",
    expiry_type: "fixed_date",
    expires_at: defaultExpiryAt(),
  });
  const [settingsTab, setSettingsTab] = useState<SettingsTab>("general");
  const [toast, setToast] = useState("");
  const [captureOpen, setCaptureOpen] = useState(false);
  const [agentOpen, setAgentOpen] = useState(false);
  const [captureForm, setCaptureForm] = useState({
    type: "requirement" as IssueType,
    title: "",
    priority: "P1" as IssueCard["priority"],
    description: "",
    owner: "产品团队",
    source: "explore",
  });
  const [captureError, setCaptureError] = useState("");
  const [drawer, setDrawer] = useState<DrawerState>({ type: "none" });
  const [drawerWidth, setDrawerWidth] = useState(760);
  const [isDrawerFullscreen, setIsDrawerFullscreen] = useState(false);
  const [markdownUploadState, setMarkdownUploadState] = useState<MarkdownUploadState>("idle");
  const [markdownUploadError, setMarkdownUploadError] = useState("");
  const [markdownMetadataOpen, setMarkdownMetadataOpen] = useState(false);
  const [choiceDialog, setChoiceDialog] = useState<ChoiceDialog>({ type: "none" });
  const [actionDialog, setActionDialog] = useState<ActionDialog>({ type: "none" });
  const [lockedActionId, setLockedActionId] = useState("");
  const [aiMessages, setAiMessages] = useState<Array<{ role: "ai" | "user"; content: string }>>([
    { role: "ai", content: "我会在这里汇总卡片动作、命令上下文和失败原因。" },
  ]);
  const [aiDraft, setAiDraft] = useState("");
  const [draftWorkspace, setDraftWorkspace] = useState(emptyWorkspace);
  const closeTimerRef = useRef<number | null>(null);
  const userZoneRef = useRef<HTMLDivElement>(null);
  const spacePopoverRef = useRef<HTMLElement>(null);
  const captureTitleRef = useRef<HTMLInputElement | null>(null);
  const drawerResizeRef = useRef({ active: false, startX: 0, startWidth: 760 });
  const markdownEditorRef = useRef<HTMLTextAreaElement | null>(null);
  const pendingMarkdownSelectionRef = useRef<{ start: number; end: number } | null>(null);
  const issues = context?.issues ?? [];
  const availableWorkspaces = context?.workspaces ?? [];
  const [sessionFallbackUser, setSessionFallbackUser] = useState<FrontendUser>(() => fallbackUserFromSession());
  const activeUser = context?.currentUser ?? sessionFallbackUser;
  const sprintOptions = context?.sprintOptions || context?.sprint_options || [];

  const isEditableDocument = (state: DrawerState): state is Extract<DrawerState, { type: "markdown" }> => (
    state.type === "markdown" && canEditDocument(state.document)
  );

  const isTaskToggleDocument = (state: DrawerState): state is Extract<DrawerState, { type: "markdown" }> => (
    state.type === "markdown" && canToggleTaskDocument(state.document)
  );

  const isMutableMarkdownDrawer = (state: DrawerState): state is Extract<DrawerState, { type: "markdown" }> => (
    state.type === "markdown" && canMutateMarkdownDocument(state.document)
  );

  const isDirtyMarkdownDrawer = useCallback((state: DrawerState = drawer) => (
    isMutableMarkdownDrawer(state) && state.dirty && composeMarkdownContent(state.content, state.draft) !== state.content
  ), [drawer]);
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
    setDrawer({ type: "none" });
  }, [drawer, isDirtyMarkdownDrawer]);

  const beginDrawerResize = (event: MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    if (isDrawerFullscreen) return;
    drawerResizeRef.current = { active: true, startX: event.clientX, startWidth: drawerWidth };
    document.body.classList.add("rc-resizing-drawer");
  };

  const loadContext = useCallback(async (mode: "initial" | "refresh" = "initial") => {
    const isRefresh = mode === "refresh";
    if (isRefresh) {
      setIsRefreshingContext(true);
    } else {
      setIsLoadingContext(true);
    }
    setContextError("");
    try {
      const frontendSession = readFrontendSession();
      if (isWorkflowDemoMode()) {
        const nextContext = buildWorkflowDemoContext(frontendSession?.username);
        const nextWorkspace = getStoredWorkspace(nextContext.workspaces, nextContext.selectedWorkspaceId);
        setContext(nextContext);
        setSessionFallbackUser(nextContext.currentUser);
        setWorkspace(nextWorkspace);
        setDraftWorkspace(nextWorkspace);
        return;
      }
      const token = readAccessToken();
      const response = await fetch("/api/v1/requirement-center/context", {
        headers: {
          accept: "application/json",
          ...(token ? { authorization: `Bearer ${token}` } : {}),
        },
      });
      if (response.status === 401 || response.status === 403) {
        setContext(null);
        clearFrontendSession();
        clearAdminSession();
        setSessionFallbackUser(emptyUser);
        if (window.location.pathname !== "/login") {
          window.history.replaceState(null, "", "/login");
          window.dispatchEvent(new PopStateEvent("popstate"));
        }
        setContextError("登录态已失效，请重新登录");
        return;
      }
      if (!response.ok) {
        throw new Error(`需求中心数据加载失败：${response.status}`);
      }
      const envelope = (await response.json()) as ApiEnvelope<RequirementCenterContext>;
      const nextContext = normalizeContext(envelope.data, frontendSession?.username);
      const nextWorkspace = getStoredWorkspace(nextContext.workspaces, nextContext.selectedWorkspaceId);
      setContext(nextContext);
      setSessionFallbackUser(nextContext.currentUser);
      setWorkspace(nextWorkspace);
      setDraftWorkspace(nextWorkspace);
    } catch {
      if (isRefresh) {
        setToast("刷新失败，已保留当前看板");
      } else {
        setContext(null);
        setContextError("需求中心数据暂时不可用，请稍后重试");
      }
    } finally {
      if (isRefresh) {
        setIsRefreshingContext(false);
      } else {
        setIsLoadingContext(false);
      }
    }
  }, []);

  useEffect(() => {
    void loadContext();
  }, [loadContext]);

  useEffect(() => {
    const syncTheme = () => setTheme(readUiPreferences().theme);
    window.addEventListener(UI_PREFERENCES_EVENT, syncTheme);
    window.addEventListener("storage", syncTheme);
    return () => {
      window.removeEventListener(UI_PREFERENCES_EVENT, syncTheme);
      window.removeEventListener("storage", syncTheme);
    };
  }, []);

  useEffect(() => {
    const closeOnEscape = (event: globalThis.KeyboardEvent) => {
      if (event.key !== "Escape") return;
      setIsSpacePopoverOpen(false);
      setIsUserMenuOpen(false);
      setIsSettingsOpen(false);
      setIsProfileModalOpen(false);
      setIsPasswordModalOpen(false);
      setCaptureOpen(false);
      setAgentOpen(false);
      setChoiceDialog({ type: "none" });
      setActionDialog({ type: "none" });
      closeDrawer();
    };
    document.addEventListener("keydown", closeOnEscape);
    return () => document.removeEventListener("keydown", closeOnEscape);
  }, [closeDrawer]);

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
    const closeOnOutsideClick = (event: globalThis.MouseEvent) => {
      const target = event.target as Node;
      if (userZoneRef.current?.contains(target) || spacePopoverRef.current?.contains(target)) return;
      setIsUserMenuOpen(false);
      setIsSpacePopoverOpen(false);
    };
    document.addEventListener("mousedown", closeOnOutsideClick);
    return () => document.removeEventListener("mousedown", closeOnOutsideClick);
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

  const owners = useMemo(() => ["全部负责人", ...Array.from(new Set(issues.map((issue) => issue.owner)))], [issues]);
  const priorities = ["全部优先级", "P0", "P1", "P2"];
  const captureOwners = ["产品团队", "研发团队", "设计团队", "未分配"];
  const captureSources = [
    { value: "explore", label: "explore · 前置探索" },
    { value: "user-feedback", label: "user-feedback · 用户反馈" },
    { value: "internal", label: "internal · 内部提出" },
    { value: "incident", label: "incident · 故障复盘" },
  ];
  const sprints = useMemo(
    () => ["全部 Sprint", ...Array.from(new Set(issues.map((issue) => visibleSprintId(issue)).filter(Boolean)))],
    [issues],
  );

  const filteredIssues = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    return issues.filter((issue) => {
      const matchesType = typeFilter === "all" || issue.type === typeFilter;
      const matchesSearch =
        !query ||
        issue.id.toLowerCase().includes(query) ||
        issue.title.toLowerCase().includes(query) ||
        issue.owner.toLowerCase().includes(query) ||
        issue.documents.some((doc) => doc.toLowerCase().includes(query));
      const matchesOwner = ownerFilter === "全部负责人" || issue.owner === ownerFilter;
      const matchesPriority = priorityFilter === "全部优先级" || issue.priority === priorityFilter;
      const matchesSprint = sprintFilter === "全部 Sprint" || visibleSprintId(issue) === sprintFilter;
      return matchesType && matchesSearch && matchesOwner && matchesPriority && matchesSprint;
    });
  }, [issues, ownerFilter, priorityFilter, searchQuery, sprintFilter, typeFilter]);

  const manageableWorkspace = canManageWorkspace(workspace);

  const stats = [
    { label: "全部对象", value: filteredIssues.length },
    { label: "需求", value: filteredIssues.filter((issue) => issue.type === "requirement").length },
    { label: "Bug", value: filteredIssues.filter((issue) => issue.type === "bug").length },
    { label: "当前阻塞", value: filteredIssues.filter((issue) => issue.blocked).length },
  ];
  const activeFilterCount = [
    ownerFilter !== "全部负责人",
    priorityFilter !== "全部优先级",
    sprintFilter !== "全部 Sprint",
  ].filter(Boolean).length;

  const cancelSpacePopoverClose = () => {
    if (closeTimerRef.current) window.clearTimeout(closeTimerRef.current);
    closeTimerRef.current = null;
  };

  const scheduleSpacePopoverClose = () => {
    cancelSpacePopoverClose();
    closeTimerRef.current = window.setTimeout(() => {
      setIsSpacePopoverOpen(false);
    }, 180);
  };

  const closeSpacePopoverNow = () => {
    cancelSpacePopoverClose();
    setIsSpacePopoverOpen(false);
  };

  const openApplicationCenter = () => {
    closeSpacePopoverNow();
    setIsUserMenuOpen(false);
    setIsApplicationOpen(true);
    setApplicationError("");
    setCreatedSpaceResult(null);
  };

  const submitCreateApplication = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const validationError = validateCreateApplicationForm(createApplicationForm);
    if (validationError) {
      setApplicationError(validationError);
      return;
    }
    setIsSubmittingApplication(true);
    setApplicationError("");
    try {
      const token = readAccessToken();
      const response = await fetch("/api/v1/catalog/workspace-applications/create", {
        method: "POST",
        headers: { "content-type": "application/json", authorization: `Bearer ${token}` },
        body: JSON.stringify({
          ...createApplicationForm,
          member_quota: Number(createApplicationForm.member_quota),
          storage_quota_gb: Number(createApplicationForm.storage_quota_gb),
          ai_quota_tokens: Number(createApplicationForm.ai_quota_tokens),
          expires_at: createApplicationForm.expiry_type === "fixed_date" ? createApplicationForm.expires_at : null,
        }),
      });
      if (!response.ok) throw new Error(await response.text());
      const envelope = (await response.json()) as ApiEnvelope<CreatedSpaceApplicationResult>;
      setCreatedSpaceResult(envelope.data);
      setToast("创建空间申请已提交");
      setCreateApplicationForm({ name: "", code: "", description: "", member_quota: "20", storage_quota_gb: "100", ai_quota_tokens: "1000000", expiry_type: "fixed_date", expires_at: defaultExpiryAt() });
      setIsCodeManuallyEdited(false);
      await loadContext("refresh");
    } catch {
      setApplicationError("创建空间失败，请检查必填项、空间标识和配额范围");
    } finally {
      setIsSubmittingApplication(false);
    }
  };

  const updateCreateName = (value: string) => {
    const slug = value
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9-]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 32);
    setCreateApplicationForm((current) => ({ ...current, name: value, code: isCodeManuallyEdited ? current.code : slug }));
  };

  const enterAdmin = () => {
    closeSpacePopoverNow();
    setIsUserMenuOpen(false);
    window.history.pushState(null, "", "/admin");
    window.dispatchEvent(new PopStateEvent("popstate"));
  };

  const openChangePassword = () => {
    closeSpacePopoverNow();
    setIsUserMenuOpen(false);
    setIsPasswordModalOpen(true);
  };

  const openProfile = () => {
    closeSpacePopoverNow();
    setIsUserMenuOpen(false);
    setIsProfileModalOpen(true);
  };

  const completeProfileSave = (nextUser: AdminSession["user"]) => {
    const nextFrontendUser = frontendUserFromAdmin(nextUser, activeUser);
    setContext((current) => current ? { ...current, currentUser: nextFrontendUser } : current);
    const session = readAdminSession();
    if (session) {
      saveFrontendSession({ ...session, user: nextUser });
    } else {
      saveFrontendSession(nextFrontendUser.name);
    }
    setIsProfileModalOpen(false);
    setToast("个人资料已更新");
  };

  const completePasswordChange = () => {
    setIsPasswordModalOpen(false);
    clearFrontendSession();
    window.history.pushState(null, "", "/login");
    window.dispatchEvent(new PopStateEvent("popstate"));
  };

  const openIssueDetail = (issue: IssueCard) => {
    window.open(issueDetailUrl(issue), "_blank", "noopener,noreferrer");
  };

  const openDocument = async (issue: IssueCard, document: IssueDocument) => {
    const mode = document.openMode || document.open_mode;
    if (document.status && document.status !== "available") {
      setToast("文档暂不可用，未触发卡片流转");
      return;
    }
    if (document.type === "html" || mode === "new-tab") {
      if (document.htmlContent) {
        const demoUrl = URL.createObjectURL(new Blob([document.htmlContent], { type: "text/html" }));
        window.open(demoUrl, "_blank", "noopener,noreferrer");
        window.setTimeout(() => URL.revokeObjectURL(demoUrl), 30_000);
        return;
      }
      window.open(document.url || `${issueDetailUrl(issue)}?document=${encodeURIComponent(document.name)}`, "_blank", "noopener,noreferrer");
      return;
    }
    setMarkdownUploadState("idle");
    setMarkdownUploadError("");
    setMarkdownMetadataOpen(false);
    setIsDrawerFullscreen(false);
    setDrawer({ type: "markdown", issue, document, content: "", draft: "", loading: true, saving: false, error: "", mode: "preview", dirty: false });
    if (document.content) {
      setDrawer({
        type: "markdown",
        issue,
        document,
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
      const token = readAccessToken();
      const response = await fetch(document.url || `/api/v1/requirement-center/issues/${issue.id}/documents/${document.name}`, {
        headers: { accept: "application/json", ...(token ? { authorization: `Bearer ${token}` } : {}) },
      });
      if (!response.ok) throw new Error(response.status === 403 ? "无权读取该文档" : "文档读取失败");
      const envelope = (await response.json()) as ApiEnvelope<{ content: string }>;
      setDrawer({ type: "markdown", issue, document, content: envelope.data.content, draft: parseMarkdownFrontmatter(envelope.data.content).body, loading: false, saving: false, error: "", mode: "preview", dirty: false });
    } catch (error) {
      setDrawer({ type: "markdown", issue, document, content: "", draft: "", loading: false, saving: false, error: sanitizeFeedback(error instanceof Error ? error.message : "文档读取失败"), mode: "preview", dirty: false });
    }
  };

  const saveMarkdownDocument = async () => {
    if (drawer.type !== "markdown" || !isMutableMarkdownDrawer(drawer) || drawer.saving) return;
    const currentDrawer = drawer;
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
      const response = await fetch(isTaskToggleDocument(currentDrawer) ? `${baseUrl}/tasks` : baseUrl, {
        method: "PUT",
        headers: {
          accept: "application/json",
          "content-type": "application/json",
          ...(token ? { authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ content: contentToSave }),
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
      const envelope = (await response.json()) as ApiEnvelope<{ content: string }>;
      if (typeof envelope.data?.content !== "string") {
        throw new Error("文档保存响应异常，内容已保留");
      }
      setDrawer({ ...currentDrawer, content: envelope.data.content, draft: parseMarkdownFrontmatter(envelope.data.content).body, saving: false, error: "", mode: "preview", dirty: false, savedAt: "刚刚保存" });
      setToast(`${currentDrawer.document.name} 已保存`);
    } catch (error) {
      const message = sanitizeFeedback(error instanceof Error ? error.message : "文档保存失败，内容已保留");
      setDrawer((latest) => (latest.type === "markdown" ? { ...latest, saving: false, error: message } : latest));
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

  const submitCapture = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const title = captureForm.title.trim();
    if (!title) {
      setCaptureError("标题不能为空");
      return;
    }
    const prefix = captureForm.type === "requirement" ? "REQ" : "BUG";
    const nextNumber = Math.max(
      0,
      ...issues
        .filter((issue) => issue.id.startsWith(`${prefix}-`))
        .map((issue) => Number(issue.id.split("-")[1]) || 0),
    ) + 1;
    const id = `${prefix}-${String(nextNumber).padStart(4, "0")}`;
    const newIssue: IssueCard = {
      id,
      type: captureForm.type,
      title,
      priority: captureForm.priority,
      owner: captureForm.owner,
      source: captureForm.source,
      stage: "capture",
      documents: ["capture.md", "trace.md"],
      documentEntries: [
        { name: "capture.md", type: "markdown", openMode: "drawer", label: "capture.md", status: "available" },
        { name: "trace.md", type: "markdown", openMode: "drawer", label: "trace.md", status: "available" },
      ],
      updatedAt: "刚刚",
      detailUrl: `/requirements/${id}`,
      action: {
        command: `${captureForm.type === "requirement" ? "/req-generate" : "/bug-generate"} ${id}`,
        label: captureForm.type === "requirement" ? "生成需求" : "生成 Bug",
        requiresChoice: "generation",
      },
    };
    setContext((current) => current ? { ...current, issues: [newIssue, ...current.issues] } : current);
    setCaptureForm({ type: "requirement", title: "", priority: "P1", description: "", owner: "产品团队", source: "explore" });
    setCaptureError("");
    setCaptureOpen(false);
    setToast("Capture 已创建并插入采集池");
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
    const action = auxAction || issueAction(issue);
    if (actionDisabledReason(action as IssueAction)) {
      appendAiMessage(`${issue.id} 前置条件不满足：${actionDisabledReason(action as IssueAction)}`);
      setDrawer({ type: "ai" });
      return;
    }
    const type = actionDialogType(issue, action);
    const sprintEstimate = issueSprintEstimate(issue);
    const sprintModels = sprintOptionModels(sprintOptions, sprintEstimate);
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
    if (lockedActionId) return;
    if (actionDisabledReason(action)) {
      appendAiMessage(`${issue.id} 前置条件不满足：${actionDisabledReason(action)}`);
      setDrawer({ type: "ai" });
      return;
    }
    const choice = actionChoice(action, issue);
    if (choice && !options) {
      setChoiceDialog({ type: choice as ChoiceDialog["type"], issue, error: "" });
      return;
    }
    if (issue.stage === "development") {
      setDrawer({ type: "tasks", issue, focus: "development" });
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
    if (actionDialog.type === "none" || actionDialog.running) return;
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

  const logoutFrontend = async () => {
    closeSpacePopoverNow();
    setIsUserMenuOpen(false);
    const adminSession = readAdminSession();
    if (adminSession?.access_token) {
      await logoutAdmin();
    } else {
      clearFrontendSession();
    }
    window.history.pushState(null, "", "/login");
    window.dispatchEvent(new PopStateEvent("popstate"));
  };

  const toggleSidebar = () => {
    setIsSidebarCollapsed((value) => !value);
    setIsUserMenuOpen(false);
    setIsSpacePopoverOpen(false);
  };

  const selectWorkspace = (item: Workspace) => {
    setWorkspace(item);
    setDraftWorkspace(item);
    setContext((current) => current ? { ...current, selectedWorkspaceId: item.workspaceId } : current);
    setTypeFilter("all");
    setSearchQuery("");
    setOwnerFilter("全部负责人");
    setPriorityFilter("全部优先级");
    setSprintFilter("全部 Sprint");
    window.localStorage.setItem("moonbox.workspace", JSON.stringify(item));
    setIsSpacePopoverOpen(false);
    setIsUserMenuOpen(false);
    setToast(`已切换到 ${item.name}`);
  };

  const openSpaceSettings = (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    setDraftWorkspace(workspace);
    setIsSettingsOpen(true);
    setIsUserMenuOpen(false);
    setIsSpacePopoverOpen(false);
  };

  const updateDraft = (field: keyof Workspace) => (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setDraftWorkspace((current) => ({ ...current, [field]: event.target.value }));
  };

  const saveSpaceSettings = () => {
    setWorkspace(draftWorkspace);
    window.localStorage.setItem("moonbox.workspace", JSON.stringify(draftWorkspace));
    setIsSettingsOpen(false);
    setToast("空间设置已保存");
    void loadContext();
  };

  const handleMenuKey = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Escape") {
      setIsUserMenuOpen(false);
      setIsSpacePopoverOpen(false);
    }
  };

  const stageColumns = stages.map((stage) => ({
    stage,
    items: filteredIssues.filter((issue) => issue.stage === stage.id),
  }));

  const runAgentStageAction = (stage: Stage, issue: IssueCard) => {
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
    const actionLabel = action.label || stageActionLabel[stage.id][issue.type];
    const isDoneStage = stage.id === "done";
    const showArchive = !isDoneStage && (stage.id !== "acceptance" || canArchive(issue));
    const isLocked = lockedActionId === issue.id;
    const documents = visibleIssueDocuments(stage, issue);
    const taskProgress = visibleTaskProgress(issue);
    const manualProgress = visibleManualAcceptanceProgress(issue);
    const auxActions = auxiliaryActions(issue);

    return (
      <article className={`rc-card ${issue.type}`} data-issue-id={issue.id} key={issue.id}>
        <div className="rc-card-top">
          <strong>{issue.id}</strong>
          {visibleSprintId(issue) && <span className="rc-sprint-tag">{visibleSprintId(issue)}</span>}
        </div>
        <button className="rc-card-title" type="button" onClick={() => openIssueDetail(issue)}>{issue.title}</button>
        <div className="rc-card-meta rc-card-tags">
          <span className={`rc-priority-tag rc-tag ${issue.priority.toLowerCase()}`}>{issue.priority}</span>
          <span className="rc-owner-tag rc-tag">{issue.owner}</span>
        </div>
        <div className="rc-docs" aria-label={`${issue.id} 关联文档`}>
          {documents.map((document, index) => (
            <span className="rc-doc-item" key={document.name}>
              {index > 0 && <span className="rc-doc-separator" aria-hidden="true"> </span>}
              <button type="button" onClick={(event) => { event.stopPropagation(); void openDocument(issue, document); }}>
                {document.label || document.name}
              </button>
            </span>
          ))}
        </div>
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
                onClick={() => setDrawer({ type: "tasks", issue, focus: "development" })}
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
                onClick={() => setDrawer({ type: "tasks", issue, focus: "test" })}
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
                onClick={() => setDrawer({ type: "tasks", issue, focus: "manual" })}
              >
                <span className="rc-progress-label">人工验收</span>
                <b className="rc-progress-value">{manualProgress[0]}/{manualProgress[1]}</b>
              </button>
            )}
          </div>
        )}
        <footer>
          <span className="rc-updated">更新 {issue.updatedAt}</span>
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
              <button className="primary" type="button" title={action.command} disabled={isLocked || Boolean(actionDisabledReason(action))} onClick={() => openIssueActionDialog(issue)}>
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
    const taskProgress = dialog.issue.taskProgress || [0, 0];
    const testProgress = dialog.issue.testProgress;
    const estimate = dialog.issue.priority === "P0" ? 5 : dialog.issue.priority === "P1" ? 3 : 2;
    const changeCount = dialog.issue.type === "requirement" && ["P0", "P1"].includes(dialog.issue.priority) ? 2 : 1;

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
      const options = sprintOptionModels(sprintOptions, dialog.sprintEstimate || estimate);
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
                          <span className="rc-sprint-option-name">{option.id}<em className={`rc-sprint-status-pill ${option.status === "进行中" ? "active" : "planned"}`}>{option.status}</em>{option.disabled && <em className="rc-sprint-capacity-badge">容量不足</em>}</span>
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

    if (dialog.type === "progress") {
      return (
        <div className="rc-action-field">
          <label>Change 研发进度</label>
          <div className="rc-action-change">
            <div className="rc-action-change-head"><strong>{dialog.issue.id}</strong><span>{taskProgress[0]}/{taskProgress[1]}</span></div>
            <small>{dialog.issue.title}</small>
            <div className="rc-mini-bar"><span style={{ width: `${taskProgress[1] ? Math.round((taskProgress[0] / taskProgress[1]) * 100) : 0}%` }} /></div>
          </div>
          {testProgress && (
            <div className="rc-action-change">
              <div className="rc-action-change-head"><strong>自动化测试</strong><span>{testProgress[0]}/{testProgress[1]}</span></div>
              <div className="rc-mini-bar"><span style={{ width: `${testProgress[1] ? Math.round((testProgress[0] / testProgress[1]) * 100) : 0}%` }} /></div>
            </div>
          )}
        </div>
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
      <aside className={`rc-sidebar ${isSidebarCollapsed ? "collapsed" : ""}`}>
        <div className="rc-brand">
          <span className="rc-brand-mark">
            <img src="/brand/moonbox/moonbox-app-icon-256.png" alt="MoonBox 产品图标" />
          </span>
          {!isSidebarCollapsed && (
            <div className="rc-brand-copy">
              <strong>MoonBox</strong>
              <small>OPS WORKBENCH</small>
            </div>
          )}
          {!isSidebarCollapsed && <span className="rc-version-badge">{PRODUCT_VERSION}</span>}
          <button
            className="rc-collapse"
            type="button"
            onClick={toggleSidebar}
            aria-label={isSidebarCollapsed ? "展开侧边栏" : "收起侧边栏"}
          >
            {isSidebarCollapsed ? "›" : "‹"}
          </button>
        </div>
        <nav className="rc-nav" aria-label="前台导航">
          {frontendNavGroups.map((group) => (
            <div className="rc-nav-group" key={group.group}>
              <span className="rc-nav-group-label">{group.group}</span>
              {group.items.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    className={`rc-nav-item ${item.active ? "active" : ""}`}
                    type="button"
                    title={item.title}
                    aria-current={item.active ? "page" : undefined}
                    key={item.label}
                  >
                    <Icon className="rc-nav-icon" size={16} strokeWidth={1.5} aria-hidden="true" />
                    <span className="rc-nav-label">{item.label}</span>
                  </button>
                );
              })}
            </div>
          ))}
        </nav>
        <div className="rc-sidebar-bottom">
          <div className="rc-user-zone" ref={userZoneRef} onKeyDown={handleMenuKey}>
            <button
              className="rc-user-trigger"
              type="button"
              onClick={() => setIsUserMenuOpen((value) => !value)}
              aria-haspopup="menu"
              aria-expanded={isUserMenuOpen}
            >
              <AuthenticatedRequirementAvatar avatarUrl={activeUser.avatarUrl} alt={`${activeUser.name} 头像`} fallback={activeUser.avatarInitial} />
              {!isSidebarCollapsed && (
              <span className="rc-user-copy">
                <strong>{activeUser.name}</strong>
                <em>{workspace.name}</em>
              </span>
            )}
              {!isSidebarCollapsed && <span className={`rc-user-chevron ${isUserMenuOpen ? "open" : ""}`} aria-hidden="true">{isUserMenuOpen ? "⌄" : "⌃"}</span>}
            </button>
            {isUserMenuOpen && !isSidebarCollapsed && (
              <div className="rc-user-menu" role="menu" aria-label="用户菜单" onMouseLeave={scheduleSpacePopoverClose} onMouseEnter={cancelSpacePopoverClose}>
                <div className="rc-menu-group" role="group" aria-label="账号">
                  <button role="menuitem" type="button" onMouseEnter={closeSpacePopoverNow} onClick={openProfile}>
                    <UserRound className="rc-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" /> 个人资料
                  </button>
                  <button role="menuitem" type="button" onMouseEnter={closeSpacePopoverNow} onClick={openChangePassword}>
                    <KeyRound className="rc-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" /> 修改密码
                  </button>
                  {activeUser.canAccessAdmin && (
                    <button role="menuitem" type="button" onMouseEnter={closeSpacePopoverNow} onClick={enterAdmin}>
                      <LayoutDashboard className="rc-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" /> 进入后台
                    </button>
                  )}
                </div>
                <div className="rc-menu-group" role="group" aria-label="空间">
                  <button
                    className="rc-has-submenu"
                    role="menuitem"
                    type="button"
                    onMouseEnter={() => {
                      cancelSpacePopoverClose();
                      setIsSpacePopoverOpen(true);
                    }}
                  >
                    <Users className="rc-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" />
                    <span>切换空间</span>
                    <span className="rc-submenu-arrow" aria-hidden="true">&gt;</span>
                  </button>
                  {manageableWorkspace && (
                    <button role="menuitem" type="button" onMouseEnter={closeSpacePopoverNow} onClick={openSpaceSettings}>
                      <Settings className="rc-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" /> 设置空间
                    </button>
                  )}
                </div>
                <div className="rc-menu-group" role="group" aria-label="偏好">
                  <button
                    id="themeSwitch"
                    className="rc-theme-switch"
                    role="switch"
                    type="button"
                    aria-checked={theme === "light"}
                    aria-label="切换明暗主题"
                    onMouseEnter={closeSpacePopoverNow}
                    onClick={() => {
                      const nextTheme = theme === "dark" ? "light" : "dark";
                      setTheme(nextTheme);
                      saveUiTheme(nextTheme);
                      setToast(nextTheme === "light" ? "已切换为浅色主题" : "已切换为深色主题");
                    }}
                  >
                    <SunMoon className="rc-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" />
                    <span>界面主题</span>
                    <i className={`rc-theme-toggle ${theme === "light" ? "on" : ""}`} aria-hidden="true" />
                  </button>
                </div>
                <div className="rc-menu-group rc-menu-session" role="group" aria-label="会话">
                  <button className="logout" role="menuitem" type="button" onMouseEnter={closeSpacePopoverNow} onClick={() => void logoutFrontend()}>
                    <LogOut className="rc-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" /> 退出登录
                  </button>
                </div>
              </div>
            )}
            {isSpacePopoverOpen && !isSidebarCollapsed && (
              <section
                className="rc-space-popover"
                data-testid="space-switcher-popover"
                ref={spacePopoverRef}
                role="dialog"
                aria-label="切换空间"
                onMouseEnter={cancelSpacePopoverClose}
                onMouseLeave={scheduleSpacePopoverClose}
              >
                <div className="rc-space-list" data-state={isLoadingContext ? "loading" : contextError ? "error" : availableWorkspaces.length ? "ready" : "empty"}>
                  {isLoadingContext && (
                    <div className="rc-space-state" data-testid="space-loading-state" role="status">空间加载中</div>
                  )}
                  {!isLoadingContext && contextError && (
                    <div className="rc-space-state error" data-testid="space-error-state" role="alert">空间暂不可用，请稍后重试</div>
                  )}
                  {!isLoadingContext && !contextError && availableWorkspaces.length === 0 && (
                    <div className="rc-space-state" data-testid="space-empty-state">暂无空间</div>
                  )}
                  {!isLoadingContext && !contextError && availableWorkspaces.map((item) => (
                    <button
                      className={`${item.workspaceId === workspace.workspaceId ? "selected" : ""} ${isReadonlyWorkspace(item) ? "readonly" : ""}`.trim()}
                      type="button"
                      key={item.workspaceId}
                      data-testid={`space-option-${item.workspaceId}`}
                      data-current={item.workspaceId === workspace.workspaceId ? "true" : "false"}
                      data-readonly={isReadonlyWorkspace(item) ? "true" : "false"}
                      onClick={() => selectWorkspace(item)}
                    >
                      <span>
                        <strong>{item.name}</strong>
                        <em>{item.role} · {item.memberCount} 人</em>
                      </span>
                      {isReadonlyWorkspace(item) && <i className="rc-space-status" data-testid="space-frozen-badge">只读</i>}
                      {item.workspaceId === workspace.workspaceId && <Check size={15} aria-label="当前空间" />}
                    </button>
                  ))}
                </div>
                <div className="rc-space-actions">
                  <button type="button" data-testid="space-create-or-join-entry" onClick={openApplicationCenter}><Plus size={14} /> 创建空间</button>
                </div>
              </section>
            )}
          </div>
        </div>
      </aside>

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

        <section className="rc-stats" aria-label="需求中心统计" data-state={isLoadingContext ? "loading" : contextError ? "error" : "ready"}>
          {stats.map((item, index) => (
            <article className="rc-stat" key={item.label}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </article>
          ))}
        </section>

        <section className="rc-toolbar" aria-label="需求中心筛选">
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
            ].map(([value, label]) => (
              <button
                className={typeFilter === value ? "selected" : ""}
                type="button"
                key={value}
                onClick={() => setTypeFilter(value as "all" | IssueType)}
                disabled={isLoadingContext || Boolean(contextError)}
              >
                {label}
              </button>
            ))}
          </div>
          <details className="rc-filter-popover">
            <summary aria-label="打开筛选条件">
              筛选
              <span className="rc-filter-badge" aria-label={`已启用 ${activeFilterCount} 个筛选`}>{activeFilterCount}</span>
            </summary>
            <div className="rc-filter-menu" role="group" aria-label="筛选条件">
              <label className="rc-filter-field">
                <span>负责人</span>
                <select aria-label="负责人筛选" value={ownerFilter} onChange={(event) => setOwnerFilter(event.target.value)} disabled={isLoadingContext || Boolean(contextError)}>
                  {owners.map((owner) => <option key={owner}>{owner}</option>)}
                </select>
              </label>
              <label className="rc-filter-field">
                <span>优先级</span>
                <select aria-label="优先级筛选" value={priorityFilter} onChange={(event) => setPriorityFilter(event.target.value)} disabled={isLoadingContext || Boolean(contextError)}>
                  {priorities.map((priority) => <option key={priority}>{priority}</option>)}
                </select>
              </label>
              <label className="rc-filter-field">
                <span>Sprint</span>
                <select aria-label="Sprint 筛选" value={sprintFilter} onChange={(event) => setSprintFilter(event.target.value)} disabled={isLoadingContext || Boolean(contextError)}>
                  {sprints.map((sprint) => <option key={sprint}>{sprint}</option>)}
                </select>
              </label>
            </div>
          </details>
          <button
            className={`rc-refresh-button ${isRefreshingContext ? "refreshing" : ""}`}
            type="button"
            aria-label="刷新需求中心"
            aria-busy={isRefreshingContext}
            title="刷新"
            disabled={isLoadingContext || isRefreshingContext}
            onClick={() => void loadContext("refresh")}
          >
            <RefreshCw size={15} aria-hidden="true" />
          </button>
        </section>

        <section className="rc-board-wrap" aria-label="9 阶段需求研发流转看板" data-state={isLoadingContext ? "loading" : contextError ? "error" : filteredIssues.length ? "ready" : "empty"}>
          {isLoadingContext && (
            <div className="rc-state-panel" role="status">
              <span className="rc-skeleton" />
              <strong>正在聚合需求中心数据</strong>
              <p>读取 REQ、BUG、Sprint 和 OpenSpec Change 状态。</p>
            </div>
          )}
          {!isLoadingContext && contextError && (
            <div className="rc-state-panel error" role="alert">
              <strong>{contextError}</strong>
              <p>筛选与看板已暂停，避免展示过期治理信息。</p>
              <button type="button" onClick={() => void loadContext()}>重试</button>
            </div>
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
                <span aria-label={`${stage.title} ${items.length} 个对象`}>{String(items.length).padStart(2, "0")}</span>
              </header>
            ))}
            {stageColumns.map(({ stage, items }) => (
              <section className="rc-column" data-stage={stage.id} aria-labelledby={`stage-${stage.id}`} key={stage.id}>
                <div className={`rc-column-body ${items.length === 0 ? "empty" : ""}`}>
                  {items.length === 0 && (
                    <div className="rc-empty-stage" aria-label={`${stage.title}暂无对象`}>
                      <span className="rc-empty-stage-icon" aria-hidden="true">◌</span>
                      <strong>{stage.emptyTitle}</strong>
                      <p>{stage.emptyHint}<br />{stage.emptyDetail}</p>
                    </div>
                  )}
                  {items.map((issue) => renderIssueCard(stage, issue))}
                </div>
              </section>
            ))}
          </div>
        </section>
      </section>

      {isPasswordModalOpen && (
        <ChangePasswordModal
          onClose={() => setIsPasswordModalOpen(false)}
          onChanged={completePasswordChange}
        />
      )}

      {isProfileModalOpen && (
        <FrontendProfileModal
          user={activeUser}
          onClose={() => setIsProfileModalOpen(false)}
          onSaved={completeProfileSave}
        />
      )}

      {captureOpen && (
        <div className="rc-settings-mask rc-capture-mask" role="presentation" onMouseDown={() => setCaptureOpen(false)}>
          <form className="rc-flow-dialog rc-capture-dialog" role="dialog" aria-modal="true" aria-label="新建 Capture" onSubmit={submitCapture} onKeyDown={handleCaptureKeyDown} onMouseDown={(event) => event.stopPropagation()}>
            <header className="rc-dialog-head">
              <div>
                <h2>新建 Capture</h2>
                <span>快速记录一条需求或缺陷，稍后可在采集池中生成正式需求</span>
              </div>
              <button aria-label="关闭 Capture 表单" type="button" onClick={() => setCaptureOpen(false)}><X size={17} /></button>
            </header>
            <section className="rc-capture-body">
              <fieldset className="rc-capture-fieldset">
                <legend>类型 <b aria-hidden="true">*</b></legend>
                <div className="rc-capture-segmented" role="group" aria-label="Capture 类型" aria-required="true">
                  {[
                    ["requirement", "◆ 需求"],
                    ["bug", "◈ Bug"],
                  ].map(([value, label]) => (
                    <button
                      className={captureForm.type === value ? "selected" : ""}
                      data-type={value}
                      key={value}
                      type="button"
                      onClick={() => setCaptureForm({ ...captureForm, type: value as IssueType })}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </fieldset>
              <label className="rc-form-row">
                <span className="rc-field-label">标题 <b aria-hidden="true">*</b></span>
              <input
                ref={captureTitleRef}
                aria-label="Capture 标题"
                aria-invalid={captureError ? "true" : undefined}
                className={captureError ? "invalid" : ""}
                maxLength={60}
                placeholder="例如：本地存量项目导入 MoonBox 并支持产品内迭代闭环"
                required
                value={captureForm.title}
                onChange={(event) => {
                  setCaptureForm({ ...captureForm, title: event.target.value });
                  if (captureError) setCaptureError("");
                }}
              />
              </label>
              <label className="rc-form-row">
                <span className="rc-field-label">一句话描述</span>
                <textarea aria-label="一句话描述" maxLength={200} placeholder="用一两句话说清楚背景和诉求，方便后续生成需求时理解上下文..." value={captureForm.description} onChange={(event) => setCaptureForm({ ...captureForm, description: event.target.value })} />
                <small className="rc-capture-count">{captureForm.description.length}/200</small>
              </label>
              <div className="rc-capture-grid">
                <label className="rc-form-row">
                  <span className="rc-field-label">负责人</span>
                  <select aria-label="负责人" value={captureForm.owner} onChange={(event) => setCaptureForm({ ...captureForm, owner: event.target.value })}>
                    {captureOwners.map((owner) => <option key={owner}>{owner}</option>)}
                  </select>
                </label>
                <label className="rc-form-row">
                  <span className="rc-field-label">来源 <b aria-hidden="true">*</b></span>
                  <select aria-label="来源" required value={captureForm.source} onChange={(event) => setCaptureForm({ ...captureForm, source: event.target.value })}>
                    {captureSources.map((source) => <option key={source.value} value={source.value}>{source.label}</option>)}
                  </select>
                </label>
              </div>
              <fieldset className="rc-capture-fieldset">
                <legend>优先级 <b aria-hidden="true">*</b></legend>
                <div className="rc-capture-segmented priority" role="group" aria-label="Capture 优先级" aria-required="true">
                  {(["P0", "P1", "P2", "P3"] as const).map((priority) => (
                    <button
                      className={captureForm.priority === priority ? "selected" : ""}
                      data-priority={priority}
                      key={priority}
                      type="button"
                      onClick={() => setCaptureForm({ ...captureForm, priority })}
                    >
                      {priority}
                    </button>
                  ))}
                </div>
              </fieldset>
            </section>
            {captureError && <p className="rc-application-alert" role="alert">{captureError}</p>}
            <footer className="rc-dialog-actions rc-capture-actions-only">
              <div>
                <button className="rc-secondary-action" type="button" onClick={() => setCaptureOpen(false)}>取消</button>
                <button className="rc-primary-action" type="submit" disabled={!captureForm.title.trim()}>＋ 创建 Capture</button>
              </div>
            </footer>
          </form>
        </div>
      )}

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
                  ? (isDone ? "查看归档" : (action?.label || stageActionLabel[stage.id][selectedIssue.type]).replace(" →", ""))
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

      {drawer.type !== "none" && (
        <div className="rc-drawer-layer" role="presentation">
          <button className="rc-drawer-backdrop" type="button" aria-label="关闭右侧抽屉蒙层" onClick={closeDrawer} />
          <aside className={`rc-drawer${isDrawerFullscreen ? " fullscreen" : ""}`} style={isDrawerFullscreen ? undefined : { width: drawerWidth }} role="dialog" aria-modal="true" aria-label={drawerTitle(drawer)} onMouseDown={(event) => event.stopPropagation()}>
            {!isDrawerFullscreen && <button className="rc-drawer-resizer" type="button" aria-label="调整右侧抽屉宽度" onMouseDown={beginDrawerResize} />}
            <header className="rc-drawer-head">
              {drawer.type === "markdown" ? (
                <div className="rc-drawer-title-block">
                  <div className="rc-drawer-crumb">{drawer.issue.id}<span>·</span>{drawer.document.name}</div>
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
                  {drawer.error && <p role="alert">{drawer.error}</p>}
                  {!drawer.loading && (
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
                        content={composeMarkdownContent(drawer.content, drawer.draft)}
                        metadataOpen={markdownMetadataOpen}
                        onToggleMetadata={() => setMarkdownMetadataOpen((open) => !open)}
                        onTaskToggle={isMutableMarkdownDrawer(drawer) ? toggleMarkdownTask : undefined}
                      />
                    )
                  )}
                </section>
                {!drawer.loading && (
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
                        <button type="button" className="primary" disabled={drawer.saving || !isCurrentMarkdownDirty} onClick={() => void saveMarkdownDocument()}>
                          {drawer.saving && <Loader2 size={13} aria-hidden="true" />} 保存
                        </button>
                      </div>
                    )}
                  </footer>
                )}
              </>
            )}
            {drawer.type === "tasks" && (
              <section className="rc-tasks-view" data-testid="tasks-drawer">
                {(() => {
                  const taskDone = drawer.issue.tasks?.done ?? drawer.issue.taskProgress?.[0] ?? 0;
                  const taskTotal = drawer.issue.tasks?.total ?? drawer.issue.taskProgress?.[1] ?? 0;
                  const testDone = drawer.issue.testProgress?.[0] ?? 0;
                  const testTotal = drawer.issue.testProgress?.[1] ?? 0;
                  const manualProgress = visibleManualAcceptanceProgress(drawer.issue) || [0, 0];
                  const manualCount = drawer.issue.manualAcceptanceCount ?? 0;
                  return (
                    <>
                <div className="rc-progress-drawer-summary">
                  <strong>{progressFocusLabel[drawer.focus]}</strong>
                  <p>{drawer.issue.id} · {drawer.issue.tasks?.source || "tasks.md"} · 只读进度</p>
                </div>
                <div className="rc-progress-drawer-grid">
                  <section className={`rc-progress-drawer-section ${drawer.focus === "development" ? "active" : ""}`} aria-label="研发任务进度">
                    <div className="rc-progress-drawer-section-head">
                      <span>研发任务</span>
                      <b>{taskDone}/{taskTotal}</b>
                    </div>
                    <div className="rc-mini-bar"><span style={{ width: `${progressPercent(taskDone, taskTotal)}%` }} /></div>
                  </section>
                  <section className={`rc-progress-drawer-section ${drawer.focus === "test" ? "active" : ""}`} aria-label="自动化测试进度">
                    <div className="rc-progress-drawer-section-head">
                      <span>自动化测试</span>
                      <b>{testDone}/{testTotal}</b>
                    </div>
                    <div className="rc-mini-bar"><span style={{ width: `${progressPercent(testDone, testTotal)}%` }} /></div>
                  </section>
                  <section className={`rc-progress-drawer-section ${drawer.focus === "manual" ? "active" : ""}`} aria-label="人工验收进度">
                    <div className="rc-progress-drawer-section-head">
                      <span>人工验收</span>
                      <b>{manualProgress[0]}/{manualProgress[1]}</b>
                    </div>
                    <div className="rc-mini-bar"><span style={{ width: `${progressPercent(manualProgress[0], manualProgress[1])}%` }} /></div>
                    <p>{manualCount > 0 ? `仍有 ${manualCount} 项需要人工处理` : "暂无待处理人工验收项"}</p>
                  </section>
                </div>
                {(drawer.issue.tasks?.blocked || []).length ? drawer.issue.tasks?.blocked?.map((item) => <span key={item}>{item}</span>) : <span>暂无阻塞</span>}
                    </>
                  );
                })()}
              </section>
            )}
            {drawer.type === "ai" && (
              <section className="rc-ai-chat" data-testid="ai-chat-drawer">
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

      {isApplicationOpen && (
        <div className="rc-settings-mask" role="presentation" onMouseDown={() => setIsApplicationOpen(false)}>
          <section className="rc-space-application" role="dialog" aria-modal="true" aria-labelledby="space-application-title" onMouseDown={(event) => event.stopPropagation()}>
            <header className="rc-settings-head">
              <div>
                <h2 id="space-application-title">创建空间</h2>
                <p>每个空间对应一个产品，成员与数据相互隔离；提交后进入平台管理员审批，通过后系统会创建空间并分配你为负责人。</p>
              </div>
              <button aria-label="关闭空间申请" type="button" onClick={() => setIsApplicationOpen(false)}><X size={17} /></button>
            </header>
            {applicationError && <p className="rc-application-alert" role="alert">{applicationError}</p>}
            {createdSpaceResult ? (
              <section className="rc-application-result" role="status">
                <strong>{createdSpaceResult.application.name} 申请已提交</strong>
                <p>{createdSpaceResult.application.code} · 当前状态：{createdSpaceResult.application.status}，待平台管理员审批后才可使用。</p>
                <button className="rc-primary-action" type="button" onClick={() => setIsApplicationOpen(false)}>知道了</button>
              </section>
            ) : (
              <form className="rc-application-panel" aria-label="创建空间" onSubmit={submitCreateApplication}>
                <div className="rc-application-grid">
                  <div className="rc-form-row"><label htmlFor="create-space-name">空间名称 <b aria-hidden="true">*</b></label><input id="create-space-name" aria-label="空间名称" required value={createApplicationForm.name} onChange={(event) => updateCreateName(event.target.value)} placeholder="例如：MoonBox 产品研发" /></div>
                  <div className="rc-form-row"><label htmlFor="create-space-code">空间标识 <b aria-hidden="true">*</b></label><input id="create-space-code" aria-label="空间标识" required value={createApplicationForm.code} onChange={(event) => { setIsCodeManuallyEdited(true); setCreateApplicationForm({ ...createApplicationForm, code: event.target.value }); }} placeholder="moonbox-product" /></div>
                </div>
                <div className="rc-form-row"><label htmlFor="create-space-description">空间说明</label><textarea id="create-space-description" value={createApplicationForm.description} onChange={(event) => setCreateApplicationForm({ ...createApplicationForm, description: event.target.value })} placeholder="简要说明这个空间对应的产品与协作目标" /></div>
                <strong className="rc-application-section">空间配额</strong>
                <div className="rc-application-grid">
                  <div className="rc-form-row">
                    <label htmlFor="create-space-members">成员上限 <b aria-hidden="true">*</b></label>
                    <div className="rc-unit-field">
                      <input id="create-space-members" aria-label="成员上限" required type="number" min="1" max="100000" step="1" value={createApplicationForm.member_quota} onChange={(event) => setCreateApplicationForm({ ...createApplicationForm, member_quota: event.target.value })} />
                      <span>人</span>
                    </div>
                  </div>
                  <div className="rc-form-row">
                    <label htmlFor="create-space-storage">存储空间 <b aria-hidden="true">*</b></label>
                    <div className="rc-unit-field">
                      <input id="create-space-storage" aria-label="存储空间" required type="number" min="0.01" step="0.01" value={createApplicationForm.storage_quota_gb} onChange={(event) => setCreateApplicationForm({ ...createApplicationForm, storage_quota_gb: event.target.value })} />
                      <span>GB</span>
                    </div>
                  </div>
                  <div className="rc-form-row">
                    <label htmlFor="create-space-ai">AI Tokens <b aria-hidden="true">*</b></label>
                    <input id="create-space-ai" aria-label="AI Tokens" required type="number" min="0" step="1" value={createApplicationForm.ai_quota_tokens} onChange={(event) => setCreateApplicationForm({ ...createApplicationForm, ai_quota_tokens: event.target.value })} />
                  </div>
                  <div className="rc-form-row">
                    <label>有效期 <b aria-hidden="true">*</b></label>
                    <div className="rc-period-options">
                      <label><input type="radio" checked={createApplicationForm.expiry_type === "long_term"} onChange={() => setCreateApplicationForm({ ...createApplicationForm, expiry_type: "long_term", expires_at: "" })} /> 长期有效</label>
                      <label><input type="radio" checked={createApplicationForm.expiry_type === "fixed_date"} onChange={() => setCreateApplicationForm({ ...createApplicationForm, expiry_type: "fixed_date", expires_at: nextFixedExpiryValue(createApplicationForm.expires_at) })} /> 固定日期</label>
                    </div>
                  </div>
                </div>
                {createApplicationForm.expiry_type === "fixed_date" && (
                  <div className="rc-form-row rc-application-date-row">
                    <label htmlFor="create-space-expires">到期时间 <b aria-hidden="true">*</b></label>
                    <RequirementDateTimePicker ariaLabel="到期时间" value={createApplicationForm.expires_at} onChange={(value) => setCreateApplicationForm({ ...createApplicationForm, expires_at: value })} />
                  </div>
                )}
                <div className="rc-application-actions">
                  <button type="button" onClick={() => setIsApplicationOpen(false)}>取消</button>
                  <button className="rc-primary-action" type="submit" disabled={isSubmittingApplication}>{isSubmittingApplication ? "正在创建..." : "创建空间"}</button>
                </div>
              </form>
            )}
          </section>
        </div>
      )}

      {isSettingsOpen && (
        <div className="rc-settings-mask" role="presentation" onMouseDown={() => setIsSettingsOpen(false)}>
          <section
            className="rc-space-settings"
            role="dialog"
            aria-modal="true"
            aria-labelledby="space-settings-title"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <aside className="rc-settings-nav">
              <div className="rc-settings-head">
                <h2 id="space-settings-title">空间设置</h2>
                <button aria-label="关闭空间设置" type="button" onClick={() => setIsSettingsOpen(false)}>
                  <X size={17} />
                </button>
              </div>
              <p>{workspace.organizationName}</p>
              {settingsTabs.map((tab) => (
                <button
                  className={settingsTab === tab.id ? "selected" : ""}
                  key={tab.id}
                  type="button"
                  onClick={() => setSettingsTab(tab.id)}
                >
                  {tab.label}
                </button>
              ))}
            </aside>
            <div className="rc-settings-body">
              <form className="rc-settings-panel" aria-label="空间常规设置" onSubmit={(event) => event.preventDefault()}>
                {settingsTab === "general" ? (
                  <>
                    <div className="rc-panel-intro">
                      <h3>常规</h3>
                      <p>配置当前空间“{workspace.name}”的基本信息。</p>
                    </div>
                    <div className="rc-form-row">
                      <label htmlFor="workspace-name">空间名称</label>
                      <input id="workspace-name" value={draftWorkspace.name} onChange={updateDraft("name")} />
                      <span>用于侧边栏、通知和空间切换列表。</span>
                    </div>
                    <div className="rc-form-row">
                      <label htmlFor="workspace-slug">空间标识</label>
                      <input id="workspace-slug" value={draftWorkspace.slug} onChange={updateDraft("slug")} />
                      <span>创建后可修改，修改可能影响外部集成。</span>
                    </div>
                    <div className="rc-form-row">
                      <label htmlFor="workspace-description">空间描述</label>
                      <textarea id="workspace-description" value={draftWorkspace.description} onChange={updateDraft("description")} />
                    </div>
                    <div className="rc-form-row">
                      <label htmlFor="workspace-timezone">默认时区</label>
                      <select id="workspace-timezone" value={draftWorkspace.timezone} onChange={updateDraft("timezone")}>
                        <option value="Asia/Shanghai">Asia/Shanghai (UTC+08:00)</option>
                        <option value="Asia/Tokyo">Asia/Tokyo</option>
                        <option value="UTC">UTC</option>
                      </select>
                    </div>
                  </>
                ) : (
                  <div className="rc-settings-placeholder">
                    <FileCheck size={20} aria-hidden="true" />
                    <strong>{settingsTabs.find((tab) => tab.id === settingsTab)?.label}</strong>
                    <span>当前分组配置项已预留，后续按权限与集成契约接入。</span>
                  </div>
                )}
              </form>
            </div>
            <footer>
              <button type="button" onClick={() => setIsSettingsOpen(false)}>取消</button>
              <button className="primary" type="button" onClick={saveSpaceSettings}>保存更改</button>
            </footer>
          </section>
        </div>
      )}

      {toast && (
        <div className="rc-toast" role="status">
          <Check size={15} aria-hidden="true" /> {toast}
        </div>
      )}
    </main>
  );
}

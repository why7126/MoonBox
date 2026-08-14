import {
  Archive,
  Calendar,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Database,
  Network,
  Plus,
  ShieldAlert,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { AdminCrudListTemplate, AdminModalBackdrop } from "./AdminCrudListTemplate";
import { AdminSelect } from "./AdminSelect";
import { AdminSidebar, AuthenticatedAvatar } from "./AdminSidebar";
import { AdminSession, logoutAdmin, readAdminSession } from "./adminAuth";
import { ChangePasswordModal, ProfileModal } from "./AdminUserManagementPage";
import { readUiPreferences, UI_PREFERENCES_EVENT } from "../home/uiPreferences";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";
type SpaceStatus = "ACTIVE" | "FROZEN" | "RECYCLE";
type SpaceSource = "后台创建" | "申请审批";
type ExpiryType = "fixed_date" | "long_term";

type AdminSpace = {
  id: string;
  name: string;
  code: string;
  description: string | null;
  owner_id: string;
  owner_name: string | null;
  owner_role: string | null;
  owner_avatar_url: string | null;
  status: SpaceStatus;
  source: SpaceSource;
  member_count: number;
  member_quota: number;
  storage_used_gb: number;
  storage_quota_gb: number;
  ai_used_tokens: number;
  ai_quota_tokens: number;
  product_id: string;
  product_name: string;
  expiry_type: ExpiryType;
  expires_at: string | null;
  protected: boolean;
  deleted_at: string | null;
  deleted_by: string | null;
  deleted_by_name: string | null;
  delete_reason: string | null;
  purge_at: string | null;
  allowed_actions: string[];
  created_at: string;
  updated_at: string;
};

const moreActionCodes = ["QUOTA", "RENEW", "TRANSFER_OWNER", "DELETE", "PURGE"] as const;

function hasMoreActions(space: AdminSpace) {
  return moreActionCodes.some((action) => space.allowed_actions.includes(action));
}

type SpaceApplication = {
  id: string;
  name: string;
  code: string;
  applicant_name: string | null;
  proposed_owner_name: string | null;
  product_name: string;
  purpose: string;
  expected_members: number;
  requested_storage_gb: number;
  requested_ai_tokens: number;
  expires_at: string | null;
  status: "待审批" | "已通过" | "已拒绝";
  created_at: string;
};

type AdminUserOption = {
  id: string;
  username: string;
  nickname: string | null;
  avatar_url?: string | null;
  role: string;
  status: string;
};

type SpaceMemberRole = "管理员" | "编辑者" | "查看者";

type SpaceMember = {
  id: string;
  space_id: string;
  user_id: string;
  user_name: string | null;
  username: string;
  avatar_url: string | null;
  role: SpaceMemberRole;
  user_status: string;
  joined_at: string;
  updated_at: string;
};

type SpaceAuditEvent = {
  id: string;
  space_id: string;
  actor: string;
  actor_display_name: string | null;
  action: string;
  before_value: string | null;
  after_value: string | null;
  reason: string;
  result: string;
  request_id: string;
  created_at: string;
};

type PageResponse<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
};

type ActionMode = "create" | "edit" | "freeze" | "restore" | "delete" | "purge" | "quota" | "renew" | "transfer" | "approve" | "reject" | "member-add" | "member-edit" | "member-remove";
type DetailTab = "overview" | "members" | "product" | "quota" | "logs";

type PendingAction = {
  mode: ActionMode;
  space?: AdminSpace;
  application?: SpaceApplication;
  member?: SpaceMember;
};

type FormState = {
  name: string;
  code: string;
  description: string;
  owner_id: string;
  product_id: string;
  product_name: string;
  member_quota: string;
  storage_quota_gb: string;
  ai_quota_tokens: string;
  expiry_type: ExpiryType;
  expires_at: string;
  reason: string;
  member_user_id: string;
  member_role: SpaceMemberRole;
};

const emptyForm: FormState = {
  name: "",
  code: "",
  description: "",
  owner_id: "",
  product_id: "",
  product_name: "",
  member_quota: "20",
  storage_quota_gb: "100",
  ai_quota_tokens: "1000000",
  expiry_type: "fixed_date",
  expires_at: defaultExpiryAt(),
  reason: "",
  member_user_id: "",
  member_role: "查看者",
};

function defaultExpiryAt() {
  const now = new Date();
  const quarterEndMonth = Math.floor(now.getMonth() / 3) * 3 + 2;
  const quarterEnd = new Date(now.getFullYear(), quarterEndMonth + 1, 0, 23, 59, 59);
  if (quarterEnd <= now) {
    quarterEnd.setMonth(quarterEnd.getMonth() + 3);
  }
  return `${toLocalDateTimeInputValue(quarterEnd)}Z`;
}

function toLocalDateTimeInputValue(date: Date) {
  const pad = (value: number) => String(value).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function currentDateTimeInputValue() {
  return toLocalDateTimeInputValue(new Date());
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
  if (!value) return false;
  const parsed = new Date(value.replace("Z", "+00:00"));
  return Number.isFinite(parsed.getTime()) && parsed > new Date();
}

function nextFixedExpiryValue(currentValue: string) {
  return isFutureExpiry(currentValue) ? currentValue : defaultExpiryAt();
}

function apiUrl(path: string) {
  return `${API_BASE_URL}${path}`;
}

function authHeaders(session: AdminSession) {
  return {
    authorization: `Bearer ${session.access_token}`,
    "content-type": "application/json",
  };
}

async function requestAdminApi<T>(path: string, session: AdminSession, options: RequestInit = {}): Promise<T> {
  const response = await fetch(apiUrl(path), {
    ...options,
    headers: {
      ...authHeaders(session),
      ...(options.headers || {}),
    },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload?.detail || payload?.message || "请求失败");
  }
  return payload.data as T;
}

function navigateTo(path: string) {
  window.history.pushState(null, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

function statusText(status: SpaceStatus) {
  return status === "ACTIVE" ? "正常" : status === "FROZEN" ? "已冻结" : "回收站";
}

function formatDate(value?: string | null) {
  if (!value) return "长期";
  return value.replace("T", " ").replace("Z", "");
}

function remainingDays(value?: string | null) {
  if (!value) return "-";
  const diff = new Date(value).getTime() - Date.now();
  return `${Math.max(0, Math.ceil(diff / 86400000))} 天`;
}

function formatExpiry(space: AdminSpace) {
  return space.expiry_type === "long_term" ? "长期有效" : formatDate(space.expires_at);
}

function formatApplicationExpiry(application: SpaceApplication) {
  return application.expires_at ? formatDate(application.expires_at) : "长期有效";
}

function formatTokenAmount(value: number) {
  if (value >= 10000 && value % 10000 === 0) {
    return `${value / 10000}万`;
  }
  return new Intl.NumberFormat("zh-CN").format(value);
}

function formatStorageAmount(value: number) {
  return Number.isInteger(value) ? `${value} GB` : `${value.toFixed(1)} GB`;
}

function datetimeLocalValue(value: string) {
  return value.replace("Z", "").slice(0, 19);
}

function percent(used: number, quota: number) {
  if (!quota) return "0%";
  return `${Math.min(999, Math.round((used / quota) * 100))}%`;
}

function percentValue(used: number, quota: number) {
  if (!quota) return 0;
  return Math.min(100, Math.round((used / quota) * 100));
}

function usageLevel(used: number, quota: number) {
  const value = percentValue(used, quota);
  if (value >= 100) return "bad";
  if (value >= 80) return "warn";
  return "normal";
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("en-US").format(value);
}

function usageQuotaText(used: number, quota: number) {
  return `${formatNumber(used)} / ${formatNumber(quota)}`;
}

function auditActionText(action: string) {
  const labels: Record<string, string> = {
    create_space: "创建空间",
    application_approved_create_space: "审批通过创建空间",
    update_space: "编辑空间",
    add_member: "添加成员",
    update_member_role: "编辑成员角色",
    remove_member: "移除成员",
    update_quota: "调整配额",
    renew_space: "续期空间",
    transfer_owner: "变更负责人",
    purge_space: "永久删除空间",
    "set_status:FROZEN": "冻结空间",
    "set_status:ACTIVE": "恢复空间",
    "set_status:RECYCLE": "删除空间",
    "application:已通过": "通过空间申请",
    "application:已拒绝": "拒绝空间申请",
  };
  return labels[action] || action;
}

function auditResultText(result: string) {
  return result === "success" ? "成功" : result || "-";
}

function auditStatusText(value: unknown) {
  if (value === "ACTIVE") return "正常";
  if (value === "FROZEN") return "已冻结";
  if (value === "RECYCLE") return "回收站";
  if (value === "fixed_date") return "固定日期";
  if (value === "long_term") return "长期";
  return String(value);
}

function auditSourceText(action: string) {
  return action.startsWith("application") ? "申请审批" : "后台管理";
}

function auditActionTone(action: string) {
  if (action.includes("member")) return "member";
  if (action.includes("quota")) return "quota";
  if (action.includes("renew")) return "renew";
  if (action.includes("FROZEN")) return "freeze";
  if (action.includes("RECYCLE") || action.includes("purge")) return "danger";
  if (action.includes("create") || action.includes("approved")) return "create";
  return "action";
}

function parseAuditValue(value: string | null) {
  if (!value) return null;
  try {
    return JSON.parse(value) as Record<string, unknown>;
  } catch {
    return null;
  }
}

function compactAuditValue(value: string | null) {
  if (!value) return "无";
  try {
    const parsed = JSON.parse(value) as Record<string, unknown>;
    const labels: Record<string, string> = {
      name: "名称",
      code: "编码",
      status: "状态",
      owner_id: "负责人",
      source: "来源",
      role: "角色",
      user_id: "用户",
      member_quota: "成员",
      storage_quota_gb: "存储",
      ai_quota_tokens: "AI",
      expiry_type: "有效期类型",
      expires_at: "到期时间",
      product_name: "产品",
      product_id: "产品 ID",
    };
    const pairs = Object.keys(labels)
      .filter((key) => parsed[key] !== undefined && parsed[key] !== null)
      .slice(0, 4)
      .map((key) => `${labels[key]}：${auditStatusText(parsed[key])}`);
    return pairs.length > 0 ? pairs.join("，") : "已记录";
  } catch {
    return value.length > 96 ? `${value.slice(0, 96)}...` : value;
  }
}

function auditChangeSummary(event: SpaceAuditEvent) {
  const before = parseAuditValue(event.before_value);
  const after = parseAuditValue(event.after_value);
  const labels: Record<string, string> = {
    name: "名称",
    status: "状态",
    owner_id: "负责人",
    role: "角色",
    user_id: "用户",
    member_quota: "成员",
    storage_quota_gb: "存储",
    ai_quota_tokens: "AI",
    expiry_type: "有效期类型",
    expires_at: "到期时间",
  };
  if (!before && !after) return ["已记录"];
  const keys = Object.keys(labels).filter((key) => before?.[key] !== after?.[key] && (before?.[key] !== undefined || after?.[key] !== undefined));
  if (keys.length === 0) {
    return [`前：${compactAuditValue(event.before_value)}`, `后：${compactAuditValue(event.after_value)}`];
  }
  return keys.slice(0, 3).map((key) => `${labels[key]}：${before?.[key] === undefined ? "无" : auditStatusText(before[key])} → ${after?.[key] === undefined ? "无" : auditStatusText(after[key])}`);
}

function isEmptyAuditValue(value: string | null) {
  return !value || value.trim() === "" || value.trim() === "无" || value.trim().toLowerCase() === "null";
}

function formatAuditJson(value: string) {
  try {
    return JSON.stringify(JSON.parse(value), null, 2);
  } catch {
    return value;
  }
}

function AuditValueBlock({ value }: { value: string | null }) {
  if (isEmptyAuditValue(value)) {
    return <div className="admin-space-audit-empty">无</div>;
  }
  return <pre className="admin-space-audit-json">{formatAuditJson(value ?? "")}</pre>;
}

function productCountLabel(space: AdminSpace) {
  return space.product_name || space.product_id ? "1" : "0";
}

function ownerInitial(space: AdminSpace) {
  return (space.owner_name || space.owner_id || "负").slice(0, 1);
}

function SpaceStatusIcon({ status }: { status: SpaceStatus }) {
  if (status === "ACTIVE") return <CheckCircle2 size={14} strokeWidth={1.8} aria-hidden="true" />;
  if (status === "FROZEN") return <ShieldAlert size={14} strokeWidth={1.8} aria-hidden="true" />;
  return <Archive size={14} strokeWidth={1.8} aria-hidden="true" />;
}

function formFromSpace(space: AdminSpace): FormState {
  return {
    ...emptyForm,
    name: space.name,
    code: space.code,
    description: space.description || "",
    owner_id: space.owner_id,
    product_id: space.product_id,
    product_name: space.product_name,
    member_quota: String(space.member_quota),
    storage_quota_gb: String(space.storage_quota_gb),
    ai_quota_tokens: String(space.ai_quota_tokens),
    expiry_type: space.expiry_type,
    expires_at: space.expires_at || "",
    reason: "",
  };
}

function deriveProductId(code: string) {
  return code.trim();
}

function deriveProductName(name: string) {
  return name.trim();
}

function optionLabel(user: AdminUserOption) {
  return user.nickname || user.username;
}

function FieldLabel({ label, required = false }: { label: string; required?: boolean }) {
  return <span className="admin-space-field-label">{label}{required && <b aria-hidden="true">*</b>}</span>;
}

function AdminDateTimePicker({ ariaLabel, value, onChange }: { ariaLabel: string; value: string; onChange: (value: string) => void }) {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState(toDateTimeDisplayValue(value));
  const [panelRect, setPanelRect] = useState({ top: 0, left: 0, width: 0 });
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
      setPanelRect({ top: rect.bottom + 4, left, width });
    };
    const handlePointerDown = (event: MouseEvent) => {
      const target = event.target as Node;
      const panel = document.querySelector(".admin-datetime-panel");
      if (rootRef.current?.contains(target) || panel?.contains(target)) return;
      setOpen(false);
    };
    updatePanelRect();
    window.addEventListener("resize", updatePanelRect);
    window.addEventListener("scroll", updatePanelRect, true);
    document.addEventListener("mousedown", handlePointerDown);
    return () => {
      window.removeEventListener("resize", updatePanelRect);
      window.removeEventListener("scroll", updatePanelRect, true);
      document.removeEventListener("mousedown", handlePointerDown);
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
      return;
    }
    if (mode === "year") {
      commitLocalValue(`${now.getFullYear() + 1}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}T23:59:59`);
      return;
    }
    commitLocalValue(datetimeLocalValue(defaultExpiryAt()));
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

  const panelTheme = typeof document === "undefined" ? "dark" : document.querySelector(".admin-shell.light") ? "light" : "dark";
  const panel = open && createPortal(
    <div className={`admin-datetime-panel ${panelTheme}`} role="dialog" aria-label={`${ariaLabel}选择器`} style={{ top: panelRect.top, left: panelRect.left, width: panelRect.width }}>
      <div className="admin-datetime-calendar-head">
        <button type="button" aria-label="上个月" onClick={() => shiftMonth(-1)}><ChevronLeft size={16} /></button>
        <strong>{year}年{month + 1}月</strong>
        <button type="button" aria-label="下个月" onClick={() => shiftMonth(1)}><ChevronRight size={16} /></button>
      </div>
      <div className="admin-datetime-weekdays">{weekdays.map((day) => <span key={day}>{day}</span>)}</div>
      <div className="admin-datetime-days">
        {days.map((day, index) => day === 0 ? <span key={`blank-${index}`} /> : (
          <button
            key={day}
            type="button"
            className={day === calendarDate.getDate() ? "active" : ""}
            onClick={() => updateDatePart(new Date(year, month, day, calendarDate.getHours(), calendarDate.getMinutes(), calendarDate.getSeconds()))}
          >
            {day}
          </button>
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
    <div className="admin-datetime-picker" ref={rootRef} data-testid="admin-datetime-picker">
      <input
        ref={inputRef}
        aria-label={ariaLabel}
        type="text"
        required
        value={draft}
        onBlur={commitDraft}
        onChange={(event) => setDraft(event.target.value)}
        onFocus={() => setOpen(true)}
        placeholder="yyyy-mm-dd hh:mm:ss"
      />
      <button type="button" aria-label={`选择${ariaLabel}`} onClick={() => { setOpen((current) => !current); inputRef.current?.focus(); }}><Calendar size={16} /></button>
      {panel}
    </div>
  );
}

function actionTitle(mode: ActionMode) {
  const titles: Record<ActionMode, string> = {
    create: "新增空间",
    edit: "编辑空间",
    freeze: "冻结空间",
    restore: "恢复空间",
    delete: "删除空间",
    purge: "永久删除空间",
    quota: "调整配额",
    renew: "续期空间",
    transfer: "移交负责人",
    approve: "通过空间申请",
    reject: "拒绝空间申请",
    "member-add": "添加成员",
    "member-edit": "编辑成员角色",
    "member-remove": "移除成员",
  };
  return titles[mode];
}

function SpaceQuotaRows({ space }: { space: AdminSpace }) {
  const rows = [
    { label: "成员数", value: `${space.member_count} / ${space.member_quota}`, used: space.member_count, quota: space.member_quota },
    { label: "存储量", value: `${space.storage_used_gb} / ${space.storage_quota_gb} GB`, used: space.storage_used_gb, quota: space.storage_quota_gb },
    { label: "AI Token", value: usageQuotaText(space.ai_used_tokens, space.ai_quota_tokens), used: space.ai_used_tokens, quota: space.ai_quota_tokens, tone: usageLevel(space.ai_used_tokens, space.ai_quota_tokens) },
  ];
  return (
    <div className="admin-space-quota-list">
      {rows.map((row) => (
        <div className={`admin-space-quota-row ${row.tone || ""}`} key={row.label}>
          <div><span>{row.label}</span><b>{row.value}</b></div>
          <span className="admin-space-quota-bar"><i style={{ width: percent(row.used, row.quota) }} /></span>
        </div>
      ))}
    </div>
  );
}

export function AdminSpaceManagementPage({ session, onLogout }: { session: AdminSession; onLogout: () => void }) {
  const [activeTab, setActiveTab] = useState<"spaces" | "approvals" | "recycle" | "detail">("spaces");
  const [spaces, setSpaces] = useState<AdminSpace[]>([]);
  const [recycleSpaces, setRecycleSpaces] = useState<AdminSpace[]>([]);
  const [applications, setApplications] = useState<SpaceApplication[]>([]);
  const [ownerOptions, setOwnerOptions] = useState<AdminUserOption[]>([]);
  const [spaceMembers, setSpaceMembers] = useState<SpaceMember[]>([]);
  const [spaceAuditEvents, setSpaceAuditEvents] = useState<SpaceAuditEvent[]>([]);
  const [recentAuditEvents, setRecentAuditEvents] = useState<SpaceAuditEvent[]>([]);
  const [auditPage, setAuditPage] = useState(1);
  const [auditPageSize, setAuditPageSize] = useState(10);
  const [auditTotal, setAuditTotal] = useState(0);
  const [selectedAuditEvent, setSelectedAuditEvent] = useState<SpaceAuditEvent | null>(null);
  const [selectedSpace, setSelectedSpace] = useState<AdminSpace | null>(null);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("");
  const [source, setSource] = useState("");
  const [usageStatus, setUsageStatus] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);
  const [recyclePage, setRecyclePage] = useState(1);
  const [recyclePageSize, setRecyclePageSize] = useState(10);
  const [recycleTotal, setRecycleTotal] = useState(0);
  const [applicationPage, setApplicationPage] = useState(1);
  const [applicationPageSize, setApplicationPageSize] = useState(10);
  const [applicationTotal, setApplicationTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [toast, setToast] = useState("");
  const [pendingAction, setPendingAction] = useState<PendingAction | null>(null);
  const [moreMenu, setMoreMenu] = useState<{ space: AdminSpace; top: number; left: number; placement: "top" | "bottom" } | null>(null);
  const [detailTab, setDetailTab] = useState<DetailTab>("overview");
  const [form, setForm] = useState<FormState>(emptyForm);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isLightTheme, setIsLightTheme] = useState(() => readUiPreferences().theme === "light");
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [currentSessionUser, setCurrentSessionUser] = useState<AdminSession["user"] | null>(session.user ?? readAdminSession()?.user ?? null);
  const [hasTriedConfirm, setHasTriedConfirm] = useState(false);

  const showToast = useCallback((message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2400);
  }, []);

  const loadSpaces = useCallback(async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
      if (query) params.set("q", query);
      if (status) params.set("status", status);
      if (source) params.set("source", source);
      if (usageStatus) params.set("usage_status", usageStatus);
      const payload = await requestAdminApi<PageResponse<AdminSpace>>(`/api/v1/admin/spaces?${params}`, session);
      setSpaces(payload.items);
      setTotal(payload.total);
    } catch (error) {
      showToast(error instanceof Error ? error.message : "空间列表加载失败");
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, query, session, showToast, source, status, usageStatus]);

  const loadRecycleSpaces = useCallback(async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams({ page: String(recyclePage), page_size: String(recyclePageSize), status: "RECYCLE" });
      if (query) params.set("q", query);
      if (source) params.set("source", source);
      const payload = await requestAdminApi<PageResponse<AdminSpace>>(`/api/v1/admin/spaces?${params}`, session);
      setRecycleSpaces(payload.items);
      setRecycleTotal(payload.total);
    } catch (error) {
      showToast(error instanceof Error ? error.message : "回收站加载失败");
    } finally {
      setIsLoading(false);
    }
  }, [query, recyclePage, recyclePageSize, session, showToast, source]);

  const loadApplications = useCallback(async () => {
    try {
      const params = new URLSearchParams({ page: String(applicationPage), page_size: String(applicationPageSize) });
      const payload = await requestAdminApi<PageResponse<SpaceApplication>>(`/api/v1/admin/space-applications?${params}`, session);
      setApplications(payload.items);
      setApplicationTotal(payload.total);
    } catch (error) {
      showToast(error instanceof Error ? error.message : "申请列表加载失败");
    }
  }, [applicationPage, applicationPageSize, session, showToast]);

  const loadOwnerOptions = useCallback(async () => {
    try {
      const payload = await requestAdminApi<PageResponse<AdminUserOption>>("/api/v1/admin/users?status=正常&page=1&page_size=100", session);
      setOwnerOptions(payload.items);
    } catch (error) {
      showToast(error instanceof Error ? error.message : "负责人列表加载失败");
    }
  }, [session, showToast]);

  const loadSpaceMembers = useCallback(async (spaceId: string) => {
    try {
      const payload = await requestAdminApi<SpaceMember[]>(`/api/v1/admin/spaces/${spaceId}/members`, session);
      setSpaceMembers(payload);
    } catch (error) {
      showToast(error instanceof Error ? error.message : "成员列表加载失败");
    }
  }, [session, showToast]);

  const loadSpaceDetail = useCallback(async (spaceId: string) => {
    const payload = await requestAdminApi<AdminSpace>(`/api/v1/admin/spaces/${spaceId}`, session);
    setSelectedSpace(payload);
    return payload;
  }, [session]);

  const loadSpaceAuditEvents = useCallback(async (spaceId: string, nextPage = auditPage, nextPageSize = auditPageSize) => {
    try {
      const payload = await requestAdminApi<PageResponse<SpaceAuditEvent>>(`/api/v1/admin/spaces/${spaceId}/audit-events?page=${nextPage}&page_size=${nextPageSize}`, session);
      setSpaceAuditEvents(payload.items);
      setAuditTotal(payload.total);
      setAuditPage(payload.page);
      setAuditPageSize(payload.page_size);
    } catch (error) {
      showToast(error instanceof Error ? error.message : "操作记录加载失败");
    }
  }, [auditPage, auditPageSize, session, showToast]);

  const loadRecentAuditEvents = useCallback(async (spaceId: string) => {
    try {
      const payload = await requestAdminApi<PageResponse<SpaceAuditEvent>>(`/api/v1/admin/spaces/${spaceId}/audit-events?page=1&page_size=6`, session);
      setRecentAuditEvents(payload.items);
    } catch (error) {
      showToast(error instanceof Error ? error.message : "最近操作加载失败");
    }
  }, [session, showToast]);

  useEffect(() => {
    if (activeTab === "spaces") {
      void loadSpaces();
    }
  }, [activeTab, loadSpaces]);

  useEffect(() => {
    if (activeTab === "recycle") {
      void loadRecycleSpaces();
    }
  }, [activeTab, loadRecycleSpaces]);

  useEffect(() => {
    void loadApplications();
  }, [loadApplications]);

  useEffect(() => {
    void loadOwnerOptions();
  }, [loadOwnerOptions]);

  useEffect(() => {
    if (activeTab === "detail" && detailTab === "members" && selectedSpace) {
      void loadSpaceMembers(selectedSpace.id);
    }
  }, [activeTab, detailTab, loadSpaceMembers, selectedSpace]);

  useEffect(() => {
    if (activeTab === "detail" && selectedSpace) {
      void loadSpaceAuditEvents(selectedSpace.id);
      void loadRecentAuditEvents(selectedSpace.id);
    }
  }, [activeTab, loadRecentAuditEvents, loadSpaceAuditEvents, selectedSpace?.id]);

  useEffect(() => {
    const syncTheme = () => setIsLightTheme(readUiPreferences().theme === "light");
    window.addEventListener(UI_PREFERENCES_EVENT, syncTheme);
    window.addEventListener("storage", syncTheme);
    return () => {
      window.removeEventListener(UI_PREFERENCES_EVENT, syncTheme);
      window.removeEventListener("storage", syncTheme);
    };
  }, []);

  useEffect(() => {
    if (!moreMenu) return;
    const close = () => setMoreMenu(null);
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") close();
    };
    window.addEventListener("click", close);
    window.addEventListener("resize", close);
    window.addEventListener("scroll", close, true);
    window.addEventListener("keydown", closeOnEscape);
    return () => {
      window.removeEventListener("click", close);
      window.removeEventListener("resize", close);
      window.removeEventListener("scroll", close, true);
      window.removeEventListener("keydown", closeOnEscape);
    };
  }, [moreMenu]);

  const currentRows = activeTab === "recycle" ? recycleSpaces : spaces;
  const currentPage = activeTab === "recycle" ? recyclePage : page;
  const currentPageSize = activeTab === "recycle" ? recyclePageSize : pageSize;
  const currentTotal = activeTab === "recycle" ? recycleTotal : total;
  const spaceStats = useMemo(() => {
    const normal = spaces.filter((space) => space.status === "ACTIVE").length;
    const frozen = spaces.filter((space) => space.status === "FROZEN").length;
    const warning = spaces.filter((space) => usageLevel(space.ai_used_tokens, space.ai_quota_tokens) !== "normal").length;
    return [
      { label: "空间总数", value: total || spaces.length },
      { label: "正常运行", value: normal },
      { label: "已冻结", value: frozen },
      { label: "资源预警", value: warning, tone: "warning" },
    ];
  }, [spaces, total]);
  const pageCount = Math.max(1, Math.ceil(currentTotal / currentPageSize));
  const applicationPageCount = Math.max(1, Math.ceil(applicationTotal / applicationPageSize));
  const auditPageCount = Math.max(1, Math.ceil(auditTotal / auditPageSize));
  const memberRoleOptions = [
    { value: "管理员", label: "管理员" },
    { value: "编辑者", label: "编辑者" },
    { value: "查看者", label: "查看者" },
  ];
  const memberCandidateOptions = useMemo(() => ownerOptions.filter((user) => user.status === "正常" && user.id !== selectedSpace?.owner_id && !spaceMembers.some((member) => member.user_id === user.id)), [ownerOptions, selectedSpace?.owner_id, spaceMembers]);

  const openAction = (action: PendingAction) => {
    setMoreMenu(null);
    setPendingAction(action);
    setForm(action.space ? { ...formFromSpace(action.space), member_role: action.member?.role || "查看者", member_user_id: action.member?.user_id || "" } : { ...emptyForm, reason: "", member_role: action.member?.role || "查看者", member_user_id: action.member?.user_id || "" });
    setHasTriedConfirm(false);
  };

  const openDetail = (space: AdminSpace) => {
    setSelectedSpace(space);
    setSpaceMembers([]);
    setSpaceAuditEvents([]);
    setRecentAuditEvents([]);
    setAuditPage(1);
    setAuditTotal(0);
    setSelectedAuditEvent(null);
    setDetailTab("overview");
    setActiveTab("detail");
  };

  const toggleMoreMenu = (space: AdminSpace, trigger: HTMLButtonElement) => {
    if (!hasMoreActions(space)) {
      setMoreMenu(null);
      return;
    }
    const rect = trigger.getBoundingClientRect();
    const menuWidth = 108;
    const gap = 6;
    const bottomTop = rect.bottom + gap;
    const left = Math.min(Math.max(12, rect.left), window.innerWidth - menuWidth - 12);
    setMoreMenu((current) => current?.space.id === space.id ? null : {
      space,
      top: bottomTop,
      left,
      placement: "bottom",
    });
  };

  const submitAction = async () => {
    if (!pendingAction) return;
    const needsReason = !["create", "member-add", "member-edit"].includes(pendingAction.mode);
    if (needsReason && form.reason.trim().length < 4) {
      setHasTriedConfirm(true);
      return;
    }
    const needsExpiryValidation = ["create", "edit", "renew"].includes(pendingAction.mode);
    if (needsExpiryValidation && form.expiry_type === "fixed_date" && !isFutureExpiry(form.expires_at)) {
      showToast("到期时间必须晚于当前时间");
      return;
    }
    try {
      const productId = deriveProductId(form.code);
      const productName = deriveProductName(form.name);
      const body = JSON.stringify({
        reason: form.reason,
        name: form.name,
        code: form.code,
        description: form.description || null,
        owner_id: form.owner_id,
        product_id: pendingAction.mode === "create" ? productId : form.product_id,
        product_name: pendingAction.mode === "create" ? productName : form.product_name,
        member_quota: Number(form.member_quota),
        storage_quota_gb: Number(form.storage_quota_gb),
        ai_quota_tokens: Number(form.ai_quota_tokens),
        expiry_type: form.expiry_type,
        expires_at: form.expiry_type === "long_term" ? null : form.expires_at,
      });
      const space = pendingAction.space;
      let updatedSpace: AdminSpace | null = null;
      if (pendingAction.mode === "create") {
        updatedSpace = await requestAdminApi<AdminSpace>("/api/v1/admin/spaces", session, { method: "POST", body });
      } else if (pendingAction.mode === "edit" && space) {
        updatedSpace = await requestAdminApi<AdminSpace>(`/api/v1/admin/spaces/${space.id}`, session, { method: "PUT", body });
      } else if (pendingAction.mode === "quota" && space) {
        updatedSpace = await requestAdminApi<AdminSpace>(`/api/v1/admin/spaces/${space.id}/quota`, session, { method: "POST", body });
      } else if (pendingAction.mode === "renew" && space) {
        updatedSpace = await requestAdminApi<AdminSpace>(`/api/v1/admin/spaces/${space.id}/renew`, session, { method: "POST", body });
      } else if (pendingAction.mode === "transfer" && space) {
        updatedSpace = await requestAdminApi<AdminSpace>(`/api/v1/admin/spaces/${space.id}/transfer-owner`, session, { method: "POST", body });
      } else if (pendingAction.mode === "freeze" && space) {
        updatedSpace = await requestAdminApi<AdminSpace>(`/api/v1/admin/spaces/${space.id}/freeze`, session, { method: "POST", body: JSON.stringify({ reason: form.reason }) });
      } else if (pendingAction.mode === "restore" && space) {
        updatedSpace = await requestAdminApi<AdminSpace>(`/api/v1/admin/spaces/${space.id}/restore`, session, { method: "POST", body: JSON.stringify({ reason: form.reason }) });
      } else if (pendingAction.mode === "delete" && space) {
        updatedSpace = await requestAdminApi<AdminSpace>(`/api/v1/admin/spaces/${space.id}`, session, { method: "DELETE", body: JSON.stringify({ reason: form.reason }) });
      } else if (pendingAction.mode === "purge" && space) {
        updatedSpace = await requestAdminApi<AdminSpace>(`/api/v1/admin/spaces/${space.id}/purge`, session, { method: "DELETE", body: JSON.stringify({ reason: form.reason }) });
      } else if (pendingAction.mode === "approve" && pendingAction.application) {
        await requestAdminApi<SpaceApplication>(`/api/v1/admin/space-applications/${pendingAction.application.id}/approve`, session, { method: "POST", body: JSON.stringify({ reason: form.reason }) });
      } else if (pendingAction.mode === "reject" && pendingAction.application) {
        await requestAdminApi<SpaceApplication>(`/api/v1/admin/space-applications/${pendingAction.application.id}/reject`, session, { method: "POST", body: JSON.stringify({ reason: form.reason }) });
      } else if (pendingAction.mode === "member-add" && space) {
        await requestAdminApi<SpaceMember>(`/api/v1/admin/spaces/${space.id}/members`, session, { method: "POST", body: JSON.stringify({ user_id: form.member_user_id, role: form.member_role }) });
        await loadSpaceMembers(space.id);
        updatedSpace = await requestAdminApi<AdminSpace>(`/api/v1/admin/spaces/${space.id}`, session);
      } else if (pendingAction.mode === "member-edit" && space && pendingAction.member) {
        await requestAdminApi<SpaceMember>(`/api/v1/admin/spaces/${space.id}/members/${pendingAction.member.id}`, session, { method: "PUT", body: JSON.stringify({ role: form.member_role }) });
        await loadSpaceMembers(space.id);
        updatedSpace = await requestAdminApi<AdminSpace>(`/api/v1/admin/spaces/${space.id}`, session);
      } else if (pendingAction.mode === "member-remove" && space && pendingAction.member) {
        await requestAdminApi<SpaceMember>(`/api/v1/admin/spaces/${space.id}/members/${pendingAction.member.id}`, session, { method: "DELETE", body: JSON.stringify({ reason: form.reason }) });
        await loadSpaceMembers(space.id);
        updatedSpace = await requestAdminApi<AdminSpace>(`/api/v1/admin/spaces/${space.id}`, session);
      }
      if (updatedSpace && activeTab === "detail") {
        if (updatedSpace.status === "RECYCLE") {
          setSelectedSpace(null);
          setActiveTab("recycle");
        } else {
          const refreshedSpace = await loadSpaceDetail(updatedSpace.id);
          await loadSpaceAuditEvents(refreshedSpace.id, 1, auditPageSize);
          await loadRecentAuditEvents(refreshedSpace.id);
        }
      }
      showToast("操作已完成");
      setPendingAction(null);
      await loadSpaces();
      await loadRecycleSpaces();
      await loadApplications();
    } catch (error) {
      showToast(error instanceof Error ? error.message : "操作失败");
    }
  };

  const logout = async () => {
    await logoutAdmin();
    showToast("已退出登录");
    onLogout();
  };

  const mainTabs = (
    <div className="admin-space-tabs" role="tablist" aria-label="空间管理视图" data-testid="admin-space-tabs">
      <button className={activeTab === "spaces" ? "active" : ""} onClick={() => setActiveTab("spaces")} data-testid="space-tab-list"><Database size={16} />空间列表</button>
      <button className={activeTab === "approvals" ? "active" : ""} onClick={() => setActiveTab("approvals")} data-testid="space-tab-approvals"><CheckCircle2 size={16} />申请审批<span>{applicationTotal}</span></button>
      <button className={activeTab === "recycle" ? "active" : ""} onClick={() => setActiveTab("recycle")} data-testid="space-tab-recycle"><Archive size={16} />回收站</button>
    </div>
  );

  return (
    <main className={`admin-shell admin-space-shell ${isCollapsed ? "collapsed" : ""} ${isLightTheme ? "light" : ""}`} data-theme={isLightTheme ? "light" : "dark"}>
      <AdminSidebar
        active="spaces"
        currentUser={currentSessionUser}
        isCollapsed={isCollapsed}
        isLightTheme={isLightTheme}
        isUserMenuOpen={isUserMenuOpen}
        onToggleCollapse={() => setIsCollapsed((value) => !value)}
        onToggleUserMenu={() => setIsUserMenuOpen((value) => !value)}
        onCloseUserMenu={() => setIsUserMenuOpen(false)}
        onNavigate={navigateTo}
        onOpenProfile={() => setIsProfileModalOpen(true)}
        onOpenPassword={() => setIsPasswordModalOpen(true)}
        onThemeChange={setIsLightTheme}
        onLogout={logout}
        onToast={showToast}
      />

      <section className="admin-space-main" data-testid="admin-space-management-page">
        {activeTab !== "approvals" && activeTab !== "detail" && (
          <>
          <AdminCrudListTemplate
            eyebrow="Space Management"
            title={activeTab === "recycle" ? "空间回收站" : "空间管理"}
            description="管理空间、产品绑定、负责人、配额与生命周期"
            primaryAction={activeTab === "spaces" ? <button className="admin-btn admin-primary" onClick={() => openAction({ mode: "create" })}><Plus size={16} />新增空间</button> : undefined}
            headerAddon={mainTabs}
            bodyAddon={activeTab === "spaces" ? (
              <div className="admin-space-stats" data-testid="space-stats">
                {spaceStats.map((stat) => (
                  <article className="admin-space-stat-card" key={stat.label}>
                    <span>{stat.label}</span>
                    <strong className={stat.tone === "warning" ? "warning" : ""}>{stat.value}</strong>
                  </article>
                ))}
              </div>
            ) : undefined}
            filters={activeTab === "recycle" ? [
              { id: "q", node: <input aria-label="搜索空间" value={query} onChange={(event) => { setQuery(event.target.value); setRecyclePage(1); }} placeholder="空间名、编码或负责人" /> },
              { id: "source", node: <AdminSelect ariaLabel="空间来源" value={source} options={[{ value: "", label: "全部来源" }, { value: "后台创建", label: "后台创建" }, { value: "申请审批", label: "申请审批" }]} onChange={(value) => { setSource(value); setRecyclePage(1); }} /> },
            ] : [
              { id: "q", node: <input aria-label="搜索空间" value={query} onChange={(event) => { setQuery(event.target.value); setPage(1); }} placeholder="空间名、编码或负责人" /> },
              { id: "status", node: <AdminSelect ariaLabel="空间状态" value={status} options={[{ value: "", label: "全部状态" }, { value: "ACTIVE", label: "正常" }, { value: "FROZEN", label: "已冻结" }, { value: "RECYCLE", label: "回收站" }]} onChange={(value) => { setStatus(value); setPage(1); }} /> },
              { id: "source", node: <AdminSelect ariaLabel="空间来源" value={source} options={[{ value: "", label: "全部来源" }, { value: "后台创建", label: "后台创建" }, { value: "申请审批", label: "申请审批" }]} onChange={(value) => { setSource(value); setPage(1); }} /> },
              { id: "usage", node: <AdminSelect ariaLabel="用量状态" value={usageStatus} options={[{ value: "", label: "全部用量" }, { value: "normal", label: "正常" }, { value: "over_quota", label: "超额" }]} onChange={(value) => { setUsageStatus(value); setPage(1); }} /> },
            ]}
            columns={activeTab === "recycle" ? [
              { key: "space", label: "空间名称/编码" },
              { key: "owner", label: "负责人" },
              { key: "deleted_at", label: "删除时间" },
              { key: "deleted_by", label: "删除人" },
              { key: "delete_reason", label: "删除原因" },
              { key: "remaining", label: "剩余天数" },
              { key: "source", label: "创建来源" },
              { key: "actions", label: "操作" },
            ] : [
              { key: "space", label: "空间名称/编码" },
              { key: "owner", label: "负责人" },
              { key: "members", label: "成员数" },
              { key: "product", label: "产品数" },
              { key: "usage", label: "AI 用量" },
              { key: "expiry", label: "有效期" },
              { key: "status", label: "状态" },
              { key: "source", label: "创建来源" },
              { key: "updated", label: "更新时间" },
              { key: "actions", label: "操作" },
            ]}
            tableClassName="admin-space-table"
            colgroup={activeTab === "recycle" ? (
              <colgroup>
                <col className="admin-space-col-space" />
                <col className="admin-space-col-owner" />
                <col className="admin-space-col-expiry" />
                <col className="admin-space-col-owner" />
                <col className="admin-space-col-updated" />
                <col className="admin-space-col-members" />
                <col className="admin-space-col-source" />
                <col className="admin-space-col-actions" />
              </colgroup>
            ) : (
              <colgroup>
                <col className="admin-space-col-space" />
                <col className="admin-space-col-owner" />
                <col className="admin-space-col-members" />
                <col className="admin-space-col-product" />
                <col className="admin-space-col-usage" />
                <col className="admin-space-col-expiry" />
                <col className="admin-space-col-status" />
                <col className="admin-space-col-source" />
                <col className="admin-space-col-updated" />
                <col className="admin-space-col-actions" />
              </colgroup>
            )}
            isLoading={isLoading}
            rowCount={currentRows.length}
            pagination={{
              label: activeTab === "recycle" ? "回收站分页" : "空间分页",
              totalLabel: "共",
              total: currentTotal,
              totalUnit: "个空间",
              page: currentPage,
              pageCount,
              pageSize: currentPageSize,
              pageSizeOptions: [10, 20, 50],
              onPageChange: activeTab === "recycle" ? setRecyclePage : setPage,
              onPageSizeChange: activeTab === "recycle"
                ? (value) => { setRecyclePageSize(value); setRecyclePage(1); }
                : (value) => { setPageSize(value); setPage(1); },
            }}
            toast={toast}
          >
            {currentRows.map((space) => (
              <tr key={space.id} data-testid="space-row">
                <td><button className="admin-link-button" onClick={() => openDetail(space)}>{space.name}</button><small>{space.code}</small></td>
                <td>{space.owner_name || space.owner_id}</td>
                {activeTab === "recycle" ? (
                  <>
                    <td>{formatDate(space.deleted_at)}</td>
                    <td>{space.deleted_by_name || space.deleted_by || "-"}</td>
                    <td>{space.delete_reason || "-"}</td>
                    <td>{remainingDays(space.purge_at)}</td>
                    <td><span className="admin-source-tag">{space.source}</span></td>
                  </>
                ) : (
                  <>
                    <td>{space.member_count} / {space.member_quota}</td>
                    <td>{productCountLabel(space)}</td>
                    <td>
                      <span className={`admin-space-usage ${usageLevel(space.ai_used_tokens, space.ai_quota_tokens)}`} aria-label={`AI 用量 ${percent(space.ai_used_tokens, space.ai_quota_tokens)} ${usageQuotaText(space.ai_used_tokens, space.ai_quota_tokens)}`}>
                        <span className="admin-space-usage-bar"><i style={{ width: percent(space.ai_used_tokens, space.ai_quota_tokens) }} /></span>
                        <small>{percent(space.ai_used_tokens, space.ai_quota_tokens)}</small>
                      </span>
                    </td>
                    <td>{space.expiry_type === "long_term" ? "长期有效" : formatDate(space.expires_at)}</td>
                    <td><span className={`admin-space-status ${space.status.toLowerCase()}`}><SpaceStatusIcon status={space.status} />{statusText(space.status)}</span></td>
                    <td><span className="admin-source-tag">{space.source}</span></td>
                    <td>{formatDate(space.updated_at)}</td>
                  </>
                )}
                <td>
                  <div className="admin-operation-set admin-space-row-actions">
                  {space.allowed_actions.includes("VIEW") && <button onClick={() => openDetail(space)}>查看</button>}
                  {space.allowed_actions.includes("EDIT") && <button onClick={() => openAction({ mode: "edit", space })}>编辑</button>}
                  {space.allowed_actions.includes("FREEZE") && <button onClick={() => openAction({ mode: "freeze", space })}>冻结</button>}
                  {space.allowed_actions.includes("RESTORE") && <button onClick={() => openAction({ mode: "restore", space })}>恢复</button>}
                  {hasMoreActions(space) && (
                    <button
                      aria-expanded={moreMenu?.space.id === space.id}
                      aria-haspopup="menu"
                      onClick={(event) => {
                        event.stopPropagation();
                        toggleMoreMenu(space, event.currentTarget);
                      }}
                    >
                      更多
                    </button>
                  )}
                  </div>
                </td>
              </tr>
            ))}
          </AdminCrudListTemplate>
          {moreMenu && createPortal(
            <div
              className={`admin-space-more-menu ${isLightTheme ? "light" : "dark"}`}
              data-scope={activeTab === "recycle" ? "recycle" : "spaces"}
              data-placement={moreMenu.placement}
              role="menu"
              style={{ top: moreMenu.top, left: moreMenu.left }}
              onClick={(event) => event.stopPropagation()}
            >
              {moreMenu.space.allowed_actions.includes("QUOTA") && <button role="menuitem" onClick={() => openAction({ mode: "quota", space: moreMenu.space })}>配额</button>}
              {moreMenu.space.allowed_actions.includes("RENEW") && <button role="menuitem" onClick={() => openAction({ mode: "renew", space: moreMenu.space })}>续期</button>}
              {moreMenu.space.allowed_actions.includes("TRANSFER_OWNER") && <button role="menuitem" onClick={() => openAction({ mode: "transfer", space: moreMenu.space })}>负责人</button>}
              {moreMenu.space.allowed_actions.includes("DELETE") && <button role="menuitem" className="danger" onClick={() => openAction({ mode: "delete", space: moreMenu.space })}>删除</button>}
              {moreMenu.space.allowed_actions.includes("PURGE") && <button role="menuitem" className="danger" onClick={() => openAction({ mode: "purge", space: moreMenu.space })}>彻删</button>}
            </div>,
            document.body,
          )}
          </>
        )}

        {activeTab === "approvals" && (
          <AdminCrudListTemplate
            eyebrow="Applications"
            title="申请审批"
            description="通过或拒绝空间开通申请，审批通过后自动创建空间"
            headerAddon={mainTabs}
            filters={[]}
            columns={[
              { key: "space", label: "空间名称/编码" },
              { key: "applicant", label: "申请人" },
              { key: "owner", label: "负责人" },
              { key: "resource", label: "资源申请" },
              { key: "expiry", label: "有效期" },
              { key: "created", label: "申请时间" },
              { key: "actions", label: "操作" },
            ]}
            tableClassName="admin-space-table admin-space-application-table"
            colgroup={(
              <colgroup>
                <col className="admin-space-col-application-space" />
                <col className="admin-space-col-application-person" />
                <col className="admin-space-col-application-person" />
                <col className="admin-space-col-application-resource" />
                <col className="admin-space-col-expiry" />
                <col className="admin-space-col-updated" />
                <col className="admin-space-col-application-actions" />
              </colgroup>
            )}
            rowCount={applications.length}
            emptyText="暂无待审批申请"
            pagination={{
              label: "申请审批分页",
              totalLabel: "共",
              total: applicationTotal,
              totalUnit: "条申请",
              page: applicationPage,
              pageCount: applicationPageCount,
              pageSize: applicationPageSize,
              pageSizeOptions: [10, 20, 50],
              onPageChange: setApplicationPage,
              onPageSizeChange: (value) => { setApplicationPageSize(value); setApplicationPage(1); },
            }}
            toast={toast}
          >
            {applications.map((item) => (
              <tr key={item.id} data-testid="space-application-row">
                <td>
                  <strong className="admin-space-application-name">{item.name}</strong>
                  <small>{item.code}</small>
                </td>
                <td>{item.applicant_name || "-"}</td>
                <td>{item.proposed_owner_name || "-"}</td>
                <td>
                  <div className="admin-space-resource-cell">
                    <span className="admin-space-resource-item">{item.expected_members} 人</span>
                    <span className="admin-space-resource-item">{formatStorageAmount(item.requested_storage_gb)}</span>
                    <span className="admin-space-resource-item">{formatTokenAmount(item.requested_ai_tokens)} Tokens</span>
                  </div>
                </td>
                <td>{formatApplicationExpiry(item)}</td>
                <td>{formatDate(item.created_at)}</td>
                <td>
                  <div className="admin-operation-set admin-space-row-actions admin-space-application-actions">
                    <button onClick={() => openAction({ mode: "approve", application: item })}>通过</button>
                    <button className="danger-text" onClick={() => openAction({ mode: "reject", application: item })}>拒绝</button>
                  </div>
                </td>
              </tr>
            ))}
          </AdminCrudListTemplate>
        )}

        {activeTab === "detail" && selectedSpace && (
          <section className="admin-content" data-testid="space-detail-page">
            <nav className="admin-space-crumb" aria-label="空间详情路径">
              <button onClick={() => setActiveTab("spaces")}>空间管理</button>
              <span>/</span>
              <button onClick={() => setActiveTab("spaces")}>空间列表</button>
              <span>/</span>
              <strong>{selectedSpace.name}</strong>
            </nav>
            <header className="admin-space-detail-head">
              <div className="admin-space-detail-main">
                <p>Space Detail</p>
                <div className="admin-space-detail-title-row">
                  <h1>{selectedSpace.name}</h1>
                  <span className={`admin-space-status ${selectedSpace.status.toLowerCase()}`}><SpaceStatusIcon status={selectedSpace.status} />{statusText(selectedSpace.status)}</span>
                </div>
                <div className="admin-space-detail-meta">
                  <span>{selectedSpace.code} · {selectedSpace.source}</span>
                  <span className="admin-space-detail-divider" aria-hidden="true" />
                  <span className="admin-space-detail-owner"><AuthenticatedAvatar avatarUrl={selectedSpace.owner_avatar_url} alt={`${selectedSpace.owner_name || selectedSpace.owner_id}头像`} fallback={ownerInitial(selectedSpace)} /><b>{selectedSpace.owner_name || selectedSpace.owner_id}</b><button onClick={() => openAction({ mode: "transfer", space: selectedSpace })}>变更</button></span>
                </div>
              </div>
              <div className="admin-space-detail-actions">
                <button className="admin-space-return" onClick={() => setActiveTab("spaces")}>返回空间列表</button>
                <div>
                  {selectedSpace.allowed_actions.includes("RENEW") && <button className="admin-space-action-btn" onClick={() => openAction({ mode: "renew", space: selectedSpace })}>续期</button>}
                  {selectedSpace.allowed_actions.includes("FREEZE") && <button className="admin-space-action-btn" onClick={() => openAction({ mode: "freeze", space: selectedSpace })}>冻结</button>}
                  {selectedSpace.allowed_actions.includes("RESTORE") && <button className="admin-space-action-btn" onClick={() => openAction({ mode: "restore", space: selectedSpace })}>恢复</button>}
                  {selectedSpace.allowed_actions.includes("DELETE") && <button className="admin-space-action-btn danger" onClick={() => openAction({ mode: "delete", space: selectedSpace })}>删除</button>}
                </div>
              </div>
            </header>
            <div className="admin-space-detail-tabs" role="tablist" aria-label="空间详情分区">
              {[
                { key: "overview", label: "概览" },
                { key: "members", label: "成员" },
                { key: "product", label: "产品" },
                { key: "quota", label: "配额与用量" },
                { key: "logs", label: "操作记录" },
              ].map((tab) => (
                <button key={tab.key} className={detailTab === tab.key ? "active" : ""} onClick={() => setDetailTab(tab.key as DetailTab)}>{tab.label}</button>
              ))}
            </div>
            {detailTab === "overview" && (
              <section className="admin-space-detail-section" data-testid="space-detail-overview">
                <div className="admin-space-detail-overview">
                  <article data-testid="space-detail-base"><h2>基础信息 <button onClick={() => openAction({ mode: "edit", space: selectedSpace })}>编辑</button></h2><dl className="admin-space-detail-field-grid"><div><dt>空间名称</dt><dd>{selectedSpace.name}</dd></div><div><dt>唯一标识</dt><dd>{selectedSpace.code}（不可修改）</dd></div><div><dt>创建来源</dt><dd>{selectedSpace.source}</dd></div><div><dt>创建时间</dt><dd>{formatDate(selectedSpace.created_at)}</dd></div><div><dt>有效期</dt><dd>{formatExpiry(selectedSpace)}</dd></div></dl></article>
                  <article data-testid="space-detail-quota"><h2>配额与用量 <button onClick={() => openAction({ mode: "quota", space: selectedSpace })}>调整</button></h2><SpaceQuotaRows space={selectedSpace} /></article>
                  <article data-testid="space-detail-recent">
                    <h2>最近操作</h2>
                    {recentAuditEvents.length === 0 ? (
                      <div className="admin-table-state">暂无操作记录。</div>
                    ) : (
                      <div className="admin-space-timeline">
                        {recentAuditEvents.map((event) => (
                          <div key={event.id}>
                            <b>{auditActionText(event.action)}</b>
                            <span>{event.actor_display_name || event.actor} · {formatDate(event.created_at)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </article>
                </div>
              </section>
            )}
            {detailTab === "members" && (
              <section className="admin-space-detail-section" data-testid="space-detail-members">
                <article>
                  <h2>成员管理 <button className="admin-btn admin-primary" onClick={() => openAction({ mode: "member-add", space: selectedSpace })}>添加成员</button></h2>
                  <table className="admin-space-member-table">
                    <thead>
                      <tr><th>用户</th><th>角色</th><th>加入时间</th><th>状态</th><th>操作</th></tr>
                    </thead>
                    <tbody>
                      {spaceMembers.map((member) => (
                        <tr key={member.id}>
                          <td><span className="admin-space-member-user"><AuthenticatedAvatar avatarUrl={member.avatar_url} alt={`${member.user_name || member.username}头像`} fallback={(member.user_name || member.username).slice(0, 1)} /><span><b>{member.user_name || member.username}</b><small>{member.username}</small></span></span></td>
                          <td>{member.role}</td>
                          <td>{formatDate(member.joined_at)}</td>
                          <td><span className="admin-status">{member.user_status}</span></td>
                          <td><div className="admin-operation-set"><button onClick={() => openAction({ mode: "member-edit", space: selectedSpace, member })}>编辑</button><button className="danger-text" onClick={() => openAction({ mode: "member-remove", space: selectedSpace, member })}>移除</button></div></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {spaceMembers.length === 0 && <div className="admin-table-state">暂无成员，负责人不在成员列表。</div>}
                </article>
              </section>
            )}
            {detailTab === "product" && (
              <section className="admin-space-detail-section" data-testid="space-detail-product">
                <div className="admin-space-notice">绑定关系不可解除或迁移，产品名称始终与空间名称一致。</div>
                <div className="admin-space-product-list">
                  <article className="admin-space-product-card">
                    <dl className="admin-space-detail-field-grid">
                      <div><dt>产品名称</dt><dd>{selectedSpace.product_name}</dd></div>
                      <div><dt>产品 ID</dt><dd>{selectedSpace.product_id}</dd></div>
                      <div><dt>绑定状态</dt><dd>永久绑定</dd></div>
                      <div><dt>研发状态</dt><dd>进行中</dd></div>
                    </dl>
                  </article>
                </div>
              </section>
            )}
            {detailTab === "quota" && (
              <section className="admin-space-detail-section" data-testid="space-detail-quota-section"><article><h2>资源配额详情 <button className="admin-btn admin-primary" onClick={() => openAction({ mode: "quota", space: selectedSpace })}>调整配额</button></h2>{usageLevel(selectedSpace.ai_used_tokens, selectedSpace.ai_quota_tokens) !== "normal" && <div className="admin-space-alert">AI Token 用量已达到 {percent(selectedSpace.ai_used_tokens, selectedSpace.ai_quota_tokens)}，已通知空间负责人及平台管理员。</div>}<SpaceQuotaRows space={selectedSpace} /></article></section>
            )}
            {detailTab === "logs" && (
              <section className="admin-space-detail-section" data-testid="space-detail-logs">
                <article>
                  {spaceAuditEvents.length === 0 ? (
                    <div className="admin-table-state">暂无操作记录。</div>
                  ) : (
                    <div className="admin-space-audit-table-wrap">
                      <table className="admin-space-audit-table">
                        <thead>
                          <tr><th>时间</th><th>操作人</th><th>操作动作</th><th>变更摘要</th><th>结果</th><th>操作</th></tr>
                        </thead>
                        <tbody>
                          {spaceAuditEvents.map((event) => (
                            <tr key={event.id}>
                              <td>{formatDate(event.created_at)}</td>
                              <td>{event.actor_display_name || event.actor}</td>
                              <td><span className={`admin-space-audit-tag ${auditActionTone(event.action)}`}>{auditActionText(event.action)}</span></td>
                              <td>
                                <span className="admin-space-audit-diff">
                                  {auditChangeSummary(event).map((item) => <small key={item}>{item}</small>)}
                                </span>
                              </td>
                              <td><span className={`admin-space-audit-tag result ${event.result}`}>{auditResultText(event.result)}</span></td>
                              <td><button className="admin-link-button" onClick={() => setSelectedAuditEvent(event)}>查看</button></td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      <footer className="admin-pagination admin-space-audit-pagination" aria-label="操作记录分页">
                        <div className="admin-pagination-total">共 <strong>{auditTotal}</strong> 条记录</div>
                        <div className="admin-pagination-actions">
                          <button className="admin-page-btn page-icon" aria-label="上一页" disabled={auditPage <= 1} onClick={() => setAuditPage(auditPage - 1)}>‹</button>
                          {Array.from({ length: auditPageCount }, (_, index) => (
                            <button key={index + 1} className={`admin-page-btn ${auditPage === index + 1 ? "active" : ""}`} onClick={() => setAuditPage(index + 1)}>{index + 1}</button>
                          ))}
                          <button className="admin-page-btn page-icon" aria-label="下一页" disabled={auditPage >= auditPageCount} onClick={() => setAuditPage(auditPage + 1)}>›</button>
                          <span className="admin-page-size-label">每页显示</span>
                          <AdminSelect ariaLabel="操作记录每页显示条数" className="admin-page-size" value={auditPageSize} options={[10, 20, 50].map((option) => ({ value: option, label: `${option} 条` }))} onChange={(value) => { setAuditPageSize(Number(value)); setAuditPage(1); }} />
                        </div>
                      </footer>
                    </div>
                  )}
                </article>
              </section>
            )}
          </section>
        )}
      </section>

      {selectedAuditEvent && selectedSpace && (
        <aside className="admin-space-audit-drawer" role="dialog" aria-modal="true" aria-label="操作记录明细" data-testid="space-audit-drawer">
          <header>
            <div><span>Audit Detail</span><h2>{auditActionText(selectedAuditEvent.action)}</h2></div>
            <button aria-label="关闭操作记录明细" onClick={() => setSelectedAuditEvent(null)}>×</button>
          </header>
          <dl>
            <div><dt>来源</dt><dd><span className="admin-space-audit-tag source">{auditSourceText(selectedAuditEvent.action)}</span></dd></div>
            <div><dt>对象</dt><dd>{selectedSpace.name}</dd></div>
            <div><dt>请求 ID</dt><dd>{selectedAuditEvent.request_id}</dd></div>
            <div><dt>操作人</dt><dd>{selectedAuditEvent.actor_display_name || selectedAuditEvent.actor}</dd></div>
            <div><dt>时间</dt><dd>{formatDate(selectedAuditEvent.created_at)}</dd></div>
            <div><dt>原因</dt><dd>{selectedAuditEvent.reason || "-"}</dd></div>
            <div><dt>结果</dt><dd><span className={`admin-space-audit-tag result ${selectedAuditEvent.result}`}>{auditResultText(selectedAuditEvent.result)}</span></dd></div>
          </dl>
          <section>
            <h3>变更前</h3>
            <AuditValueBlock value={selectedAuditEvent.before_value} />
          </section>
          <section>
            <h3>变更后</h3>
            <AuditValueBlock value={selectedAuditEvent.after_value} />
          </section>
        </aside>
      )}

      {pendingAction && (
        <AdminModalBackdrop>
          <div className="admin-space-modal" role="dialog" aria-modal="true" data-testid="space-action-modal">
            <header><h2>{actionTitle(pendingAction.mode)}</h2></header>
            {(pendingAction.mode === "create" || pendingAction.mode === "edit") && (
              <div className="admin-form-grid">
                <label><FieldLabel label="空间名称" required /><input minLength={2} maxLength={80} required value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="请输入空间名称" /><small>一空间仅绑定一款产品，空间名称即产品名称，2-80个字符</small></label>
                <label><FieldLabel label="空间编码" required /><input disabled={pendingAction.mode === "edit"} minLength={3} maxLength={48} pattern="[a-z][a-z0-9-]*" required value={form.code} onChange={(event) => setForm({ ...form, code: event.target.value })} placeholder="请输入空间编码" /><small>系统唯一，3-48 位；仅允许小写字母/数字/短横线，且必须以字母开头；创建后不可修改。</small></label>
                {pendingAction.mode === "create" && (
                  <label>
                    <FieldLabel label="负责人" required />
                    <AdminSelect ariaLabel="负责人" value={form.owner_id} options={[{ value: "", label: "请选择" }, ...ownerOptions.map((user) => ({ value: user.id, label: optionLabel(user) }))]} onChange={(value) => setForm({ ...form, owner_id: value })} />
                    {ownerOptions.length === 0 && <small>暂无可选负责人，请先在用户管理中创建或激活用户。</small>}
                  </label>
                )}
                {pendingAction.mode === "create" && <label><FieldLabel label="成员上限" required /><input type="number" min="1" required value={form.member_quota} onChange={(event) => setForm({ ...form, member_quota: event.target.value })} /></label>}
                {pendingAction.mode === "create" && <label><FieldLabel label="存储空间" required /><input type="number" min="1" required value={form.storage_quota_gb} onChange={(event) => setForm({ ...form, storage_quota_gb: event.target.value })} /></label>}
                {pendingAction.mode === "create" && <label><FieldLabel label="AI Tokens" required /><input type="number" min="1" required value={form.ai_quota_tokens} onChange={(event) => setForm({ ...form, ai_quota_tokens: event.target.value })} /></label>}
                <label><FieldLabel label="有效期类型" required /><AdminSelect ariaLabel="有效期类型" value={form.expiry_type} options={[{ value: "fixed_date", label: "固定日期" }, { value: "long_term", label: "长期有效" }]} onChange={(value) => setForm({ ...form, expiry_type: value as ExpiryType, expires_at: value === "fixed_date" ? nextFixedExpiryValue(form.expires_at) : "" })} /></label>
                {form.expiry_type === "fixed_date" && <label><FieldLabel label="到期时间" required /><AdminDateTimePicker ariaLabel="到期时间" value={form.expires_at} onChange={(value) => setForm({ ...form, expires_at: value })} /></label>}
                <label className="admin-form-field-full"><FieldLabel label="描述" /><textarea maxLength={500} value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} placeholder="请输入空间用途或业务范围，最多 500 个字符" /></label>
              </div>
            )}
            {pendingAction.mode === "quota" && (
              <div className="admin-form-grid">
                <label><FieldLabel label="成员上限" required /><input type="number" min="1" required value={form.member_quota} onChange={(event) => setForm({ ...form, member_quota: event.target.value })} /></label>
                <label><FieldLabel label="存储空间" required /><input type="number" min="1" required value={form.storage_quota_gb} onChange={(event) => setForm({ ...form, storage_quota_gb: event.target.value })} /></label>
                <label><FieldLabel label="AI Tokens" required /><input type="number" min="1" required value={form.ai_quota_tokens} onChange={(event) => setForm({ ...form, ai_quota_tokens: event.target.value })} /></label>
              </div>
            )}
            {pendingAction.mode === "renew" && (
              <div className="admin-form-grid">
                <label><FieldLabel label="有效期类型" required /><AdminSelect ariaLabel="有效期类型" value={form.expiry_type} options={[{ value: "fixed_date", label: "固定日期" }, { value: "long_term", label: "长期有效" }]} onChange={(value) => setForm({ ...form, expiry_type: value as ExpiryType, expires_at: value === "fixed_date" ? nextFixedExpiryValue(form.expires_at) : "" })} /></label>
                {form.expiry_type === "fixed_date" && <label><FieldLabel label="到期时间" required /><AdminDateTimePicker ariaLabel="到期时间" value={form.expires_at} onChange={(value) => setForm({ ...form, expires_at: value })} /></label>}
              </div>
            )}
            {pendingAction.mode === "transfer" && (
              <label>
                <FieldLabel label="新负责人" required />
                <AdminSelect ariaLabel="新负责人" value={form.owner_id} options={[{ value: "", label: "请选择" }, ...ownerOptions.map((user) => ({ value: user.id, label: optionLabel(user) }))]} onChange={(value) => setForm({ ...form, owner_id: value })} />
                {ownerOptions.length === 0 && <small>暂无可选负责人，请先在用户管理中创建或激活用户。</small>}
              </label>
            )}
            {pendingAction.mode === "member-add" && (
              <div className="admin-form-stack">
                <label>
                  <FieldLabel label="用户" required />
                  <AdminSelect portal ariaLabel="用户" value={form.member_user_id} options={[{ value: "", label: "请选择" }, ...memberCandidateOptions.map((user) => ({ value: user.id, label: optionLabel(user) }))]} onChange={(value) => setForm({ ...form, member_user_id: value })} />
                  {memberCandidateOptions.length === 0 && <small>暂无可添加的正常状态用户。</small>}
                </label>
                <label>
                  <FieldLabel label="角色" required />
                  <AdminSelect portal ariaLabel="成员角色" value={form.member_role} options={memberRoleOptions} onChange={(value) => setForm({ ...form, member_role: value as SpaceMemberRole })} />
                </label>
              </div>
            )}
            {pendingAction.mode === "member-edit" && (
              <div className="admin-form-stack">
                <label><FieldLabel label="用户" /><input disabled value={pendingAction.member?.user_name || pendingAction.member?.username || ""} readOnly /></label>
                <label>
                  <FieldLabel label="角色" required />
                  <AdminSelect portal ariaLabel="成员角色" value={form.member_role} options={memberRoleOptions} onChange={(value) => setForm({ ...form, member_role: value as SpaceMemberRole })} />
                </label>
              </div>
            )}
            {!["create", "member-add", "member-edit"].includes(pendingAction.mode) && (
              <div className="admin-form-row">
                <label className="required admin-space-reason-label" htmlFor="admin-space-action-reason"><span>操作原因</span></label>
                <textarea
                  id="admin-space-action-reason"
                  value={form.reason}
                  aria-invalid={(hasTriedConfirm || form.reason.length > 0) && form.reason.trim().length < 4}
                  onChange={(event) => {
                    setForm({ ...form, reason: event.target.value });
                    if (hasTriedConfirm) setHasTriedConfirm(false);
                  }}
                  placeholder="请输入不少于 4 个字符的原因"
                />
                <div className="admin-form-hint">请填写至少 4 个字，便于审计追踪。</div>
                {(hasTriedConfirm || form.reason.length > 0) && form.reason.trim().length < 4 && <div className="admin-form-error" aria-live="polite">操作原因至少需要 4 个字。</div>}
              </div>
            )}
            <footer><button className="admin-btn" onClick={() => setPendingAction(null)}>取消</button><button className="admin-btn admin-primary" onClick={submitAction}>确认</button></footer>
          </div>
        </AdminModalBackdrop>
      )}
      {isProfileModalOpen && currentSessionUser && (
        <ProfileModal
          user={currentSessionUser}
          roleLabel={currentSessionUser.is_system_superadmin ? "超级管理员" : "后台管理员"}
          onClose={() => setIsProfileModalOpen(false)}
          onSaved={(nextUser) => {
            setCurrentSessionUser(nextUser);
            setIsProfileModalOpen(false);
            showToast("个人资料已更新");
          }}
        />
      )}
      {isPasswordModalOpen && (
        <ChangePasswordModal
          onClose={() => setIsPasswordModalOpen(false)}
          onChanged={() => {
            setIsPasswordModalOpen(false);
            showToast("密码已更新，请重新登录");
            onLogout();
          }}
        />
      )}
    </main>
  );
}

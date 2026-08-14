import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AdminSpaceManagementPage } from "./pages/admin/AdminSpaceManagementPage";

const session = {
  access_token: "admin-token",
  expires_at: "2026-08-12T23:59:59Z",
  user: {
    id: "user_superadmin",
    username: "superadmin",
    nickname: "平台超级管理员",
    avatar_url: null,
    role: "后台管理员" as const,
    status: "正常" as const,
    is_system_superadmin: true,
  },
};

const spaces = [
  {
    id: "space_one",
    name: "MoonBox 运营空间",
    code: "moonbox-ops",
    description: "运营团队空间",
    owner_id: "user_owner",
    owner_name: "空间负责人",
    owner_role: "前台用户",
    owner_avatar_url: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'/%3E",
    status: "ACTIVE",
    source: "后台创建",
    member_count: 3,
    member_quota: 20,
    storage_used_gb: 12,
    storage_quota_gb: 100,
    ai_used_tokens: 860000,
    ai_quota_tokens: 1000000,
    product_id: "moonbox-platform",
    product_name: "MoonBox Platform",
    expiry_type: "fixed_date",
    expires_at: "2027-12-31T23:59:59Z",
    protected: false,
    deleted_at: null,
    deleted_by: null,
    deleted_by_name: null,
    delete_reason: null,
    purge_at: null,
    allowed_actions: ["VIEW", "EDIT", "FREEZE", "DELETE", "QUOTA", "RENEW", "TRANSFER_OWNER"],
    created_at: "2026-08-12T10:00:00Z",
    updated_at: "2026-08-12T10:00:00Z",
  },
  {
    id: "space_deleted",
    name: "历史空间",
    code: "old-space",
    description: null,
    owner_id: "user_owner",
    owner_name: "空间负责人",
    owner_role: "前台用户",
    owner_avatar_url: null,
    status: "RECYCLE",
    source: "后台创建",
    member_count: 1,
    member_quota: 10,
    storage_used_gb: 1,
    storage_quota_gb: 10,
    ai_used_tokens: 0,
    ai_quota_tokens: 1000,
    product_id: "moonbox-platform",
    product_name: "MoonBox Platform",
    expiry_type: "long_term",
    expires_at: null,
    protected: false,
    deleted_at: "2026-08-12T10:00:00Z",
    deleted_by: "user_superadmin",
    deleted_by_name: "平台超级管理员",
    delete_reason: "空间生命周期结束",
    purge_at: "2026-09-11T10:00:00Z",
    allowed_actions: ["VIEW", "RESTORE", "PURGE"],
    created_at: "2026-08-01T10:00:00Z",
    updated_at: "2026-08-12T10:00:00Z",
  },
] as const;

const applications = [
  {
    id: "space_app_1",
    name: "新项目空间",
    code: "new-project",
    applicant_id: "user_owner",
    applicant_name: "申请人",
    proposed_owner_id: "user_owner",
    proposed_owner_name: "空间负责人",
    product_id: "moonbox-platform",
    product_name: "MoonBox Platform",
    purpose: "业务团队申请开通",
    expected_members: 12,
    requested_storage_gb: 80,
    requested_ai_tokens: 900000,
    expires_at: null,
    status: "待审批",
    decision_reason: null,
    decision_by: null,
    decision_at: null,
    created_at: "2026-08-12T10:00:00Z",
    updated_at: "2026-08-12T10:00:00Z",
  },
] as const;

const ownerUsers = [
  {
    id: "user_owner",
    username: "owner",
    nickname: "空间负责人",
    avatar_url: null,
    role: "前台用户",
    status: "正常",
    is_system_superadmin: false,
    created_at: "2026-08-12T10:00:00Z",
    updated_at: "2026-08-12T10:00:00Z",
  },
  {
    id: "user_admin",
    username: "admin-owner",
    nickname: "后台负责人",
    avatar_url: null,
    role: "后台管理员",
    status: "正常",
    is_system_superadmin: false,
    created_at: "2026-08-12T10:00:00Z",
    updated_at: "2026-08-12T10:00:00Z",
  },
  {
    id: "user_viewer",
    username: "viewer",
    nickname: "观察员",
    avatar_url: null,
    role: "前台用户",
    status: "正常",
    is_system_superadmin: false,
    created_at: "2026-08-12T10:00:00Z",
    updated_at: "2026-08-12T10:00:00Z",
  },
  {
    id: "user_editor",
    username: "editor",
    nickname: "编辑候选",
    avatar_url: null,
    role: "前台用户",
    status: "正常",
    is_system_superadmin: false,
    created_at: "2026-08-12T10:00:00Z",
    updated_at: "2026-08-12T10:00:00Z",
  },
] as const;

const spaceMembers = [
  {
    id: "space_member_admin",
    space_id: "space_one",
    user_id: "user_admin",
    user_name: "后台负责人",
    username: "admin-owner",
    avatar_url: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'/%3E",
    role: "管理员",
    user_status: "正常",
    joined_at: "2026-08-12T12:00:00Z",
    updated_at: "2026-08-12T12:00:00Z",
  },
  {
    id: "space_member_viewer",
    space_id: "space_one",
    user_id: "user_viewer",
    user_name: "观察员",
    username: "viewer",
    avatar_url: null,
    role: "查看者",
    user_status: "正常",
    joined_at: "2026-08-12T11:00:00Z",
    updated_at: "2026-08-12T11:00:00Z",
  },
] as const;

const spaceAuditEvents = [
  {
    id: "audit_approval",
    space_id: "space_one",
    actor: "superadmin",
    actor_display_name: "平台超级管理员",
    action: "application_approved_create_space",
    before_value: JSON.stringify({ id: "space_app_1", status: "待审批", name: "MoonBox 运营空间", code: "moonbox-ops" }),
    after_value: JSON.stringify({ id: "space_one", source: "申请审批", name: "MoonBox 运营空间", code: "moonbox-ops" }),
    reason: "资料完整准予开通",
    result: "success",
    request_id: "req_audit_1",
    created_at: "2026-08-12T10:20:00Z",
  },
  {
    id: "audit_member_role",
    space_id: "space_one",
    actor: "superadmin",
    actor_display_name: "平台超级管理员",
    action: "add_member",
    before_value: null,
    after_value: JSON.stringify({ user_id: "user_viewer", role: "查看者" }),
    reason: "后台添加空间成员",
    result: "success",
    request_id: "req_audit_2",
    created_at: "2026-08-12T10:15:00Z",
  },
  ...Array.from({ length: 5 }, (_, index) => ({
    id: `audit_extra_${index}`,
    space_id: "space_one",
    actor: "superadmin",
    actor_display_name: "平台超级管理员",
    action: index % 2 === 0 ? "update_quota" : "renew_space",
    before_value: JSON.stringify({ ai_quota_tokens: 1000000 + index }),
    after_value: JSON.stringify({ ai_quota_tokens: 2000000 + index }),
    reason: `补充审计 ${index}`,
    result: "success",
    request_id: `req_audit_extra_${index}`,
    created_at: `2026-08-12T10:1${index}:00Z`,
  })),
] as const;

function jsonResponse(data: unknown, ok = true) {
  return {
    ok,
    json: async () => data,
  } as Response;
}

function mockSpaceApi(options: { emptyMembers?: boolean; normalizedAvatarUrls?: boolean; longTermActive?: boolean; recycleWithoutMoreActions?: boolean } = {}) {
  const adjustedSpaces = options.recycleWithoutMoreActions
    ? spaces.map((space) => space.status === "RECYCLE" ? { ...space, allowed_actions: ["VIEW", "RESTORE"] } : space)
    : spaces;
  const sourceSpaces = options.longTermActive ? adjustedSpaces.map((space, index) => index === 0 ? { ...space, expiry_type: "long_term", expires_at: null } : space) : adjustedSpaces;
  const spaceItems = options.normalizedAvatarUrls
    ? spaces.map((space, index) =>
        index === 0 ? { ...space, owner_avatar_url: "/api/v1/auth/avatar/owner-legacy.webp" } : space,
      )
    : sourceSpaces;
  let currentSpace: Record<string, unknown> = { ...spaceItems[0] };
  const memberItems = options.normalizedAvatarUrls
    ? spaceMembers.map((member, index) =>
        index === 0 ? { ...member, avatar_url: "/api/v1/auth/avatar/member-legacy.webp" } : member,
      )
    : spaceMembers;
  return vi.spyOn(window, "fetch").mockImplementation(async (input, init) => {
    const url = String(input);
    const method = init?.method || "GET";
    const body = init?.body ? JSON.parse(String(init.body)) : {};
    if (url.includes("/api/v1/auth/avatar/") && method === "GET") {
      return {
        ok: true,
        blob: async () => new Blob(["avatar"], { type: "image/webp" }),
        json: async () => ({}),
      } as Response;
    }
    if (url.includes("/api/v1/admin/users/avatar/") && method === "GET") {
      return jsonResponse({ detail: "legacy avatar route should not be requested" }, false);
    }
    if (url.includes("/api/v1/admin/space-applications") && method === "GET") {
      return jsonResponse({ data: { items: applications, total: applications.length, page: 1, page_size: 10 } });
    }
    if (url.includes("/api/v1/admin/users") && method === "GET") {
      return jsonResponse({ data: { items: ownerUsers, total: ownerUsers.length, page: 1, page_size: 100 } });
    }
    if (url.includes("/api/v1/admin/spaces/space_one/members") && method === "GET") {
      return jsonResponse({ data: options.emptyMembers ? [] : memberItems });
    }
    if (url.includes("/api/v1/admin/spaces/space_one/audit-events") && method === "GET") {
      const params = new URL(url, window.location.origin).searchParams;
      const requestedPage = Number(params.get("page") || 1);
      const requestedPageSize = Number(params.get("page_size") || 10);
      const start = (requestedPage - 1) * requestedPageSize;
      return jsonResponse({ data: { items: spaceAuditEvents.slice(start, start + requestedPageSize), total: spaceAuditEvents.length, page: requestedPage, page_size: requestedPageSize } });
    }
    if (url.includes("/api/v1/admin/spaces/space_one/members") && method === "POST") {
      return jsonResponse({ data: { ...spaceMembers[1], id: "space_member_new", user_id: body.user_id, role: body.role } });
    }
    if (url.includes("/api/v1/admin/spaces/space_one/members/space_member_admin") && method === "PUT") {
      return jsonResponse({ data: { ...memberItems[0], role: body.role } });
    }
    if (url.includes("/api/v1/admin/spaces/space_one/members/space_member_admin") && method === "DELETE") {
      return jsonResponse({ data: memberItems[0] });
    }
    if (url.endsWith("/api/v1/admin/spaces/space_one") && method === "GET") {
      return jsonResponse({ data: currentSpace });
    }
    if (url.includes("/api/v1/auth/me") && method === "PATCH") {
      const body = JSON.parse(String(init?.body || "{}"));
      return jsonResponse({ data: { user: { ...session.user, nickname: body.nickname, avatar_url: body.avatar_url ?? null } } });
    }
    if (url.includes("/api/v1/auth/change-password") && method === "POST") {
      return jsonResponse({ data: { status: "done" } });
    }
    if (url.includes("/api/v1/admin/space-applications") && method === "POST") {
      return jsonResponse({ data: { ...applications[0], status: "已通过", decision_reason: "审批通过" } });
    }
    if (url.includes("/api/v1/admin/spaces") && method === "GET") {
      const params = new URL(url, window.location.origin).searchParams;
      const requestedStatus = params.get("status");
      const allSpaces = [currentSpace, ...spaceItems.slice(1)];
      const filtered = requestedStatus ? allSpaces.filter((item) => item.status === requestedStatus) : allSpaces.filter((item) => item.status !== "RECYCLE");
      if (!requestedStatus) {
        return jsonResponse({ data: { items: filtered, total: filtered.length, page: 1, page_size: 10 } });
      }
      return jsonResponse({ data: { items: filtered, total: filtered.length, page: 1, page_size: 10 } });
    }
    if (url.includes("/api/v1/admin/spaces/space_one/quota")) {
      currentSpace = { ...currentSpace, member_quota: body.member_quota, storage_quota_gb: body.storage_quota_gb, ai_quota_tokens: body.ai_quota_tokens, updated_at: "2026-08-13T10:00:00Z" };
      return jsonResponse({ data: currentSpace });
    }
    if (url.includes("/api/v1/admin/spaces/space_one/renew")) {
      currentSpace = { ...currentSpace, expiry_type: body.expiry_type, expires_at: body.expires_at, updated_at: "2026-08-13T10:00:00Z" };
      return jsonResponse({ data: currentSpace });
    }
    if (url.includes("/api/v1/admin/spaces/space_one/transfer-owner")) {
      const owner = (ownerUsers as readonly { id: string; nickname: string | null; username: string }[]).find((user) => user.id === body.owner_id);
      currentSpace = { ...currentSpace, owner_id: body.owner_id, owner_name: owner?.nickname || owner?.username || body.owner_id, updated_at: "2026-08-13T10:00:00Z" };
      return jsonResponse({ data: currentSpace });
    }
    if (url.includes("/api/v1/admin/spaces/space_one/freeze")) {
      currentSpace = { ...currentSpace, status: "FROZEN", allowed_actions: ["VIEW", "EDIT", "RESTORE", "DELETE", "QUOTA", "RENEW", "TRANSFER_OWNER"], updated_at: "2026-08-13T10:00:00Z" };
      return jsonResponse({ data: currentSpace });
    }
    if (url.includes("/api/v1/admin/spaces/space_one/restore")) {
      currentSpace = { ...currentSpace, status: "ACTIVE", deleted_at: null, deleted_by: null, deleted_by_name: null, delete_reason: null, purge_at: null, allowed_actions: ["VIEW", "EDIT", "FREEZE", "DELETE", "QUOTA", "RENEW", "TRANSFER_OWNER"], updated_at: "2026-08-13T10:00:00Z" };
      return jsonResponse({ data: currentSpace });
    }
    if (url.includes("/api/v1/admin/spaces/space_one/purge")) {
      currentSpace = { ...currentSpace, status: "PURGED", updated_at: "2026-08-13T10:00:00Z" };
      return jsonResponse({ data: currentSpace });
    }
    if (url.includes("/api/v1/admin/spaces/space_one") && method === "DELETE") {
      currentSpace = { ...currentSpace, status: "RECYCLE", deleted_at: "2026-08-13T10:00:00Z", deleted_by: "user_superadmin", deleted_by_name: "平台超级管理员", delete_reason: body.reason, purge_at: "2026-09-12T10:00:00Z", allowed_actions: ["VIEW", "RESTORE", "PURGE"], updated_at: "2026-08-13T10:00:00Z" };
      return jsonResponse({ data: currentSpace });
    }
    if (url.includes("/api/v1/admin/spaces/space_one") && method === "PUT") {
      currentSpace = { ...currentSpace, name: body.name, product_name: body.name, description: body.description, expiry_type: body.expiry_type, expires_at: body.expires_at, updated_at: "2026-08-13T10:00:00Z" };
      return jsonResponse({ data: currentSpace });
    }
    if (url.includes("/api/v1/admin/spaces")) {
      return jsonResponse({ data: { ...spaceItems[0], name: body.name || spaceItems[0].name, code: body.code || spaceItems[0].code, product_id: body.product_id || spaceItems[0].product_id, product_name: body.product_name || spaceItems[0].product_name } });
    }
    return jsonResponse({ data: null });
  });
}

function chooseAdminSelect(label: string, option: string) {
  const modal = screen.queryByTestId("space-action-modal");
  const trigger = modal
    ? Array.from(modal.querySelectorAll("button")).find((button) => button.getAttribute("aria-label") === label)
    : screen.getByRole("button", { name: label });
  fireEvent.click(trigger as HTMLElement);
  fireEvent.click(screen.getByRole("option", { name: option }));
}

function openModalAdminSelect(label: string) {
  const modal = screen.getByTestId("space-action-modal");
  const trigger = Array.from(modal.querySelectorAll("button")).find((button) => button.getAttribute("aria-label") === label);
  fireEvent.click(trigger as HTMLElement);
}

function openMoreMenu(index = 0) {
  fireEvent.click(screen.getAllByText("更多")[index]);
}

beforeEach(() => {
  window.history.replaceState(null, "", "/admin/spaces");
  window.localStorage.setItem("moonbox.session", JSON.stringify(session));
  mockSpaceApi();
  window.confirm = vi.fn();
});

afterEach(() => {
  cleanup();
  window.localStorage.clear();
  vi.restoreAllMocks();
});

describe("AdminSpaceManagementPage", () => {
  it("shows long-term expiry text in the space list", async () => {
    vi.restoreAllMocks();
    mockSpaceApi({ longTermActive: true });
    window.confirm = vi.fn();
    render(<AdminSpaceManagementPage session={session} onLogout={() => undefined} />);

    expect(await screen.findByText("MoonBox 运营空间")).toBeTruthy();
    expect(screen.getByText("长期有效")).toBeTruthy();
    expect(screen.queryByText(/^长期$/)).toBeNull();
  });

  it("loads recycle bin from RECYCLE status API and shows recycle fields", async () => {
    const fetchSpy = vi.mocked(window.fetch);
    render(<AdminSpaceManagementPage session={session} onLogout={() => undefined} />);

    expect(await screen.findByText("MoonBox 运营空间")).toBeTruthy();
    fireEvent.click(screen.getByTestId("space-tab-recycle"));

    await screen.findByText("历史空间");
    expect(fetchSpy.mock.calls.some(([url]) => String(url).includes("/api/v1/admin/spaces?") && String(url).includes("status=RECYCLE"))).toBe(true);
    expect(screen.getByRole("heading", { name: "空间回收站" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "删除时间" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "删除人" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "删除原因" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "剩余天数" })).toBeTruthy();
    expect(screen.getByText("2026-08-12 10:00:00")).toBeTruthy();
    expect(screen.getAllByText("平台超级管理员").length).toBeGreaterThan(1);
    expect(screen.getAllByText("空间生命周期结束").length).toBeGreaterThan(0);
    expect(screen.getByText(/天$/)).toBeTruthy();
    expect(screen.getByLabelText("回收站分页").textContent).toContain("共 1 个空间");
    expect(screen.getByRole("button", { name: "恢复" })).toBeTruthy();
    Object.defineProperty(window, "innerWidth", { configurable: true, value: 1440 });
    const recycleMoreButton = screen.getByRole("button", { name: "更多" }) as HTMLButtonElement;
    vi.spyOn(recycleMoreButton, "getBoundingClientRect").mockReturnValue({
      x: 1120,
      y: 520,
      width: 56,
      height: 28,
      top: 520,
      right: 1176,
      bottom: 548,
      left: 1120,
      toJSON: () => ({}),
    } as DOMRect);
    openMoreMenu();
    const menu = screen.getByRole("menu");
    expect(menu.parentElement).toBe(document.body);
    expect(menu.className).toContain("admin-space-more-menu");
    expect(menu.getAttribute("data-scope")).toBe("recycle");
    expect(menu.getAttribute("data-placement")).toBe("bottom");
    expect(menu.getAttribute("style")).toContain("left: 1120px");
    expect(menu.getAttribute("style")).toContain("top: 554px");
    expect(screen.getByRole("menuitem", { name: "彻删" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "编辑" })).toBeNull();
    expect(screen.queryByRole("button", { name: "冻结" })).toBeNull();
  });

  it("does not render an empty recycle more menu when no more actions are allowed", async () => {
    vi.restoreAllMocks();
    mockSpaceApi({ recycleWithoutMoreActions: true });
    window.confirm = vi.fn();
    render(<AdminSpaceManagementPage session={session} onLogout={() => undefined} />);

    expect(await screen.findByText("MoonBox 运营空间")).toBeTruthy();
    fireEvent.click(screen.getByTestId("space-tab-recycle"));
    await screen.findByText("历史空间");

    expect(screen.getByRole("button", { name: "查看" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "恢复" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "更多" })).toBeNull();
    expect(document.body.querySelector(".admin-space-more-menu")).toBeNull();
  });

  it("refreshes recycle bin after deleting a space from detail", async () => {
    const fetchSpy = vi.mocked(window.fetch);
    render(<AdminSpaceManagementPage session={session} onLogout={() => undefined} />);

    fireEvent.click(await screen.findByText("MoonBox 运营空间"));
    fireEvent.click(screen.getByRole("button", { name: "删除" }));
    fireEvent.change(screen.getByLabelText("操作原因"), { target: { value: "空间生命周期结束" } });
    fireEvent.click(screen.getByRole("button", { name: "确认" }));

    await waitFor(() => expect(screen.queryByTestId("space-detail-page")).toBeNull());
    expect(screen.getByRole("heading", { name: "空间回收站" })).toBeTruthy();
    expect(await screen.findByText("MoonBox 运营空间")).toBeTruthy();
    expect(screen.getAllByText("空间生命周期结束").length).toBeGreaterThan(0);
    expect(fetchSpy.mock.calls.some(([url]) => String(url).includes("/api/v1/admin/spaces?") && String(url).includes("status=RECYCLE"))).toBe(true);
  });

  it("shows compact empty text when a space has no regular members", async () => {
    vi.restoreAllMocks();
    mockSpaceApi({ emptyMembers: true });
    window.confirm = vi.fn();
    render(<AdminSpaceManagementPage session={session} onLogout={() => undefined} />);

    fireEvent.click(await screen.findByText("MoonBox 运营空间"));
    fireEvent.click(screen.getByRole("button", { name: "成员" }));

    expect(await screen.findByText("暂无成员，负责人不在成员列表。")).toBeTruthy();
    expect(screen.queryByText("暂无普通成员；负责人不在成员列表中展示，请通过详情头变更负责人。")).toBeNull();
  });

  it("requests normalized auth avatar urls for detail owner and members", async () => {
    vi.restoreAllMocks();
    const fetchSpy = mockSpaceApi({ normalizedAvatarUrls: true });
    window.confirm = vi.fn();
    render(<AdminSpaceManagementPage session={session} onLogout={() => undefined} />);

    fireEvent.click(await screen.findByText("MoonBox 运营空间"));
    await waitFor(() => {
      expect(fetchSpy.mock.calls.some(([url]) => String(url).includes("/api/v1/auth/avatar/owner-legacy.webp"))).toBe(true);
    });

    fireEvent.click(screen.getByRole("button", { name: "成员" }));
    await waitFor(() => {
      expect(fetchSpy.mock.calls.some(([url]) => String(url).includes("/api/v1/auth/avatar/member-legacy.webp"))).toBe(true);
    });
    expect(fetchSpy.mock.calls.some(([url]) => String(url).includes("/api/v1/admin/users/avatar/"))).toBe(false);
  });

  it("renders space tabs, real list data and stable detail cards", async () => {
    render(<AdminSpaceManagementPage session={session} onLogout={() => undefined} />);

    expect(screen.getByTestId("admin-space-management-page")).toBeTruthy();
    expect(screen.getByRole("button", { name: "空间列表" })).toBeTruthy();
    expect(screen.queryByTestId("space-tab-detail")).toBeNull();
    expect(await screen.findByText("MoonBox 运营空间")).toBeTruthy();
    expect(screen.getByTestId("space-stats").textContent).toContain("空间总数");
    expect(screen.getByTestId("space-stats").textContent).toContain("正常运行");
    expect(screen.getByTestId("space-stats").textContent).toContain("已冻结");
    expect(screen.getByTestId("space-stats").textContent).toContain("资源预警");
    expect(screen.getByLabelText("空间分页")).toBeTruthy();
    expect(screen.getByLabelText("搜索空间")).toBeTruthy();
    expect(document.querySelector(".admin-space-table colgroup")).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "空间名称/编码" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "成员数" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "产品数" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "AI 用量" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "创建来源" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "更新时间" })).toBeTruthy();
    expect(screen.getByText("3 / 20")).toBeTruthy();
    const usage = screen.getByLabelText("AI 用量 86% 860,000 / 1,000,000");
    expect(usage.className).toContain("warn");
    expect(usage.querySelector(".admin-space-usage-bar i")).toBeTruthy();
    expect(screen.getByText("86%")).toBeTruthy();
    expect(screen.queryByText("86% · 预警")).toBeNull();
    expect(screen.getByText("后台创建").className).toBe("admin-source-tag");
    expect(screen.getByText("2026-08-12 10:00:00")).toBeTruthy();
    expect(screen.queryByText("MoonBox Platform")).toBeNull();
    const spaceName = screen.getByRole("button", { name: "MoonBox 运营空间" });
    expect(spaceName.className).toBe("admin-link-button");
    expect(screen.getByRole("columnheader", { name: "操作" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "查看" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "编辑" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "冻结" }).querySelector("svg")).toBeNull();
    expect(screen.getByText("更多")).toBeTruthy();
    expect(document.querySelector(".admin-space-row-actions")?.className).toContain("admin-operation-set");
    expect(document.querySelector(".admin-space-status")?.className).toContain("active");
    expect(document.querySelector(".admin-space-status svg")).toBeTruthy();
    const content = screen.getByRole("heading", { name: "空间管理" }).closest(".admin-content");
    const orderedNodes = Array.from(content?.children || []);
    expect(orderedNodes.indexOf(screen.getByRole("heading", { name: "空间管理" }).closest(".admin-page-head") as Element)).toBeLessThan(
      orderedNodes.indexOf(screen.getByTestId("admin-space-tabs")),
    );

    fireEvent.click(screen.getByText("MoonBox 运营空间"));
    expect(screen.getByTestId("space-detail-page")).toBeTruthy();
    expect(screen.queryByTestId("admin-space-tabs")).toBeNull();
    expect(document.querySelector(".admin-sidebar-user")).toBeTruthy();
    expect(document.querySelector(".admin-user-trigger")).toBeTruthy();
    expect(screen.getByLabelText("空间详情路径").textContent).toContain("空间管理/空间列表/MoonBox 运营空间");
    expect(screen.getByText("moonbox-ops · 后台创建")).toBeTruthy();
    expect(screen.getByRole("button", { name: "变更" })).toBeTruthy();
    const detailOwner = document.querySelector(".admin-space-detail-owner");
    expect(detailOwner?.textContent).toBe("空间负责人变更");
    await waitFor(() => expect(detailOwner?.querySelector("img")?.getAttribute("alt")).toBe("空间负责人头像"));
    expect(screen.getByRole("button", { name: "续期" })).toBeTruthy();
    expect(document.querySelector(".admin-space-detail-title-row h1")?.textContent).toBe("MoonBox 运营空间");
    expect(document.querySelector(".admin-space-detail-title-row .admin-space-status")).toBeTruthy();
    expect(document.querySelector(".admin-space-action-btn.danger")?.textContent).toBe("删除");
    expect(document.querySelector(".admin-space-detail-field-grid")).toBeTruthy();
    expect(screen.getByTestId("space-detail-base")).toBeTruthy();
    expect(Array.from(screen.getByTestId("space-detail-base").querySelectorAll("dt")).map((item) => item.textContent)).toEqual(["空间名称", "唯一标识", "创建来源", "创建时间", "有效期"]);
    expect(screen.getByTestId("space-detail-quota")).toBeTruthy();
    expect(screen.getByTestId("space-detail-recent")).toBeTruthy();
    await waitFor(() => expect(screen.getByTestId("space-detail-recent").querySelectorAll(".admin-space-timeline > div")).toHaveLength(6));
    expect(screen.queryByText("空间与产品永久一对一绑定；修改空间名称将同步修改产品名称。")).toBeNull();
    expect(screen.getByRole("button", { name: "概览" }).className).toContain("active");

    fireEvent.click(screen.getByRole("button", { name: "成员" }));
    expect(screen.getByTestId("space-detail-members")).toBeTruthy();
    expect(screen.queryByText("空间成员（同时为产品成员）")).toBeNull();
    expect(await screen.findByRole("columnheader", { name: "用户" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "角色" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "加入时间" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "状态" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "操作" })).toBeTruthy();
    expect(screen.getByText("后台负责人")).toBeTruthy();
    await waitFor(() => expect(screen.getByTestId("space-detail-members").querySelector(".admin-space-member-user img")?.getAttribute("alt")).toBe("后台负责人头像"));
    expect(screen.getByText("管理员")).toBeTruthy();
    expect(screen.getByText("2026-08-12 12:00:00")).toBeTruthy();
    expect(screen.getByTestId("space-detail-members").textContent).not.toContain("空间负责人");
    expect(screen.getByRole("button", { name: "添加成员" })).toBeTruthy();
    expect(screen.getAllByRole("button", { name: "编辑" }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole("button", { name: "移除" }).some((button) => button.closest("[data-testid='space-detail-members']"))).toBe(true);
    expect(screen.queryByText("成员占位")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "产品" }));
    const productSection = screen.getByTestId("space-detail-product");
    expect(productSection).toBeTruthy();
    expect(screen.getByText("绑定关系不可解除或迁移，产品名称始终与空间名称一致。")).toBeTruthy();
    expect(productSection.querySelector(".admin-space-product-list")).toBeTruthy();
    expect(productSection.querySelectorAll(".admin-space-product-card")).toHaveLength(1);
    expect(productSection.querySelector(".admin-space-detail-field-grid")).toBeTruthy();
    expect(productSection.querySelector("h2")).toBeNull();
    expect(productSection.textContent).not.toContain("绑定产品");
    expect(screen.getByText("产品 ID")).toBeTruthy();
    expect(screen.getByText("moonbox-platform")).toBeTruthy();
    expect(screen.getByText("研发状态")).toBeTruthy();
    expect(screen.getByText("进行中")).toBeTruthy();
    expect(productSection.textContent).not.toContain("产品数");
    expect(screen.queryByRole("button", { name: /解绑|迁移|新增产品/ })).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "配额与用量" }));
    expect(screen.getByTestId("space-detail-quota-section")).toBeTruthy();
    expect(screen.getByText("资源配额详情")).toBeTruthy();
    expect(screen.getByRole("button", { name: "调整配额" })).toBeTruthy();

    const fetchSpy = vi.mocked(window.fetch);
    fireEvent.click(screen.getByRole("button", { name: "操作记录" }));
    expect(screen.getByTestId("space-detail-logs")).toBeTruthy();
    await screen.findByText("审批通过创建空间");
    expect(screen.getByTestId("space-detail-logs").querySelector("h2")).toBeNull();
    expect(screen.getByRole("columnheader", { name: "时间" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "操作人" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "操作动作" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "变更摘要" })).toBeTruthy();
    expect(screen.queryByRole("columnheader", { name: "来源" })).toBeNull();
    expect(screen.getByTestId("space-detail-logs").querySelector(".admin-pagination")?.textContent).toContain("7");
    expect(screen.getAllByText("平台超级管理员")[0]).toBeTruthy();
    expect(screen.getAllByText("成功")[0].className).toContain("admin-space-audit-tag");
    expect(screen.getByText(/状态：待审批 → 无|来源：无 → 申请审批/)).toBeTruthy();
    fireEvent.click(screen.getAllByRole("button", { name: "查看" })[0]);
    expect(screen.getByTestId("space-audit-drawer")).toBeTruthy();
    expect(screen.getByText("请求 ID")).toBeTruthy();
    expect(screen.getByText("资料完整准予开通")).toBeTruthy();
    expect(screen.getAllByText("申请审批")[0].className).toContain("admin-space-audit-tag");
    const auditJsonBlocks = screen.getByTestId("space-audit-drawer").querySelectorAll(".admin-space-audit-json");
    expect(auditJsonBlocks).toHaveLength(2);
    expect(auditJsonBlocks[0].textContent).toContain('\n  "status": "待审批"');
    expect(auditJsonBlocks[1].textContent).toContain('\n  "source": "申请审批"');
    fireEvent.click(screen.getByRole("button", { name: "关闭操作记录明细" }));
    expect(screen.queryByTestId("space-audit-drawer")).toBeNull();

    fireEvent.click(screen.getAllByRole("button", { name: "查看" })[1]);
    const emptyDrawer = screen.getByTestId("space-audit-drawer");
    expect(emptyDrawer.querySelectorAll(".admin-space-audit-empty")).toHaveLength(1);
    expect(emptyDrawer.querySelector(".admin-space-audit-empty")?.textContent).toBe("无");
    expect(emptyDrawer.querySelectorAll(".admin-space-audit-json")).toHaveLength(1);
    fireEvent.click(screen.getByRole("button", { name: "关闭操作记录明细" }));

    expect(screen.queryByText("操作记录列表暂未接入真实审计数据源；高风险操作仍会写入服务端审计，完整记录请以后续审计接口为准。")).toBeNull();
    expect(screen.queryByText("创建空间与同名产品")).toBeNull();
    expect(fetchSpy.mock.calls.some(([url]) => String(url).includes("/api/v1/admin/spaces/space_one/audit-events?page=1&page_size=10"))).toBe(true);
  });

  it("renders the row more menu as a body-level popover and closes it from keyboard or outside click", async () => {
    render(<AdminSpaceManagementPage session={session} onLogout={() => undefined} />);

    await screen.findByText("MoonBox 运营空间");
    Object.defineProperty(window, "innerWidth", { configurable: true, value: 1440 });
    const firstMoreButton = screen.getAllByText("更多")[0] as HTMLButtonElement;
    vi.spyOn(firstMoreButton, "getBoundingClientRect").mockReturnValue({
      x: 1000,
      y: 320,
      width: 56,
      height: 28,
      top: 320,
      right: 1056,
      bottom: 348,
      left: 1000,
      toJSON: () => ({}),
    } as DOMRect);
    openMoreMenu();
    const menu = screen.getByRole("menu");
    expect(menu.className).toContain("admin-space-more-menu");
    expect(menu.className).toContain("dark");
    expect(menu.parentElement).toBe(document.body);
    expect(menu.getAttribute("style")).toContain("left: 1000px");
    expect(menu.getAttribute("style")).toContain("top: 354px");
    expect(screen.getByRole("menuitem", { name: "配额" })).toBeTruthy();
    fireEvent.keyDown(window, { key: "Escape" });
    expect(screen.queryByRole("menu")).toBeNull();

    openMoreMenu();
    expect(screen.getByRole("menu")).toBeTruthy();
    fireEvent.click(document.body);
    expect(screen.queryByRole("menu")).toBeNull();

    vi.spyOn(firstMoreButton, "getBoundingClientRect").mockReturnValue({
      x: 1000,
      y: 720,
      width: 56,
      height: 28,
      top: 720,
      right: 1056,
      bottom: 748,
      left: 1000,
      toJSON: () => ({}),
    } as DOMRect);
    Object.defineProperty(window, "innerHeight", { configurable: true, value: 760 });
    openMoreMenu();
    expect(screen.getByRole("menu").getAttribute("data-placement")).toBe("bottom");
    expect(screen.getByRole("menu").getAttribute("style")).toContain("top: 754px");
  });

  it("keeps the admin sidebar aligned with user management interactions", async () => {
    const onLogout = vi.fn();
    render(<AdminSpaceManagementPage session={session} onLogout={onLogout} />);

    expect(screen.getByRole("button", { name: "收起侧边栏" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "空间管理" }).className).toContain("active");
    fireEvent.click(screen.getByRole("button", { name: "收起侧边栏" }));
    expect(screen.getByRole("button", { name: "展开侧边栏" })).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: /平台超级管理员/ }));
    expect(screen.getByRole("menuitem", { name: "个人资料" })).toBeTruthy();
    expect(screen.getByRole("menuitem", { name: "修改密码" })).toBeTruthy();
    expect(screen.getByRole("menuitem", { name: "返回前台" })).toBeTruthy();
    expect(screen.getByRole("switch", { name: "切换明暗主题" })).toBeTruthy();
    expect(screen.getByRole("menuitem", { name: "退出登录" })).toBeTruthy();

    fireEvent.click(screen.getByRole("switch", { name: "切换明暗主题" }));
    expect(screen.getByRole("status").textContent).toContain("已切换为亮色主题");

    fireEvent.click(screen.getByRole("menuitem", { name: "个人资料" }));
    expect(screen.getByRole("heading", { name: "个人资料" })).toBeTruthy();
  });

  it("uses design-system modal instead of native confirm for high-risk actions", async () => {
    const fetchSpy = vi.mocked(window.fetch);
    render(<AdminSpaceManagementPage session={session} onLogout={() => undefined} />);

    await screen.findByText("MoonBox 运营空间");
    fireEvent.click(screen.getByRole("button", { name: /冻结/ }));
    expect(screen.getByTestId("space-action-modal")).toBeTruthy();
    expect(window.confirm).not.toHaveBeenCalled();
    expect(document.querySelector('label.required[for="admin-space-action-reason"]')?.textContent).toBe("操作原因");
    expect(document.querySelector('label.required[for="admin-space-action-reason"]')?.className).toContain("admin-space-reason-label");

    fireEvent.click(screen.getByRole("button", { name: "确认" }));
    expect(screen.getByText("操作原因至少需要 4 个字。").className).toBe("admin-form-error");
    expect(fetchSpy.mock.calls.some(([url]) => String(url).includes("/api/v1/admin/spaces/space_one/freeze"))).toBe(false);

    fireEvent.change(screen.getByLabelText("操作原因"), { target: { value: "短" } });
    expect(screen.getByText("操作原因至少需要 4 个字。").className).toBe("admin-form-error");
    expect(screen.getByText("请填写至少 4 个字，便于审计追踪。")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "确认" }));
    expect(fetchSpy.mock.calls.some(([url]) => String(url).includes("/api/v1/admin/spaces/space_one/freeze"))).toBe(false);

    fireEvent.change(screen.getByLabelText("操作原因"), { target: { value: "安全巡检冻结" } });
    fireEvent.click(screen.getByRole("button", { name: "确认" }));
    await waitFor(() => expect(window.fetch).toHaveBeenCalledWith(expect.stringContaining("/api/v1/admin/spaces/space_one/freeze"), expect.objectContaining({ method: "POST" })));
  });

  it("uses normal user options for create and transfer owner forms", async () => {
    const fetchSpy = vi.mocked(window.fetch);
    render(<AdminSpaceManagementPage session={session} onLogout={() => undefined} />);

    await screen.findByText("MoonBox 运营空间");
    await waitFor(() => {
      expect(fetchSpy.mock.calls.some(([url]) => String(url).includes("/api/v1/admin/users?") && String(url).includes("status=正常"))).toBe(true);
    });

    fireEvent.click(screen.getByRole("button", { name: /新增空间/ }));
    expect(screen.getByLabelText(/负责人/)).toBeTruthy();
    expect(screen.queryByText("负责人候选来自用户管理，仅显示状态正常用户。")).toBeNull();
    expect(screen.queryByText("负责人 ID")).toBeNull();
    expect(screen.queryByText("产品 ID")).toBeNull();
    expect(screen.queryByText("产品名称")).toBeNull();
    expect(screen.getByPlaceholderText("请输入空间名称")).toBeTruthy();
    expect(screen.getByText("一空间仅绑定一款产品，空间名称即产品名称，2-80个字符")).toBeTruthy();
    expect(screen.getByPlaceholderText("请输入空间编码")).toBeTruthy();
    expect(screen.getByText("系统唯一，3-48 位；仅允许小写字母/数字/短横线，且必须以字母开头；创建后不可修改。")).toBeTruthy();
    openModalAdminSelect("负责人");
    expect(screen.getByRole("option", { name: "请选择" })).toBeTruthy();
    expect(screen.getByRole("option", { name: "空间负责人" })).toBeTruthy();
    expect(screen.queryByRole("option", { name: /前台用户/ })).toBeNull();
    fireEvent.click(screen.getByRole("option", { name: "空间负责人" }));
    const modal = screen.getByTestId("space-action-modal");
    expect(modal.querySelector("header svg")).toBeNull();
    expect(modal.querySelector(".admin-space-field-label b")?.textContent).toBe("*");
    const labels = Array.from(modal.querySelectorAll(".admin-form-grid > label")).map((label) => label.textContent || "");
    expect(labels[0]).toContain("空间名称");
    expect(labels[1]).toContain("空间编码");
    expect(labels[2]).toContain("负责人");
    expect(labels[3]).toContain("成员上限");
    expect(labels[4]).toContain("存储空间");
    expect(labels[5]).toContain("AI Tokens");
    expect(labels[6]).toContain("有效期类型");
    expect(labels[7]).toContain("到期时间");
    expect(labels[8]).toContain("描述");
    expect(modal.querySelector(".admin-form-field-full")?.textContent).toContain("描述");
    const expiryInput = screen.getByLabelText("到期时间") as HTMLInputElement;
    expect(expiryInput.type).toBe("text");
    expect(expiryInput.value).toMatch(/\d{4}-\d{2}-\d{2} 23:59:59/);
    fireEvent.focus(expiryInput);
    expect(screen.getByRole("dialog", { name: "到期时间选择器" })).toBeTruthy();
    expect(screen.getByLabelText("时间选择")).toBeTruthy();
    fireEvent.change(screen.getByLabelText("时"), { target: { value: "22" } });
    expect(expiryInput.value).toMatch(/\d{4}-\d{2}-\d{2} 22:59:59/);

    fireEvent.change(screen.getByLabelText(/空间名称/), { target: { value: "Project Alpha" } });
    fireEvent.change(screen.getByLabelText(/空间编码/), { target: { value: "project-alpha" } });
    fireEvent.click(screen.getByRole("button", { name: "确认" }));
    await waitFor(() => {
      const createCall = fetchSpy.mock.calls.find(([url, init]) => String(url).includes("/api/v1/admin/spaces") && init?.method === "POST");
      expect(createCall).toBeTruthy();
      const body = JSON.parse(String(createCall?.[1]?.body));
      expect(body.owner_id).toBe("user_owner");
      expect(body.product_id).toBe("project-alpha");
      expect(body.product_name).toBe("Project Alpha");
    });

    openMoreMenu();
    fireEvent.click(screen.getByRole("menuitem", { name: "负责人" }));
    expect(screen.getByLabelText(/新负责人/)).toBeTruthy();
    expect(screen.queryByText("新负责人 ID")).toBeNull();
    expect(screen.queryByText("负责人候选来自用户管理，仅显示状态正常用户。")).toBeNull();
  });

  it("keeps owner transfer outside the edit form", async () => {
    render(<AdminSpaceManagementPage session={session} onLogout={() => undefined} />);

    await screen.findByText("MoonBox 运营空间");
    fireEvent.click(screen.getByRole("button", { name: "编辑" }));

    expect(screen.getByLabelText(/空间名称/)).toBeTruthy();
    expect(screen.queryByLabelText(/负责人/)).toBeNull();
    expect(screen.queryByLabelText(/成员上限/)).toBeNull();
    expect(screen.queryByLabelText(/存储空间/)).toBeNull();
    expect(screen.queryByLabelText(/AI Tokens/)).toBeNull();
    expect(screen.queryByText("负责人 ID")).toBeNull();
    expect(screen.getByTestId("space-action-modal").querySelector(".admin-form-field-full")?.textContent).toContain("描述");
  });

  it("keeps detail actions functional and refreshes the current detail state", async () => {
    const fetchSpy = vi.mocked(window.fetch);
    render(<AdminSpaceManagementPage session={session} onLogout={() => undefined} />);

    await screen.findByText("MoonBox 运营空间");
    fireEvent.click(screen.getByText("MoonBox 运营空间"));
    expect(screen.getByTestId("space-detail-page")).toBeTruthy();

    fireEvent.click(screen.getByTestId("space-detail-base").querySelector("button") as HTMLButtonElement);
    expect(screen.getByRole("heading", { name: "编辑空间" })).toBeTruthy();
    fireEvent.change(screen.getByLabelText(/空间名称/), { target: { value: "MoonBox 运营空间新版" } });
    fireEvent.change(screen.getByLabelText("操作原因"), { target: { value: "验收编辑详情" } });
    fireEvent.click(screen.getByRole("button", { name: "确认" }));
    await waitFor(() => expect(screen.getByRole("heading", { name: "MoonBox 运营空间新版" })).toBeTruthy());
    expect(fetchSpy.mock.calls.some(([url, init]) => String(url).includes("/api/v1/admin/spaces/space_one") && init?.method === "PUT")).toBe(true);

    fireEvent.click(screen.getByTestId("space-detail-quota").querySelector("button") as HTMLButtonElement);
    expect(screen.getByRole("heading", { name: "调整配额" })).toBeTruthy();
    fireEvent.change(screen.getByLabelText(/成员上限/), { target: { value: "30" } });
    fireEvent.change(screen.getByLabelText(/存储空间/), { target: { value: "200" } });
    fireEvent.change(screen.getByLabelText(/AI Tokens/), { target: { value: "2000000" } });
    fireEvent.change(screen.getByLabelText("操作原因"), { target: { value: "业务增长调整" } });
    fireEvent.click(screen.getByRole("button", { name: "确认" }));
    await waitFor(() => expect(screen.getByText("3 / 30")).toBeTruthy());
    expect(fetchSpy.mock.calls.some(([url, init]) => String(url).includes("/api/v1/admin/spaces/space_one/quota") && init?.method === "POST")).toBe(true);

    fireEvent.click(screen.getByRole("button", { name: "配额与用量" }));
    fireEvent.click(screen.getByRole("button", { name: "调整配额" }));
    expect(screen.getByRole("heading", { name: "调整配额" })).toBeTruthy();
    fireEvent.change(screen.getByLabelText(/成员上限/), { target: { value: "35" } });
    fireEvent.change(screen.getByLabelText("操作原因"), { target: { value: "详情分区调整" } });
    fireEvent.click(screen.getByRole("button", { name: "确认" }));
    await waitFor(() => expect(screen.getByText("3 / 35")).toBeTruthy());

    fireEvent.click(screen.getByRole("button", { name: "续期" }));
    expect(screen.getByRole("heading", { name: "续期空间" })).toBeTruthy();
    chooseAdminSelect("有效期类型", "长期有效");
    fireEvent.change(screen.getByLabelText("操作原因"), { target: { value: "客户续约长期" } });
    fireEvent.click(screen.getByRole("button", { name: "确认" }));
    fireEvent.click(screen.getByRole("button", { name: "概览" }));
    await waitFor(() => expect(screen.getByText("长期有效")).toBeTruthy());
    expect(fetchSpy.mock.calls.some(([url, init]) => String(url).includes("/api/v1/admin/spaces/space_one/renew") && init?.method === "POST")).toBe(true);

    fireEvent.click(screen.getByRole("button", { name: "成员" }));
    expect(await screen.findByText("后台负责人")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "添加成员" }));
    expect(screen.getByRole("heading", { name: "添加成员" })).toBeTruthy();
    expect(screen.getByTestId("space-action-modal").querySelector(".admin-form-stack")).toBeTruthy();
    openModalAdminSelect("用户");
    expect(document.body.querySelector(".admin-select-menu-portal")).toBeTruthy();
    expect(screen.getByTestId("space-action-modal").querySelector(".admin-select-menu-portal")).toBeNull();
    fireEvent.click(screen.getByRole("option", { name: "编辑候选" }));
    openModalAdminSelect("成员角色");
    expect(document.body.querySelector(".admin-select-menu-portal")).toBeTruthy();
    expect(screen.getByTestId("space-action-modal").querySelector(".admin-select-menu-portal")).toBeNull();
    fireEvent.click(screen.getByRole("option", { name: "编辑者" }));
    fireEvent.click(screen.getByRole("button", { name: "确认" }));
    await waitFor(() => expect(fetchSpy.mock.calls.some(([url, init]) => String(url).includes("/api/v1/admin/spaces/space_one/members") && init?.method === "POST")).toBe(true));

    const memberEdit = screen.getAllByRole("button", { name: "编辑" }).find((button) => button.closest("[data-testid='space-detail-members']")) as HTMLButtonElement;
    fireEvent.click(memberEdit);
    expect(screen.getByRole("heading", { name: "编辑成员角色" })).toBeTruthy();
    expect(screen.getByTestId("space-action-modal").querySelector(".admin-form-stack")).toBeTruthy();
    openModalAdminSelect("成员角色");
    expect(document.body.querySelector(".admin-select-menu-portal")).toBeTruthy();
    expect(screen.getByTestId("space-action-modal").querySelector(".admin-select-menu-portal")).toBeNull();
    fireEvent.click(screen.getByRole("option", { name: "查看者" }));
    fireEvent.click(screen.getByRole("button", { name: "确认" }));
    await waitFor(() => expect(fetchSpy.mock.calls.some(([url, init]) => String(url).includes("/api/v1/admin/spaces/space_one/members/space_member_admin") && init?.method === "PUT")).toBe(true));

    const memberRemove = screen.getAllByRole("button", { name: "移除" }).find((button) => button.closest("[data-testid='space-detail-members']")) as HTMLButtonElement;
    fireEvent.click(memberRemove);
    expect(screen.getByRole("heading", { name: "移除成员" })).toBeTruthy();
    fireEvent.change(screen.getByLabelText("操作原因"), { target: { value: "成员离开项目" } });
    fireEvent.click(screen.getByRole("button", { name: "确认" }));
    await waitFor(() => expect(fetchSpy.mock.calls.some(([url, init]) => String(url).includes("/api/v1/admin/spaces/space_one/members/space_member_admin") && init?.method === "DELETE")).toBe(true));

    fireEvent.click(screen.getByRole("button", { name: "变更" }));
    expect(screen.getByRole("heading", { name: "移交负责人" })).toBeTruthy();
    chooseAdminSelect("新负责人", "后台负责人");
    fireEvent.change(screen.getByLabelText("操作原因"), { target: { value: "组织职责调整" } });
    fireEvent.click(screen.getByRole("button", { name: "确认" }));
    await waitFor(() => expect(document.querySelector(".admin-space-detail-owner")?.textContent).toBe("后台负责人变更"));
    expect(fetchSpy.mock.calls.some(([url, init]) => String(url).includes("/api/v1/admin/spaces/space_one/transfer-owner") && init?.method === "POST")).toBe(true);

    fireEvent.click(screen.getByRole("button", { name: "冻结" }));
    expect(screen.getByRole("heading", { name: "冻结空间" })).toBeTruthy();
    fireEvent.change(screen.getByLabelText("操作原因"), { target: { value: "安全巡检冻结" } });
    fireEvent.click(screen.getByRole("button", { name: "确认" }));
    await waitFor(() => expect(document.querySelector(".admin-space-detail-title-row .admin-space-status")?.textContent).toContain("已冻结"));
    expect(fetchSpy.mock.calls.some(([url, init]) => String(url).includes("/api/v1/admin/spaces/space_one/freeze") && init?.method === "POST")).toBe(true);

    fireEvent.click(screen.getByRole("button", { name: "删除" }));
    expect(screen.getByRole("heading", { name: "删除空间" })).toBeTruthy();
    fireEvent.change(screen.getByLabelText("操作原因"), { target: { value: "空间生命周期结束" } });
    fireEvent.click(screen.getByRole("button", { name: "确认" }));
    await waitFor(() => expect(screen.queryByTestId("space-detail-page")).toBeNull());
    expect(screen.getByTestId("admin-space-tabs")).toBeTruthy();
    expect(fetchSpy.mock.calls.some(([url, init]) => String(url).includes("/api/v1/admin/spaces/space_one") && init?.method === "DELETE")).toBe(true);
  });

  it("renders application approval workflow from API data", async () => {
    render(<AdminSpaceManagementPage session={session} onLogout={() => undefined} />);

    fireEvent.click(screen.getByTestId("space-tab-approvals"));
    expect(await screen.findByText("新项目空间")).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "空间名称/编码" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "申请人" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "负责人" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "资源申请" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "有效期" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "申请时间" })).toBeTruthy();
    expect(screen.getByLabelText("申请审批分页")).toBeTruthy();
    const applicationRow = screen.getByTestId("space-application-row");
    expect(applicationRow.querySelector(".admin-space-application-name")?.textContent).toBe("新项目空间");
    expect(applicationRow.textContent).toContain("new-project");
    expect(applicationRow.textContent).not.toContain("MoonBox Platform");
    expect(applicationRow.textContent).toContain("12 人");
    expect(applicationRow.textContent).toContain("80 GB");
    expect(applicationRow.textContent).toContain("90万 Tokens");
    expect(applicationRow.textContent).not.toContain("Â·");
    expect(applicationRow.querySelectorAll(".admin-space-resource-item")).toHaveLength(3);
    expect(applicationRow.textContent).toContain("长期有效");
    expect(applicationRow.textContent).toContain("2026-08-12 10:00:00");
    expect(document.querySelector(".admin-space-application-table colgroup")).toBeTruthy();
    expect(document.querySelector(".admin-space-application-actions")?.className).toContain("admin-operation-set");
    fireEvent.click(screen.getByRole("button", { name: /通过/ }));
    expect(screen.getByTestId("space-action-modal")).toBeTruthy();
    fireEvent.change(screen.getByPlaceholderText("请输入不少于 4 个字符的原因"), { target: { value: "资料完整准予开通" } });
    fireEvent.click(screen.getByRole("button", { name: "确认" }));
    await waitFor(() => expect(window.fetch).toHaveBeenCalledWith(expect.stringContaining("/api/v1/admin/space-applications/space_app_1/approve"), expect.objectContaining({ method: "POST" })));
  });
});

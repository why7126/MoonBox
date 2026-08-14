import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
// @ts-expect-error Vitest runs this assertion in Node, while the web tsconfig intentionally omits Node globals.
import { readFileSync } from "node:fs";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { RequirementCenterPage } from "./pages/catalog/RequirementCenterPage";

const contextFixture = {
  issues: [
    {
      id: "REQ-0012",
      type: "requirement",
      title: "MoonBox 前台需求中心",
      priority: "P1",
      owner: "产品团队",
      source: "review",
      stage: "ready-dev",
      documents: ["proposal.md", "design.md", "tasks.md", "trace.md"],
      updated_at: "09:13",
      sprint_id: "sprint-002",
      task_progress: [0, 36],
    },
    {
      id: "REQ-0013",
      type: "requirement",
      title: "需求中心真实数据接入",
      priority: "P1",
      owner: "产品团队",
      source: "review",
      stage: "ready-dev",
      documents: ["proposal.md", "tasks.md", "trace.md"],
      updated_at: "20:04",
      sprint_id: "sprint-002",
      task_progress: [0, 36],
    },
    {
      id: "REQ-0011",
      type: "requirement",
      title: "后台管理用户菜单栏个人资料",
      priority: "P1",
      owner: "前端体验",
      source: "review",
      stage: "sprint-planning",
      documents: ["sprint.md", "trace.md"],
      updated_at: "08:48",
      sprint_id: "sprint-002",
    },
    {
      id: "BUG-0001",
      type: "bug",
      title: "管理后台登录代理与 SPA fallback",
      priority: "P1",
      owner: "平台工程",
      source: "review",
      stage: "acceptance",
      documents: ["acceptance.md", "trace.md"],
      updated_at: "08:44",
      sprint_id: "sprint-002",
      test_progress: [1, 3],
      manual_acceptance_count: 1,
    },
    {
      id: "BUG-0002",
      type: "bug",
      title: "首页前台登录入口误跳后台登录页",
      priority: "P1",
      owner: "平台工程",
      source: "review",
      stage: "review-ready",
      documents: ["bug.md", "trace.md"],
      updated_at: "20:07",
      blocked: "缺少 acceptance.md",
    },
    {
      id: "REQ-0006",
      type: "requirement",
      title: "品牌资产管理能力",
      priority: "P1",
      owner: "平台工程",
      source: "archive",
      stage: "done",
      documents: ["archive.md", "trace.md"],
      updated_at: "07:58",
      sprint_id: "sprint-001",
    },
  ],
  workspaces: [
    {
      organization_name: "MoonBox Lab",
      workspace_id: "moonbox-platform",
      name: "Platform Operations",
      slug: "platform-ops",
      description: "需求、缺陷、迭代和 OpenSpec 的主工作空间",
      timezone: "Asia/Shanghai",
      member_count: 12,
      role: "拥有者",
    },
    {
      organization_name: "MoonBox Lab",
      workspace_id: "moonbox-growth",
      name: "Growth Studio",
      slug: "growth-studio",
      description: "产品手册、发布公告与增长实验",
      timezone: "Asia/Shanghai",
      member_count: 5,
      role: "编辑者",
    },
  ],
  current_user: {
    name: "许同学",
    avatar_initial: "许",
    can_access_admin: true,
    permissions: ["requirement:read", "admin:access"],
  },
  selected_workspace_id: "moonbox-platform",
  stats: {
    total: 6,
    requirements: 4,
    bugs: 2,
    blocked: 1,
    drift: 0,
  },
};

function seedRequirementSession() {
  window.localStorage.setItem(
    "moonbox.session",
    JSON.stringify({
      username: "founder",
      started_at: "2026-08-11T00:00:00.000Z",
    }),
  );
}

function seedFrontendTokenSession() {
  window.localStorage.setItem(
    "moonbox.session",
    JSON.stringify({
      username: "frontuser",
      started_at: "2026-08-11T00:00:00.000Z",
      access_token: "front-token",
      expires_at: "2026-08-11 00:00:00",
      user: {
        id: "front-user",
        username: "frontuser",
        nickname: "前台用户",
        role: "前台用户",
        status: "正常",
        is_system_superadmin: false,
      },
    }),
  );
}

function seedAdminSession() {
  window.localStorage.setItem(
    "moonbox.session",
    JSON.stringify({
      access_token: "admin-token",
      expires_at: "2026-08-11 00:00:00",
      user: {
        id: "user_superadmin",
        username: "superadmin",
        role: "后台管理员",
        status: "正常",
        is_system_superadmin: true,
      },
    }),
  );
}

beforeEach(() => {
  window.history.replaceState(null, "", "/requirements");
  window.localStorage.clear();
  seedRequirementSession();
  vi.stubGlobal("scrollTo", vi.fn());
  vi.stubGlobal(
    "fetch",
    vi.fn(() =>
      Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: contextFixture }),
      }),
    ),
  );
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  window.localStorage.clear();
  window.history.replaceState(null, "", "/");
});

describe("RequirementCenterPage", () => {
  it("is routed from the frontend app and renders the 9-stage board", async () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "需求研发流转看板" })).toBeTruthy();
    expect(screen.getByAltText("MoonBox 产品图标")).toBeTruthy();
    expect(screen.getByText("AI原生软件工厂")).toBeTruthy();
    expect(screen.getByText("v0.1.0")).toBeTruthy();
    expect(screen.getByText("WORKSPACE")).toBeTruthy();
    expect(screen.getByText("CAPABILITIES")).toBeTruthy();
    ["研发总览", "Chat 工作台", "需求中心", "Spec", "任务中心", "Skill Center", "Agent Center", "知识中心"].forEach((item) => {
      expect(screen.getByRole("button", { name: item })).toBeTruthy();
    });
    expect(screen.getByRole("button", { name: "需求中心" }).getAttribute("aria-current")).toBe("page");
    ["采集池", "规划中", "待评审", "已通过", "迭代规划", "待开发", "研发中", "验收中", "已完成"].forEach((stage) => {
      expect(screen.getByRole("heading", { name: stage })).toBeTruthy();
    });
    expect(screen.queryByText("按住 Shift 横向滚动 · 共 9 个阶段")).toBeNull();
    expect(screen.getByText("Capture / req-capture / bug-capture")).toBeTruthy();
    expect(screen.getByText("req-generate / bug-generate")).toBeTruthy();
    expect(document.querySelectorAll("[data-stage]").length).toBe(9);
    expect(await screen.findByText("REQ-0012")).toBeTruthy();
    expect(document.querySelector('[aria-label="待开发 2 个对象"]')).toBeTruthy();
    expect(screen.getByText("需求中心真实数据接入")).toBeTruthy();
    expect(screen.getByText("BUG-0001")).toBeTruthy();
    expect(screen.getAllByText("P1 · 产品团队").length).toBeGreaterThan(0);
    expect(document.querySelectorAll(".rc-card-meta span").length).toBeGreaterThan(0);
    document.querySelectorAll(".rc-card-meta").forEach((meta) => {
      expect(meta.querySelectorAll("span").length).toBe(1);
    });
  });

  it("keeps the sticky board header above cards while scrolling", () => {
    const source = readFileSync("src/styles/globals.css", "utf8");

    expect(source).toContain(".rc-column-head::before");
    expect(source).toContain("position: sticky;");
    expect(source).toContain("inset: -18px 0 0;");
    expect(source).toContain("background: var(--rc-panel-2);");
    expect(source).toContain("pointer-events: none;");
    expect(source).toContain("z-index: 8;");
  });

  it("bridges frontend theme tokens for the reused admin change-password modal", () => {
    const source = readFileSync("src/styles/globals.css", "utf8");

    expect(source).toContain(".requirement-center .admin-modal-backdrop");
    expect(source).toContain("--admin-panel-bg: var(--rc-panel);");
    expect(source).toContain("--admin-panel-strong-bg: var(--rc-panel-2);");
    expect(source).toContain("--admin-text: var(--rc-text);");
    expect(source).toContain("--admin-heading: var(--rc-heading);");
    expect(source).toContain("--admin-border-strong: var(--rc-menu-border);");
    expect(source).toContain("--admin-gold: var(--rc-accent);");
  });

  it("uses the frontend login before opening the requirement center route", () => {
    window.localStorage.clear();

    render(<App />);

    expect(window.location.pathname).toBe("/login");
    expect(screen.getByRole("form", { name: "MoonBox login" })).toBeTruthy();
    expect(screen.queryByRole("form", { name: "管理后台登录" })).toBeNull();
    expect(screen.queryByRole("heading", { name: "需求研发流转看板" })).toBeNull();
  });

  it("filters by type and searches by document, title and owner", async () => {
    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    fireEvent.click(screen.getByRole("button", { name: "Bug" }));
    expect(screen.queryByText("REQ-0012")).toBeNull();
    expect(screen.getByText("BUG-0001")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Bug" }).className).toContain("selected");
    expect(document.querySelectorAll("[data-stage]").length).toBe(9);
    expect(screen.queryByText("按住 Shift 横向滚动 · 共 9 个阶段")).toBeNull();
    expect(screen.getAllByText("00").length).toBeGreaterThan(0);

    fireEvent.click(screen.getByRole("button", { name: "全部" }));
    fireEvent.change(screen.getByLabelText("搜索治理对象"), { target: { value: "proposal.md" } });
    expect(screen.getByText("REQ-0012")).toBeTruthy();
    expect(screen.queryByText("BUG-0001")).toBeNull();

    fireEvent.change(screen.getByLabelText("搜索治理对象"), { target: { value: "平台工程" } });
    expect(screen.getByText("BUG-0001")).toBeTruthy();
    expect(screen.getByText("REQ-0006")).toBeTruthy();
  });

  it("keeps action gates for missing documents and acceptance archive entry", async () => {
    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    expect(screen.getByText(/缺失 acceptance.md/)).toBeTruthy();
    expect(screen.queryByRole("button", { name: "完成 / 归档 →" })).toBeNull();
    expect(screen.getByRole("button", { name: "生成 Opsx →" }).getAttribute("title")).toBe("/req-opsx");
    expect(screen.getAllByRole("button", { name: "开始开发 →" }).length).toBeGreaterThan(0);
  });

  it("supports sidebar collapse and user-menu theme switching without a standalone sidebar theme row", async () => {
    const { container } = render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    fireEvent.click(screen.getByRole("button", { name: "收起侧边栏" }));
    expect(screen.getByRole("button", { name: "展开侧边栏" })).toBeTruthy();
    expect(container.querySelector(".rc-sidebar.collapsed")).toBeTruthy();
    expect(screen.getByTitle("Chat 工作台")).toBeTruthy();
    expect(document.querySelector(".rc-sidebar.collapsed .rc-nav-label")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "展开侧边栏" }));
    fireEvent.click(screen.getByRole("button", { name: /许同学/ }));
    expect(screen.queryByText("MoonBox Lab / 拥有者")).toBeNull();
    expect(screen.getByRole("group", { name: "账号" })).toBeTruthy();
    expect(screen.getByRole("group", { name: "空间" })).toBeTruthy();
    expect(screen.getByRole("group", { name: "偏好" })).toBeTruthy();
    expect(screen.getByRole("group", { name: "会话" })).toBeTruthy();
    expect(screen.getByRole("menuitem", { name: "进入后台" })).toBeTruthy();
    const profileIcon = screen.getByRole("menuitem", { name: "个人资料" }).querySelector("svg")?.outerHTML;
    const passwordIcon = screen.getByRole("menuitem", { name: "修改密码" }).querySelector("svg")?.outerHTML;
    const adminIcon = screen.getByRole("menuitem", { name: "进入后台" }).querySelector("svg")?.outerHTML;
    expect(profileIcon).toBeTruthy();
    expect(passwordIcon).toBeTruthy();
    expect(adminIcon).toBeTruthy();
    expect(new Set([profileIcon, passwordIcon, adminIcon]).size).toBe(3);
    const switchButton = screen.getByRole("switch", { name: "切换明暗主题" });
    expect(document.querySelectorAll("#themeSwitch").length).toBe(1);
    expect(switchButton.querySelector(".rc-theme-toggle")).toBeTruthy();
    expect(switchButton.getAttribute("aria-checked")).toBe("false");
    fireEvent.click(switchButton);
    expect(switchButton.getAttribute("aria-checked")).toBe("true");
    expect(switchButton.querySelector(".rc-theme-toggle.on")).toBeTruthy();
    expect(container.querySelector(".requirement-center.theme-light")).toBeTruthy();
    expect(window.localStorage.getItem("moonbox.ui.preferences")).toContain("\"theme\":\"light\"");
    expect(screen.queryByText("Sidebar 底部主题")).toBeNull();
  });

  it("keeps the frontend profile nickname input readable in rc themes", () => {
    const source = readFileSync("src/styles/globals.css", "utf8");
    const inputBlock = source.match(/\.rc-profile-modal input\s*\{[^}]+\}/)?.[0] || "";

    expect(inputBlock).toContain("background: var(--rc-panel-2);");
    expect(inputBlock).toContain("color: var(--rc-heading);");
    expect(inputBlock).toContain("caret-color: var(--rc-accent);");
    expect(source).toContain(".rc-profile-modal input::placeholder");
    expect(source).toContain("color: var(--rc-muted);");
  });

  it("guards the admin entry by frontend user permission", () => {
    const source = readFileSync("src/pages/catalog/RequirementCenterPage.tsx", "utf8");

    expect(source).toContain("canAccessAdmin: boolean");
    expect(source).toContain("activeUser.canAccessAdmin &&");
    expect(source).not.toContain("const initialIssues");
    expect(source).not.toContain("const workspaces");
    expect(source).not.toContain("const currentUser");
  });

  it("opens space switcher on hover and stores the selected workspace", async () => {
    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    fireEvent.click(screen.getByRole("button", { name: /许同学/ }));
    fireEvent.mouseEnter(screen.getByRole("menuitem", { name: /切换空间/ }));
    expect(screen.getByRole("dialog", { name: "切换空间" })).toBeTruthy();
    expect(screen.queryByPlaceholderText("搜索空间")).toBeNull();
    expect(screen.queryByText("MoonBox Lab")).toBeNull();
    expect(screen.getByText("拥有者 · 12 人")).toBeTruthy();
    expect(document.querySelector(".rc-user-menu")).toBeTruthy();
    expect(document.querySelector(".rc-space-popover")).toBeTruthy();
    expect(document.querySelector(".rc-space-list button")).toBeTruthy();
    const source = readFileSync("src/styles/globals.css", "utf8");
    expect(source).toContain(".rc-space-list button:hover");
    expect(source).toContain(".rc-space-list button.selected::before");
    expect(source).toContain("background: transparent;");
    expect(source).toContain("border: 0;");
    expect(source).toContain("background: var(--rc-hover-bg);");
    expect(source).toContain("width: 2px;");
    expect(source).toContain("pointer-events: none;");
    expect(source).toContain(".rc-space-actions button");
    expect(source).toContain("border-color: var(--rc-border);");
    fireEvent.mouseEnter(screen.getByRole("menuitem", { name: "个人资料" }));
    expect(screen.queryByRole("dialog", { name: "切换空间" })).toBeNull();

    fireEvent.mouseEnter(screen.getByRole("menuitem", { name: /切换空间/ }));
    expect(screen.getByRole("dialog", { name: "切换空间" })).toBeTruthy();
    fireEvent.mouseDown(document.body);
    expect(screen.queryByRole("dialog", { name: "切换空间" })).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: /许同学/ }));
    fireEvent.mouseEnter(screen.getByRole("menuitem", { name: /切换空间/ }));
    fireEvent.click(screen.getByRole("button", { name: /Growth Studio/ }));

    expect(JSON.parse(window.localStorage.getItem("moonbox.workspace") || "{}").workspaceId).toBe("moonbox-growth");
    expect(screen.getByRole("status").textContent).toContain("已切换到 Growth Studio");
  });

  it("edits space settings, closes by escape and saves with a fixed toast", async () => {
    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    fireEvent.click(screen.getByRole("button", { name: /许同学/ }));
    expect(screen.getByRole("menuitem", { name: "进入后台" })).toBeTruthy();
    fireEvent.click(screen.getByRole("menuitem", { name: /设置空间/ }));
    expect(screen.getByRole("dialog", { name: "空间设置" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "常规" }).className).toContain("selected");
    expect(screen.getByRole("button", { name: "成员与权限" })).toBeTruthy();

    fireEvent.change(screen.getByLabelText("空间名称"), { target: { value: "Platform QA" } });
    fireEvent.click(screen.getByRole("button", { name: "保存更改" }));

    expect(screen.queryByRole("dialog", { name: "空间设置" })).toBeNull();
    expect(document.querySelector(".rc-toast")?.textContent).toContain("空间设置已保存");
    expect(JSON.parse(window.localStorage.getItem("moonbox.workspace") || "{}").name).toBe("Platform QA");
  });

  it("shows an error state and retries the context request", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: false, status: 503, json: () => Promise.resolve({}) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: () => Promise.resolve({ data: contextFixture }) });
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);

    expect((await screen.findByRole("alert")).textContent).toContain("需求中心数据暂时不可用");
    fireEvent.click(screen.getByRole("button", { name: "重试" }));
    expect(await screen.findByText("REQ-0013")).toBeTruthy();
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("refreshes the 9-stage board manually while keeping the current filters", async () => {
    const refreshedContext = {
      ...contextFixture,
      issues: [
        ...contextFixture.issues,
        {
          id: "REQ-0099",
          type: "requirement",
          title: "刷新后的需求",
          priority: "P1",
          owner: "产品团队",
          source: "review",
          stage: "capture",
          documents: ["capture.md", "trace.md"],
          updated_at: "23:20",
          sprint_id: "sprint-002",
        },
      ],
      stats: {
        ...contextFixture.stats,
        total: 7,
        requirements: 5,
      },
    };
    let resolveRefresh!: (value: Response) => void;
    const refreshPromise = new Promise<Response>((resolve) => {
      resolveRefresh = resolve;
    });
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, status: 200, json: () => Promise.resolve({ data: contextFixture }) })
      .mockReturnValueOnce(refreshPromise);
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    fireEvent.change(screen.getByLabelText("搜索治理对象"), { target: { value: "REQ" } });
    const refreshButton = screen.getByRole("button", { name: "刷新需求中心" }) as HTMLButtonElement;
    fireEvent.click(refreshButton);

    expect(refreshButton.disabled).toBe(true);
    expect(refreshButton.getAttribute("aria-busy")).toBe("true");
    expect((screen.getByLabelText("搜索治理对象") as HTMLInputElement).value).toBe("REQ");

    resolveRefresh({ ok: true, status: 200, json: () => Promise.resolve({ data: refreshedContext }) } as Response);

    expect(await screen.findByText("REQ-0099")).toBeTruthy();
    expect((screen.getByLabelText("搜索治理对象") as HTMLInputElement).value).toBe("REQ");
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("keeps the current board when a manual refresh fails", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, status: 200, json: () => Promise.resolve({ data: contextFixture }) })
      .mockRejectedValueOnce(new Error("network down"));
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    fireEvent.change(screen.getByLabelText("搜索治理对象"), { target: { value: "REQ-0012" } });
    fireEvent.click(screen.getByRole("button", { name: "刷新需求中心" }));

    expect(await screen.findByText("刷新失败，已保留当前看板")).toBeTruthy();
    expect(screen.getByText("REQ-0012")).toBeTruthy();
    expect(screen.queryByRole("alert")).toBeNull();
    expect((screen.getByLabelText("搜索治理对象") as HTMLInputElement).value).toBe("REQ-0012");
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("keeps the session user visible while the context request is pending", () => {
    const fetchMock = vi.fn(() => new Promise<Response>(() => undefined));
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);

    expect(screen.getByRole("button", { name: /founder/ })).toBeTruthy();
    expect(screen.queryByText("未登录")).toBeNull();
  });

  it("clears frontend and admin sessions and returns to login when context auth fails", async () => {
    seedAdminSession();
    const fetchMock = vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ detail: "登录态已失效" }),
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);

    await waitFor(() => expect(window.location.pathname).toBe("/login"));
    expect(window.localStorage.getItem("moonbox.session")).toBeNull();
    expect(window.localStorage.getItem("moonbox.session")).toBeNull();
  });

  it("sends the admin token when an admin session exists and keeps the admin entry visible", async () => {
    seedAdminSession();
    const fetchMock = vi.fn(() =>
      Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: contextFixture }),
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/requirement-center/context",
      expect.objectContaining({
        headers: expect.objectContaining({ authorization: "Bearer admin-token" }),
      }),
    );
    fireEvent.click(screen.getByRole("button", { name: /许同学/ }));
    expect(screen.getByRole("menuitem", { name: "进入后台" })).toBeTruthy();
  });

  it("loads the frontend user avatar with the admin token", async () => {
    seedAdminSession();
    const createObjectUrlSpy = vi.fn(() => "blob:requirement-avatar");
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createObjectUrlSpy });
    const avatarContext = {
      ...contextFixture,
      current_user: {
        ...contextFixture.current_user,
        avatar_url: "/api/v1/auth/avatar/requirement-user.png",
      },
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: avatarContext }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        blob: () => Promise.resolve(new Blob(["avatar"], { type: "image/png" })),
      });
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);

    await screen.findByText("REQ-0012");
    await waitFor(() => expect(screen.getByAltText("许同学 头像")).toBeTruthy());
    expect(createObjectUrlSpy).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "/api/v1/auth/avatar/requirement-user.png",
      expect.objectContaining({
        headers: expect.objectContaining({ authorization: "Bearer admin-token" }),
      }),
    );
  });

  it("opens the frontend profile modal, uploads one avatar and refreshes the user menu after saving", async () => {
    seedAdminSession();
    const createObjectUrlSpy = vi.fn(() => "blob:rc-profile-preview");
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createObjectUrlSpy });
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: contextFixture }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: { url: "/api/v1/auth/avatar/rc-profile.png", status: "done" } }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        blob: () => Promise.resolve(new Blob(["avatar"], { type: "image/png" })),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () =>
          Promise.resolve({
            data: {
              user: {
                id: "user_superadmin",
                username: "superadmin",
                nickname: "月盒同学",
                avatar_url: "/api/v1/auth/avatar/rc-profile.png",
                role: "后台管理员",
                status: "正常",
                is_system_superadmin: true,
              },
            },
          }),
      });
    vi.stubGlobal("fetch", fetchMock);
    const sessionChanged = vi.fn();
    window.addEventListener("moonbox.session.changed", sessionChanged);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    fireEvent.click(screen.getByRole("button", { name: /许同学/ }));
    fireEvent.click(screen.getByRole("menuitem", { name: "个人资料" }));

    const dialog = screen.getByRole("form", { name: "个人资料" });
    expect(dialog.querySelectorAll(".rc-profile-avatar-picker .rc-avatar")).toHaveLength(1);
    expect(dialog.querySelector(".rc-profile-head")).toBeTruthy();
    expect(dialog.querySelector(".rc-profile-summary")?.textContent).toBe("superadmin");
    expect(screen.getByRole("button", { name: "关闭个人资料" })).toBeTruthy();
    expect(screen.queryByText("Account Profile")).toBeNull();
    expect(screen.queryByText("保存后同步刷新前台用户菜单。")).toBeNull();
    expect(screen.queryByText("修改密码")).toBeNull();

    fireEvent.change(screen.getByLabelText("选择头像文件"), {
      target: { files: [new File(["avatar"], "rc-profile.webp", { type: "image/webp" })] },
    });
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/auth/avatar"),
        expect.objectContaining({ method: "POST", headers: { authorization: "Bearer admin-token" } }),
      ),
    );
    await waitFor(() => expect(screen.getByAltText("头像预览").getAttribute("src")).toBe("blob:rc-profile-preview"));

    fireEvent.change(screen.getByLabelText("昵称"), { target: { value: "月盒同学" } });
    fireEvent.click(screen.getByRole("button", { name: "保存" }));

    await waitFor(() => expect(screen.queryByRole("form", { name: "个人资料" })).toBeNull());
    expect(screen.getByRole("button", { name: /月盒同学/ })).toBeTruthy();
    expect(screen.getByRole("status").textContent).toContain("个人资料已更新");
    expect(window.localStorage.getItem("moonbox.session")).toContain("月盒同学");
    expect(window.localStorage.getItem("moonbox.session")).toContain("/api/v1/auth/avatar/rc-profile.png");
    expect(sessionChanged).toHaveBeenCalled();
    window.removeEventListener("moonbox.session.changed", sessionChanged);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/auth/me",
      expect.objectContaining({
        method: "PATCH",
        headers: expect.objectContaining({
          "content-type": "application/json",
          authorization: "Bearer admin-token",
        }),
        body: JSON.stringify({ nickname: "月盒同学", avatar_url: "/api/v1/auth/avatar/rc-profile.png" }),
      }),
    );
  });

  it("keeps frontend profile modal avatar aligned with restored context and two-character fallback", async () => {
    const restoredContext = {
      ...contextFixture,
      current_user: {
        ...contextFixture.current_user,
        avatar_initial: "许",
        avatar_url: "/api/v1/auth/avatar/restored-profile.webp",
      },
    };
    window.localStorage.setItem(
      "moonbox.session",
      JSON.stringify({
        access_token: "admin-token",
        expires_at: "2026-08-11 00:00:00",
        user: {
          id: "user_superadmin",
          username: "superadmin",
          nickname: "许同学",
          avatar_url: "/api/v1/admin/users/avatar/stale-profile.webp",
          role: "后台管理员",
          status: "正常",
          is_system_superadmin: true,
        },
      }),
    );
    const createObjectUrlSpy = vi.fn(() => "blob:restored-profile");
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createObjectUrlSpy });
    const fetchMock = vi.fn(async (input) => {
      const url = String(input);
      if (url.includes("/api/v1/requirement-center/context")) {
        return {
          ok: true,
          status: 200,
          json: () => Promise.resolve({ data: restoredContext }),
        } as Response;
      }
      return {
        ok: true,
        status: 200,
        blob: () => Promise.resolve(new Blob(["restored"], { type: "image/webp" })),
      } as Response;
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    await waitFor(() => expect((screen.getByAltText("许同学 头像") as HTMLImageElement).getAttribute("src")).toBe("blob:restored-profile"));
    fireEvent.click(screen.getByRole("button", { name: /许同学/ }));
    fireEvent.click(screen.getByRole("menuitem", { name: "个人资料" }));

    await waitFor(() => expect((screen.getByAltText("头像预览") as HTMLImageElement).getAttribute("src")).toBe("blob:restored-profile"));
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/auth/avatar/restored-profile.webp"),
      expect.objectContaining({ headers: { authorization: "Bearer admin-token" } }),
    );
    expect(fetchMock).not.toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/admin/users/avatar/stale-profile.webp"),
      expect.anything(),
    );

  });

  it("keeps the frontend profile modal open when avatar upload fails", async () => {
    seedAdminSession();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: contextFixture }),
      })
      .mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ detail: "仅支持 JPG、PNG、WEBP 格式头像" }),
      });
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    fireEvent.click(screen.getByRole("button", { name: /许同学/ }));
    fireEvent.click(screen.getByRole("menuitem", { name: "个人资料" }));
    fireEvent.change(screen.getByLabelText("选择头像文件"), {
      target: { files: [new File(["avatar"], "rc-profile.gif", { type: "image/gif" })] },
    });

    expect(await screen.findByText("仅支持 JPG、PNG、WEBP 格式头像")).toBeTruthy();
    expect(screen.getByRole("form", { name: "个人资料" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "上传或更换头像" }).textContent).toBe("上传");
  });

  it("falls back to username when nickname is cleared from the frontend profile modal", async () => {
    seedAdminSession();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: contextFixture }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () =>
          Promise.resolve({
            data: {
              user: {
                id: "user_superadmin",
                username: "superadmin",
                nickname: null,
                avatar_url: null,
                role: "后台管理员",
                status: "正常",
                is_system_superadmin: true,
              },
            },
          }),
      });
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    fireEvent.click(screen.getByRole("button", { name: /许同学/ }));
    fireEvent.click(screen.getByRole("menuitem", { name: "个人资料" }));
    fireEvent.change(screen.getByLabelText("昵称"), { target: { value: "   " } });
    fireEvent.click(screen.getByRole("button", { name: "保存" }));

    await waitFor(() => expect(screen.queryByRole("form", { name: "个人资料" })).toBeNull());
    expect(screen.getByRole("button", { name: /superadmin/ })).toBeTruthy();
    expect(window.localStorage.getItem("moonbox.session")).toContain("superadmin");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/auth/me",
      expect.objectContaining({
        body: JSON.stringify({ nickname: null, avatar_url: null }),
      }),
    );
  });

  it("keeps the frontend profile modal input when saving fails", async () => {
    seedAdminSession();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: contextFixture }),
      })
      .mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ detail: "个人资料保存失败。" }),
      });
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    fireEvent.click(screen.getByRole("button", { name: /许同学/ }));
    fireEvent.click(screen.getByRole("menuitem", { name: "个人资料" }));
    fireEvent.change(screen.getByLabelText("昵称"), { target: { value: "保留的昵称" } });
    fireEvent.click(screen.getByRole("button", { name: "保存" }));

    expect(await screen.findByText("个人资料保存失败。")).toBeTruthy();
    expect(screen.getByRole("form", { name: "个人资料" })).toBeTruthy();
    expect(screen.getByLabelText("昵称").getAttribute("value")).toBe("保留的昵称");
  });

  it("shows the frontend user nickname with the current workspace and falls back to username", async () => {
    const usernameContext = {
      ...contextFixture,
      current_user: {
        name: "admin",
        avatar_initial: "A",
        can_access_admin: true,
        permissions: ["requirement:read", "admin:access"],
      },
    };
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ data: usernameContext }),
        }),
      ),
    );

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    const userCopy = document.querySelector(".rc-user-copy");
    expect(userCopy?.querySelector("strong")?.textContent).toBe("admin");
    expect(userCopy?.querySelector("em")?.textContent).toBe("Platform Operations");
    expect(document.querySelector(".rc-avatar")?.textContent).toBe("AD");
    expect(document.querySelector(".rc-avatar img")).toBeNull();
  });

  it("logs out from the requirement center and clears frontend and admin sessions", async () => {
    seedAdminSession();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: contextFixture }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: { status: "done" } }),
      });
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    fireEvent.click(screen.getByRole("button", { name: /许同学/ }));
    fireEvent.click(screen.getByRole("menuitem", { name: "退出登录" }));

    await waitFor(() => expect(window.location.pathname).toBe("/login"));
    expect(window.localStorage.getItem("moonbox.session")).toBeNull();
    expect(window.localStorage.getItem("moonbox.session")).toBeNull();
    expect(fetchMock).toHaveBeenLastCalledWith(
      "/api/v1/auth/logout",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ authorization: "Bearer admin-token" }),
      }),
    );
  });

  it("opens change-password modal from the frontend user menu and clears sessions after success", async () => {
    seedAdminSession();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: contextFixture }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: { changed: true } }),
      });
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    fireEvent.click(screen.getByRole("button", { name: /许同学/ }));
    fireEvent.click(screen.getByRole("menuitem", { name: "修改密码" }));

    expect(screen.getByRole("form", { name: "修改密码" })).toBeTruthy();
    fireEvent.change(screen.getByLabelText("当前密码"), { target: { value: "OldPass123!" } });
    fireEvent.change(screen.getByLabelText("新密码"), { target: { value: "NewPass123!@#" } });
    fireEvent.change(screen.getByLabelText("确认新密码"), { target: { value: "Mismatch123!@#" } });
    expect(screen.getByText("两次输入的新密码不一致。")).toBeTruthy();
    expect((screen.getByRole("button", { name: "更新密码" }) as HTMLButtonElement).disabled).toBe(true);
    expect(fetchMock).toHaveBeenCalledTimes(1);

    fireEvent.change(screen.getByLabelText("确认新密码"), { target: { value: "NewPass123!@#" } });
    fireEvent.click(screen.getByRole("button", { name: "更新密码" }));

    await waitFor(() => expect(window.location.pathname).toBe("/login"));
    expect(window.localStorage.getItem("moonbox.session")).toBeNull();
    expect(window.localStorage.getItem("moonbox.session")).toBeNull();
    expect(fetchMock).toHaveBeenLastCalledWith(
      "/api/v1/auth/change-password",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          "content-type": "application/json",
          authorization: "Bearer admin-token",
        }),
        body: JSON.stringify({
          current_password: "OldPass123!",
          new_password: "NewPass123!@#",
          confirm_password: "NewPass123!@#",
        }),
      }),
    );
  });

  it("uses the frontend session token when a frontend-only user changes password", async () => {
    seedFrontendTokenSession();
    const frontendOnlyContext = {
      ...contextFixture,
      current_user: {
        name: "前台用户",
        avatar_initial: "前",
        can_access_admin: false,
        permissions: ["requirement:read"],
      },
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: frontendOnlyContext }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: { changed: true } }),
      });
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    fireEvent.click(screen.getByRole("button", { name: /前台用户/ }));
    fireEvent.click(screen.getByRole("menuitem", { name: "修改密码" }));
    fireEvent.change(screen.getByLabelText("当前密码"), { target: { value: "OldPass123!" } });
    fireEvent.change(screen.getByLabelText("新密码"), { target: { value: "NewPass123!@#" } });
    fireEvent.change(screen.getByLabelText("确认新密码"), { target: { value: "NewPass123!@#" } });
    fireEvent.click(screen.getByRole("button", { name: "更新密码" }));

    await waitFor(() => expect(window.location.pathname).toBe("/login"));
    expect(window.localStorage.getItem("moonbox.session")).toBeNull();
    expect(window.localStorage.getItem("moonbox.session")).toBeNull();
    expect(fetchMock).toHaveBeenLastCalledWith(
      "/api/v1/auth/change-password",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          "content-type": "application/json",
          authorization: "Bearer front-token",
        }),
      }),
    );
    expect(screen.queryByText("登录已失效，请重新登录")).toBeNull();
  });

  it("keeps the change-password modal open and preserves sessions when the API rejects", async () => {
    seedAdminSession();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: contextFixture }),
      })
      .mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ detail: "当前密码不正确" }),
      });
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    fireEvent.click(screen.getByRole("button", { name: /许同学/ }));
    fireEvent.click(screen.getByRole("menuitem", { name: "修改密码" }));
    fireEvent.change(screen.getByLabelText("当前密码"), { target: { value: "WrongPass123!" } });
    fireEvent.change(screen.getByLabelText("新密码"), { target: { value: "NewPass123!@#" } });
    fireEvent.change(screen.getByLabelText("确认新密码"), { target: { value: "NewPass123!@#" } });
    fireEvent.click(screen.getByRole("button", { name: "更新密码" }));

    expect(await screen.findByText("当前密码不正确")).toBeTruthy();
    fireEvent.change(screen.getByLabelText("确认新密码"), { target: { value: "Mismatch123!@#" } });
    expect(screen.getByText("两次输入的新密码不一致。")).toBeTruthy();
    expect(screen.queryByText("当前密码不正确")).toBeNull();
    expect(screen.getByRole("form", { name: "修改密码" })).toBeTruthy();
    expect(window.location.pathname).toBe("/requirements");
    expect(window.localStorage.getItem("moonbox.session")).toBeTruthy();
    expect(window.localStorage.getItem("moonbox.session")).toBeTruthy();
  });

  it.each([
    ["explicit anonymous name", { name: "未登录", avatar_initial: "未", can_access_admin: false, permissions: ["requirement:read"] }],
    ["blank anonymous name", { name: "", avatar_initial: "", can_access_admin: false, permissions: ["requirement:read"] }],
    ["missing user object", undefined],
  ])("uses the frontend session name when the context user is anonymous: %s", async (_caseName, currentUser) => {
    const anonymousContext = {
      ...contextFixture,
      current_user: currentUser,
      currentUser,
    };
    const fetchMock = vi.fn(() =>
      Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: anonymousContext }),
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    expect(screen.getByRole("button", { name: /founder/ })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: /founder/ }));
    expect(screen.queryByRole("menuitem", { name: "进入后台" })).toBeNull();
  });
});

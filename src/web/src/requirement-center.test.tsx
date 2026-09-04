import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
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
      documents: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"],
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
      documents: ["proposal.md", "trace.md", "tasks.md"],
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
      documents: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"],
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
      documents: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md", "archive.md"],
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
      status: "ACTIVE",
      readonly: false,
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
      status: "FROZEN",
      readonly: true,
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
    expect(screen.getByText("OPS WORKBENCH")).toBeTruthy();
    expect(screen.getByText("v0.1.0")).toBeTruthy();
    expect(screen.getByText("WORKSPACE")).toBeTruthy();
    expect(screen.getByText("CAPABILITIES")).toBeTruthy();
    ["研发总览", "Chat 工作台", "需求中心", "Spec", "任务中心", "Skill Center", "Agent Center", "知识中心"].forEach((item) => {
      expect(screen.getByRole("button", { name: item })).toBeTruthy();
    });
    expect(screen.getByRole("button", { name: "需求中心" }).getAttribute("aria-current")).toBe("page");
    ["采集池", "规划中", "待评审", "已评审", "迭代规划", "待开发", "研发中", "验收中", "已完成"].forEach((stage) => {
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
    expect(screen.queryByText("P1 · 产品团队")).toBeNull();
    expect(screen.getAllByText("P1").length).toBeGreaterThan(0);
    expect(screen.getAllByText("产品团队").length).toBeGreaterThan(0);
    expect(document.querySelectorAll(".rc-card-meta span").length).toBeGreaterThan(0);
    document.querySelectorAll(".rc-card-meta").forEach((meta) => {
      expect(meta.querySelectorAll("span").length).toBe(2);
      expect(meta.querySelector(".rc-priority-tag")).toBeTruthy();
      expect(meta.querySelector(".rc-owner-tag")).toBeTruthy();
    });
  });

  it("uses controlled workflow demo data only when mock query is explicit", async () => {
    const fetchMock = vi.fn(() =>
      Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: contextFixture }),
      }),
    );
    vi.stubGlobal("fetch", fetchMock);
    window.history.replaceState(null, "", "/requirements?mock=workflow");

    render(<RequirementCenterPage />);

    expect(await screen.findByText("DEMO-REQ-CAPTURE-READY")).toBeTruthy();
    expect(fetchMock).not.toHaveBeenCalledWith(
      "/api/v1/requirement-center/context",
      expect.anything(),
    );
    ["采集池", "规划中", "待评审", "已评审", "迭代规划", "待开发", "研发中", "验收中", "已完成"].forEach((stage) => {
      const label = document.querySelector(`[aria-label^="${stage} "]`)?.getAttribute("aria-label") || "";
      expect(label).toMatch(new RegExp(`^${stage} 0*[1-9]`));
    });
    expect(screen.getByText("需求中心演示空间")).toBeTruthy();
    expect(screen.getAllByText("sprint-004").length).toBeGreaterThan(0);
    expect(screen.getAllByText("需求分析").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Bug 分析").length).toBeGreaterThan(0);
  });

  it("keeps workflow demo planning requirement.md editable by the capability matrix", async () => {
    window.history.replaceState(null, "", "/requirements?mock=workflow");

    render(<RequirementCenterPage />);

    expect(await screen.findByText("DEMO-REQ-PLANNING-READY")).toBeTruthy();
    const planningCard = document.querySelector('[data-issue-id="DEMO-REQ-PLANNING-READY"]') as HTMLElement;
    fireEvent.click(within(planningCard).getByRole("button", { name: /requirement\.md/ }));

    expect(await screen.findByRole("heading", { name: "Demo REQ-PLANNING-READY Requirement" })).toBeTruthy();
    expect(screen.getByRole("group", { name: "Markdown 查看模式" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "编辑" })).toBeTruthy();
    expect(screen.queryByText(/当前阶段只读/)).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "编辑" }));
    expect(await screen.findByLabelText("编辑 requirement.md")).toBeTruthy();
    expect(screen.getByRole("toolbar", { name: "Vditor Markdown 工具栏" })).toBeTruthy();
  });

  it("keeps real context loading as the default when workflow mock query is absent", async () => {
    const fetchMock = vi.fn(() =>
      Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: contextFixture }),
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);

    expect(await screen.findByText("REQ-0012")).toBeTruthy();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/requirement-center/context",
      expect.anything(),
    );
    expect(screen.queryByText("DEMO-REQ-CAPTURE-READY")).toBeNull();
  });

  it("renders workflow demo document bodies without calling the real document API", async () => {
    const fetchMock = vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: "unexpected real api call" }),
      }),
    );
    const openSpy = vi.spyOn(window, "open").mockImplementation(() => null);
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const originalCreateObjectURL = URL.createObjectURL;
    const originalRevokeObjectURL = URL.revokeObjectURL;
    const createObjectURLMock = vi.fn(() => "blob:workflow-demo-prototype");
    const revokeObjectURLMock = vi.fn();
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createObjectURLMock });
    Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: revokeObjectURLMock });
    vi.stubGlobal("fetch", fetchMock);
    window.history.replaceState(null, "", "/requirements?mock=workflow");

    try {
      render(<RequirementCenterPage />);

      expect(await screen.findByText("DEMO-REQ-CAPTURE-READY")).toBeTruthy();
      fireEvent.click(screen.getAllByRole("button", { name: /capture\.md/ })[0]);

      expect(await screen.findByRole("heading", { name: "Demo REQ-CAPTURE-READY Capture" })).toBeTruthy();
      expect(screen.getByText("这是一份用于需求中心受控 demo 模式的采集记录。")).toBeTruthy();
      expect(fetchMock).not.toHaveBeenCalled();

      fireEvent.click(screen.getByLabelText("关闭右侧抽屉"));
      fireEvent.click(screen.getByRole("button", { name: "Bug" }));
      fireEvent.click(await screen.findByRole("button", { name: /prototype\.html/ }));

      expect(createObjectURLMock).toHaveBeenCalledWith(expect.any(Blob));
      expect(openSpy).toHaveBeenCalledWith("blob:workflow-demo-prototype", "_blank", "noopener,noreferrer");
      expect(fetchMock).not.toHaveBeenCalled();
    } finally {
      Object.defineProperty(URL, "createObjectURL", { configurable: true, value: originalCreateObjectURL });
      Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: originalRevokeObjectURL });
    }
  });

  it("covers workflow demo scenarios for gates, tips, sprint visibility and progress", async () => {
    window.history.replaceState(null, "", "/requirements?mock=workflow");

    render(<RequirementCenterPage />);
    await screen.findByText("DEMO-REQ-CAPTURE-READY");

    const captureReady = document.querySelector('[data-issue-id="DEMO-REQ-CAPTURE-READY"]') as HTMLElement;
    const captureMissing = document.querySelector('[data-issue-id="DEMO-REQ-CAPTURE-MISSING-TRACE"]') as HTMLElement;
    const bugCaptureEmpty = document.querySelector('[data-issue-id="DEMO-BUG-CAPTURE-EMPTY-CAPTURE"]') as HTMLElement;
    const planningReqMissing = document.querySelector('[data-issue-id="DEMO-REQ-PLANNING-MISSING-REQ"]') as HTMLElement;
    const planningBugEmpty = document.querySelector('[data-issue-id="DEMO-BUG-PLANNING-EMPTY-BUG"]') as HTMLElement;
    const reviewReqMissing = document.querySelector('[data-issue-id="DEMO-REQ-REVIEW-MISSING-STORIES"]') as HTMLElement;
    const reviewBugEmpty = document.querySelector('[data-issue-id="DEMO-BUG-REVIEW-EMPTY-ROOT-CAUSE"]') as HTMLElement;
    const approvedReqMissing = document.querySelector('[data-issue-id="DEMO-REQ-APPROVED-MISSING-REVIEW"]') as HTMLElement;
    const approvedBugDrift = document.querySelector('[data-issue-id="DEMO-BUG-APPROVED-DRIFT"]') as HTMLElement;
    const sprintCard = document.querySelector('[data-issue-id="DEMO-REQ-SPRINT-READY"]') as HTMLElement;
    const readyDevCard = document.querySelector('[data-issue-id="DEMO-REQ-READY-DEV"]') as HTMLElement;
    const acceptanceReady = document.querySelector('[data-issue-id="DEMO-REQ-ACCEPTANCE-READY"]') as HTMLElement;
    const acceptanceBlocked = document.querySelector('[data-issue-id="DEMO-BUG-ACCEPTANCE-BLOCKED"]') as HTMLElement;
    const doneReq = document.querySelector('[data-issue-id="DEMO-REQ-DONE"]') as HTMLElement;
    const doneBug = document.querySelector('[data-issue-id="DEMO-BUG-DONE"]') as HTMLElement;

    expect(within(captureReady).getByRole("button", { name: "需求分析" }).hasAttribute("disabled")).toBe(false);
    expect(within(captureReady).getByRole("button", { name: "生成需求 →" }).hasAttribute("disabled")).toBe(false);
    expect(within(captureMissing).getByText("缺少 trace.md")).toBeTruthy();
    expect(within(captureMissing).getByRole("button", { name: "生成需求 →" }).hasAttribute("disabled")).toBe(true);
    expect(within(bugCaptureEmpty).getByText("文档内容为空：capture.md")).toBeTruthy();
    expect(within(planningReqMissing).getByText("缺少 requirement.md")).toBeTruthy();
    expect(within(planningBugEmpty).getByText("文档内容为空：bug.md")).toBeTruthy();
    expect(within(reviewReqMissing).getByText("缺少 user-stories.md")).toBeTruthy();
    expect(within(reviewBugEmpty).getByText("文档内容为空：root-cause.md")).toBeTruthy();
    expect(within(approvedReqMissing).getByText("缺少 review.md")).toBeTruthy();
    expect(within(approvedBugDrift).getByText("存在数据漂移")).toBeTruthy();

    expect(within(captureReady).queryByText("sprint-004")).toBeNull();
    expect(within(approvedBugDrift).queryByText("sprint-004")).toBeNull();
    expect(within(sprintCard).getByText("sprint-004")).toBeTruthy();
    ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"].forEach((doc) => {
      expect(within(readyDevCard).getByRole("button", { name: doc })).toBeTruthy();
      expect(within(acceptanceReady).getByRole("button", { name: doc })).toBeTruthy();
    });
    expect(within(acceptanceReady).queryByRole("button", { name: "acceptance.md" })).toBeNull();
    expect(within(acceptanceReady).queryByRole("button", { name: "test-plan.md" })).toBeNull();
    expect(within(readyDevCard).getByRole("button", { name: "研发 0/10" })).toBeTruthy();
    expect(within(acceptanceReady).getByRole("button", { name: "完成 / 归档 →" })).toBeTruthy();
    expect(within(acceptanceBlocked).queryByRole("button", { name: "完成 / 归档 →" })).toBeNull();
    expect(within(doneReq).queryByText(/研发 6\/6/)).toBeNull();
    expect(within(doneReq).queryByText(/测试/)).toBeNull();
    expect(within(doneReq).queryByText(/人工验收/)).toBeNull();
    expect(within(doneReq).queryByRole("button", { name: /查看归档/ })).toBeNull();
    ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md", "archive.md"].forEach((doc) => {
      expect(within(doneReq).getByRole("button", { name: doc })).toBeTruthy();
    });
    expect(within(doneReq).getByRole("button", { name: "archive.md" })).toBeTruthy();
    expect(within(doneReq).getByRole("button", { name: "trace.md" })).toBeTruthy();
    expect(within(doneBug).queryByText(/研发 4\/4/)).toBeNull();
    expect(within(doneBug).queryByRole("button", { name: /查看归档/ })).toBeNull();
  });

  it("keeps the board columns close to the attachment-style ops dashboard proportions", () => {
    const source = readFileSync("src/styles/globals.css", "utf8");
    const boardWrap = source.match(/\.rc-board-wrap\s*\{[^}]*\}/)?.[0] ?? "";
    const board = source.match(/\.rc-board\s*\{[^}]*\}/)?.[0] ?? "";
    const column = source.match(/\.rc-column\s*\{[^}]*\}/)?.[0] ?? "";
    const head = source.match(/\.rc-column-head\s*\{[^}]*\}/)?.[0] ?? "";
    const title = source.match(/\.rc-column-head h2\s*\{[^}]*\}/)?.[0] ?? "";
    const subtitle = source.match(/\.rc-column-head p\s*\{\n  margin-top:[^}]*\}/)?.[0] ?? "";
    const count = source.match(/\.rc-column-head > span\s*\{[^}]*\}/)?.[0] ?? "";
    const body = source.match(/\.rc-column-body\s*\{[^}]*\}/)?.[0] ?? "";
    const empty = source.match(/\.rc-column-body\.empty\s*\{[^}]*\}/)?.[0] ?? "";
    const emptyStage = source.match(/\.rc-empty-stage\s*\{[^}]*\}/)?.[0] ?? "";
    const card = source.match(/\.rc-card\s*\{[^}]*\}/)?.[0] ?? "";
    const cardId = source.match(/\.rc-card-top strong\s*\{[^}]*\}/)?.[0] ?? "";
    const cardTitle = source.match(/\.rc-card \.rc-card-title\s*\{[^}]*\}/)?.[0] ?? "";
    const cardTags = source.match(/\.rc-card-top,\n\.rc-card-meta,\n\.rc-card-tags\s*\{[^}]*\}/)?.[0] ?? "";
    const cardMeta = source.match(/\.rc-card > \.rc-card-meta\s*\{[^}]*\}/)?.[0] ?? "";
    const footer = source.match(/\.rc-card footer\s*\{[^}]*\}/)?.[0] ?? "";
    const tag = source.match(/\.rc-tag\s*\{[^}]*\}/)?.[0] ?? "";
    const priorityTag = source.match(/\.rc-priority-tag\s*\{[^}]*\}/)?.[0] ?? "";
    const ownerTag = source.match(/\.rc-owner-tag\s*\{[^}]*\}/)?.[0] ?? "";
    const progress = source.match(/\.rc-card \.rc-progress\s*\{[^}]*\}/)?.[0] ?? "";
    const progressMargin = source.match(/\.rc-card \.rc-progress\s*\{\n  margin:[^}]*\}/)?.[0] ?? "";
    const progressAction = source.match(/\.rc-card \.rc-progress-action\s*\{[^}]*\}/)?.[0] ?? "";
    const progressLabel = source.match(/\.rc-card \.rc-progress-label\s*\{[^}]*\}/)?.[0] ?? "";
    const progressValue = source.match(/\.rc-card \.rc-progress-value\s*\{[^}]*\}/)?.[0] ?? "";
    const docsButton = source.match(/\.rc-docs button\s*\{[^}]*\}/)?.[0] ?? "";
    const docsLayout = source.match(/\.rc-docs\s*\{\n  display:[^}]*\}/)?.[0] ?? "";
    const pageSource = readFileSync("src/pages/catalog/RequirementCenterPage.tsx", "utf8");
    const stat = source.match(/\.rc-stat\s*\{[^}]*\}/)?.[0] ?? "";
    const agentFab = source.match(/\.rc-agent-fab\s*\{[^}]*\}/)?.[0] ?? "";
    const agentFabHover = source.match(/\.rc-agent-fab:hover,\n\.rc-agent-fab:focus-visible\s*\{[^}]*\}/)?.[0] ?? "";
    const agentMask = source.match(/\.rc-agent-mask\s*\{[^}]*\}/)?.[0] ?? "";
    const agentDialog = source.match(/\.rc-agent-dialog\s*\{[^}]*\}/)?.[0] ?? "";
    const agentBody = source.match(/\.rc-agent-body\s*\{[^}]*\}/)?.[0] ?? "";

    expect(stat).toContain("align-content: center;");
    expect(stat).toContain("min-height: 74px;");
    expect(stat).toContain("padding: 14px 16px;");
    expect(source).not.toContain(".rc-stat-trend");
    expect(pageSource).not.toContain("statTrends");
    expect(pageSource).not.toContain("rc-stat-trend");
    expect(pageSource).not.toContain(">flow<");
    expect(pageSource).not.toContain(">scope<");
    expect(pageSource).not.toContain(">quality<");
    expect(pageSource).not.toContain(">risk<");
    expect(boardWrap).toContain("overflow-x: auto;");
    expect(boardWrap).toContain("overflow-y: hidden;");
    expect(board).toContain("grid-template-columns: repeat(9, 320px);");
    expect(board).toContain("grid-template-rows: auto minmax(260px, 1fr);");
    expect(board).toContain("gap: 10px;");
    expect(board).toContain("row-gap: 6px;");
    expect(board).toContain("height: 100%;");
    expect(column).toContain("min-height: 0;");
    expect(column).toContain("height: 100%;");
    expect(column).toContain("border: 0;");
    expect(column).toContain("background: transparent;");
    expect(column).toContain("box-shadow: none;");
    expect(head).toContain("position: sticky;");
    expect(head).toContain("top: 0;");
    expect(head).toContain("z-index: 2;");
    expect(head).toContain("align-items: baseline;");
    expect(head).toContain("min-height: 50px;");
    expect(head).toContain("padding: 12px 10px 12px 4px;");
    expect(head).toContain("border-bottom: 0;");
    expect(head).toContain("background: var(--rc-bg);");
    expect(source).not.toContain(".rc-column-head::before");
    expect(source).not.toContain(".rc-board-wrap::before");
    expect(source).not.toContain(".rc-board-head-mask");
    expect(title).toContain("font-size: 14.5px;");
    expect(title).toContain('font-family: "Space Grotesk", var(--rc-font-heading);');
    expect(subtitle).toContain("margin-top: 3px;");
    expect(subtitle).toContain("font-size: 10.5px;");
    expect(subtitle).toContain("font-family: var(--rc-font-accent);");
    expect(count).toContain("font-family: var(--rc-font-accent);");
    expect(count).toContain("font-size: 11.5px;");
    expect(count).toContain("padding: 2px 9px;");
    expect(count).toContain("border-radius: 20px;");
    expect(pageSource).toContain('className={`rc-column-head ${items.length > 0 ? "filled" : "empty"}`');
    expect(source).toContain(".rc-column-head.filled > span");
    expect(source).toContain(".rc-column-head.empty h2");
    expect(source).toContain(".rc-column-head.empty p,");
    expect(source).toContain(".rc-column-head.empty > span");
    expect(body).toContain("min-height: 0;");
    expect(body).toContain("height: 100%;");
    expect(body).toContain("display: flex;");
    expect(body).toContain("flex-direction: column;");
    expect(body).toContain("align-items: stretch;");
    expect(body).toContain("padding: 20px 10px 34px;");
    expect(body).toContain("scroll-padding-bottom: 34px;");
    expect(body).toContain("gap: 12px;");
    expect(body).toContain("border: 0;");
    expect(body).toContain("background: transparent;");
    expect(body).toContain("overflow-x: hidden;");
    expect(body).toContain("overflow-y: auto;");
    expect(empty).toContain("min-height: 0;");
    expect(empty).toContain("height: 100%;");
    const emptyFrame = source.match(/\.rc-column-body\.empty::before\s*\{[^}]*\}/)?.[0] ?? "";
    expect(empty).toContain("margin: 0;");
    expect(empty).toContain("border: 0;");
    expect(empty).toContain("padding: 20px 10px 34px;");
    expect(empty).toContain("background: transparent;");
    expect(emptyFrame).toContain("inset: 20px 0 34px;");
    expect(emptyFrame).toContain("border: 1.5px dashed rgba(64, 77, 106, .48);");
    expect(emptyFrame).toContain("border-radius: 12px;");
    expect(emptyFrame).toContain("background: rgba(255, 255, 255, .012);");
    expect(empty).not.toContain("repeating-linear-gradient");
    expect(empty).not.toContain("var(--rc-accent)");
    expect(emptyStage).toContain("justify-items: center;");
    expect(emptyStage).toContain("gap: 0;");
    expect(emptyStage).toContain("padding: 20px 14px;");
    expect(emptyStage).toContain("font-family: var(--rc-font-body);");
    expect(emptyStage).toContain("text-align: center;");
    expect(source).toContain(".rc-empty-stage-icon");
    expect(source).toContain("font-size: 20px;");
    expect(source).toContain("line-height: 1.5;");
    expect(card).toContain("display: flex;");
    expect(card).toContain("flex-direction: column;");
    expect(card).toContain("align-items: stretch;");
    expect(card).toContain("flex: 0 0 auto;");
    expect(card).toContain("min-height: 150px;");
    expect(card).toContain("height: auto;");
    expect(card).toContain("overflow: visible;");
    expect(card).toContain("padding: 15px 16px 18px;");
    expect(card).toContain("border-left: 3px solid var(--rc-accent);");
    expect(card).toContain("border-radius: 11px;");
    expect(cardId).toContain("font-size: 10.5px;");
    expect(cardId).toContain("font-style: italic;");
    expect(cardTitle).toContain("margin: 8px 0 0;");
    expect(cardTitle).toContain("font-size: 13.5px;");
    expect(cardTitle).toContain("font-weight: 600;");
    expect(cardTitle).toContain("line-height: 1.5;");
    expect(cardTags).toContain("gap: 6px;");
    expect(cardMeta).toContain("margin-top: 10px;");
    expect(source).toContain(".rc-docs,\n.rc-progress,\n.rc-blocked {\n  margin-top: 8px;");
    expect(source).toContain(".rc-blocked {\n  display: inline-flex;");
    expect(source).toContain(".rc-blocked {\n  display: inline-flex;\n  align-items: center;\n  gap: 5px;\n  width: fit-content;\n  margin-top: 8px;");
    expect(footer).toContain("flex: 0 0 auto;");
    expect(footer).toContain("margin-top: 8px;");
    expect(docsLayout).toContain("margin: 8px 0 0;");
    expect(tag).toContain("border-radius: 20px;");
    expect(tag).toContain("padding: 3px 8px;");
    expect(tag).toContain("font-family: var(--rc-font-mono);");
    expect(tag).toContain("font-size: 10px;");
    expect(priorityTag).toContain("background: color-mix(in srgb, var(--rc-warning) 16%, transparent);");
    expect(priorityTag).toContain("color: color-mix(in srgb, var(--rc-warning) 88%, var(--rc-heading));");
    expect(ownerTag).toContain("background: var(--rc-panel-2);");
    expect(ownerTag).toContain("color: var(--rc-muted);");
    expect(pageSource).toContain('className="rc-card-meta rc-card-tags"');
    expect(pageSource).toContain("rc-priority-tag rc-tag");
    expect(pageSource).toContain("rc-owner-tag rc-tag");
    expect(docsButton).toContain("text-decoration: none;");
    expect(source).toContain(".rc-docs button:hover,");
    expect(source).toContain(".rc-docs button:focus-visible");
    expect(progress).toContain("flex-wrap: nowrap;");
    expect(progress).toContain("border: 0;");
    expect(progress).toContain("background: transparent;");
    expect(progress).toContain("color: color-mix(in srgb, var(--rc-quiet) 80%, var(--rc-bg));");
    expect(progress).toContain("font-family: var(--rc-font-accent);");
    expect(progress).toContain("font-size: 10.5px;");
    expect(progress).toContain("font-weight: var(--rc-weight-regular);");
    expect(progress).toContain("gap: 10px;");
    expect(progressMargin).toContain("margin: 8px 0 0;");
    expect(progressAction).toContain("display: inline-flex;");
    expect(progressAction).toContain("align-items: baseline;");
    expect(progressAction).toContain("gap: 4px;");
    expect(progressAction).toContain("font: inherit;");
    expect(progressAction).toContain("text-decoration: none;");
    expect(progressLabel).toContain("color: color-mix(in srgb, var(--rc-quiet) 80%, var(--rc-bg));");
    expect(progressValue).toContain("color: var(--rc-muted);");
    expect(progressValue).toContain("font-weight: var(--rc-weight-semibold);");
    expect(source).not.toContain(".rc-card .rc-progress-action + .rc-progress-action::before");
    expect(source).not.toContain('content: "·";');
    expect(source).not.toContain('content: "\\00B7";');
    expect(source).not.toContain("Â·");
    expect(pageSource).toContain('className="rc-progress-action"');
    expect(pageSource).toContain('className="rc-progress-label"');
    expect(pageSource).toContain('className="rc-progress-value"');
    expect(pageSource).toContain("aria-label={`研发 ${taskProgress[0]}/${taskProgress[1]}`}");
    expect(pageSource).toContain("aria-label={`测试 ${issue.testProgress[0]}/${issue.testProgress[1]}`}");
    expect(pageSource).toContain("aria-label={`人工验收 ${manualProgress[0]}/${manualProgress[1]}`}");
    expect(pageSource).toContain('aria-label="自动化测试进度"');
    expect(pageSource).toContain('aria-label="人工验收进度"');
    expect(source).not.toContain(".rc-column-body:empty");
    expect(agentFab).toContain("right: 32px;");
    expect(agentFab).toContain("bottom: 28px;");
    expect(agentFab).toContain("height: 48px;");
    expect(agentFab).toContain("border-radius: 24px;");
    expect(agentFab).toContain("gap: 9px;");
    expect(agentFab).toContain("padding: 0 18px 0 15px;");
    expect(agentFab).toContain("background: var(--rc-accent) !important;");
    expect(agentFab).toContain("font-size: 13px;");
    expect(agentFabHover).toContain("background: var(--rc-accent-hover) !important;");
    expect(agentFabHover).toContain("transform: translateY(-1px);");
    expect(agentMask).toContain("z-index: 90;");
    expect(agentDialog).toContain("width: min(560px, calc(100vw - 32px));");
    expect(agentDialog).toContain("border-radius: 12px;");
    expect(agentDialog).toContain("background: var(--rc-sidebar-bg);");
    expect(agentBody).toContain("max-height: min(58vh, 520px);");
    expect(pageSource).toContain('className="rc-ai-fab rc-agent-fab"');
    expect(pageSource).toContain('aria-label="打开 Agent 助手"');
    expect(pageSource).toContain('aria-label="Agent 助手"');
    expect(pageSource).toContain("runAgentStageAction");
  });

  it("uses attachment-style action modals for card workflow actions", async () => {
    window.history.replaceState(null, "", "/requirements?mock=workflow");

    render(<RequirementCenterPage />);
    await screen.findByText("DEMO-REQ-CAPTURE-READY");

    const captureCard = document.querySelector('[data-issue-id="DEMO-REQ-CAPTURE-READY"]') as HTMLElement;
    fireEvent.click(within(captureCard).getByRole("button", { name: "生成需求 →" }));
    let dialog = screen.getByRole("dialog", { name: "生成需求" });
    expect(within(dialog).getByText("/req-generate DEMO-REQ-CAPTURE-READY")).toBeTruthy();
    expect(within(dialog).getByText("本次将生成 / 更新")).toBeTruthy();
    expect(within(dialog).getByText("requirement.md")).toBeTruthy();
    expect(within(dialog).getByText("Esc")).toBeTruthy();
    fireEvent.click(within(dialog).getByRole("button", { name: "关闭生成需求" }));

    fireEvent.click(within(captureCard).getByRole("button", { name: "需求分析" }));
    dialog = screen.getByRole("dialog", { name: "需求分析" });
    expect(within(dialog).getByText(/AI 正在分析上下文/)).toBeTruthy();
    await waitFor(() => expect(within(dialog).getByText("解决方案要点（可选择采纳）")).toBeTruthy());
    expect(within(dialog).getAllByRole("button", { name: /补充|明确|识别/ }).length).toBe(3);
    const adoptButtons = within(dialog).getAllByRole("button", { name: /补充|明确|识别/ });
    adoptButtons.forEach((button) => expect(button.getAttribute("aria-pressed")).toBe("true"));
    expect(within(dialog).getByRole("button", { name: "采纳 3/3 项并保留分析 →" })).toBeTruthy();
    fireEvent.click(within(dialog).getByRole("button", { name: /明确验收标准边界/ }));
    expect(within(dialog).getByRole("button", { name: /明确验收标准边界/ }).getAttribute("aria-pressed")).toBe("false");
    expect(within(dialog).getByRole("button", { name: "采纳 2/3 项并保留分析 →" })).toBeTruthy();
    fireEvent.click(within(dialog).getByRole("button", { name: /补充/ }));
    fireEvent.click(within(dialog).getByRole("button", { name: /识别/ }));
    expect((within(dialog).getByRole("button", { name: "采纳 0/3 项并保留分析 →" }) as HTMLButtonElement).disabled).toBe(true);
    fireEvent.click(within(dialog).getByRole("button", { name: /明确验收标准边界/ }));
    expect(within(dialog).getByRole("button", { name: "采纳 1/3 项并保留分析 →" })).toBeTruthy();
    fireEvent.click(within(dialog).getByRole("button", { name: "关闭需求分析" }));

    const planningCard = document.querySelector('[data-issue-id="DEMO-REQ-PLANNING-READY"]') as HTMLElement;
    fireEvent.click(within(planningCard).getByRole("button", { name: "完善需求 →" }));
    dialog = screen.getByRole("dialog", { name: "完善需求" });
    expect(within(dialog).getByRole("tab", { name: "AI 生成" }).getAttribute("aria-selected")).toBe("true");
    fireEvent.click(within(dialog).getByRole("tab", { name: "导入文档" }));
    expect(within(dialog).getByLabelText("导入完善文档")).toBeTruthy();
    expect((within(dialog).getByRole("button", { name: "生成完善文档 →" }) as HTMLButtonElement).disabled).toBe(true);
    fireEvent.change(within(dialog).getByLabelText("导入完善文档"), { target: { files: [new File(["ok"], "requirement-pack.zip", { type: "application/zip" })] } });
    dialog = screen.getByRole("dialog", { name: "完善需求" });
    expect(within(dialog).getByText(/requirement-pack\.zip/)).toBeTruthy();
    expect((within(dialog).getByRole("button", { name: "生成完善文档 →" }) as HTMLButtonElement).disabled).toBe(false);
    fireEvent.click(within(dialog).getByRole("button", { name: "关闭完善需求" }));

    const approvedCard = document.querySelector('[data-issue-id="DEMO-REQ-APPROVED-READY"]') as HTMLElement;
    fireEvent.click(within(approvedCard).getByRole("button", { name: "加入迭代 →" }));
    dialog = screen.getByRole("dialog", { name: "加入迭代" });
    expect(within(dialog).getByText(/正在评估工作量/)).toBeTruthy();
    await waitFor(() => expect(within(dialog).getByText(/预估工作量/)).toBeTruthy());
    expect(within(dialog).getByText("对象")).toBeTruthy();
    expect(within(dialog).getByText("DEMO-REQ-APPROVED-READY")).toBeTruthy();
    expect(within(dialog).getByRole("tab", { name: "加入现有迭代" })).toBeTruthy();
    expect(within(dialog).getByRole("tab", { name: "新建迭代" })).toBeTruthy();
    expect(within(dialog).getByRole("radio", { name: /sprint-004/ })).toBeTruthy();
    expect(within(dialog).getByText("8/12 项")).toBeTruthy();
    expect(within(dialog).getByText("容量不足")).toBeTruthy();
    expect(dialog.querySelector(".rc-sprint-capacity-bar")).toBeTruthy();
    expect(within(dialog).getByRole("button", { name: "加入 sprint-004" })).toBeTruthy();
    fireEvent.click(within(dialog).getByRole("tab", { name: "新建迭代" }));
    expect(within(dialog).getByLabelText("迭代编号")).toBeTruthy();
    fireEvent.change(within(dialog).getByLabelText("迭代编号"), { target: { value: "" } });
    expect((within(dialog).getByRole("button", { name: "创建 新迭代 并加入" }) as HTMLButtonElement).disabled).toBe(true);
    fireEvent.change(within(dialog).getByLabelText("迭代编号"), { target: { value: "sprint-006" } });
    expect((within(dialog).getByRole("button", { name: "创建 sprint-006 并加入" }) as HTMLButtonElement).disabled).toBe(false);
    fireEvent.click(within(dialog).getByRole("button", { name: "关闭加入迭代" }));

    const sprintCard = document.querySelector('[data-issue-id="DEMO-REQ-SPRINT-READY"]') as HTMLElement;
    fireEvent.click(within(sprintCard).getByRole("button", { name: "生成 Opsx →" }));
    dialog = screen.getByRole("dialog", { name: "生成 Opsx" });
    expect(within(dialog).getByText(/AI 正在拆解 Change/)).toBeTruthy();
    await waitFor(() => expect(within(dialog).getByText(/已完成拆解/)).toBeTruthy());
    expect(within(dialog).getAllByText("proposal.md").length).toBeGreaterThan(0);
    fireEvent.click(within(dialog).getByRole("button", { name: "关闭生成 Opsx" }));

    const developmentCard = document.querySelector('[data-issue-id="DEMO-REQ-DEVELOPMENT"]') as HTMLElement;
    fireEvent.click(within(developmentCard).getByRole("button", { name: "查看进度 →" }));
    dialog = screen.getByRole("dialog", { name: "查看进度" });
    expect(within(dialog).getByText("Change 研发进度")).toBeTruthy();
    expect(dialog.querySelector(".rc-mini-bar")).toBeTruthy();
    fireEvent.mouseDown(document.querySelector(".rc-action-mask") as HTMLElement);
    expect(screen.queryByRole("dialog", { name: "查看进度" })).toBeNull();
  });

  it("locks the action modal style contract against the reference component family", () => {
    const source = readFileSync("src/styles/globals.css", "utf8");
    const pageSource = readFileSync("src/pages/catalog/RequirementCenterPage.tsx", "utf8");
    const mask = source.match(/\.rc-action-mask\s*\{[^}]*\}/)?.[0] ?? "";
    const dialog = source.match(/\.rc-action-dialog\s*\{[^}]*\}/)?.[0] ?? "";
    const head = source.match(/\.rc-action-dialog \.rc-dialog-head\s*\{[^}]*\}/)?.[0] ?? "";
    const title = source.match(/\.rc-action-dialog \.rc-dialog-head h2\s*\{[^}]*\}/)?.[0] ?? "";
    const eyebrow = source.match(/\.rc-action-dialog \.rc-dialog-head p\s*\{[^}]*\}/)?.[0] ?? "";
    const body = source.match(/\.rc-action-body\s*\{[^}]*\}/)?.[0] ?? "";
    const command = source.match(/\.rc-action-command\s*\{[^}]*\}/)?.[0] ?? "";
    const docs = source.match(/\.rc-action-doc\s*\{[^}]*\}/)?.[0] ?? "";
    const tabs = source.match(/\.rc-action-tabs\s*\{[^}]*\}/)?.[0] ?? "";
    const dropzone = source.match(/\.rc-action-dropzone\s*\{[^}]*\}/)?.[0] ?? "";
    const adoptButton = source.match(/\.rc-action-adopt-list button\s*\{[^}]*\}/)?.[0] ?? "";
    const checkedAdoptButton = source.match(/\.rc-action-adopt-list button\.checked\s*\{[^}]*\}/)?.[0] ?? "";
    const adoptDot = source.match(/\.rc-action-adopt-list button span\s*\{[^}]*\}/)?.[0] ?? "";
    const checkedAdoptDot = source.match(/\.rc-action-adopt-list button\.checked span\s*\{[^}]*\}/)?.[0] ?? "";
    const sprintDialog = source.match(/\.rc-action-dialog\.sprint\s*\{[^}]*\}/)?.[0] ?? "";
    const sprintContext = source.match(/\.rc-sprint-context-strip\s*\{[^}]*\}/)?.[0] ?? "";
    const sprintOption = source.match(/\.rc-sprint-options button\s*\{[^}]*\}/)?.[0] ?? "";
    const selectedSprintOption = source.match(/\.rc-sprint-options button\.selected\s*\{[^}]*\}/)?.[0] ?? "";
    const sprintRadio = source.match(/\.rc-sprint-radio\s*\{[^}]*\}/)?.[0] ?? "";
    const sprintCapacityBar = source.match(/\.rc-sprint-capacity-bar\s*\{[^}]*\}/)?.[0] ?? "";
    const footer = source.match(/\.rc-action-dialog \.rc-dialog-actions\s*\{[^}]*\}/)?.[0] ?? "";
    const primary = source.match(/\.rc-action-dialog \.rc-primary-action\s*\{[^}]*\}/)?.[0] ?? "";

    expect(pageSource).toContain('type ActionDialogKind = "analysis" | "command" | "complete" | "sprint" | "opsx" | "apply" | "progress"');
    expect(pageSource).toContain("adoptedPointIndexes");
    expect(pageSource).toContain("采纳 ${adoptedCount}/3 项并保留分析 →");
    expect(pageSource).toContain('加入现有迭代');
    expect(pageSource).toContain('新建迭代');
    expect(pageSource).toContain('AI 工作量评估');
    expect(pageSource).toContain('rc-sprint-capacity-badge');
    expect(pageSource).toContain('创建 ${actionDialog.newSprintId.trim() || "新迭代"} 并加入');
    expect(pageSource).toContain("openIssueActionDialog(issue, auxAction)");
    expect(pageSource).toContain("openIssueActionDialog(issue)");
    expect(pageSource).toContain("renderActionDialog()");
    expect(pageSource).toContain("runIssueAction(issue, { confirmed: true })");
    expect(mask).toContain("z-index: 96;");
    expect(mask).toContain("align-items: center;");
    expect(mask).toContain("background: rgba(4, 5, 9, .62);");
    expect(dialog).toContain("width: min(560px, calc(100vw - 32px));");
    expect(dialog).toContain("max-height: 88vh;");
    expect(dialog).toContain("border-radius: 16px;");
    expect(dialog).toContain("background: var(--rc-sidebar-bg);");
    expect(head).toContain("padding: 22px 24px 16px;");
    expect(head).toContain("border-bottom: 1px solid var(--rc-border-soft);");
    expect(eyebrow).toContain("font-family: var(--rc-font-accent);");
    expect(eyebrow).toContain("font-size: 10.5px;");
    expect(eyebrow).toContain("letter-spacing: .12em;");
    expect(title).toContain('font-family: "Space Grotesk", var(--rc-font-heading);');
    expect(title).toContain("font-size: 18px;");
    expect(body).toContain("gap: 14px;");
    expect(body).toContain("padding: 20px 24px 4px;");
    expect(command).toContain("font-family: var(--rc-font-accent);");
    expect(command).toContain("background: var(--rc-panel-2);");
    expect(docs).toContain("min-height: 32px;");
    expect(tabs).toContain("width: fit-content;");
    expect(tabs).toContain("border-radius: 9px;");
    expect(dropzone).toContain("border: 1px dashed");
    expect(dropzone).toContain("border-radius: 12px;");
    expect(adoptButton).toContain("text-align: left;");
    expect(checkedAdoptButton).toContain("border-color:");
    expect(adoptDot).toContain("background: transparent;");
    expect(checkedAdoptDot).toContain("background: color-mix(in srgb, var(--rc-accent) 72%, transparent);");
    expect(sprintDialog).toContain("width: min(520px, calc(100vw - 32px));");
    expect(sprintContext).toContain("border-left: 3px solid var(--rc-accent);");
    expect(sprintOption).toContain("border-width: 1.5px;");
    expect(sprintOption).toContain("border-radius: 11px;");
    expect(selectedSprintOption).toContain("background: color-mix(in srgb, var(--rc-accent) 10%, var(--rc-menu-surface-raised));");
    expect(sprintRadio).toContain("border-radius: 50%;");
    expect(sprintCapacityBar).toContain("height: 5px;");
    expect(footer).toContain("justify-content: space-between;");
    expect(footer).toContain("padding: 16px 24px 22px;");
    expect(primary).toContain("background: var(--rc-accent);");
  });

  it("renders stage-specific empty copy inside empty kanban columns", () => {
    const source = readFileSync("src/pages/catalog/RequirementCenterPage.tsx", "utf8");

    expect(source).toContain('emptyTitle: "暂无需求"');
    expect(source).toContain('emptyHint: "从采集池生成需求"');
    expect(source).toContain('emptyDetail: "后会显示在这里"');
    expect(source).toContain('className={`rc-column-body ${items.length === 0 ? "empty" : ""}`}');
    expect(source).toContain("stageColumns.map(({ stage, items })");
    expect(source).toContain('className="rc-empty-stage"');
    expect(source).toContain('className="rc-empty-stage-icon"');
    expect(source).toContain("{stage.emptyTitle}");
    expect(source).toContain("{stage.emptyHint}");
    expect(source).toContain("{stage.emptyDetail}");
    expect(source).toContain("<br />");
  });

  it("keeps rendered markdown documents at drawer reading density", () => {
    const source = readFileSync("src/styles/globals.css", "utf8");
    const rendered = source.match(/\.rc-rendered-markdown\s*\{[^}]*\}/)?.[0] ?? "";
    const compact = source.match(/\.rc-markdown-prototype-preview\.compact \.rc-rendered-markdown\s*\{[^}]*\}/)?.[0] ?? "";
    const heading = source.match(/\.rc-rendered-markdown h3\s*\{[^}]*\}/)?.[0] ?? "";
    const level1 = source.match(/\.rc-rendered-markdown h3\.level-1\s*\{[^}]*\}/)?.[0] ?? "";
    const level2 = source.match(/\.rc-rendered-markdown h3\.level-2\s*\{[^}]*\}/)?.[0] ?? "";
    const level3 = source.match(/\.rc-rendered-markdown h3\.level-3\s*\{[^}]*\}/)?.[0] ?? "";
    const taskInput = source.match(/\.rc-rendered-markdown \.task-list-item input\s*\{[^}]*\}/)?.[0] ?? "";
    const unorderedList = source.match(/\.rc-rendered-markdown ul\s*\{[^}]*\}/)?.[0] ?? "";
    const codeBlock = source.match(/\.rc-rendered-markdown \.code-block\s*\{[^}]*\}/)?.[0] ?? "";
    const copyButton = source.match(/\.rc-rendered-markdown \.copy-code\s*\{[^}]*\}/)?.[0] ?? "";
    const codePre = source.match(/\.rc-rendered-markdown pre\.code\s*\{[^}]*\}/)?.[0] ?? "";
    const tableCell = source.match(/\.rc-rendered-markdown td\s*\{[^}]*\}/)?.[0] ?? "";

    expect(rendered).toContain("font-size: 12.5px;");
    expect(rendered).toContain("line-height: 1.68;");
    expect(rendered).toContain("gap: 10px;");
    expect(rendered).toContain("font-family: var(--rc-font-body);");
    expect(compact).toContain("font-size: 12px;");
    expect(compact).toContain("line-height: 1.64;");
    expect(heading).toContain("font-family: var(--rc-font-heading);");
    expect(heading).not.toContain("Noto Serif SC");
    expect(level1).toContain("font-size: 18px;");
    expect(level2).toContain("font-size: 15px;");
    expect(level3).toContain("font-size: 13.5px;");
    expect(unorderedList).toContain("gap: 5px;");
    expect(taskInput).toContain("margin: 4px 0 0;");
    expect(codeBlock).toContain("position: relative;");
    expect(copyButton).toContain("position: absolute;");
    expect(copyButton).toContain("top: 6px;");
    expect(copyButton).toContain("right: 6px;");
    expect(copyButton).toContain("width: 26px;");
    expect(copyButton).toContain("opacity: .56;");
    expect(source).toContain(".rc-rendered-markdown .copy-code span");
    expect(source).toContain(".rc-rendered-markdown .code-block:hover .copy-code");
    expect(source).toContain(".rc-rendered-markdown .copy-code.copied");
    expect(codePre).toContain("padding: 10px 44px 9px 10px;");
    expect(tableCell).toContain("font-size: 12px;");
    expect(tableCell).toContain("line-height: 1.48;");
    expect(tableCell).toContain("padding: 6px 8px;");
    expect(source).toContain(".rc-rendered-markdown code");
    expect(source).toContain("font-family: var(--rc-font-mono);");
  });

  it("keeps the requirement page header aligned with admin page head without a topbar treatment", () => {
    const source = readFileSync("src/styles/globals.css", "utf8");
    const pageSource = readFileSync("src/pages/catalog/RequirementCenterPage.tsx", "utf8");
    const block = source.match(/\.rc-page-header\s*\{[^}]*\}/)?.[0] ?? "";
    const actionBlock = source.match(/\.rc-header-action\s*\{[^}]*\}/)?.[0] ?? "";
    const hoverBlock = source.match(/\.rc-header-action:hover\s*\{[^}]*\}/)?.[0] ?? "";

    expect(pageSource).toContain("<p>Requirement Operations</p>");
    expect(pageSource).not.toContain("<p>MoonBox Ops</p>");
    expect(block).toContain("align-items: flex-end;");
    expect(block).toContain("gap: 24px;");
    expect(block).toContain("background: transparent;");
    expect(block).not.toContain("border-bottom");
    expect(block).not.toContain("backdrop-filter");
    expect(block).not.toContain("position: sticky");
    expect(actionBlock).toContain("background: var(--rc-accent);");
    expect(actionBlock).toMatch(/color:\s*#[0-9a-f]{6};/);
    expect(actionBlock).toContain("border-radius: 9px;");
    expect(actionBlock).toContain("padding: 0 18px;");
    expect(actionBlock).toContain("border-color: transparent;");
    expect(hoverBlock).toContain("transform: translateY(-1px);");
  });

  it("keeps the frontend brand area visually aligned with the admin sidebar brand", () => {
    render(<RequirementCenterPage />);

    expect(screen.getByText("OPS WORKBENCH")).toBeTruthy();

    const source = readFileSync("src/styles/globals.css", "utf8");
    const brandTitle = source.match(/\.rc-brand-copy strong\s*\{[^}]*\}/)?.[0] ?? "";
    const brandSubtitle = source.match(/\.rc-brand-copy small\s*\{[^}]*\}/)?.[0] ?? "";
    const versionBadge = source.match(/\.rc-version-badge\s*\{[^}]*\}/)?.[0] ?? "";
    const collapse = source.match(/\.rc-collapse\s*\{[^}]*\}/)?.[0] ?? "";
    const collapsedCollapse = source.match(/\.rc-sidebar\.collapsed \.rc-collapse\s*\{[^}]*\}/)?.[0] ?? "";

    expect(brandTitle).toContain("font-size: var(--rc-text-lg);");
    expect(brandSubtitle).toContain("font-family: var(--rc-font-accent);");
    expect(brandSubtitle).toContain("font-size: var(--rc-text-micro);");
    expect(brandSubtitle).toContain("line-height: var(--rc-leading-label);");
    expect(brandSubtitle).toContain("text-transform: uppercase;");
    expect(versionBadge).toContain("right: 42px;");
    expect(versionBadge).toContain("border-radius: var(--ops-radius-sm);");
    expect(versionBadge).not.toContain("line-height:");
    expect(collapse).toContain("width: 24px;");
    expect(collapse).toContain("height: 24px !important;");
    expect(collapse).toContain("gap: 11px;");
    expect(collapse).toContain("background: transparent !important;");
    expect(collapse).toContain("line-height: var(--rc-leading-label);");
    expect(collapse).not.toContain("z-index:");
    expect(collapsedCollapse).toContain("right: -13px;");
    expect(collapsedCollapse).toContain("background: var(--rc-sidebar-bg) !important;");
    expect(collapsedCollapse).not.toContain("z-index:");
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
    fireEvent.change(screen.getByLabelText("搜索治理对象"), { target: { value: "MoonBox" } });
    expect(screen.getByText("REQ-0012")).toBeTruthy();
    expect(screen.queryByText("BUG-0001")).toBeNull();

    fireEvent.change(screen.getByLabelText("搜索治理对象"), { target: { value: "平台工程" } });
    expect(screen.getByText("BUG-0001")).toBeTruthy();
    expect(screen.getByText("REQ-0006")).toBeTruthy();
  });

  it("hides historical sprint labels and sprint filter options before sprint planning", async () => {
    const earlySprintContext = {
      ...contextFixture,
      issues: [
        {
          id: "REQ-0100",
          type: "requirement",
          title: "已评审但未入迭代",
          priority: "P1",
          owner: "产品团队",
          source: "review",
          stage: "approved",
          documents: ["review.md", "trace.md"],
          updated_at: "10:30",
          sprint_id: "sprint-099",
        },
        {
          id: "REQ-0101",
          type: "requirement",
          title: "已入迭代",
          priority: "P1",
          owner: "产品团队",
          source: "review",
          stage: "sprint-planning",
          documents: ["sprint.md", "trace.md"],
          updated_at: "10:31",
          sprint_id: "sprint-003",
        },
      ],
    };
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ data: earlySprintContext }),
        }),
      ),
    );

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0100");

    const earlyCard = document.querySelector('[data-issue-id="REQ-0100"]');
    const sprintCard = document.querySelector('[data-issue-id="REQ-0101"]');
    expect(earlyCard?.querySelector(".rc-sprint-tag")).toBeNull();
    expect(sprintCard?.querySelector(".rc-sprint-tag")?.textContent).toBe("sprint-003");
    expect(screen.queryByRole("option", { name: "sprint-099" })).toBeNull();
    expect(screen.getByRole("option", { name: "sprint-003" })).toBeTruthy();
  });

  it("filters card documents by stage and keeps capture exploration actions lightweight", async () => {
    const fixture = {
      ...contextFixture,
      issues: [
        {
          id: "REQ-0199",
          type: "requirement",
          title: "采集池历史文档过滤",
          priority: "P1",
          owner: "产品团队",
          source: "capture",
          stage: "capture",
          documents: ["acceptance.md", "business-flow.md", "capture.md", "requirement.md", "review.md", "trace.md", "user-stories.md"],
          document_entries: [
            { name: "acceptance.md", type: "markdown", open_mode: "drawer", label: "acceptance.md" },
            { name: "business-flow.md", type: "markdown", open_mode: "drawer", label: "business-flow.md" },
            { name: "capture.md", type: "markdown", open_mode: "drawer", label: "capture.md" },
            { name: "requirement.md", type: "markdown", open_mode: "drawer", label: "requirement.md" },
            { name: "review.md", type: "markdown", open_mode: "drawer", label: "review.md" },
            { name: "trace.md", type: "markdown", open_mode: "drawer", label: "trace.md" },
            { name: "user-stories.md", type: "markdown", open_mode: "drawer", label: "user-stories.md" },
          ],
          action: { command: "/req-generate REQ-0199", label: "生成需求", requires_choice: "generation", disabled_reason: "文档内容为空：capture.md" },
          task_progress: [18, 18],
          updated_at: "20:14",
        },
        {
          id: "BUG-0199",
          type: "bug",
          title: "采集池 Bug 探索入口",
          priority: "P1",
          owner: "平台工程",
          source: "capture",
          stage: "capture",
          documents: ["capture.md", "trace.md"],
          updated_at: "20:16",
        },
      ],
    };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve({ data: fixture }) }));

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0199");

    const reqCard = document.querySelector('[data-issue-id="REQ-0199"]') as HTMLElement;
    expect(within(reqCard).getByRole("button", { name: /capture.md/ })).toBeTruthy();
    expect(within(reqCard).getByRole("button", { name: /trace.md/ })).toBeTruthy();
    expect(within(reqCard).queryByRole("button", { name: /acceptance.md/ })).toBeNull();
    expect(within(reqCard).queryByRole("button", { name: /requirement.md/ })).toBeNull();
    expect(within(reqCard).queryByRole("button", { name: /研发 18\/18/ })).toBeNull();
    expect(within(reqCard).getByRole("button", { name: "需求分析" }).getAttribute("title")).toBe("/req-explore REQ-0199");
    expect(reqCard.querySelector(".rc-docs")?.textContent).toBe("capture.md trace.md");
    expect(reqCard.querySelector(".rc-doc-separator")?.textContent).toBe(" ");
    const reqCardActionsText = reqCard.querySelector("footer .rc-card-actions")?.textContent || "";
    expect(reqCardActionsText).toContain("生成需求");
    expect(reqCardActionsText).toContain("需求分析");
    expect(reqCardActionsText.indexOf("需求分析")).toBeLessThan(reqCardActionsText.indexOf("生成需求"));
    expect(reqCard.querySelector("footer .rc-card-actions button.primary")?.textContent).toContain("生成需求");
    expect(reqCard.querySelector("footer .rc-card-actions button.secondary")?.textContent).toContain("需求分析");
    expect(within(reqCard).getByRole("button", { name: "生成需求 →" }).hasAttribute("disabled")).toBe(true);
    expect(within(reqCard).getByRole("button", { name: "需求分析" }).hasAttribute("disabled")).toBe(false);

    const bugCard = document.querySelector('[data-issue-id="BUG-0199"]') as HTMLElement;
    expect(within(bugCard).getByRole("button", { name: "Bug 分析" }).getAttribute("title")).toBe("/bug-explore BUG-0199");
    fireEvent.click(within(reqCard).getByRole("button", { name: "需求分析" }));
    const actionDialog = await screen.findByRole("dialog", { name: "需求分析" });
    expect(within(actionDialog).getByText("/req-explore REQ-0199")).toBeTruthy();
    expect(within(actionDialog).getByText(/AI 正在分析上下文/)).toBeTruthy();
    await waitFor(() => expect(within(actionDialog).getByText("解决方案要点（可选择采纳）")).toBeTruthy());
    fireEvent.click(within(actionDialog).getByRole("button", { name: "采纳 3/3 项并保留分析 →" }));
    await waitFor(() => expect(screen.queryByRole("dialog", { name: "需求分析" })).toBeNull());
    expect(screen.getByRole("status").textContent).toContain("已保存分析结论");
  });

  it("keeps action gates for missing documents and acceptance archive entry", async () => {
    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    expect(screen.getByText(/缺少 acceptance.md/)).toBeTruthy();
    expect(screen.queryByRole("button", { name: "完成 / 归档 →" })).toBeNull();
    expect(screen.getByRole("button", { name: "生成 Opsx →" }).getAttribute("title")).toBe("/req-opsx REQ-0011");
    expect(screen.getAllByRole("button", { name: "开始开发 →" }).length).toBeGreaterThan(0);

    const acceptanceCard = Array.from(document.querySelectorAll(".rc-card")).find(
      (card) => card.querySelector(".rc-docs") && card.querySelector(".rc-blocked") && card.querySelector(".rc-progress"),
    ) as HTMLElement;
    const docs = acceptanceCard.querySelector(".rc-docs") as HTMLElement;
    const blocked = acceptanceCard.querySelector(".rc-blocked") as HTMLElement;
    const progress = acceptanceCard.querySelector(".rc-progress") as HTMLElement;
    expect(docs.compareDocumentPosition(blocked) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(blocked.compareDocumentPosition(progress) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    const progressActions = Array.from(progress.querySelectorAll(".rc-progress-action"));
    expect(progressActions.length).toBeGreaterThan(0);
    progressActions.forEach((action) => {
      expect(action.querySelector(".rc-progress-label")?.textContent).toMatch(/^(研发|测试|人工验收)$/);
      expect(action.querySelector(".rc-progress-value")?.textContent).toMatch(/^\d+\/\d+$/);
    });
  });

  it("renders missing document tips from stage and issue type action gates", async () => {
    const fixture = {
      ...contextFixture,
      issues: [
        {
          id: "REQ-9300",
          type: "requirement",
          title: "待评审需求缺用户故事",
          priority: "P1",
          owner: "产品团队",
          source: "review",
          stage: "review-ready",
          documents: ["capture.md", "trace.md", "requirement.md", "acceptance.md", "business-flow.md"],
          updated_at: "12:20",
        },
        {
          id: "BUG-9300",
          type: "bug",
          title: "待评审 Bug 空根因",
          priority: "P0",
          owner: "平台工程",
          source: "review",
          stage: "review-ready",
          documents: ["capture.md", "trace.md", "bug.md", "root-cause.md", "workaround.md", "acceptance.md"],
          action: { command: "/bug-review BUG-9300 --approve", label: "确认修复", disabled_reason: "文档内容为空：root-cause.md" },
          updated_at: "12:21",
        },
        {
          id: "REQ-9301",
          type: "requirement",
          title: "已评审需求缺 review",
          priority: "P1",
          owner: "产品团队",
          source: "review",
          stage: "approved",
          documents: ["capture.md", "trace.md", "requirement.md", "acceptance.md", "business-flow.md", "user-stories.md"],
          updated_at: "12:22",
        },
        {
          id: "BUG-9301",
          type: "bug",
          title: "已评审 Bug 数据漂移",
          priority: "P1",
          owner: "平台工程",
          source: "review",
          stage: "approved",
          documents: ["capture.md", "trace.md", "bug.md", "root-cause.md", "workaround.md", "acceptance.md", "review.md"],
          action: { command: "/sprint-propose --bug BUG-9301", label: "加入迭代", disabled_reason: "存在数据漂移" },
          updated_at: "12:23",
        },
      ],
    };
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: fixture }) })),
    );

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-9300");

    const reqReviewCard = document.querySelector('[data-issue-id="REQ-9300"]') as HTMLElement;
    const bugReviewCard = document.querySelector('[data-issue-id="BUG-9300"]') as HTMLElement;
    const reqApprovedCard = document.querySelector('[data-issue-id="REQ-9301"]') as HTMLElement;
    const bugApprovedCard = document.querySelector('[data-issue-id="BUG-9301"]') as HTMLElement;
    expect(within(reqReviewCard).getByText("缺少 user-stories.md")).toBeTruthy();
    expect(within(bugReviewCard).getByText("文档内容为空：root-cause.md")).toBeTruthy();
    expect(within(reqApprovedCard).getByText("缺少 review.md")).toBeTruthy();
    expect(within(bugApprovedCard).getByText("存在数据漂移")).toBeTruthy();
  });

  it("requires confirmation for review actions and recomputes the approved action", async () => {
    const fixture = {
      ...contextFixture,
      issues: [
        {
          id: "REQ-9400",
          type: "requirement",
          title: "待评审需求可通过",
          priority: "P1",
          owner: "产品团队",
          source: "review",
          stage: "review-ready",
          documents: ["capture.md", "trace.md", "requirement.md", "acceptance.md", "business-flow.md", "user-stories.md"],
          action: { command: "/req-review REQ-9400 --approve", label: "发起评审" },
          updated_at: "12:40",
        },
        {
          id: "BUG-9400",
          type: "bug",
          title: "待评审 Bug 可确认",
          priority: "P0",
          owner: "平台工程",
          source: "review",
          stage: "review-ready",
          documents: ["capture.md", "trace.md", "bug.md", "root-cause.md", "workaround.md", "acceptance.md"],
          action: { command: "/bug-review BUG-9400 --approve", label: "确认修复" },
          updated_at: "12:41",
        },
      ],
    };
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: fixture }) })),
    );

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-9400");

    const reqCard = document.querySelector('[data-issue-id="REQ-9400"]') as HTMLElement;
    fireEvent.click(within(reqCard).getByRole("button", { name: "发起评审 →" }));
    let reviewDialog = screen.getByRole("dialog", { name: "发起评审" });
    expect(within(reviewDialog).getByText("/req-review REQ-9400 --approve")).toBeTruthy();
    expect(within(reviewDialog).getByText("review.md")).toBeTruthy();
    fireEvent.click(within(reviewDialog).getByRole("button", { name: "发起评审，进入已评审 →" }));
    let reqApprovedCard = reqCard;
    await waitFor(() => {
      reqApprovedCard = document.querySelector('[data-issue-id="REQ-9400"]') as HTMLElement;
      expect(within(reqApprovedCard).getByRole("button", { name: "加入迭代 →" })).toBeTruthy();
    });
    expect(within(reqApprovedCard).queryByRole("button", { name: "发起评审 →" })).toBeNull();
    const reqJoinButton = within(reqApprovedCard).getByRole("button", { name: "加入迭代 →" });
    expect(reqJoinButton.getAttribute("title")).toBe("/sprint-propose --req REQ-9400");
    fireEvent.click(reqJoinButton);
    const sprintDialog = screen.getByRole("dialog", { name: "加入迭代" });
    expect(within(sprintDialog).getByText(/正在评估工作量/)).toBeTruthy();
    await waitFor(() => expect(within(sprintDialog).getByText(/预估工作量/)).toBeTruthy());
    expect(within(sprintDialog).getByRole("tab", { name: "加入现有迭代" })).toBeTruthy();
    fireEvent.click(within(sprintDialog).getByRole("button", { name: "关闭加入迭代" }));

    const bugCard = document.querySelector('[data-issue-id="BUG-9400"]') as HTMLElement;
    fireEvent.click(within(bugCard).getByRole("button", { name: "确认修复 →" }));
    reviewDialog = screen.getByRole("dialog", { name: "确认修复" });
    expect(within(reviewDialog).getByText("/bug-review BUG-9400 --approve")).toBeTruthy();
    fireEvent.click(within(reviewDialog).getByRole("button", { name: "确认修复，进入已评审 →" }));
    let bugApprovedCard = bugCard;
    await waitFor(() => {
      bugApprovedCard = document.querySelector('[data-issue-id="BUG-9400"]') as HTMLElement;
      expect(within(bugApprovedCard).getByRole("button", { name: "加入迭代 →" })).toBeTruthy();
    });
    expect(within(bugApprovedCard).queryByRole("button", { name: "确认修复 →" })).toBeNull();
    expect(within(bugApprovedCard).getByRole("button", { name: "加入迭代 →" }).getAttribute("title")).toBe("/sprint-propose --bug BUG-9400");
  });

  it("creates a capture card from the reference-style modal", async () => {
    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    fireEvent.click(screen.getByRole("button", { name: "新建 Capture" }));
    const dialog = screen.getByRole("dialog", { name: "新建 Capture" });
    const titleInput = screen.getByLabelText("Capture 标题") as HTMLInputElement;
    await waitFor(() => expect(document.activeElement).toBe(titleInput));
    expect(within(dialog).queryByText("Capture · req-capture / bug-capture")).toBeNull();
    expect(within(dialog).getByText("快速记录一条需求或缺陷，稍后可在采集池中生成正式需求")).toBeTruthy();
    expect(screen.queryByLabelText("Capture 类型", { selector: "select" })).toBeNull();
    const typeGroup = screen.getByRole("group", { name: "Capture 类型" });
    const priorityGroup = screen.getByRole("group", { name: "Capture 优先级" });
    expect(typeGroup.getAttribute("aria-required")).toBe("true");
    expect(priorityGroup.getAttribute("aria-required")).toBe("true");
    expect(within(typeGroup).getByRole("button", { name: "◆ 需求" }).className).toContain("selected");
    expect(within(priorityGroup).getByRole("button", { name: "P1" }).className).toContain("selected");
    expect(within(priorityGroup).getByRole("button", { name: "P3" })).toBeTruthy();
    expect(titleInput.maxLength).toBe(60);
    expect(titleInput.required).toBe(true);
    expect((within(dialog).getByLabelText("来源") as HTMLSelectElement).required).toBe(true);
    expect(Array.from(dialog.querySelectorAll(".rc-field-label b, .rc-capture-fieldset legend b")).map((item) => item.textContent)).toEqual(["*", "*", "*", "*"]);
    expect(within(dialog).queryByText(/Esc/)).toBeNull();
    expect((screen.getByLabelText("一句话描述") as HTMLTextAreaElement).maxLength).toBe(200);
    expect(screen.getByText("0/200")).toBeTruthy();
    expect(screen.getByRole("button", { name: "＋ 创建 Capture" }).hasAttribute("disabled")).toBe(true);

    fireEvent.change(titleInput, { target: { value: "新的采集需求" } });
    fireEvent.change(within(dialog).getByLabelText("一句话描述"), { target: { value: "需要补充上下文" } });
    fireEvent.change(within(dialog).getByLabelText("负责人"), { target: { value: "研发团队" } });
    fireEvent.change(within(dialog).getByLabelText("来源"), { target: { value: "user-feedback" } });
    expect(screen.getByText("7/200")).toBeTruthy();
    fireEvent.keyDown(dialog, { key: "Enter", ctrlKey: true });

    await waitFor(() => expect(screen.queryByRole("dialog", { name: "新建 Capture" })).toBeNull());
    expect(screen.getByText("新的采集需求")).toBeTruthy();
    expect(Array.from(document.querySelectorAll(".rc-owner-tag")).some((tag) => tag.textContent === "研发团队")).toBe(true);
    expect(screen.getByText("更新 刚刚")).toBeTruthy();
    expect(screen.getByRole("status").textContent).toContain("Capture 已创建");
  });

  it("opens markdown in a right drawer, html in a new tab and routes the floating agent assistant through its action modal", async () => {
    const openSpy = vi.spyOn(window, "open").mockImplementation(() => null);
    const fixture = {
      ...contextFixture,
      issues: [
        {
          ...contextFixture.issues[0],
          stage: "planning",
          documents: ["requirement.md", "prototype.html", "trace.md"],
          document_entries: [
            { name: "requirement.md", type: "markdown", open_mode: "drawer", label: "requirement.md", url: "/api/v1/requirement-center/issues/REQ-0012/documents/requirement.md" },
            { name: "prototype.html", type: "html", open_mode: "new-tab", label: "prototype.html", url: "/api/v1/requirement-center/issues/REQ-0012/documents/prototype.html/preview" },
          ],
        },
      ],
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, status: 200, json: () => Promise.resolve({ data: fixture }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: () => Promise.resolve({ data: { content: "# PRD\n正文" } }) });
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");
    fireEvent.click(screen.getByRole("button", { name: /requirement.md/ }));
    expect(await screen.findByTestId("markdown-drawer")).toBeTruthy();
    expect(screen.getByRole("heading", { name: "PRD" })).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "关闭右侧抽屉" }));
    fireEvent.click(screen.getByRole("button", { name: /prototype.html/ }));
    expect(openSpy).toHaveBeenCalledWith("/api/v1/requirement-center/issues/REQ-0012/documents/prototype.html/preview", "_blank", "noopener,noreferrer");

    fireEvent.click(screen.getByRole("button", { name: "打开 Agent 助手" }));
    const dialog = screen.getByRole("dialog", { name: "Agent 助手" });
    expect(within(dialog).getByText("Requirement Operations")).toBeTruthy();
    expect(within(dialog).getByText("待开发")).toBeTruthy();
    expect(within(dialog).getByText(/REQ-0012/)).toBeTruthy();

    fireEvent.mouseDown(within(dialog).getByText("Requirement Operations"));
    expect(screen.getByRole("dialog", { name: "Agent 助手" })).toBeTruthy();
    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.queryByRole("dialog", { name: "Agent 助手" })).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "打开 Agent 助手" }));
    const reopenedDialog = screen.getByRole("dialog", { name: "Agent 助手" });
    fireEvent.click(within(reopenedDialog).getByRole("button", { name: "完善需求 →" }));
    await waitFor(() => expect(screen.queryByRole("dialog", { name: "Agent 助手" })).toBeNull());
    const actionDialog = screen.getByRole("dialog", { name: "完善需求" });
    expect(within(actionDialog).getByText("/req-complete REQ-0012")).toBeTruthy();
    expect(within(actionDialog).getByText("本次将生成 / 更新")).toBeTruthy();
    fireEvent.click(within(actionDialog).getByRole("button", { name: "生成完善文档 →" }));
    await waitFor(() => expect(screen.getByRole("status").textContent).toContain("已流转到 待评审"));
  });

  it("edits only capture.md in capture stage and guards dirty markdown drawer close", async () => {
    const fixture = {
      ...contextFixture,
      issues: [
        {
          id: "REQ-0199",
          type: "requirement",
          title: "采集池可编辑 Capture",
          priority: "P1",
          owner: "产品团队",
          source: "capture",
          stage: "capture",
          documents: ["capture.md", "trace.md"],
          document_entries: [
            { name: "capture.md", type: "markdown", open_mode: "drawer", label: "capture.md", editable: true, url: "/api/v1/requirement-center/issues/REQ-0199-full/documents/capture.md" },
            { name: "trace.md", type: "markdown", open_mode: "drawer", label: "trace.md", editable: false, url: "/api/v1/requirement-center/issues/REQ-0199-full/documents/trace.md" },
          ],
          updated_at: "12:35",
        },
      ],
    };
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/context")) {
        return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: fixture }) });
      }
      if (init?.method === "PUT") {
        expect(url).toContain("/capture.md");
        expect(init.body).toContain("更新后的 capture");
        expect(init.body).toContain("req_id: REQ-0199");
        expect(init.body).toContain("status: captured");
        return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: { content: "---\nreq_id: REQ-0199\nstatus: captured\n---\n\n# 更新后的 capture" } }) });
      }
      if (url.includes("trace.md")) {
        return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: { content: "# trace read only" } }) });
      }
      return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: { content: "---\nreq_id: REQ-0199\nstatus: captured\n---\n\n# old capture\n\n一句话内容" } }) });
    });
    vi.stubGlobal("fetch", fetchMock);
    const confirmSpy = vi.spyOn(window, "confirm").mockReturnValueOnce(false).mockReturnValueOnce(true);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0199");
    fireEvent.click(screen.getByRole("button", { name: /capture.md/ }));

    expect(await screen.findByRole("heading", { name: "old capture" })).toBeTruthy();
    expect(screen.queryByText("Capture Brief")).toBeNull();
    expect(screen.queryByText(/当前预览以安全文本方式/)).toBeNull();
    expect(screen.queryByLabelText("Frontmatter 摘要")).toBeNull();
    expect(screen.queryByRole("button", { name: /元信息/ })).toBeNull();
    expect(screen.queryByText("文档内容")).toBeNull();
    expect(screen.getByText("P1 · 产品团队负责 · 采集池")).toBeTruthy();
    expect(screen.queryByText("预览 capture.md")).toBeNull();
    expect(screen.queryByTestId("markdown-drawer-spec")).toBeNull();
    expect(screen.getByRole("button", { name: /文档属性.*展开/ })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: /文档属性.*展开/ }));
    expect(within(screen.getByLabelText("Frontmatter 摘要")).getByText("REQ-0199")).toBeTruthy();
    expect(screen.queryByText("对象")).toBeNull();
    expect(within(screen.getByLabelText("Frontmatter 摘要")).getByText("REQ-0199")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: /文档属性.*收起/ }));
    expect(screen.queryByLabelText("Frontmatter 摘要")).toBeNull();
    expect(screen.queryByText(/---/)).toBeNull();
    expect(screen.queryByLabelText("编辑 capture.md")).toBeNull();
    expect(screen.getByRole("group", { name: "Markdown 查看模式" })).toBeTruthy();
    expect(screen.getByTestId("markdown-rendered-preview")).toBeTruthy();
    expect(screen.queryByRole("toolbar", { name: "Vditor Markdown 工具栏" })).toBeNull();
    expect(screen.queryByText("Markdown Source")).toBeNull();
    expect(screen.queryByText("Live Preview")).toBeNull();
    expect(screen.getByRole("button", { name: "编辑" })).toBeTruthy();
    expect(document.querySelector(".rc-drawer-backdrop")).toBeTruthy();
    expect(document.querySelector(".rc-drawer")?.getAttribute("style")).toContain("width: 760px");
    expect(screen.getByRole("button", { name: "放大右侧抽屉" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "放大右侧抽屉" }));
    expect(document.querySelector(".rc-drawer")?.classList.contains("fullscreen")).toBe(true);
    expect(screen.queryByRole("button", { name: "调整右侧抽屉宽度" })).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "恢复右侧抽屉" }));
    expect(document.querySelector(".rc-drawer")?.classList.contains("fullscreen")).toBe(false);
    expect(document.querySelector(".rc-drawer")?.getAttribute("style")).toContain("width: 760px");

    fireEvent.mouseDown(screen.getByRole("button", { name: "调整右侧抽屉宽度" }), { clientX: 900 });
    fireEvent.mouseMove(document, { clientX: 1250 });
    await waitFor(() => expect(document.querySelector(".rc-drawer")?.getAttribute("style")).toContain("420px"));
    fireEvent.mouseUp(document);

    fireEvent.click(screen.getByRole("button", { name: "编辑" }));
    const editor = await screen.findByLabelText("编辑 capture.md");
    expect((editor as HTMLTextAreaElement).value).toBe("# old capture\n\n一句话内容");
    expect((editor as HTMLTextAreaElement).value).not.toContain("req_id: REQ-0199");
    expect(screen.getByRole("button", { name: "编辑" }).classList.contains("active")).toBe(true);
    expect(screen.getByTestId("vditor-editor-shell")).toBeTruthy();
    expect(screen.getByRole("toolbar", { name: "Vditor Markdown 工具栏" })).toBeTruthy();
    expect(screen.queryByText("Markdown Source")).toBeNull();
    expect(screen.queryByText("Live Preview")).toBeNull();
    expect(screen.queryByTestId("vditor-upload-state")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "分栏" }));
    expect(screen.getByRole("button", { name: "分栏" }).classList.contains("active")).toBe(true);
    expect(screen.queryByText("Markdown Source")).toBeNull();
    expect(screen.queryByText("Live Preview")).toBeNull();
    fireEvent.change(editor, { target: { value: "alpha\nomega" } });
    (editor as HTMLTextAreaElement).setSelectionRange(6, 6);
    fireEvent.click(screen.getByRole("button", { name: "插入表格" }));
    await waitFor(() => expect((editor as HTMLTextAreaElement).value).toContain("alpha\n| 列 1 | 列 2 |\n| --- | --- |\n| 内容 | 内容 |\n\nomega"));
    await waitFor(() => expect(document.activeElement).toBe(editor));
    await waitFor(() => expect((editor as HTMLTextAreaElement).selectionStart).toBeGreaterThan("alpha\n".length));
    expect((editor as HTMLTextAreaElement).selectionStart).toBeLessThan((editor as HTMLTextAreaElement).value.indexOf("omega"));
    const omegaStart = (editor as HTMLTextAreaElement).value.indexOf("omega");
    (editor as HTMLTextAreaElement).setSelectionRange(omegaStart, omegaStart + "omega".length);
    fireEvent.click(screen.getByRole("button", { name: "插入代码块" }));
    await waitFor(() => expect((editor as HTMLTextAreaElement).value).toContain("```ts\nomega\n```"));
    expect(document.activeElement).toBe(editor);
    const codeBlockStart = (editor as HTMLTextAreaElement).value.indexOf("```ts");
    const codeBlockEnd = (editor as HTMLTextAreaElement).value.indexOf("```", codeBlockStart + 3) + 4;
    expect((editor as HTMLTextAreaElement).selectionStart).toBeGreaterThan(codeBlockStart);
    expect((editor as HTMLTextAreaElement).selectionStart).toBeLessThanOrEqual(codeBlockEnd);
    const endPosition = (editor as HTMLTextAreaElement).value.length;
    (editor as HTMLTextAreaElement).setSelectionRange(endPosition, endPosition);
    fireEvent.click(screen.getByRole("button", { name: "插入数学公式" }));
    await waitFor(() => expect((editor as HTMLTextAreaElement).value).toContain("$$\nE = mc^2\n$$"));
    const formulaStart = (editor as HTMLTextAreaElement).value.lastIndexOf("$$\nE = mc^2");
    const formulaEnd = (editor as HTMLTextAreaElement).value.lastIndexOf("$$") + 2;
    expect((editor as HTMLTextAreaElement).selectionStart).toBeGreaterThanOrEqual(formulaStart);
    expect((editor as HTMLTextAreaElement).selectionStart).toBeLessThanOrEqual(formulaEnd + 1);
    expect(within(screen.getByTestId("markdown-rendered-preview")).getByText("列 1")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "插入图片" }));
    expect(screen.getByTestId("vditor-upload-state").textContent).toContain("暂不可用");
    expect(screen.getByTestId("vditor-upload-state").textContent).toContain("文档图片上传接口暂未启用");
    fireEvent.change(editor, { target: { value: "# 未保存 capture" } });
    fireEvent.click(screen.getByRole("button", { name: "关闭右侧抽屉蒙层" }));
    expect(confirmSpy).toHaveBeenCalledWith("capture.md 有未保存修改，确认关闭？");
    expect(screen.getByLabelText("编辑 capture.md")).toBeTruthy();

    fireEvent.change(editor, { target: { value: "# 更新后的 capture" } });
    fireEvent.click(screen.getAllByRole("button").find((button) => button.textContent?.trim() === "保存") as HTMLElement);
    expect(await screen.findByText("capture.md 已保存")).toBeTruthy();
    expect(await screen.findByRole("heading", { name: "更新后的 capture" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "预览" }).classList.contains("active")).toBe(true);
    expect(screen.queryByLabelText("编辑 capture.md")).toBeNull();
    expect(screen.getByRole("button", { name: "编辑" })).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "关闭右侧抽屉" }));
    fireEvent.click(screen.getByRole("button", { name: /trace.md/ }));
    expect(await screen.findByRole("heading", { name: "trace read only" })).toBeTruthy();
    expect(screen.getByText("P1 · 产品团队负责 · 采集池")).toBeTruthy();
    expect(screen.queryByRole("group", { name: "Markdown 查看模式" })).toBeNull();
    expect(screen.queryByLabelText("编辑 capture.md")).toBeNull();
  });

  it("copies rendered markdown code blocks without markdown fences", async () => {
    const fixture = {
      ...contextFixture,
      issues: [
        {
          id: "REQ-0202",
          type: "requirement",
          title: "只读代码复制",
          priority: "P1",
          owner: "产品团队",
          source: "capture",
          stage: "capture",
          documents: ["trace.md"],
          document_entries: [{ name: "trace.md", type: "markdown", open_mode: "drawer", label: "trace.md", editable: false, url: "/api/v1/requirement-center/issues/REQ-0202-full/documents/trace.md" }],
          updated_at: "12:38",
        },
      ],
    };
    const writeText = vi.fn(() => Promise.resolve());
    vi.stubGlobal("navigator", { ...navigator, clipboard: { writeText } });
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/context")) {
        return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: fixture }) });
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: { content: "# trace\n\n```bash\npnpm test\npnpm build\n```" } }),
      });
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0202");
    const reqCard = document.querySelector('[data-issue-id="REQ-0202"]') as HTMLElement;
    fireEvent.click(within(reqCard).getByRole("button", { name: /trace.md/ }));
    await waitFor(() => expect(screen.getByTestId("markdown-rendered-preview").textContent).toContain("pnpm test"));
    fireEvent.click(screen.getByRole("button", { name: "复制代码块" }));

    await waitFor(() => expect(writeText).toHaveBeenCalledWith("pnpm test\npnpm build"));
    expect(screen.getByRole("button", { name: "复制代码块" }).textContent).toContain("已复制");
    expect(screen.queryByRole("group", { name: "Markdown 查看模式" })).toBeNull();
  });

  it("does not warn when closing read-only markdown or untouched capture.md", async () => {
    const fixture = {
      ...contextFixture,
      issues: [
        {
          id: "REQ-0198",
          type: "requirement",
          title: "关闭确认边界",
          priority: "P1",
          owner: "产品团队",
          source: "capture",
          stage: "capture",
          documents: ["capture.md", "trace.md"],
          document_entries: [
            { name: "capture.md", type: "markdown", open_mode: "drawer", label: "capture.md", editable: true, url: "/api/v1/requirement-center/issues/REQ-0198-full/documents/capture.md" },
            { name: "trace.md", type: "markdown", open_mode: "drawer", label: "trace.md", editable: false, url: "/api/v1/requirement-center/issues/REQ-0198-full/documents/trace.md" },
          ],
          updated_at: "12:34",
        },
      ],
    };
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/context")) {
        return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: fixture }) });
      }
      if (url.includes("trace.md")) {
        return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: { content: "---\nreq_id: REQ-0198\n---\n\n# trace read only" } }) });
      }
      return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: { content: "---\nreq_id: REQ-0198\nstatus: captured\n---\n\n# untouched capture" } }) });
    });
    vi.stubGlobal("fetch", fetchMock);
    const confirmSpy = vi.spyOn(window, "confirm").mockReturnValue(true);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0198");

    fireEvent.click(screen.getByRole("button", { name: /trace.md/ }));
    expect(await screen.findByRole("heading", { name: "trace read only" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "关闭右侧抽屉" }));
    expect(confirmSpy).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: /capture.md/ }));
    expect(await screen.findByRole("heading", { name: "untouched capture" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "关闭右侧抽屉" }));
    expect(confirmSpy).not.toHaveBeenCalled();
  });

  it("keeps markdown draft visible when capture.md save fails", async () => {
    const fixture = {
      ...contextFixture,
      issues: [
        {
          id: "REQ-0200",
          type: "requirement",
          title: "采集池保存失败",
          priority: "P1",
          owner: "产品团队",
          source: "capture",
          stage: "capture",
          documents: ["capture.md"],
          document_entries: [{ name: "capture.md", type: "markdown", open_mode: "drawer", label: "capture.md", editable: true, url: "/api/v1/requirement-center/issues/REQ-0200-full/documents/capture.md" }],
          updated_at: "12:36",
        },
      ],
    };
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/context")) {
        return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: fixture }) });
      }
      if (init?.method === "PUT") {
        return Promise.resolve({
          ok: false,
          status: 503,
          json: () => Promise.resolve({ detail: "文档保存失败，治理目录暂不可写" }),
        });
      }
      return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: { content: "---\nreq_id: REQ-0200\nstatus: captured\n---\n\n# old capture" } }) });
    });
    vi.stubGlobal("fetch", fetchMock);
    const confirmSpy = vi.spyOn(window, "confirm").mockReturnValueOnce(false);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0200");
    fireEvent.click(screen.getByRole("button", { name: /capture.md/ }));
    fireEvent.click(await screen.findByRole("button", { name: "编辑" }));
    const editor = await screen.findByLabelText("编辑 capture.md");
    fireEvent.change(editor, { target: { value: "# 失败也保留" } });
    fireEvent.click(screen.getAllByRole("button").find((button) => button.textContent?.trim() === "保存") as HTMLElement);

    expect((await screen.findAllByText("文档保存失败，治理目录暂不可写")).length).toBeGreaterThan(0);
    expect(screen.getByLabelText("编辑 capture.md")).toBeTruthy();
    expect((screen.getByLabelText("编辑 capture.md") as HTMLTextAreaElement).value).toBe("# 失败也保留");
    expect(screen.getByRole("button", { name: "编辑" }).classList.contains("active")).toBe(true);
    expect(screen.queryByText("预览 capture.md")).toBeNull();
    expect(screen.queryByRole("heading", { name: "失败也保留" })).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "关闭右侧抽屉" }));
    expect(confirmSpy).toHaveBeenCalledWith("capture.md 有未保存修改，确认关闭？");
    expect(screen.getByLabelText("编辑 capture.md")).toBeTruthy();
  });

  it("renders capture.md task lists as preview checkboxes and saves markdown state", async () => {
    const fixture = {
      ...contextFixture,
      issues: [
        {
          id: "REQ-0201",
          type: "requirement",
          title: "采集池任务清单",
          priority: "P1",
          owner: "产品团队",
          source: "capture",
          stage: "capture",
          documents: ["capture.md"],
          document_entries: [{ name: "capture.md", type: "markdown", open_mode: "drawer", label: "capture.md", editable: true, url: "/api/v1/requirement-center/issues/REQ-0201-full/documents/capture.md" }],
          updated_at: "12:37",
        },
      ],
    };
    let shouldFailSave = false;
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/context")) {
        return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: fixture }) });
      }
      if (init?.method === "PUT") {
        const body = String(init.body);
        expect(body).toContain("- [x] MVP 是否先支持");
        expect(body).toContain("- [x] 已完成事项");
        if (shouldFailSave) {
          return Promise.resolve({ ok: false, status: 503, json: () => Promise.resolve({ detail: "文档保存失败，治理目录暂不可写" }) });
        }
        return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: { content: "---\nreq_id: REQ-0201\nstatus: captured\n---\n\n# 待澄清\n\n- [x] MVP 是否先支持\n- [x] 已完成事项" } }) });
      }
      return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: { content: "---\nreq_id: REQ-0201\nstatus: captured\n---\n\n# 待澄清\n\n- [ ] MVP 是否先支持\n- [x] 已完成事项" } }) });
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0201");
    fireEvent.click(screen.getByRole("button", { name: /capture.md/ }));
    const todo = await screen.findByRole("checkbox", { name: /MVP 是否先支持/ });
    const done = screen.getByRole("checkbox", { name: /已完成事项/ });
    expect((todo as HTMLInputElement).checked).toBe(false);
    expect((done as HTMLInputElement).checked).toBe(true);

    fireEvent.click(todo);
    expect((screen.getByRole("checkbox", { name: /MVP 是否先支持/ }) as HTMLInputElement).checked).toBe(true);
    expect(screen.getByText("有未保存修改")).toBeTruthy();

    shouldFailSave = true;
    fireEvent.click(screen.getAllByRole("button").find((button) => button.textContent?.trim() === "保存") as HTMLElement);
    expect((await screen.findAllByText("文档保存失败，治理目录暂不可写")).length).toBeGreaterThan(0);
    expect((screen.getByRole("checkbox", { name: /MVP 是否先支持/ }) as HTMLInputElement).checked).toBe(true);

    shouldFailSave = false;
    fireEvent.click(screen.getAllByRole("button").find((button) => button.textContent?.trim() === "保存") as HTMLElement);
    expect(await screen.findByText("capture.md 已保存")).toBeTruthy();
    expect(screen.getByText("刚刚保存")).toBeTruthy();
  });

  it("uses task_toggle_only capability for acceptance tasks without opening the full editor", async () => {
    const fixture = {
      ...contextFixture,
      issues: [
        {
          id: "REQ-0203",
          type: "requirement",
          title: "验收中仅勾选任务",
          priority: "P1",
          owner: "产品团队",
          source: "review",
          stage: "acceptance",
          documents: ["tasks.md", "trace.md"],
          document_entries: [
            {
              name: "tasks.md",
              type: "markdown",
              open_mode: "drawer",
              label: "tasks.md",
              editable: false,
              capability: { readable: true, human_editable: false, ai_mutable: true, task_toggle_only: true, reason: "验收中 tasks.md 仅允许勾选或取消勾选任务" },
              url: "/api/v1/requirement-center/changes/update-toggle/documents/tasks.md",
            },
            {
              name: "trace.md",
              type: "markdown",
              open_mode: "drawer",
              label: "trace.md",
              editable: false,
              capability: { readable: true, human_editable: false, ai_mutable: true, task_toggle_only: false, reason: "trace.md 仅允许系统治理链路更新，人工始终只读" },
              url: "/api/v1/requirement-center/changes/update-toggle/documents/trace.md",
            },
          ],
          updated_at: "12:39",
        },
      ],
    };
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/context")) {
        return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: fixture }) });
      }
      if (init?.method === "PUT") {
        expect(url).toBe("/api/v1/requirement-center/changes/update-toggle/documents/tasks.md/tasks");
        expect(String(init.body)).toContain("- [x] 完成验收复核");
        return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: { content: "# Tasks\n\n- [x] 完成验收复核\n- [x] 保持已完成" } }) });
      }
      return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: { content: "# Tasks\n\n- [ ] 完成验收复核\n- [x] 保持已完成" } }) });
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0203");
    fireEvent.click(screen.getByRole("button", { name: /tasks.md/ }));

    const todo = await screen.findByRole("checkbox", { name: /完成验收复核/ });
    expect(screen.queryByRole("group", { name: "Markdown 查看模式" })).toBeNull();
    expect(screen.queryByRole("toolbar", { name: "Vditor Markdown 工具栏" })).toBeNull();
    expect(screen.queryByLabelText("编辑 tasks.md")).toBeNull();
    expect(screen.getByText(/仅允许勾选任务/)).toBeTruthy();

    fireEvent.click(todo);
    expect(screen.getByText("有未保存修改")).toBeTruthy();
    fireEvent.click(screen.getAllByRole("button").find((button) => button.textContent?.trim() === "保存") as HTMLElement);
    expect(await screen.findByText("tasks.md 已保存")).toBeTruthy();
  });

  it("opens tasks progress drawer and validates generation imports", async () => {
    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    fireEvent.click(screen.getAllByRole("button", { name: /研发 0\/36/ })[0]);
    const tasksDrawer = screen.getByTestId("tasks-drawer");
    expect(tasksDrawer).toBeTruthy();
    expect(within(tasksDrawer).getByText("0/36")).toBeTruthy();
    expect(screen.getByLabelText("研发任务进度").className).toContain("active");

    fireEvent.click(screen.getByRole("button", { name: "关闭右侧抽屉" }));
    fireEvent.click(screen.getByRole("button", { name: "测试 1/3" }));
    const testTasksDrawer = screen.getByTestId("tasks-drawer");
    expect(testTasksDrawer).toBeTruthy();
    expect(screen.getByLabelText("自动化测试进度").className).toContain("active");
    expect(within(testTasksDrawer).getByText("1/3")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "关闭右侧抽屉" }));
    fireEvent.click(screen.getByRole("button", { name: "人工验收 0/1" }));
    expect(screen.getByTestId("tasks-drawer")).toBeTruthy();
    expect(screen.getByLabelText("人工验收进度").className).toContain("active");
    expect(screen.getByText("仍有 1 项需要人工处理")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "关闭右侧抽屉" }));
    fireEvent.click(screen.getByRole("button", { name: "新建 Capture" }));
    fireEvent.click(within(screen.getByRole("group", { name: "Capture 类型" })).getByRole("button", { name: "◈ Bug" }));
    fireEvent.change(screen.getByLabelText("Capture 标题"), { target: { value: "导入校验 Bug" } });
    fireEvent.click(screen.getByRole("button", { name: "＋ 创建 Capture" }));
    fireEvent.click(screen.getByRole("button", { name: "生成 Bug →" }));
    const actionDialog = screen.getByRole("dialog", { name: "生成 Bug" });
    expect(within(actionDialog).getByText(/\/bug-generate/)).toBeTruthy();
    expect(within(actionDialog).getByText("bug.md")).toBeTruthy();
    expect(within(actionDialog).queryByLabelText("导入文件")).toBeNull();
    fireEvent.click(within(actionDialog).getByRole("button", { name: "生成 Bug，进入规划中 →" }));
    await waitFor(() => expect(screen.getByRole("status").textContent).toContain("已流转到 规划中"));
  });

  it("opens the unified progress drawer from acceptance Requirement and Bug progress entries", async () => {
    window.history.replaceState(null, "", "/requirements?mock=workflow");
    render(<RequirementCenterPage />);
    await screen.findByText("DEMO-REQ-ACCEPTANCE-READY");

    const reqCard = document.querySelector('[data-issue-id="DEMO-REQ-ACCEPTANCE-READY"]') as HTMLElement;
    fireEvent.click(within(reqCard).getByRole("button", { name: "测试 3/3" }));
    let drawer = screen.getByTestId("tasks-drawer");
    expect(screen.getByLabelText("自动化测试进度").className).toContain("active");
    expect(within(screen.getByLabelText("自动化测试进度")).getByText("3/3")).toBeTruthy();
    expect(within(drawer).getByText("暂无待处理人工验收项")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "关闭右侧抽屉" }));
    fireEvent.click(within(reqCard).getByRole("button", { name: "人工验收 1/1" }));
    drawer = screen.getByTestId("tasks-drawer");
    expect(screen.getByLabelText("人工验收进度").className).toContain("active");
    expect(within(drawer).getByText("7/7")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "关闭右侧抽屉" }));
    const bugCard = document.querySelector('[data-issue-id="DEMO-BUG-ACCEPTANCE-BLOCKED"]') as HTMLElement;
    fireEvent.click(within(bugCard).getByRole("button", { name: "人工验收 0/1" }));
    drawer = screen.getByTestId("tasks-drawer");
    expect(screen.getByLabelText("人工验收进度").className).toContain("active");
    expect(within(drawer).getByText("仍有 1 项需要人工处理")).toBeTruthy();
    expect(within(drawer).getByText("等待人工验收")).toBeTruthy();
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
    expect(screen.getByTestId("space-switcher-popover")).toBeTruthy();
    expect(document.querySelector(".rc-space-list button")).toBeTruthy();
    expect(screen.getByTestId("space-option-moonbox-platform").getAttribute("data-current")).toBe("true");
    expect(screen.getByTestId("space-option-moonbox-growth").getAttribute("data-readonly")).toBe("true");
    expect(screen.getByTestId("space-frozen-badge").textContent).toBe("只读");
    const source = readFileSync("src/styles/globals.css", "utf8");
    expect(source).toContain(".rc-space-list button:hover");
    expect(source).toContain(".rc-space-list button.selected::before");
    expect(source).toContain(".rc-space-state.error");
    expect(source).toContain(".rc-space-status");
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
    expect(screen.getByRole("button", { name: /许同学/ }).textContent).toContain("Growth Studio");
  });

  it("opens the create-space modal and submits a pending workspace application", async () => {
    seedFrontendTokenSession();
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/v1/catalog/workspace-applications/create")) {
        expect(init?.method).toBe("POST");
        expect(init?.headers).toMatchObject({ authorization: "Bearer front-token" });
        expect(init?.body).toContain("\"member_quota\":20");
        expect(init?.body).toContain("\"storage_quota_gb\":100");
        expect(init?.body).toContain("\"ai_quota_tokens\":1000000");
        expect(init?.body).toContain("\"expiry_type\":\"fixed_date\"");
        expect(init?.body).toContain("\"expires_at\"");
        return Promise.resolve({
          ok: true,
          status: 201,
          json: () => Promise.resolve({ data: { application: { id: "space_app_1", name: "MoonBox Product", code: "moonbox-product", status: "待审批" } } }),
        });
      }
      return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ data: contextFixture }) });
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");
    fireEvent.click(screen.getByRole("button", { name: /许同学/ }));
    fireEvent.mouseEnter(screen.getByRole("menuitem", { name: /切换空间/ }));
    fireEvent.click(screen.getByTestId("space-create-or-join-entry"));

    expect(screen.getByRole("dialog", { name: "创建空间" })).toBeTruthy();
    expect(screen.queryByText("加入空间")).toBeNull();
    expect(screen.getByText("每个空间对应一个产品，成员与数据相互隔离；提交后进入平台管理员审批，通过后系统会创建空间并分配你为负责人。")).toBeTruthy();
    expect(screen.queryByText("创建空间申请提交后将进入平台管理员审批，审批通过后系统会创建空间并分配你为负责人。")).toBeNull();
    expect(screen.getByLabelText("成员上限").getAttribute("max")).toBe("100000");
    expect(screen.getByLabelText("存储空间").getAttribute("min")).toBe("0.01");
    expect(screen.getByLabelText("AI Tokens").nextElementSibling).toBeNull();
    expect(screen.getByLabelText("到期时间")).toBeTruthy();
    expect((screen.getByLabelText("到期时间") as HTMLInputElement).value).toMatch(/\d{4}-\d{2}-\d{2} 23:59:59/);
    const picker = screen.getByTestId("catalog-datetime-picker");
    vi.spyOn(picker, "getBoundingClientRect").mockReturnValue({
      x: 691,
      y: 720,
      top: 720,
      left: 691,
      right: 1040,
      bottom: 760,
      width: 349,
      height: 40,
      toJSON: () => ({}),
    } as DOMRect);
    Object.defineProperty(window, "innerHeight", { configurable: true, value: 900 });
    Object.defineProperty(window, "innerWidth", { configurable: true, value: 1440 });
    fireEvent.click(screen.getByRole("button", { name: "选择到期时间" }));
    const dateTimePanel = screen.getByRole("dialog", { name: "到期时间选择器" });
    expect(dateTimePanel.getAttribute("data-placement")).toBe("top");
    expect(Number((dateTimePanel as HTMLElement).style.top.replace("px", ""))).toBeLessThan(720);
    expect(within(dateTimePanel).queryByRole("button", { name: "取消" })).toBeNull();
    expect(within(dateTimePanel).queryByRole("button", { name: "确定" })).toBeNull();
    const initialExpiryValue = (screen.getByLabelText("到期时间") as HTMLInputElement).value;
    fireEvent.mouseDown(screen.getByLabelText("空间说明"));
    expect(screen.queryByRole("dialog", { name: "到期时间选择器" })).toBeNull();
    expect((screen.getByLabelText("到期时间") as HTMLInputElement).value).toBe(initialExpiryValue);
    fireEvent.click(screen.getByRole("button", { name: "选择到期时间" }));
    expect(screen.getByRole("dialog", { name: "到期时间选择器" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "选择到期时间" }));
    expect(screen.queryByRole("dialog", { name: "到期时间选择器" })).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "选择到期时间" }));
    const reopenedDateTimePanel = screen.getByRole("dialog", { name: "到期时间选择器" });
    fireEvent.click(within(reopenedDateTimePanel).getByRole("button", { name: "本季度末" }));
    expect(screen.queryByRole("dialog", { name: "到期时间选择器" })).toBeNull();
    fireEvent.change(screen.getByLabelText("空间名称"), { target: { value: "MoonBox Product" } });
    expect(screen.getByLabelText("空间标识").getAttribute("value")).toBe("moonbox-product");
    fireEvent.change(screen.getByLabelText("空间说明"), { target: { value: "研发协作空间" } });
    fireEvent.click(screen.getByRole("button", { name: "创建空间" }));

    await screen.findByText("MoonBox Product 申请已提交");
    expect(screen.getByText(/待平台管理员审批后才可使用/)).toBeTruthy();
    expect(screen.getByRole("button", { name: "知道了" })).toBeTruthy();
  });

  it("clears a stale recent workspace and falls back to the API selected workspace", async () => {
    window.localStorage.setItem(
      "moonbox.workspace",
      JSON.stringify({ workspaceId: "removed-space", name: "Removed Space" }),
    );

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");

    expect(JSON.parse(window.localStorage.getItem("moonbox.workspace") || "{}").workspaceId).toBe("moonbox-platform");
    expect(screen.getByRole("button", { name: /许同学/ }).textContent).toContain("Platform Operations");
    expect(screen.queryByText("Removed Space")).toBeNull();
  });

  it("shows an empty space state without rendering stale mock workspaces", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ data: { ...contextFixture, workspaces: [], selected_workspace_id: "" } }),
        }),
      ),
    );

    render(<RequirementCenterPage />);
    await screen.findByText("REQ-0012");
    fireEvent.click(screen.getByRole("button", { name: /许同学/ }));
    fireEvent.mouseEnter(screen.getByRole("menuitem", { name: /切换空间/ }));

    expect(screen.getByTestId("space-empty-state").textContent).toBe("暂无空间");
    expect(screen.queryByText("Platform Operations")).toBeNull();
    expect(window.localStorage.getItem("moonbox.workspace")).toBeNull();
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

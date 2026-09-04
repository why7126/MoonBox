import playwright from "../../../../../src/web/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.js";
import { writeFile } from "node:fs/promises";

const baseUrl = "http://127.0.0.1:5174";
const outDir = new URL("./", import.meta.url);
const { chromium } = playwright;

const users = [
  {
    id: "user_superadmin",
    username: "superadmin",
    nickname: "平台超级管理员",
    avatar_url: null,
    role: "后台管理员",
    status: "正常",
    status_before_freeze: null,
    workspace_count: 0,
    last_login_at: "2026-08-06T07:30:00Z",
    is_system_superadmin: true,
    session_invalidated_at: null,
    created_at: "2026-07-01 00:00:00",
    updated_at: "2026-08-06 07:30:00",
  },
  {
    id: "user_chenmo",
    username: "chenmo",
    nickname: "陈默",
    avatar_url: null,
    role: "后台管理员",
    status: "正常",
    status_before_freeze: null,
    workspace_count: 3,
    last_login_at: "2026-08-06 18:42:13",
    is_system_superadmin: false,
    session_invalidated_at: null,
    created_at: "2026-07-18 09:24:36",
    updated_at: "2026-08-06 18:42:13",
  },
  {
    id: "user_linyu",
    username: "linyu",
    nickname: "林宇",
    avatar_url: null,
    role: "前台用户",
    status: "已冻结",
    status_before_freeze: "待激活",
    workspace_count: 2,
    last_login_at: "2026-08-06 17:05:48",
    is_system_superadmin: false,
    session_invalidated_at: "2026-08-06 17:06:00",
    created_at: "2026-07-22 14:11:07",
    updated_at: "2026-08-06 17:06:00",
  },
];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 920 } });
await page.addInitScript(() => {
  window.localStorage.setItem("moonbox.session", JSON.stringify({
    username: "founder",
    started_at: "2026-08-11T00:00:00.000Z",
    access_token: "front-token",
    expires_at: "2026-12-31 23:59:59",
    user: {
      id: "admin",
      username: "admin",
      nickname: "平台管理员",
      role: "后台管理员",
      status: "正常",
      is_system_superadmin: true,
    },
  }));
});

await page.route("**/api/v1/admin/users?**", async (route) => {
  await route.fulfill({
    contentType: "application/json",
    body: JSON.stringify({ data: { items: users, total: users.length, page: 1, page_size: 10 } }),
  });
});
await page.route("**/api/v1/auth/me", async (route) => {
  await route.fulfill({
    contentType: "application/json",
    body: JSON.stringify({
      data: {
        user: {
          id: "admin",
          username: "admin",
          nickname: "平台管理员",
          avatar_url: null,
          role: "后台管理员",
          status: "正常",
          is_system_superadmin: true,
        },
      },
    }),
  });
});

await page.goto(`${baseUrl}/requirements?mock=workflow`, { waitUntil: "networkidle" });
await page.screenshot({ path: new URL("requirements-1440.png", outDir).pathname, fullPage: true });
await page.getByRole("button", { name: "新建 Capture" }).click();
await page.screenshot({ path: new URL("requirements-capture-modal-1440.png", outDir).pathname, fullPage: true });
const captureModalStyles = await collectStyles(page, [
  ".rc-capture-mask",
  ".rc-capture-dialog",
  ".rc-capture-dialog .rc-dialog-head",
  ".rc-capture-dialog .rc-dialog-head p",
  ".rc-capture-dialog .rc-dialog-head h2",
  ".rc-capture-dialog .rc-dialog-head span",
  ".rc-capture-body",
  ".rc-capture-fieldset",
  ".rc-capture-fieldset legend",
  ".rc-capture-fieldset legend b",
  ".rc-capture-dialog .rc-field-label",
  ".rc-capture-dialog .rc-field-label b",
  ".rc-capture-segmented",
  ".rc-capture-segmented button",
  ".rc-capture-segmented button.selected",
  ".rc-capture-segmented.priority",
  ".rc-capture-segmented.priority button",
  ".rc-capture-count",
  ".rc-capture-dialog input",
  ".rc-capture-dialog select",
  ".rc-capture-dialog textarea",
  ".rc-capture-dialog .rc-dialog-actions",
  ".rc-capture-dialog .rc-dialog-actions kbd",
  ".rc-capture-dialog .rc-primary-action",
]);
await page.keyboard.press("Escape");
await page.getByRole("button", { name: "打开 Agent 助手" }).click();
await page.screenshot({ path: new URL("requirements-agent-modal-1440.png", outDir).pathname, fullPage: true });
const agentAssistantStyles = await collectStyles(page, [
  ".rc-agent-fab",
  ".rc-agent-mask",
  ".rc-agent-dialog",
  ".rc-agent-dialog .rc-dialog-head",
  ".rc-agent-dialog .rc-dialog-head p",
  ".rc-agent-dialog .rc-dialog-head h2",
  ".rc-agent-dialog .rc-dialog-head span",
  ".rc-agent-body",
  ".rc-agent-stage",
  ".rc-agent-stage strong",
  ".rc-agent-stage p",
  ".rc-agent-count",
  ".rc-agent-stage small",
  ".rc-agent-stage button",
  ".rc-agent-dialog .rc-dialog-actions",
  ".rc-agent-dialog .rc-dialog-actions kbd",
]);
await page.keyboard.press("Escape");
await page.getByRole("button", { name: "需求分析" }).first().click();
await page.waitForTimeout(1000);
await page.screenshot({ path: new URL("requirements-action-analysis-modal-1440.png", outDir).pathname, fullPage: true });
const actionAnalysisStyles = await collectStyles(page, [
  ".rc-action-mask",
  ".rc-action-dialog",
  ".rc-action-dialog .rc-dialog-head",
  ".rc-action-dialog .rc-dialog-head p",
  ".rc-action-dialog .rc-dialog-head h2",
  ".rc-action-dialog .rc-dialog-head span",
  ".rc-action-body",
  ".rc-action-command",
  ".rc-action-analysis",
  ".rc-action-adopt-list",
  ".rc-action-dialog .rc-dialog-actions",
  ".rc-action-dialog .rc-primary-action",
]);
await page.getByRole("button", { name: /明确验收标准边界/ }).click();
await page.screenshot({ path: new URL("requirements-action-analysis-selection-1440.png", outDir).pathname, fullPage: true });
const actionAnalysisSelectionStyles = await collectStyles(page, [
  ".rc-action-adopt-list button",
  ".rc-action-adopt-list button.checked",
  ".rc-action-adopt-list button:not(.checked)",
  ".rc-action-adopt-list button span",
  ".rc-action-adopt-list button.checked span",
  ".rc-action-adopt-list button:not(.checked) span",
  ".rc-action-dialog .rc-primary-action",
]);
await page.keyboard.press("Escape");
await page.getByRole("button", { name: "生成需求 →" }).first().click();
await page.screenshot({ path: new URL("requirements-action-generate-modal-1440.png", outDir).pathname, fullPage: true });
const actionGenerateStyles = await collectStyles(page, [
  ".rc-action-command",
  ".rc-action-doc-list",
  ".rc-action-doc",
]);
await page.keyboard.press("Escape");
await page.getByRole("button", { name: "完善需求 →" }).first().click();
await page.getByRole("tab", { name: "导入文档" }).click();
await page.screenshot({ path: new URL("requirements-action-complete-modal-1440.png", outDir).pathname, fullPage: true });
const actionCompleteStyles = await collectStyles(page, [
  ".rc-action-tabs",
  ".rc-action-tabs button",
  ".rc-action-tabs button.active",
  ".rc-action-panel",
  ".rc-action-dropzone",
]);
await page.keyboard.press("Escape");
await page.getByRole("button", { name: "加入迭代 →" }).first().click();
await page.waitForTimeout(760);
await page.screenshot({ path: new URL("requirements-action-sprint-modal-1440.png", outDir).pathname, fullPage: true });
const actionSprintStyles = await collectStyles(page, [
  ".rc-action-dialog.sprint",
  ".rc-action-context",
  ".rc-sprint-context-strip",
  ".rc-action-estimate",
  ".rc-sprint-mode-toggle",
  ".rc-sprint-mode-toggle button.active",
  ".rc-sprint-options",
  ".rc-sprint-options button",
  ".rc-sprint-options button.selected",
  ".rc-sprint-options button.disabled",
  ".rc-sprint-option-name",
  ".rc-sprint-status-pill",
  ".rc-sprint-capacity-badge",
  ".rc-sprint-radio",
  ".rc-sprint-capacity-bar",
]);
await page.keyboard.press("Escape");
await page.getByRole("button", { name: "生成 Opsx →" }).first().click();
await page.waitForTimeout(1100);
await page.screenshot({ path: new URL("requirements-action-opsx-modal-1440.png", outDir).pathname, fullPage: true });
const actionOpsxStyles = await collectStyles(page, [
  ".rc-action-change-list",
  ".rc-action-change",
  ".rc-action-change-head",
]);
await page.keyboard.press("Escape");
await page.getByRole("button", { name: "查看进度 →" }).first().click();
await page.screenshot({ path: new URL("requirements-action-progress-modal-1440.png", outDir).pathname, fullPage: true });
const actionProgressStyles = await collectStyles(page, [
  ".rc-action-change",
  ".rc-action-change-head",
  ".rc-mini-bar",
  ".rc-mini-bar span",
]);
await page.keyboard.press("Escape");
await page.getByPlaceholder("搜索 ID、标题、文档或负责人").fill("DEMO-REQ-001");
await page.screenshot({ path: new URL("requirements-one-card-empty-columns-1440.png", outDir).pathname, fullPage: true });
await page.setViewportSize({ width: 1440, height: 430 });
await page.locator(".rc-column-body").first().evaluate((element) => {
  element.scrollTop = 120;
});
const stickyBoundaryMetrics = await page.evaluate(() => {
  const wrap = document.querySelector(".rc-board-wrap");
  const body = document.querySelector(".rc-column-body");
  const heads = Array.from(document.querySelectorAll(".rc-column-head")).slice(0, 4);
  const card = document.querySelector(".rc-card");
  const wrapRect = wrap?.getBoundingClientRect();
  const bodyRect = body?.getBoundingClientRect();
  const headRects = heads.map((head) => {
    const rect = head.getBoundingClientRect();
    return {
      left: rect.left,
      top: rect.top,
      bottom: rect.bottom,
    };
  });
  const cardRect = card?.getBoundingClientRect();
  return {
    boardWrapScrollTop: wrap?.scrollTop ?? null,
    columnBodyScrollTop: body?.scrollTop ?? null,
    boardWrapClientHeight: wrap?.clientHeight ?? null,
    boardWrapScrollHeight: wrap?.scrollHeight ?? null,
    boardWrapTop: wrapRect?.top ?? null,
    bodyTop: bodyRect?.top ?? null,
    bodyBottom: bodyRect?.bottom ?? null,
    headRects,
    firstHeadBottom: headRects[0]?.bottom ?? null,
    cardTop: cardRect?.top ?? null,
    cardBottom: cardRect?.bottom ?? null,
  };
});
await page.screenshot({ path: new URL("requirements-sticky-head-boundary-1440.png", outDir).pathname });
await page.locator(".rc-column-body").first().evaluate((element) => {
  element.scrollTop = 0;
});
await page.setViewportSize({ width: 1440, height: 920 });
const emptyColumnStyles = await collectStyles(page, [
  ".rc-column-head.empty",
  ".rc-column-head.empty h2",
  ".rc-column-head.empty p",
  ".rc-column-head.empty > span",
  ".rc-column-body.empty",
  ".rc-column-body.empty::before",
  ".rc-empty-stage",
  ".rc-empty-stage-icon",
  ".rc-empty-stage strong",
  ".rc-empty-stage p",
]);
await page.getByPlaceholder("搜索 ID、标题、文档或负责人").fill("");
await page.locator(".rc-board-wrap").evaluate((element) => {
  element.scrollLeft = 1180;
});
await page.screenshot({ path: new URL("requirements-board-scrolled-1440.png", outDir).pathname, fullPage: true });
await page.locator(".rc-board-wrap").evaluate((element) => {
  element.scrollLeft = 0;
});
await page.locator(".rc-filter-popover summary").click();
await page.screenshot({ path: new URL("requirements-filter-popover-1440.png", outDir).pathname, fullPage: true });
const requirementStyles = await collectStyles(page, [
  ".rc-brand-mark",
  ".rc-brand-copy strong",
  ".rc-brand-copy small",
  ".rc-version-badge",
  ".rc-collapse",
  ".rc-page-header",
  ".rc-header-action",
  ".rc-stat",
  ".rc-filter-menu",
  ".rc-board-wrap",
  ".rc-board",
  ".rc-column",
  ".rc-column-head",
  ".rc-column-head.filled",
  ".rc-column-head.empty",
  ".rc-column-head h2",
  ".rc-column-head.filled h2",
  ".rc-column-head.empty h2",
  ".rc-column-head p",
  ".rc-column-head.filled p",
  ".rc-column-head.empty p",
  ".rc-column-head > span",
  ".rc-column-head.filled > span",
  ".rc-column-head.empty > span",
  ".rc-column-body",
  ".rc-column-body:empty",
  ".rc-card",
  ".rc-card-top strong",
  ".rc-sprint-tag",
  ".rc-card-title",
  ".rc-card-tags",
  ".rc-tag",
  ".rc-priority-tag",
  ".rc-owner-tag",
  ".rc-docs",
  ".rc-docs button",
  ".rc-progress",
  ".rc-progress-action",
  ".rc-progress-label",
  ".rc-progress-value",
  ".rc-blocked",
  ".rc-card footer",
  ".rc-card-actions button.primary",
  ".rc-card-actions button.secondary",
]);
await page.keyboard.press("Escape");
await page.locator(".rc-user-trigger").click();
await page.screenshot({ path: new URL("requirements-user-menu-1440.png", outDir).pathname, fullPage: true });
await page.locator("#themeSwitch").click();
await page.screenshot({ path: new URL("requirements-light-1440.png", outDir).pathname, fullPage: true });
await page.locator(".rc-collapse").click();
await page.screenshot({ path: new URL("requirements-collapsed-1440.png", outDir).pathname, fullPage: true });
const mobilePage = await browser.newPage({ viewport: { width: 390, height: 844 } });
await mobilePage.addInitScript(() => {
  window.localStorage.setItem("moonbox.session", JSON.stringify({
    username: "founder",
    started_at: "2026-08-11T00:00:00.000Z",
    access_token: "front-token",
    expires_at: "2026-12-31 23:59:59",
    user: {
      id: "admin",
      username: "admin",
      nickname: "平台管理员",
      role: "后台管理员",
      status: "正常",
      is_system_superadmin: true,
    },
  }));
});
await mobilePage.goto(`${baseUrl}/requirements?mock=workflow`, { waitUntil: "networkidle" });
await mobilePage.screenshot({ path: new URL("requirements-mobile-390.png", outDir).pathname, fullPage: true });
await mobilePage.close();

await page.evaluate(() => {
  window.localStorage.setItem("moonbox.session", JSON.stringify({
    access_token: "admin-token",
    expires_at: "2026-12-31 23:59:59",
    user: {
      id: "admin",
      username: "admin",
      nickname: "平台管理员",
      avatar_url: null,
      role: "后台管理员",
      status: "正常",
      is_system_superadmin: true,
    },
  }));
});
await page.goto(`${baseUrl}/admin`, { waitUntil: "networkidle" });
await page.screenshot({ path: new URL("admin-users-1440.png", outDir).pathname, fullPage: true });
await page.getByRole("button", { name: /新增用户/ }).click();
await page.screenshot({ path: new URL("admin-user-modal-1440.png", outDir).pathname, fullPage: true });
const adminStyles = await collectStyles(page, [
  ".admin-mark",
  ".admin-brand strong",
  ".admin-brand small",
  ".admin-brand em",
  ".admin-collapse",
  ".admin-page-head h1",
  ".admin-table-wrap",
  ".admin-user-modal",
]);

await page.goto(`${baseUrl}/dev/design-system`, { waitUntil: "networkidle" });
await page.screenshot({ path: new URL("design-system-1440.png", outDir).pathname, fullPage: true });
const designSystemStyles = await collectStyles(page, [
  ".ds-preview-header h1",
  ".ds-token-card",
  ".ds-filter-demo",
]);

async function collectStyles(targetPage, selectors) {
  return targetPage.evaluate((items) => {
    const pick = (selector) => {
      const [baseSelector, pseudoElement] = selector.split("::");
      const element = document.querySelector(baseSelector);
      if (!element) return null;
      const computed = getComputedStyle(element, pseudoElement ? `::${pseudoElement}` : undefined);
      return {
        selector,
        content: computed.content,
        display: computed.display,
        flex: computed.flex,
        flexShrink: computed.flexShrink,
        flexDirection: computed.flexDirection,
        alignItems: computed.alignItems,
        alignContent: computed.alignContent,
        fontSize: computed.fontSize,
        fontFamily: computed.fontFamily,
        lineHeight: computed.lineHeight,
        width: computed.width,
        height: computed.height,
        minHeight: computed.minHeight,
        marginTop: computed.marginTop,
        gap: computed.gap,
        padding: computed.padding,
        border: computed.border,
        background: computed.backgroundColor,
        color: computed.color,
        zIndex: computed.zIndex,
        overflow: computed.overflow,
        position: computed.position,
        top: computed.top,
        right: computed.right,
        bottom: computed.bottom,
        left: computed.left,
      };
    };
    return items.map(pick);
  }, selectors);
}

const styles = {
  requirements: requirementStyles,
  requirementsEmptyColumns: emptyColumnStyles,
  captureModal: captureModalStyles,
  agentAssistant: agentAssistantStyles,
  actionModal: {
    analysis: actionAnalysisStyles,
    analysisSelection: actionAnalysisSelectionStyles,
    generate: actionGenerateStyles,
    complete: actionCompleteStyles,
    sprint: actionSprintStyles,
    opsx: actionOpsxStyles,
    progress: actionProgressStyles,
  },
  stickyBoundary: stickyBoundaryMetrics,
  admin: adminStyles,
  designSystem: designSystemStyles,
};
await writeFile(new URL("computed-styles.json", outDir), JSON.stringify(styles, null, 2));

await browser.close();

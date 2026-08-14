import playwrightTest from "../src/web/node_modules/@playwright/test/index.js";
import { mkdir, writeFile } from "node:fs/promises";

const { chromium } = playwrightTest;
const outDir = "openspec/changes/add-admin-space-management/implementation";
await mkdir(outDir, { recursive: true });

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
];

for (let index = 2; index <= 7; index += 1) {
  spaces.push({
    ...spaces[0],
    id: `space_visual_${index}`,
    name: `视觉验收空间 ${index}`,
    code: `visual-space-${index}`,
    ai_used_tokens: index >= 6 ? 1020000 : 420000,
    status: index === 5 ? "FROZEN" : "ACTIVE",
    updated_at: `2026-08-12T10:0${index}:00Z`,
  });
}

const applications = [
  {
    id: "space_app_1",
    name: "AI 原生软件工厂试点空间",
    code: "ai-factory-demo",
    applicant_id: "user_owner",
    applicant_name: "演示申请人",
    proposed_owner_id: "user_owner",
    proposed_owner_name: "演示负责人",
    product_id: "ai-factory-demo",
    product_name: "AI 原生软件工厂试点空间",
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
  {
    id: "space_app_2",
    name: "增长实验空间",
    code: "growth-lab-demo",
    applicant_id: "user_owner",
    applicant_name: "演示申请人",
    proposed_owner_id: "user_owner",
    proposed_owner_name: "演示负责人",
    product_id: "growth-lab-demo",
    product_name: "增长实验空间",
    purpose: "用于演示申请审批通过后自动创建空间和产品绑定。",
    expected_members: 20,
    requested_storage_gb: 120,
    requested_ai_tokens: 1500000,
    expires_at: "2026-12-31T23:59:59Z",
    status: "待审批",
    decision_reason: null,
    decision_by: null,
    decision_at: null,
    created_at: "2026-08-12T10:00:00Z",
    updated_at: "2026-08-12T10:00:00Z",
  },
  {
    id: "space_app_3",
    name: "客户交付空间",
    code: "delivery-space-demo",
    applicant_id: "user_owner",
    applicant_name: "演示申请人",
    proposed_owner_id: "user_owner",
    proposed_owner_name: "交付负责人",
    product_id: "delivery-space-demo",
    product_name: "客户交付空间",
    purpose: "用于验收拒绝申请、审批原因和待审批列表刷新。",
    expected_members: 8,
    requested_storage_gb: 60,
    requested_ai_tokens: 600000,
    expires_at: null,
    status: "待审批",
    decision_reason: null,
    decision_by: null,
    decision_at: null,
    created_at: "2026-08-12T10:00:00Z",
    updated_at: "2026-08-12T10:00:00Z",
  },
];

const ownerUsers = [
  {
    id: "user_owner",
    username: "owner",
    nickname: "空间负责人",
    role: "前台用户",
    status: "正常",
  },
  {
    id: "user_admin",
    username: "admin-owner",
    nickname: "后台负责人",
    role: "后台管理员",
    status: "正常",
  },
  {
    id: "user_editor",
    username: "editor",
    nickname: "编辑候选",
    role: "前台用户",
    status: "正常",
  },
];

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
];

const spaceAuditEvents = [
  {
    id: "audit_approval",
    space_id: "space_one",
    actor: "superadmin",
    actor_display_name: "平台超级管理员",
    action: "application_approved_create_space",
    before_value: JSON.stringify({ id: "space_app_1", status: "待审批", name: "菲尚特瓷砖", code: "tilesfst" }),
    after_value: JSON.stringify({ id: "space_one", source: "申请审批", name: "菲尚特瓷砖", code: "tilesfst" }),
    reason: "资料完整准予开通",
    result: "success",
    request_id: "req_audit_1",
    created_at: "2026-08-13T01:01:19Z",
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
    created_at: "2026-08-13T07:01:01Z",
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
    created_at: `2026-08-13T07:0${index}:01Z`,
  })),
];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
await page.route("**/api/v1/admin/space-applications**", async (route) => {
  await route.fulfill({ contentType: "application/json", body: JSON.stringify({ data: { items: applications, total: applications.length, page: 1, page_size: 10 } }) });
});
await page.route("**/api/v1/admin/users**", async (route) => {
  await route.fulfill({ contentType: "application/json", body: JSON.stringify({ data: { items: ownerUsers, total: ownerUsers.length, page: 1, page_size: 100 } }) });
});
await page.route("**/api/v1/admin/spaces/space_one/members**", async (route) => {
  await route.fulfill({ contentType: "application/json", body: JSON.stringify({ data: spaceMembers }) });
});
await page.route("**/api/v1/admin/spaces/space_one/audit-events**", async (route) => {
  const url = new URL(route.request().url());
  const pageNumber = Number(url.searchParams.get("page") || 1);
  const pageSize = Number(url.searchParams.get("page_size") || 10);
  const start = (pageNumber - 1) * pageSize;
  await route.fulfill({ contentType: "application/json", body: JSON.stringify({ data: { items: spaceAuditEvents.slice(start, start + pageSize), total: spaceAuditEvents.length, page: pageNumber, page_size: pageSize } }) });
});
await page.route("**/api/v1/admin/spaces/space_one", async (route) => {
  if (route.request().method() === "GET") {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ data: spaces[0] }) });
    return;
  }
  await route.fallback();
});
await page.route("**/api/v1/admin/spaces**", async (route) => {
  const url = new URL(route.request().url());
  if (url.pathname.endsWith("/api/v1/admin/spaces/space_one/members")) {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ data: spaceMembers }) });
    return;
  }
  if (url.pathname.endsWith("/api/v1/admin/spaces/space_one/audit-events")) {
    const pageNumber = Number(url.searchParams.get("page") || 1);
    const pageSize = Number(url.searchParams.get("page_size") || 10);
    const start = (pageNumber - 1) * pageSize;
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ data: { items: spaceAuditEvents.slice(start, start + pageSize), total: spaceAuditEvents.length, page: pageNumber, page_size: pageSize } }) });
    return;
  }
  if (url.pathname.endsWith("/api/v1/admin/spaces/space_one") && route.request().method() === "GET") {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ data: spaces[0] }) });
    return;
  }
  const status = url.searchParams.get("status");
  const filtered = status ? spaces.filter((item) => item.status === status) : spaces.filter((item) => item.status !== "RECYCLE");
  await route.fulfill({ contentType: "application/json", body: JSON.stringify({ data: { items: filtered, total: filtered.length, page: 1, page_size: 10 } }) });
});
await page.addInitScript(() => {
  window.localStorage.setItem("moonbox.session", JSON.stringify({
    access_token: "admin-token",
    expires_at: "2026-08-12T23:59:59Z",
    user: { id: "user_superadmin", username: "superadmin", nickname: "平台超级管理员", avatar_url: null, role: "后台管理员", status: "正常", is_system_superadmin: true },
  }));
});

await page.goto("http://127.0.0.1:4317/admin/spaces", { waitUntil: "networkidle" });
await page.screenshot({ path: `${outDir}/space-list-1440.png`, fullPage: true });
await page.getByText("更多").last().click();
await page.getByRole("menuitem", { name: "配额" }).hover();
await page.screenshot({ path: `${outDir}/space-list-more-1440.png`, fullPage: true });
const listPrototypeAlignment = await page.locator(".admin-content").evaluate((element) => {
  const activeTab = element.querySelector(".admin-space-tabs button.active");
  const activeTabStyle = activeTab ? window.getComputedStyle(activeTab) : null;
  const usage = element.querySelector(".admin-space-usage");
  const usageLabel = usage?.querySelector("small");
  const usageLabelStyle = usageLabel ? window.getComputedStyle(usageLabel) : null;
  const usageBar = usage?.querySelector(".admin-space-usage-bar");
  const usageBarFill = usageBar?.querySelector("i");
  const table = element.querySelector(".admin-space-table");
  const membersCol = element.querySelector(".admin-space-col-members");
  const productCol = element.querySelector(".admin-space-col-product");
  const usageCol = element.querySelector(".admin-space-col-usage");
  const tableWrap = element.querySelector(".admin-table-wrap")?.getBoundingClientRect();
  const actionCell = element.querySelector(".admin-space-table tbody td:last-child")?.getBoundingClientRect();
  const spaceLink = element.querySelector(".admin-link-button");
  const spaceLinkStyle = spaceLink ? window.getComputedStyle(spaceLink) : null;
  const actionButton = element.querySelector(".admin-space-row-actions button");
  const actionButtonStyle = actionButton ? window.getComputedStyle(actionButton) : null;
  const status = element.querySelector(".admin-space-status");
  const statusStyle = status ? window.getComputedStyle(status) : null;
  const statusIcon = status?.querySelector("svg");
  const statusIconStyle = statusIcon ? window.getComputedStyle(statusIcon) : null;
  const sourceTag = element.querySelector(".admin-source-tag");
  const sourceTagStyle = sourceTag ? window.getComputedStyle(sourceTag) : null;
  const secondHeader = element.querySelector(".admin-space-table th:nth-child(2)");
  const secondCell = element.querySelector(".admin-space-table tbody td:nth-child(2)");
  const secondHeaderStyle = secondHeader ? window.getComputedStyle(secondHeader) : null;
  const secondCellStyle = secondCell ? window.getComputedStyle(secondCell) : null;
  const moreMenuElement = document.querySelector(".admin-space-more-menu");
  const moreMenu = moreMenuElement?.getBoundingClientRect();
  const moreMenuStyle = moreMenuElement ? window.getComputedStyle(moreMenuElement) : null;
  const moreMenuButton = moreMenuElement?.querySelector("button");
  const moreMenuButtonStyle = moreMenuButton ? window.getComputedStyle(moreMenuButton) : null;
  const moreTrigger = Array.from(element.querySelectorAll(".admin-space-row-actions button[aria-haspopup='menu']")).at(-1);
  const moreTriggerRect = moreTrigger?.getBoundingClientRect();
  return {
    statCardCount: element.querySelectorAll(".admin-space-stat-card").length,
    tableHeaders: Array.from(element.querySelectorAll(".admin-space-table th")).map((item) => item.textContent?.trim()),
    activeTabBorderBottomWidth: activeTabStyle?.borderBottomWidth ?? null,
    activeTabBorderBottomColor: activeTabStyle?.borderBottomColor ?? null,
    usageText: usage?.textContent?.trim() ?? null,
    usageLabelColor: usageLabelStyle?.color ?? null,
    usageBarWidth: usageBar ? `${Math.round(usageBar.getBoundingClientRect().width)}px` : null,
    usageBarFillWidth: usageBarFill ? `${Math.round(usageBarFill.getBoundingClientRect().width)}px` : null,
    tableMinWidth: table ? window.getComputedStyle(table).minWidth : null,
    membersColumnWidth: membersCol ? window.getComputedStyle(membersCol).width : null,
    productColumnWidth: productCol ? window.getComputedStyle(productCol).width : null,
    usageColumnWidth: usageCol ? window.getComputedStyle(usageCol).width : null,
    hasUsageProgressBar: Boolean(element.querySelector(".admin-space-usage-bar i")),
    hasMoreAction: Boolean(element.querySelector(".admin-space-row-actions button[aria-haspopup='menu']")),
    spaceNameBorderWidth: spaceLinkStyle?.borderWidth ?? null,
    spaceNameBackgroundColor: spaceLinkStyle?.backgroundColor ?? null,
    actionColumnVisibleAt1440: tableWrap && actionCell ? actionCell.left < tableWrap.right && actionCell.right <= tableWrap.right + 1 : false,
    actionColumnWidth: actionCell ? `${Math.round(actionCell.width)}px` : null,
    tableWrapWidth: tableWrap ? `${Math.round(tableWrap.width)}px` : null,
    actionButtonBorderWidth: actionButtonStyle?.borderWidth ?? null,
    actionButtonColor: actionButtonStyle?.color ?? null,
    statusBorderWidth: statusStyle?.borderWidth ?? null,
    statusIconTag: statusIcon?.tagName.toLowerCase() ?? null,
    statusIconColor: statusIconStyle?.color ?? null,
    sourceTagBorderWidth: sourceTagStyle?.borderWidth ?? null,
    sourceTagColor: sourceTagStyle?.color ?? null,
    secondHeaderWhiteSpace: secondHeaderStyle?.whiteSpace ?? null,
    secondCellWhiteSpace: secondCellStyle?.whiteSpace ?? null,
    moreMenuVisible: moreMenu && tableWrap ? moreMenu.bottom > tableWrap.top && moreMenu.top < tableWrap.bottom + 240 : false,
    moreMenuClassName: moreMenuElement?.className ?? null,
    moreMenuPosition: moreMenuStyle?.position ?? null,
    moreMenuBackgroundColor: moreMenuStyle?.backgroundColor ?? null,
    moreMenuBorderColor: moreMenuStyle?.borderColor ?? null,
    moreMenuZIndex: moreMenuStyle?.zIndex ?? null,
    moreMenuWidth: moreMenu ? `${Math.round(moreMenu.width)}px` : null,
    moreMenuButtonFontSize: moreMenuButtonStyle?.fontSize ?? null,
    moreMenuButtonMinHeight: moreMenuButtonStyle?.minHeight ?? null,
    moreMenuButtonColor: moreMenuButtonStyle?.color ?? null,
    moreMenuButtonHoverBackground: moreMenuButtonStyle?.backgroundColor ?? null,
    moreMenuButtonJustifyContent: moreMenuButtonStyle?.justifyContent ?? null,
    moreMenuButtonTextAlign: moreMenuButtonStyle?.textAlign ?? null,
    moreMenuParentIsBody: moreMenuElement?.parentElement === document.body,
    moreMenuPlacement: moreMenuElement?.getAttribute("data-placement") ?? null,
    moreMenuDoesNotCoverPagination: moreMenu && element.querySelector(".admin-pagination") ? moreMenu.bottom < element.querySelector(".admin-pagination").getBoundingClientRect().top : false,
    moreMenuRightAlignedToTrigger: moreMenu && moreTriggerRect ? Math.abs(Math.round(moreMenu.right) - Math.round(moreTriggerRect.right)) <= 1 : false,
    moreMenuLeftAlignedToTrigger: moreMenu && moreTriggerRect ? Math.abs(Math.round(moreMenu.left) - Math.round(moreTriggerRect.left)) <= 1 : false,
    moreMenuHorizontalGapFromTrigger: moreMenu && moreTriggerRect ? Math.round(moreMenu.left - moreTriggerRect.left) : null,
    moreMenuVerticalGapFromTrigger: moreMenu && moreTriggerRect ? Math.round(moreMenu.top - moreTriggerRect.bottom) : null,
    moreMenuTop: moreMenu ? Math.round(moreMenu.top) : null,
    moreMenuBottom: moreMenu ? Math.round(moreMenu.bottom) : null,
  };
});
await page.mouse.click(20, 20);
await page.evaluate(() => {
  window.localStorage.setItem("moonbox.ui.preferences", JSON.stringify({ theme: "light" }));
  window.dispatchEvent(new CustomEvent("moonbox.ui.preferences.changed", { detail: { theme: "light" } }));
});
await page.waitForTimeout(50);
await page.getByText("更多").last().click();
await page.getByRole("menuitem", { name: "配额" }).hover();
const lightMoreMenuStyle = await page.locator(".admin-content").evaluate(() => {
  const moreMenuElement = document.querySelector(".admin-space-more-menu");
  const moreMenuStyle = moreMenuElement ? window.getComputedStyle(moreMenuElement) : null;
  const moreMenuButton = moreMenuElement?.querySelector("button");
  const moreMenuButtonStyle = moreMenuButton ? window.getComputedStyle(moreMenuButton) : null;
  return {
    className: moreMenuElement?.className ?? null,
    backgroundColor: moreMenuStyle?.backgroundColor ?? null,
    borderColor: moreMenuStyle?.borderColor ?? null,
    buttonColor: moreMenuButtonStyle?.color ?? null,
    buttonHoverBackground: moreMenuButtonStyle?.backgroundColor ?? null,
    buttonJustifyContent: moreMenuButtonStyle?.justifyContent ?? null,
    buttonTextAlign: moreMenuButtonStyle?.textAlign ?? null,
  };
});
await page.mouse.click(20, 20);
await page.evaluate(() => {
  window.localStorage.setItem("moonbox.ui.preferences", JSON.stringify({ theme: "dark" }));
  window.dispatchEvent(new CustomEvent("moonbox.ui.preferences.changed", { detail: { theme: "dark" } }));
});
await page.waitForTimeout(50);

await page.getByTestId("space-tab-approvals").click();
await page.screenshot({ path: `${outDir}/space-approvals-1440.png`, fullPage: true });
const approvalState = await page.locator(".admin-content").evaluate((element) => {
  const headers = Array.from(element.querySelectorAll(".admin-space-application-table th")).map((item) => item.textContent?.trim());
  const firstRow = element.querySelector("[data-testid='space-application-row']");
  const firstRowCells = Array.from(firstRow?.querySelectorAll("td") ?? []).map((item) => item.textContent?.replace(/\s+/g, " ").trim());
  const rows = Array.from(element.querySelectorAll("[data-testid='space-application-row']"));
  const resourceExpiryGaps = rows.map((row) => {
    const cells = Array.from(row.querySelectorAll("td"));
    const resourceRect = cells[3]?.getBoundingClientRect();
    const expiryRect = cells[4]?.getBoundingClientRect();
    return resourceRect && expiryRect ? Math.round(expiryRect.left - resourceRect.right) : null;
  });
  const pagination = element.querySelector(".admin-pagination");
  const actions = element.querySelector(".admin-space-application-actions");
  const approveButton = Array.from(actions?.querySelectorAll("button") ?? []).find((button) => button.textContent?.trim() === "通过");
  const rejectButton = Array.from(actions?.querySelectorAll("button") ?? []).find((button) => button.textContent?.trim() === "拒绝");
  const approveStyle = approveButton ? window.getComputedStyle(approveButton) : null;
  const rejectStyle = rejectButton ? window.getComputedStyle(rejectButton) : null;
  return {
    title: element.querySelector(".admin-page-head h1")?.textContent?.trim() ?? null,
    headers,
    firstRowCells,
    hasCardLayout: Boolean(element.querySelector(".admin-space-approval")),
    hasTableLayout: Boolean(element.querySelector(".admin-space-application-table")),
    hasColgroup: Boolean(element.querySelector(".admin-space-application-table colgroup")),
    spaceCellHasTwoLineStructure: Boolean(firstRow?.querySelector(".admin-space-application-name") && firstRow?.querySelector("small")),
    resourceText: firstRow?.querySelector(".admin-space-resource-cell")?.textContent?.replace(/\s+/g, " ").trim() ?? null,
    resourceItemTexts: Array.from(firstRow?.querySelectorAll(".admin-space-resource-item") ?? []).map((item) => item.textContent?.trim()),
    resourceItemRows: rows.map((row) => Array.from(row.querySelectorAll(".admin-space-resource-item")).map((item) => item.textContent?.trim())),
    hasBrokenSeparator: Boolean(firstRow?.textContent?.includes("Â·")),
    resourceExpiryGaps,
    resourceDoesNotOverlapExpiry: resourceExpiryGaps.every((gap) => gap !== null && gap >= 0),
    paginationLabel: pagination?.getAttribute("aria-label") ?? null,
    paginationText: pagination?.textContent?.replace(/\s+/g, " ").trim() ?? null,
    actionClassName: actions?.className ?? null,
    approveButtonBorderWidth: approveStyle?.borderWidth ?? null,
    approveButtonColor: approveStyle?.color ?? null,
    rejectButtonColor: rejectStyle?.color ?? null,
  };
});

await page.getByTestId("space-tab-recycle").click();
await page.waitForLoadState("networkidle");
await page.screenshot({ path: `${outDir}/space-recycle-1440.png`, fullPage: true });
const recycleMoreTrigger = page.locator(".admin-space-row-actions button", { hasText: "更多" }).first();
await recycleMoreTrigger.click();
await page.waitForTimeout(80);
await page.screenshot({ path: `${outDir}/space-recycle-more-1440.png`, fullPage: true });
const recycleState = await page.locator(".admin-content").evaluate((element) => {
  const headers = Array.from(element.querySelectorAll(".admin-space-table th")).map((item) => item.textContent?.trim());
  const cells = Array.from(element.querySelectorAll(".admin-space-table tbody tr:first-child td")).map((item) => item.textContent?.replace(/\s+/g, " ").trim());
  const pagination = element.querySelector(".admin-pagination");
  const restoreButton = Array.from(element.querySelectorAll(".admin-space-row-actions button")).find((button) => button.textContent?.trim() === "恢复");
  const editButton = Array.from(element.querySelectorAll(".admin-space-row-actions button")).find((button) => button.textContent?.trim() === "编辑");
  const moreTrigger = Array.from(element.querySelectorAll(".admin-space-row-actions button")).find((button) => button.textContent?.trim() === "更多");
  const moreMenu = document.querySelector(".admin-space-more-menu");
  const moreMenuStyle = moreMenu ? window.getComputedStyle(moreMenu) : null;
  const moreMenuRect = moreMenu?.getBoundingClientRect();
  const moreTriggerRect = moreTrigger?.getBoundingClientRect();
  const paginationStyle = pagination ? window.getComputedStyle(pagination) : null;
  const firstMenuItem = moreMenu?.querySelector("button");
  const firstMenuItemRect = firstMenuItem?.getBoundingClientRect();
  const firstMenuItemTopElement = firstMenuItemRect
    ? document.elementFromPoint(firstMenuItemRect.left + firstMenuItemRect.width / 2, firstMenuItemRect.top + firstMenuItemRect.height / 2)
    : null;
  const moreMenuZIndex = Number.parseInt(moreMenuStyle?.zIndex ?? "", 10);
  const paginationZIndex = Number.parseInt(paginationStyle?.zIndex ?? "", 10);
  return {
    title: element.querySelector(".admin-page-head h1")?.textContent?.trim() ?? null,
    headers,
    firstRowCells: cells,
    paginationLabel: pagination?.getAttribute("aria-label") ?? null,
    paginationText: pagination?.textContent?.replace(/\s+/g, " ").trim() ?? null,
    hasRestoreButton: Boolean(restoreButton),
    hasEditButton: Boolean(editButton),
    hasDeletedAt: cells.some((cell) => cell.includes("2026-08-12 10:00:00")),
    hasDeletedByName: cells.some((cell) => cell.includes("平台超级管理员")),
    hasDeleteReason: cells.some((cell) => cell.includes("空间生命周期结束")),
    hasRemainingDays: cells.some((cell) => /天$/.test(cell)),
    moreMenuScope: moreMenu?.getAttribute("data-scope") ?? null,
    moreMenuParentIsBody: moreMenu?.parentElement === document.body,
    moreMenuPosition: moreMenuStyle?.position ?? null,
    moreMenuZIndex: moreMenuStyle?.zIndex ?? null,
    moreMenuBackgroundColor: moreMenuStyle?.backgroundColor ?? null,
    moreMenuBorderColor: moreMenuStyle?.borderColor ?? null,
    moreMenuVisible: Boolean(moreMenuRect && moreMenuRect.width > 0 && moreMenuRect.height > 0),
    moreMenuHeight: moreMenuRect ? Math.round(moreMenuRect.height) : null,
    moreMenuItemTexts: Array.from(moreMenu?.querySelectorAll("button") ?? []).map((button) => button.textContent?.trim()),
    moreMenuFirstItemVisible: Boolean(moreMenu?.querySelector("button")?.getBoundingClientRect().height),
    moreMenuFirstItemOnTop: Boolean(moreMenu && firstMenuItemTopElement && moreMenu.contains(firstMenuItemTopElement)),
    moreMenuLeftAlignedToTrigger: moreMenuRect && moreTriggerRect ? Math.abs(Math.round(moreMenuRect.left) - Math.round(moreTriggerRect.left)) <= 1 : false,
    moreMenuPlacement: moreMenu?.getAttribute("data-placement") ?? null,
    moreMenuVerticalGapFromTrigger: moreMenuRect && moreTriggerRect ? Math.round(moreMenuRect.top - moreTriggerRect.bottom) : null,
    moreMenuZIndexAbovePagination: Number.isFinite(moreMenuZIndex) ? moreMenuZIndex > (Number.isFinite(paginationZIndex) ? paginationZIndex : 0) : null,
  };
});
await page.mouse.click(20, 20);

await page.getByTestId("space-tab-list").click();
await page.locator(".admin-user-trigger").click();
const listSidebarSnapshot = await page.locator(".admin-shell").evaluate((element) => {
  const sidebar = element.querySelector(".admin-sidebar");
  const activeItem = sidebar?.querySelector("button.active");
  const userMenu = sidebar?.querySelector(".admin-user-menu");
  const sidebarUser = sidebar?.querySelector(".admin-sidebar-user");
  const userTrigger = sidebar?.querySelector(".admin-user-trigger");
  const sidebarStyle = sidebar ? window.getComputedStyle(sidebar) : null;
  const sidebarRect = sidebar?.getBoundingClientRect();
  const sidebarUserRect = sidebarUser?.getBoundingClientRect();
  const userTriggerRect = userTrigger?.getBoundingClientRect();
  const viewportHeight = window.innerHeight;
  return {
    shellClassName: element.className,
    sidebarClassName: sidebar?.className ?? null,
    sidebarPosition: sidebarStyle?.position ?? null,
    sidebarTop: sidebarStyle?.top ?? null,
    sidebarAlignSelf: sidebarStyle?.alignSelf ?? null,
    sidebarHeight: sidebarRect ? `${Math.round(sidebarRect.height)}px` : null,
    sidebarBottomGap: sidebarRect ? Math.round(viewportHeight - sidebarRect.bottom) : null,
    sidebarUserBottomGap: sidebarUserRect ? Math.round(viewportHeight - sidebarUserRect.bottom) : null,
    userTriggerBottomGap: userTriggerRect ? Math.round(viewportHeight - userTriggerRect.bottom) : null,
    sidebarUserVisible: sidebarUserRect ? sidebarUserRect.top >= 0 && sidebarUserRect.bottom <= viewportHeight : false,
    userTriggerVisible: userTriggerRect ? userTriggerRect.top >= 0 && userTriggerRect.bottom <= viewportHeight : false,
    activeItemText: activeItem?.textContent?.trim() ?? null,
    hasUserMenu: Boolean(userMenu),
    userMenuButtonCount: userMenu?.querySelectorAll("button").length ?? 0,
    userMenuItems: Array.from(userMenu?.querySelectorAll("button") ?? []).map((item) => item.textContent?.trim()),
  };
});
await page.locator(".admin-user-trigger").click();
await page.getByText("MoonBox 运营空间").click();
await page.screenshot({ path: `${outDir}/space-detail-1440.png`, fullPage: true });
await page.locator(".admin-user-trigger").click();
const detailSidebarSnapshot = await page.locator(".admin-shell").evaluate((element) => {
  const sidebar = element.querySelector(".admin-sidebar");
  const activeItem = sidebar?.querySelector("button.active");
  const userMenu = sidebar?.querySelector(".admin-user-menu");
  const sidebarUser = sidebar?.querySelector(".admin-sidebar-user");
  const userTrigger = sidebar?.querySelector(".admin-user-trigger");
  const sidebarStyle = sidebar ? window.getComputedStyle(sidebar) : null;
  const sidebarRect = sidebar?.getBoundingClientRect();
  const sidebarUserRect = sidebarUser?.getBoundingClientRect();
  const userTriggerRect = userTrigger?.getBoundingClientRect();
  const viewportHeight = window.innerHeight;
  return {
    shellClassName: element.className,
    sidebarClassName: sidebar?.className ?? null,
    sidebarPosition: sidebarStyle?.position ?? null,
    sidebarTop: sidebarStyle?.top ?? null,
    sidebarAlignSelf: sidebarStyle?.alignSelf ?? null,
    sidebarHeight: sidebarRect ? `${Math.round(sidebarRect.height)}px` : null,
    sidebarBottomGap: sidebarRect ? Math.round(viewportHeight - sidebarRect.bottom) : null,
    sidebarUserBottomGap: sidebarUserRect ? Math.round(viewportHeight - sidebarUserRect.bottom) : null,
    userTriggerBottomGap: userTriggerRect ? Math.round(viewportHeight - userTriggerRect.bottom) : null,
    sidebarUserVisible: sidebarUserRect ? sidebarUserRect.top >= 0 && sidebarUserRect.bottom <= viewportHeight : false,
    userTriggerVisible: userTriggerRect ? userTriggerRect.top >= 0 && userTriggerRect.bottom <= viewportHeight : false,
    activeItemText: activeItem?.textContent?.trim() ?? null,
    hasUserMenu: Boolean(userMenu),
    userMenuButtonCount: userMenu?.querySelectorAll("button").length ?? 0,
    userMenuItems: Array.from(userMenu?.querySelectorAll("button") ?? []).map((item) => item.textContent?.trim()),
  };
});
await page.locator(".admin-user-trigger").click();
const detailPrototypeAlignment = await page.locator("[data-testid='space-detail-page']").evaluate((element, snapshots) => {
  const { listSidebarSnapshot, detailSidebarSnapshot } = snapshots;
  const detailHead = element.querySelector(".admin-space-detail-head");
  const detailHeadStyle = detailHead ? window.getComputedStyle(detailHead) : null;
  const detailHeadRect = detailHead ? detailHead.getBoundingClientRect() : null;
  const crumb = element.querySelector(".admin-space-crumb");
  const crumbStyle = crumb ? window.getComputedStyle(crumb) : null;
  const titleRow = element.querySelector(".admin-space-detail-title-row");
  const titleRowStyle = titleRow ? window.getComputedStyle(titleRow) : null;
  const title = element.querySelector(".admin-space-detail-title-row h1");
  const titleStyle = title ? window.getComputedStyle(title) : null;
  const crumbStrong = element.querySelector(".admin-space-crumb strong");
  const crumbStrongStyle = crumbStrong ? window.getComputedStyle(crumbStrong) : null;
  const ownerAvatar = element.querySelector(".admin-space-detail-owner .admin-avatar");
  const ownerAvatarStyle = ownerAvatar ? window.getComputedStyle(ownerAvatar) : null;
  const ownerText = element.querySelector(".admin-space-detail-owner b");
  const ownerTextStyle = ownerText ? window.getComputedStyle(ownerText) : null;
  const ownerImage = element.querySelector(".admin-space-detail-owner img");
  const notice = element.querySelector(".admin-space-detail-overview .admin-space-notice");
  const actionButton = element.querySelector(".admin-space-action-btn");
  const actionButtonStyle = actionButton ? window.getComputedStyle(actionButton) : null;
  const actionButtonRect = actionButton ? actionButton.getBoundingClientRect() : null;
  const dangerButton = element.querySelector(".admin-space-action-btn.danger");
  const dangerButtonStyle = dangerButton ? window.getComputedStyle(dangerButton) : null;
  const returnButton = element.querySelector(".admin-space-return");
  const returnButtonStyle = returnButton ? window.getComputedStyle(returnButton) : null;
  const tabs = Array.from(element.querySelectorAll(".admin-space-detail-tabs button"));
  const activeTab = element.querySelector(".admin-space-detail-tabs button.active");
  const activeTabStyle = activeTab ? window.getComputedStyle(activeTab) : null;
  const overview = element.querySelector(".admin-space-detail-overview");
  const overviewStyle = overview ? window.getComputedStyle(overview) : null;
  const baseCard = element.querySelector("[data-testid='space-detail-base']");
  const baseCardStyle = baseCard ? window.getComputedStyle(baseCard) : null;
  const fieldGrid = element.querySelector(".admin-space-detail-field-grid");
  const fieldGridStyle = fieldGrid ? window.getComputedStyle(fieldGrid) : null;
  const fieldLabel = element.querySelector(".admin-space-detail-field-grid dt");
  const fieldLabelStyle = fieldLabel ? window.getComputedStyle(fieldLabel) : null;
  const fieldValue = element.querySelector(".admin-space-detail-field-grid dd");
  const fieldValueStyle = fieldValue ? window.getComputedStyle(fieldValue) : null;
  const memberAddButton = Array.from(element.querySelectorAll("[data-testid='space-detail-members'] button")).find((item) => item.textContent?.trim() === "添加成员");
  return {
    sidebarReusedWithList: JSON.stringify({
      shellClassName: listSidebarSnapshot.shellClassName,
      sidebarClassName: listSidebarSnapshot.sidebarClassName,
      activeItemText: listSidebarSnapshot.activeItemText,
      hasUserMenu: listSidebarSnapshot.hasUserMenu,
      userMenuButtonCount: listSidebarSnapshot.userMenuButtonCount,
      userMenuItems: listSidebarSnapshot.userMenuItems,
    }) === JSON.stringify({
      shellClassName: detailSidebarSnapshot.shellClassName,
      sidebarClassName: detailSidebarSnapshot.sidebarClassName,
      activeItemText: detailSidebarSnapshot.activeItemText,
      hasUserMenu: detailSidebarSnapshot.hasUserMenu,
      userMenuButtonCount: detailSidebarSnapshot.userMenuButtonCount,
      userMenuItems: detailSidebarSnapshot.userMenuItems,
    }),
    sidebarUserBottomGapEqual: listSidebarSnapshot.sidebarUserBottomGap === detailSidebarSnapshot.sidebarUserBottomGap,
    userTriggerBottomGapEqual: listSidebarSnapshot.userTriggerBottomGap === detailSidebarSnapshot.userTriggerBottomGap,
    listSidebarSnapshot,
    detailSidebarSnapshot,
    hasCrumb: Boolean(element.querySelector(".admin-space-crumb")),
    crumbBorderWidth: crumbStyle?.borderTopWidth ?? null,
    hasDetailHead: Boolean(detailHead),
    detailHeadBackground: detailHeadStyle?.backgroundColor ?? null,
    detailHeadMinHeight: detailHeadStyle?.minHeight ?? null,
    detailHeadHeight: detailHeadRect ? `${Math.round(detailHeadRect.height)}px` : null,
    detailHeadPaddingTop: detailHeadStyle?.paddingTop ?? null,
    detailHeadPaddingRight: detailHeadStyle?.paddingRight ?? null,
    titleRowDisplay: titleRowStyle?.display ?? null,
    titleRowAlignItems: titleRowStyle?.alignItems ?? null,
    titleFontSize: titleStyle?.fontSize ?? null,
    titleFontWeight: titleStyle?.fontWeight ?? null,
    crumbCurrentFontWeight: crumbStrongStyle?.fontWeight ?? null,
    ownerAvatarWidth: ownerAvatarStyle?.width ?? null,
    ownerAvatarHeight: ownerAvatarStyle?.height ?? null,
    ownerAvatarHasImage: Boolean(ownerImage),
    ownerAvatarImageAlt: ownerImage?.getAttribute("alt") ?? null,
    ownerTextContent: element.querySelector(".admin-space-detail-owner")?.textContent?.trim() ?? null,
    ownerNameFontWeight: ownerTextStyle?.fontWeight ?? null,
    hasOwnerTransfer: Boolean(Array.from(element.querySelectorAll(".admin-space-detail-owner button")).find((item) => item.textContent?.trim() === "变更")),
    actionButtonHeight: actionButtonRect ? `${Math.round(actionButtonRect.height)}px` : null,
    actionButtonPaddingTop: actionButtonStyle?.paddingTop ?? null,
    actionButtonPaddingRight: actionButtonStyle?.paddingRight ?? null,
    actionButtonBorderRadius: actionButtonStyle?.borderRadius ?? null,
    actionButtonFontWeight: actionButtonStyle?.fontWeight ?? null,
    actionButtonBackground: actionButtonStyle?.backgroundColor ?? null,
    dangerButtonBackground: dangerButtonStyle?.backgroundColor ?? null,
    returnButtonBorderWidth: returnButtonStyle?.borderTopWidth ?? null,
    returnButtonBackground: returnButtonStyle?.backgroundColor ?? null,
    returnButtonColor: returnButtonStyle?.color ?? null,
    returnButtonTextDecoration: returnButtonStyle?.textDecorationLine ?? null,
    detailTabs: tabs.map((item) => item.textContent?.trim()),
    activeDetailTabBorderBottomColor: activeTabStyle?.borderBottomColor ?? null,
    overviewGridTemplateColumns: overviewStyle?.gridTemplateColumns ?? null,
    overviewGridTemplateAreas: overviewStyle?.gridTemplateAreas ?? null,
    overviewCardCount: element.querySelectorAll(".admin-space-detail-overview article").length,
    baseCardPaddingTop: baseCardStyle?.paddingTop ?? null,
    baseCardPaddingRight: baseCardStyle?.paddingRight ?? null,
    overviewHasProductNotice: Boolean(notice),
    fieldGridTemplateColumns: fieldGridStyle?.gridTemplateColumns ?? null,
    fieldLabelFontSize: fieldLabelStyle?.fontSize ?? null,
    fieldLabelFontWeight: fieldLabelStyle?.fontWeight ?? null,
    fieldValueFontSize: fieldValueStyle?.fontSize ?? null,
    fieldValueFontWeight: fieldValueStyle?.fontWeight ?? null,
    baseFieldLabels: Array.from(element.querySelectorAll("[data-testid='space-detail-base'] dt")).map((item) => item.textContent?.trim()),
    baseFieldValues: Array.from(element.querySelectorAll("[data-testid='space-detail-base'] dd")).map((item) => item.textContent?.trim()),
    recentOperationCount: element.querySelectorAll("[data-testid='space-detail-recent'] .admin-space-timeline > div").length,
    recentOperationFontWeight: element.querySelector("[data-testid='space-detail-recent'] .admin-space-timeline b")
      ? window.getComputedStyle(element.querySelector("[data-testid='space-detail-recent'] .admin-space-timeline b")).fontWeight
      : null,
    hasBaseCard: Boolean(element.querySelector("[data-testid='space-detail-base']")),
    hasQuotaCard: Boolean(element.querySelector("[data-testid='space-detail-quota']")),
    hasRecentCard: Boolean(element.querySelector("[data-testid='space-detail-recent']")),
    hasMemberAddButton: Boolean(memberAddButton),
  };
}, { listSidebarSnapshot, detailSidebarSnapshot });
await page.getByRole("button", { name: "成员" }).click();
await page.locator("[data-testid='space-detail-members'] tbody tr").first().waitFor({ state: "visible" });
const detailMembersVisible = await page.getByTestId("space-detail-members").isVisible();
const detailMembersState = await page.getByTestId("space-detail-members").evaluate((element) => ({
  hasAddMemberButton: Boolean(Array.from(element.querySelectorAll("button")).find((item) => item.textContent?.trim() === "添加成员")),
  hasPlaceholderMember: element.textContent?.includes("成员占位") ?? false,
  hasSectionTitle: Boolean(Array.from(element.querySelectorAll("h2")).find((item) => item.textContent?.includes("空间成员（同时为产品成员）"))),
  tableHeaders: Array.from(element.querySelectorAll("th")).map((item) => item.textContent?.trim()),
  rowCount: element.querySelectorAll("tbody tr").length,
  hasOwnerInRows: element.textContent?.includes("空间负责人") ?? false,
  memberAvatarHasImage: Boolean(element.querySelector(".admin-space-member-user .admin-avatar img")),
  memberAvatarAlt: element.querySelector(".admin-space-member-user .admin-avatar img")?.getAttribute("alt") ?? null,
  firstRoleText: element.querySelector("tbody tr td:nth-child(2)")?.textContent?.trim() ?? null,
  tableHeaderFontSize: element.querySelector("th") ? window.getComputedStyle(element.querySelector("th")).fontSize : null,
  tableHeaderFontWeight: element.querySelector("th") ? window.getComputedStyle(element.querySelector("th")).fontWeight : null,
  tableCellFontSize: element.querySelector("td") ? window.getComputedStyle(element.querySelector("td")).fontSize : null,
  tableCellFontWeight: element.querySelector("td") ? window.getComputedStyle(element.querySelector("td")).fontWeight : null,
  tableRowHeight: element.querySelector("tbody tr") ? window.getComputedStyle(element.querySelector("tbody tr")).height : null,
  tableCellHeight: element.querySelector("td") ? window.getComputedStyle(element.querySelector("td")).height : null,
  tableCellPaddingTop: element.querySelector("td") ? window.getComputedStyle(element.querySelector("td")).paddingTop : null,
  tableCellPaddingBottom: element.querySelector("td") ? window.getComputedStyle(element.querySelector("td")).paddingBottom : null,
  tableCellVerticalAlign: element.querySelector("td") ? window.getComputedStyle(element.querySelector("td")).verticalAlign : null,
  emptyStateText: element.querySelector(".admin-table-state")?.textContent?.trim() ?? null,
}));
const darkPrimaryButtonState = await page.getByTestId("space-detail-members").getByRole("button", { name: "添加成员" }).evaluate((element) => {
  const style = window.getComputedStyle(element);
  return {
    color: style.color,
    backgroundColor: style.backgroundColor,
    borderColor: style.borderColor,
    fontWeight: style.fontWeight,
  };
});
await page.evaluate(() => {
  window.localStorage.setItem("moonbox.ui.preferences", JSON.stringify({ theme: "light" }));
  window.dispatchEvent(new CustomEvent("moonbox.ui.preferences.changed", { detail: { theme: "light" } }));
});
await page.waitForTimeout(50);
await page.screenshot({ path: `${outDir}/space-detail-members-light-1440.png`, fullPage: true });
await page.getByTestId("space-detail-members").getByRole("button", { name: "添加成员" }).hover();
await page.getByTestId("space-detail-members").getByRole("button", { name: "添加成员" }).focus();
const lightPrimaryButtonState = await page.getByTestId("space-detail-members").getByRole("button", { name: "添加成员" }).evaluate((element) => {
  const style = window.getComputedStyle(element);
  return {
    color: style.color,
    backgroundColor: style.backgroundColor,
    borderColor: style.borderColor,
    fontWeight: style.fontWeight,
    outlineStyle: style.outlineStyle,
    outlineWidth: style.outlineWidth,
  };
});
await page.evaluate(() => {
  window.localStorage.setItem("moonbox.ui.preferences", JSON.stringify({ theme: "dark" }));
  window.dispatchEvent(new CustomEvent("moonbox.ui.preferences.changed", { detail: { theme: "dark" } }));
});
await page.waitForTimeout(50);
await page.locator(".admin-space-detail-tabs button", { hasText: "产品" }).click({ force: true });
const detailProductVisible = await page.getByTestId("space-detail-product").isVisible();
const detailProductState = await page.getByTestId("space-detail-product").evaluate((element) => {
  const fieldGrid = element.querySelector(".admin-space-detail-field-grid");
  const fieldGridStyle = fieldGrid ? window.getComputedStyle(fieldGrid) : null;
  const fieldLabel = element.querySelector(".admin-space-detail-field-grid dt");
  const fieldLabelStyle = fieldLabel ? window.getComputedStyle(fieldLabel) : null;
  const fieldValue = element.querySelector(".admin-space-detail-field-grid dd");
  const fieldValueStyle = fieldValue ? window.getComputedStyle(fieldValue) : null;
  return {
    productNoticeText: element.querySelector(".admin-space-notice")?.textContent?.trim() ?? null,
    productCardCount: element.querySelectorAll(".admin-space-product-card").length,
    hasProductCardTitle: Boolean(element.querySelector("h2")),
    hasProductCountField: Array.from(element.querySelectorAll("dt")).some((item) => item.textContent?.trim() === "产品数"),
    productIdText: Array.from(element.querySelectorAll("dt")).find((item) => item.textContent?.trim() === "产品 ID")?.nextElementSibling?.textContent?.trim() ?? null,
    researchStatusText: Array.from(element.querySelectorAll("dt")).find((item) => item.textContent?.trim() === "研发状态")?.nextElementSibling?.textContent?.trim() ?? null,
    fieldGridClassName: fieldGrid?.className ?? null,
    fieldGridTemplateColumns: fieldGridStyle?.gridTemplateColumns ?? null,
    fieldLabelFontSize: fieldLabelStyle?.fontSize ?? null,
    fieldLabelFontWeight: fieldLabelStyle?.fontWeight ?? null,
    fieldValueFontSize: fieldValueStyle?.fontSize ?? null,
    fieldValueFontWeight: fieldValueStyle?.fontWeight ?? null,
    hasUnsupportedActionButton: Boolean(Array.from(element.querySelectorAll("button")).find((item) => /解绑|迁移|新增产品/.test(item.textContent?.trim() || ""))),
  };
});
await page.locator(".admin-space-detail-tabs button", { hasText: "配额与用量" }).click({ force: true });
const detailQuotaVisible = await page.getByTestId("space-detail-quota-section").isVisible();
const detailQuotaState = await page.getByTestId("space-detail-quota-section").evaluate((element) => ({
  hasAdjustQuotaButton: Boolean(Array.from(element.querySelectorAll("button")).find((item) => item.textContent?.trim() === "调整配额")),
}));
await page.locator(".admin-space-detail-tabs button", { hasText: "操作记录" }).click({ force: true });
await page.getByText("审批通过创建空间").waitFor({ state: "visible" });
const detailLogsVisible = await page.getByTestId("space-detail-logs").isVisible();
const detailLogsState = await page.getByTestId("space-detail-logs").evaluate((element) => ({
  hasStaticTimeline: Boolean(element.querySelector(".admin-space-timeline")),
  emptyStateText: element.querySelector(".admin-table-state")?.textContent?.trim() ?? null,
  headers: Array.from(element.querySelectorAll("th")).map((item) => item.textContent?.trim()),
  rowCount: element.querySelectorAll("tbody tr").length,
  firstActionText: element.querySelector("tbody tr td:nth-child(3)")?.textContent?.trim() ?? null,
  hasInnerTitle: Boolean(element.querySelector("article > h2")),
  tagCount: element.querySelectorAll(".admin-space-audit-tag").length,
  actorDisplayText: element.querySelector("tbody tr td:nth-child(2)")?.textContent?.trim() ?? null,
  sourceTagText: element.querySelector(".admin-space-audit-tag.source")?.textContent?.trim() ?? null,
  resultTagText: element.querySelector(".admin-space-audit-tag.result")?.textContent?.trim() ?? null,
  firstChangeSummary: element.querySelector(".admin-space-audit-diff")?.textContent?.trim() ?? null,
  paginationText: element.querySelector(".admin-pagination")?.textContent?.trim() ?? null,
  paginationBorderWidth: element.querySelector(".admin-pagination") ? window.getComputedStyle(element.querySelector(".admin-pagination")).borderTopWidth : null,
  paginationBackground: element.querySelector(".admin-pagination") ? window.getComputedStyle(element.querySelector(".admin-pagination")).backgroundColor : null,
  activePageBorderWidth: element.querySelector(".admin-page-btn.active") ? window.getComputedStyle(element.querySelector(".admin-page-btn.active")).borderTopWidth : null,
  activePageBackground: element.querySelector(".admin-page-btn.active") ? window.getComputedStyle(element.querySelector(".admin-page-btn.active")).backgroundColor : null,
  viewButtonCount: Array.from(element.querySelectorAll("button")).filter((item) => item.textContent?.trim() === "查看").length,
  hasAuditApiPlaceholder: element.textContent?.includes("暂未接入真实审计数据源") ?? false,
  hasApprovalReason: element.textContent?.includes("资料完整准予开通") ?? false,
}));
await page.getByTestId("space-detail-logs").locator(".admin-page-btn").first().hover();
const auditPaginationHoverStyle = await page.getByTestId("space-detail-logs").locator(".admin-page-btn").first().evaluate((element) => {
  const style = window.getComputedStyle(element);
  return {
    borderWidth: style.borderTopWidth,
    background: style.backgroundColor,
    color: style.color,
  };
});
await page.getByTestId("space-detail-logs").getByRole("button", { name: "查看" }).first().click();
const auditDrawerState = await page.getByTestId("space-audit-drawer").evaluate((element) => {
  const pre = Array.from(element.querySelectorAll("pre"));
  const firstPreStyle = pre[0] ? window.getComputedStyle(pre[0]) : null;
  return {
    visible: true,
    title: element.querySelector("h2")?.textContent?.trim() ?? null,
    hasRequestId: element.textContent?.includes("请求 ID") ?? false,
    hasBeforeAfter: pre.length === 2,
    sourceTagText: element.querySelector(".admin-space-audit-tag.source")?.textContent?.trim() ?? null,
    resultTagText: element.querySelector(".admin-space-audit-tag.result")?.textContent?.trim() ?? null,
    jsonBlockCount: element.querySelectorAll(".admin-space-audit-json").length,
    beforeJsonText: pre[0]?.textContent ?? null,
    afterJsonText: pre[1]?.textContent ?? null,
    jsonFontFamily: firstPreStyle?.fontFamily ?? null,
    jsonMaxHeight: firstPreStyle?.maxHeight ?? null,
    jsonOverflow: firstPreStyle?.overflow ?? null,
    jsonWhiteSpace: firstPreStyle?.whiteSpace ?? null,
  };
});
await page.getByRole("button", { name: "关闭操作记录明细" }).click();
await page.getByTestId("space-detail-logs").getByRole("button", { name: "查看" }).nth(1).click();
await page.screenshot({ path: `${outDir}/space-audit-empty-drawer-1440.png`, fullPage: true });
const auditEmptyDrawerState = await page.getByTestId("space-audit-drawer").evaluate((element) => {
  const empty = element.querySelector(".admin-space-audit-empty");
  const emptyStyle = empty ? window.getComputedStyle(empty) : null;
  return {
    title: element.querySelector("h2")?.textContent?.trim() ?? null,
    emptyCount: element.querySelectorAll(".admin-space-audit-empty").length,
    jsonBlockCount: element.querySelectorAll(".admin-space-audit-json").length,
    emptyText: empty?.textContent?.trim() ?? null,
    emptyMinHeight: emptyStyle?.minHeight ?? null,
    emptyPaddingTop: emptyStyle?.paddingTop ?? null,
    emptyOverflow: emptyStyle?.overflow ?? null,
    emptyBackground: emptyStyle?.backgroundColor ?? null,
  };
});
await page.getByRole("button", { name: "关闭操作记录明细" }).click();
const primaryButtonThemeState = { dark: darkPrimaryButtonState, light: lightPrimaryButtonState };
const detailSections = { detailMembersVisible, detailMembersState, detailProductVisible, detailProductState, detailQuotaVisible, detailQuotaState, detailLogsVisible, detailLogsState, auditPaginationHoverStyle, primaryButtonThemeState };

await page.getByRole("button", { name: "返回空间列表" }).click();
await page.getByRole("button", { name: /冻结/ }).first().click();
await page.getByRole("button", { name: "确认" }).click();
await page.screenshot({ path: `${outDir}/space-freeze-modal-1440.png`, fullPage: true });
const freezeModal = await page.locator(".admin-space-modal").evaluate((element) => {
  const style = window.getComputedStyle(element);
  const rect = element.getBoundingClientRect();
  const reasonLabel = element.querySelector("label.required[for='admin-space-action-reason']");
  const reasonInput = element.querySelector("#admin-space-action-reason");
  const reasonError = element.querySelector(".admin-form-error");
  return {
    title: element.querySelector("header h2")?.textContent?.trim() ?? null,
    width: `${Math.round(rect.width)}px`,
    maxHeight: style.maxHeight,
    overflow: style.overflow,
    borderRadius: style.borderRadius,
    backgroundColor: style.backgroundColor,
    reasonLabelText: reasonLabel?.textContent?.trim() ?? null,
    reasonLabelDisplay: reasonLabel ? window.getComputedStyle(reasonLabel).display : null,
    reasonLabelWhiteSpace: reasonLabel ? window.getComputedStyle(reasonLabel).whiteSpace : null,
    reasonAriaInvalid: reasonInput?.getAttribute("aria-invalid") ?? null,
    reasonErrorText: reasonError?.textContent?.trim() ?? null,
    reasonErrorColor: reasonError ? window.getComputedStyle(reasonError).color : null,
  };
});
await page.getByRole("button", { name: "取消" }).click();
await page.getByRole("button", { name: /新增空间/ }).click();
await page.screenshot({ path: `${outDir}/space-create-modal-1440.png`, fullPage: true });
await page.getByRole("textbox", { name: "到期时间" }).focus();
await page.screenshot({ path: `${outDir}/space-create-modal-datetime-1440.png`, fullPage: true });
const dateTimePanelPlacement = await page.getByTestId("admin-datetime-picker").evaluate(() => {
  const picker = document.querySelector("[data-testid='admin-datetime-picker']")?.getBoundingClientRect();
  const panel = document.querySelector(".admin-datetime-panel")?.getBoundingClientRect();
  if (!picker || !panel) return null;
  return {
    pickerBottom: Math.round(picker.bottom),
    panelTop: Math.round(panel.top),
    gap: Math.round(panel.top - picker.bottom),
    doesNotCoverTrigger: panel.top >= picker.bottom,
    widthMatchesTrigger: Math.abs(panel.width - Math.max(picker.width, 360)) <= 1,
  };
});
const dateTimePanelState = await page.locator(".admin-datetime-panel").evaluate((element) => {
  const style = window.getComputedStyle(element);
  const activeDay = element.querySelector(".admin-datetime-days button.active");
  const timeInputs = Array.from(element.querySelectorAll(".admin-datetime-time input"));
  return {
    parentIsBody: element.parentElement === document.body,
    position: style.position,
    zIndex: style.zIndex,
    backgroundColor: style.backgroundColor,
    borderColor: style.borderColor,
    activeDayText: activeDay?.textContent?.trim() ?? null,
    activeDayBackground: activeDay ? window.getComputedStyle(activeDay).backgroundColor : null,
    timeInputCount: timeInputs.length,
    timeInputValues: timeInputs.map((input) => input.value),
    shortcutTexts: Array.from(element.querySelectorAll(".admin-datetime-shortcuts button")).map((item) => item.textContent?.trim()),
  };
});
await page.keyboard.press("Escape").catch(() => undefined);
await page.locator(".admin-space-modal button[aria-label='负责人']").click();
await page.screenshot({ path: `${outDir}/space-create-modal-select-1440.png`, fullPage: true });
const dropdownPlacement = await page.locator(".admin-space-modal .admin-select").first().evaluate((element) => {
  const trigger = element.querySelector(".admin-select-trigger")?.getBoundingClientRect();
  const menu = element.querySelector(".admin-select-menu")?.getBoundingClientRect();
  if (!trigger || !menu) return null;
  return {
    triggerBottom: Math.round(trigger.bottom),
    menuTop: Math.round(menu.top),
    gap: Math.round(menu.top - trigger.bottom),
    doesNotCoverTrigger: menu.top >= trigger.bottom,
  };
});
const createModal = await page.locator(".admin-space-modal").evaluate((element, evidence) => {
  const requiredMark = element.querySelector(".admin-space-field-label b");
  const descriptionField = element.querySelector(".admin-form-field-full");
  const ownerTrigger = element.querySelector("button[aria-label='负责人'] span");
  const expiryPicker = element.querySelector("[data-testid='admin-datetime-picker']");
  const expiryInput = expiryPicker?.querySelector("input");
  const style = window.getComputedStyle(element);
  return {
    headerIconCount: element.querySelectorAll("header svg").length,
    requiredMarkColor: requiredMark ? window.getComputedStyle(requiredMark).color : null,
    descriptionGridColumn: descriptionField ? window.getComputedStyle(descriptionField).gridColumn : null,
    fieldLabels: Array.from(element.querySelectorAll(".admin-form-grid > label")).map((label) => label.textContent?.replace(/\s+/g, " ").trim()),
    selectPlaceholder: ownerTrigger?.textContent || null,
    expiryInputType: expiryInput?.getAttribute("type") ?? null,
    expiryInputPlaceholder: expiryInput?.getAttribute("placeholder") ?? null,
    expiryInputValue: expiryInput?.value ?? null,
    expiryPickerExists: Boolean(expiryPicker),
    expiryInputHasSeconds: Boolean(expiryInput?.value.match(/\s\d{2}:\d{2}:\d{2}/)),
    expiryInputDefaultsToQuarterEnd: Boolean(expiryInput?.value.match(/\s23:59:59$/)),
    dropdownPlacement: evidence.dropdownPlacement,
    dateTimePanelPlacement: evidence.dateTimePanelPlacement,
    dateTimePanelState: evidence.dateTimePanelState,
    width: `${Math.round(element.getBoundingClientRect().width)}px`,
    maxHeight: style.maxHeight,
    overflow: style.overflow,
    borderRadius: style.borderRadius,
  };
}, { dropdownPlacement, dateTimePanelPlacement, dateTimePanelState });
await page.getByRole("button", { name: "取消" }).click();
await page.getByText("MoonBox 运营空间").click();
await page.getByRole("button", { name: "成员" }).click();
await page.getByRole("button", { name: "添加成员" }).click();
await page.locator(".admin-space-modal button[aria-label='用户']").click();
await page.screenshot({ path: `${outDir}/space-member-add-modal-user-select-1440.png`, fullPage: true });
const memberAddModal = await page.locator(".admin-space-modal").evaluate((element) => {
  const stack = element.querySelector(".admin-form-stack");
  const stackStyle = stack ? window.getComputedStyle(stack) : null;
  const modalRect = element.getBoundingClientRect();
  const userTrigger = element.querySelector("button[aria-label='用户']")?.getBoundingClientRect();
  const userMenu = document.querySelector(".admin-select-menu-portal")?.getBoundingClientRect();
  const userMenuStyle = document.querySelector(".admin-select-menu-portal") ? window.getComputedStyle(document.querySelector(".admin-select-menu-portal")) : null;
  return {
    title: element.querySelector("header h2")?.textContent?.trim() ?? null,
    hasStackLayout: Boolean(stack),
    stackDisplay: stackStyle?.display ?? null,
    stackGridTemplateColumns: stackStyle?.gridTemplateColumns ?? null,
    fieldLabels: Array.from(element.querySelectorAll(".admin-form-stack > label")).map((label) => label.textContent?.replace(/\s+/g, " ").trim()),
    userMenuParentIsBody: document.querySelector(".admin-select-menu-portal")?.parentElement === document.body,
    userMenuInsideModal: Boolean(element.querySelector(".admin-select-menu-portal")),
    userMenuPosition: userMenuStyle?.position ?? null,
    userMenuZIndex: userMenuStyle?.zIndex ?? null,
    userMenuBackgroundColor: userMenuStyle?.backgroundColor ?? null,
    userMenuWidthMatchesTrigger: userMenu && userTrigger ? Math.abs(Math.round(userMenu.width) - Math.round(userTrigger.width)) <= 1 : false,
    userMenuDoesNotClipByModal: userMenu && modalRect ? userMenu.bottom > modalRect.bottom : false,
    userMenuVerticalGapFromTrigger: userMenu && userTrigger ? Math.round(userMenu.top - userTrigger.bottom) : null,
  };
});
await page.keyboard.press("Escape");
await page.locator(".admin-space-modal button[aria-label='成员角色']").click();
await page.screenshot({ path: `${outDir}/space-member-add-modal-role-select-1440.png`, fullPage: true });
const memberAddRoleSelect = await page.locator(".admin-space-modal").evaluate((element) => {
  const modalRect = element.getBoundingClientRect();
  const trigger = element.querySelector("button[aria-label='成员角色']")?.getBoundingClientRect();
  const menuElement = document.querySelector(".admin-select-menu-portal");
  const menu = menuElement?.getBoundingClientRect();
  const style = menuElement ? window.getComputedStyle(menuElement) : null;
  return {
    menuParentIsBody: menuElement?.parentElement === document.body,
    menuInsideModal: Boolean(element.querySelector(".admin-select-menu-portal")),
    menuPosition: style?.position ?? null,
    menuZIndex: style?.zIndex ?? null,
    menuBackgroundColor: style?.backgroundColor ?? null,
    menuWidthMatchesTrigger: menu && trigger ? Math.abs(Math.round(menu.width) - Math.round(trigger.width)) <= 1 : false,
    menuDoesNotClipByModal: menu && modalRect ? menu.bottom > modalRect.bottom : false,
    menuVerticalGapFromTrigger: menu && trigger ? Math.round(menu.top - trigger.bottom) : null,
  };
});
await page.keyboard.press("Escape");
await page.getByRole("button", { name: "取消" }).click();
await page.getByRole("button", { name: "编辑" }).first().click();
await page.locator(".admin-space-modal button[aria-label='成员角色']").click();
await page.screenshot({ path: `${outDir}/space-member-edit-modal-role-select-1440.png`, fullPage: true });
const memberEditModal = await page.locator(".admin-space-modal").evaluate((element) => {
  const stack = element.querySelector(".admin-form-stack");
  const stackStyle = stack ? window.getComputedStyle(stack) : null;
  const modalRect = element.getBoundingClientRect();
  const trigger = element.querySelector("button[aria-label='成员角色']")?.getBoundingClientRect();
  const menuElement = document.querySelector(".admin-select-menu-portal");
  const menu = menuElement?.getBoundingClientRect();
  const style = menuElement ? window.getComputedStyle(menuElement) : null;
  return {
    title: element.querySelector("header h2")?.textContent?.trim() ?? null,
    hasStackLayout: Boolean(stack),
    stackDisplay: stackStyle?.display ?? null,
    stackGridTemplateColumns: stackStyle?.gridTemplateColumns ?? null,
    fieldLabels: Array.from(element.querySelectorAll(".admin-form-stack > label")).map((label) => label.textContent?.replace(/\s+/g, " ").trim()),
    roleMenuParentIsBody: menuElement?.parentElement === document.body,
    roleMenuInsideModal: Boolean(element.querySelector(".admin-select-menu-portal")),
    roleMenuPosition: style?.position ?? null,
    roleMenuZIndex: style?.zIndex ?? null,
    roleMenuBackgroundColor: style?.backgroundColor ?? null,
    roleMenuWidthMatchesTrigger: menu && trigger ? Math.abs(Math.round(menu.width) - Math.round(trigger.width)) <= 1 : false,
    roleMenuDoesNotClipByModal: menu && modalRect ? menu.bottom > modalRect.bottom : false,
    roleMenuVerticalGapFromTrigger: menu && trigger ? Math.round(menu.top - trigger.bottom) : null,
  };
});
await writeFile(`${outDir}/computed-style.json`, JSON.stringify({ viewport: "1440x1000", listPrototypeAlignment, lightMoreMenuStyle, approvalState, recycleState, detailPrototypeAlignment, detailSections, auditDrawerState, auditEmptyDrawerState, modal: freezeModal, createModal, memberAddModal, memberAddRoleSelect, memberEditModal }, null, 2));
await browser.close();

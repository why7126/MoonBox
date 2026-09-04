import playwright from "../../../src/web/node_modules/.pnpm/playwright@1.62.1/node_modules/playwright/index.js";
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
await page.locator(".rc-filter-popover summary").click();
await page.screenshot({ path: new URL("requirements-filter-popover-1440.png", outDir).pathname, fullPage: true });
const requirementStyles = await collectStyles(page, [
  ".rc-page-header",
  ".rc-stat",
  ".rc-filter-menu",
  ".rc-card",
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
      const element = document.querySelector(selector);
      if (!element) return null;
      const computed = getComputedStyle(element);
      return {
        selector,
        fontSize: computed.fontSize,
        fontFamily: computed.fontFamily,
        lineHeight: computed.lineHeight,
        width: computed.width,
        height: computed.height,
        gap: computed.gap,
        padding: computed.padding,
        border: computed.border,
        background: computed.backgroundColor,
        color: computed.color,
        zIndex: computed.zIndex,
        overflow: computed.overflow,
        position: computed.position,
      };
    };
    return items.map(pick);
  }, selectors);
}

const styles = {
  requirements: requirementStyles,
  admin: adminStyles,
  designSystem: designSystemStyles,
};
await writeFile(new URL("computed-styles.json", outDir), JSON.stringify(styles, null, 2));

await browser.close();

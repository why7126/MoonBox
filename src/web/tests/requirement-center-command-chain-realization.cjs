const { chromium, expect } = require("@playwright/test");
const fs = require("node:fs");
const path = require("node:path");

const out = path.resolve("../../openspec/changes/add-requirement-center-command-chain-realization/evidence/ui");

const context = {
  current_user: { name: "验收账号", permissions: ["requirement:read"] },
  workspaces: [{ workspace_id: "space", name: "验证项目", readonly: false }],
  selected_workspace_id: "space",
  snapshot_revision: "command-chain",
  stats: { total: 5, requirements: 4, bugs: 1, blocked: 0 },
  sprint_options: ["sprint-008"],
  sprint_option_details: [{ sprint_id: "sprint-008", label: "sprint-008", lifecycle_stage: "change", status: "in_progress", status_label: "进行中" }],
  issues: [
    {
      id: "REQ-8100-captured-command-chain-long-id",
      type: "requirement",
      title: "采集池需求真实生成链路",
      stage: "capture",
      priority: "P1",
      owner: "产品团队",
      source: "capture",
      sprint_id: "sprint-008",
      documents: ["capture.md", "trace.md"],
      action: { command: "/req-generate REQ-8100-captured-command-chain-long-id", label: "生成需求" },
    },
    {
      id: "REQ-8101-review-command-chain",
      type: "requirement",
      title: "待评审需求真实动作链路",
      stage: "review-ready",
      priority: "P1",
      owner: "产品团队",
      source: "review",
      sprint_id: "sprint-008",
      documents: ["capture.md", "trace.md", "requirement.md", "acceptance.md", "business-flow.md", "user-stories.md"],
      action: { command: "/req-review REQ-8101-review-command-chain --approve", label: "发起评审" },
    },
    {
      id: "REQ-8102-approved-command-chain",
      type: "requirement",
      title: "已评审需求纳入迭代",
      stage: "approved",
      priority: "P2",
      owner: "产品团队",
      source: "review",
      sprint_id: "sprint-008",
      documents: ["capture.md", "trace.md", "requirement.md", "acceptance.md", "business-flow.md", "user-stories.md", "review.md"],
      action: { command: "/sprint-propose --req REQ-8102-approved-command-chain", label: "加入迭代" },
    },
    {
      id: "REQ-8103-in-sprint-command-chain",
      type: "requirement",
      title: "迭代中需求生成 OpenSpec",
      stage: "sprint-planning",
      priority: "P1",
      owner: "产品团队",
      source: "review",
      sprint_id: "sprint-008",
      documents: ["sprint.md", "trace.md"],
      action: { command: "/req-opsx REQ-8103-in-sprint-command-chain", label: "生成 Opsx" },
    },
    {
      id: "BUG-8100-archive-command-chain",
      type: "bug",
      title: "验收中缺陷归档链路",
      stage: "acceptance",
      severity: "medium",
      owner: "平台工程",
      source: "review",
      sprint_id: "sprint-008",
      documents: ["proposal.md", "spec.md", "design.md", "trace.md", "tasks.md"],
      test_progress: [3, 3],
      manual_acceptance_count: 0,
      action: { command: "/opsx-archive BUG-8100-archive-command-chain", label: "完成 / 归档" },
    },
  ],
};

(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const evidence = [];
  try {
    for (const [theme, width, height] of [["dark", 1440, 1000], ["light", 1440, 1000], ["dark", 390, 844]]) {
      const page = await browser.newPage({ viewport: { width, height } });
      const calls = [];
      const errors = [];
      page.on("pageerror", error => errors.push(error.message));
      await page.addInitScript(selectedTheme => {
        localStorage.setItem("moonbox.session", JSON.stringify({ username: "验收账号", access_token: "synthetic-test-token" }));
        localStorage.setItem("moonbox.ui.preferences", JSON.stringify({ theme: selectedTheme }));
      }, theme);
      await page.route("**/api/v1/**", route => {
        const url = new URL(route.request().url());
        if (url.pathname.endsWith("/projects")) {
          return route.fulfill({ json: { data: { ...context, projects: [{ space_id: "space", repository_id: "repo", status: "connected", readonly: false }] } } });
        }
        if (url.pathname.endsWith("/context")) {
          return route.fulfill({ json: { data: context } });
        }
        if (url.pathname.endsWith("/governance-preparations") || url.pathname.endsWith("/object-sessions")) {
          const body = JSON.parse(route.request().postData() || "{}");
          calls.push({ path: url.pathname, body });
          return route.fulfill({ json: { data: { conversation_id: `conv-${calls.length}`, object_id: body.object_id, action: body.action, prompt: `/${body.action} ${body.object_id}` } } });
        }
        return route.fulfill({ json: { data: { ready: true, reason: "" } } });
      });
      await page.goto("http://127.0.0.1:39035/tests/governance-board-preview.html");
      const captureCard = page.locator('[data-issue-id="REQ-8100-captured-command-chain-long-id"]');
      await expect(captureCard).toBeVisible();
      await captureCard.getByRole("button", { name: "生成需求 →" }).click();
      await expect.poll(() => calls.length).toBe(1);
      await expect.poll(() => calls[0].path).toContain("/governance-preparations");
      await page.goto("http://127.0.0.1:39035/tests/governance-board-preview.html");
      await page.waitForLoadState("networkidle");
      const reviewCard = page.locator('[data-issue-id="REQ-8101-review-command-chain"]');
      await reviewCard.getByRole("button", { name: "发起评审 →" }).click();
      await expect.poll(() => calls.length).toBe(2);
      await expect.poll(() => calls[1].path).toContain("/object-sessions");
      await page.goto("http://127.0.0.1:39035/tests/governance-board-preview.html");
      await page.waitForLoadState("networkidle");
      const archiveCard = page.locator('[data-issue-id="BUG-8100-archive-command-chain"]');
      await archiveCard.scrollIntoViewIfNeeded();
      await page.screenshot({ path: path.join(out, `command-chain-${theme}-${width}.png`), fullPage: true });
      const styles = await page.locator('[data-issue-id="BUG-8100-archive-command-chain"] footer button.primary').evaluate(element => {
        const button = getComputedStyle(element);
        const card = getComputedStyle(element.closest(".rc-card"));
        const toast = document.querySelector(".rc-toast");
        const toastStyle = toast ? getComputedStyle(toast) : null;
        return {
          button: { fontSize: button.fontSize, minHeight: button.minHeight, padding: button.padding, borderRadius: button.borderRadius },
          card: { borderRadius: card.borderRadius, padding: card.padding, gap: card.gap },
          toast: toastStyle ? { zIndex: toastStyle.zIndex, maxWidth: toastStyle.maxWidth, overflowWrap: toastStyle.overflowWrap } : null,
          textFits: element.scrollWidth <= element.clientWidth + 1,
        };
      });
      evidence.push({ theme, width, height, calls: calls.map(call => call.body.action), styles, errors });
      if (errors.length) throw new Error(errors.join("\n"));
      await page.close();
    }
    fs.writeFileSync(path.join(out, "computed-styles.json"), JSON.stringify({ mode: "synthetic-http", evidence }, null, 2));
    console.log("command-chain visual evidence passed");
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});

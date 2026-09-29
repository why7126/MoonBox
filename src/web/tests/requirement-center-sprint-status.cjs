const { chromium, expect } = require("@playwright/test");
const fs = require("node:fs");
const path = require("node:path");

const out = path.resolve("../../openspec/changes/add-requirement-center-sprint-dropdown-status/evidence/ui");
const base = {
  current_user: { name: "验收账号" },
  workspaces: [{ workspace_id: "space", name: "验证项目" }],
  selected_workspace_id: "space",
  snapshot_revision: "stable",
  stats: { total: 3, requirements: 3, bugs: 0, standalone_changes: 0, blocked: 0, drift: 0 },
  sprint_options: ["sprint-002", "sprint-003", "sprint-004", "sprint-009"],
  sprint_option_details: [
    { sprint_id: "sprint-002", label: "sprint-002", lifecycle_stage: "change", status: "in_progress", status_label: "进行中", warning: null },
    { sprint_id: "sprint-003", label: "sprint-003", lifecycle_stage: "change", status: "planning", status_label: "规划中", warning: null },
    { sprint_id: "sprint-004", label: "sprint-004", lifecycle_stage: "archive", status: "archived", status_label: "已归档", warning: null },
  ],
  issues: [
    { id: "REQ-0101", type: "requirement", title: "进行中迭代样本", stage: "approved", sprint_id: "sprint-002", owner: "产品", priority: "P1", documents: ["requirement.md"], document_entries: [] },
    { id: "REQ-0102", type: "requirement", title: "规划中迭代样本", stage: "approved", sprint_id: "sprint-003", owner: "产品", priority: "P2", documents: ["requirement.md"], document_entries: [] },
    { id: "REQ-0103", type: "requirement", title: "未知迭代样本", stage: "approved", sprint_id: "sprint-009", owner: "产品", priority: "P2", documents: ["requirement.md"], document_entries: [] },
  ],
};

(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const evidence = [];
  try {
    for (const sample of [
      { theme: "dark", width: 1440, height: 1000 },
      { theme: "light", width: 390, height: 844 },
    ]) {
      const page = await browser.newPage({ viewport: { width: sample.width, height: sample.height } });
      const errors = [];
      page.on("pageerror", (error) => errors.push(error.message));
      await page.addInitScript((theme) => {
        localStorage.setItem("moonbox.session", JSON.stringify({ username: "验收账号", access_token: "synthetic-test" }));
        localStorage.setItem("moonbox.ui.preferences", JSON.stringify({ theme }));
      }, sample.theme);
      await page.route("**/api/**", (route) => {
        const url = new URL(route.request().url());
        const data = url.pathname.endsWith("/projects")
          ? { ...base, projects: [{ space_id: "space", repository_id: "repo", readonly: false, status: "connected" }] }
          : url.pathname.endsWith("/context")
            ? base
            : { ready: false };
        return route.fulfill({ json: { code: 0, data } });
      });
      await page.goto("http://127.0.0.1:18135/tests/governance-board-preview.html?page=requirements");
      await expect(page.locator("main.requirement-center")).toHaveAttribute("data-theme", sample.theme);
      await expect(page.locator('[data-issue-id="REQ-0101"]')).toBeVisible();

      await page.locator('summary[aria-label="打开筛选条件"]').click();
      await expect(page.getByLabel("显示已完成和归档")).toHaveCount(0);
      await page.getByRole("button", { name: /Sprint/ }).click();
      const trigger = page.getByTestId("requirement-filter-trigger-sprint");
      const popover = page.locator(".rc-multi-filter-popover");
      await expect(popover.getByText("sprint-002")).toBeVisible();
      await expect(popover.getByText("进行中")).toBeVisible();
      await expect(popover.getByText("规划中")).toBeVisible();
      await expect(popover.getByText("已归档")).toBeVisible();
      await expect(popover.getByText("状态待核实")).toBeVisible();

      const styles = await popover.locator(".rc-sprint-status-pill").evaluateAll((items) =>
        items.map((item) => {
          const style = getComputedStyle(item);
          return {
            text: item.textContent,
            className: item.className,
            color: style.color,
            background: style.backgroundColor,
            borderColor: style.borderColor,
            fontSize: style.fontSize,
            display: style.display,
          };
        }),
      );
      const popoverGapPx = await Promise.all([
        trigger.boundingBox(),
        popover.boundingBox(),
      ]).then(([triggerBox, popoverBox]) => {
        if (!triggerBox || !popoverBox) throw new Error("missing sprint filter geometry");
        return Math.round(popoverBox.y - (triggerBox.y + triggerBox.height));
      });
      expect(popoverGapPx).toBeGreaterThanOrEqual(4);
      expect(popoverGapPx).toBeLessThanOrEqual(10);
      await page.screenshot({ path: path.join(out, `sprint-status-${sample.theme}-${sample.width}.png`), fullPage: true });
      if (errors.length) throw new Error(errors.join("\n"));
      evidence.push({ ...sample, styles, popoverGapPx, pageErrors: errors });
      await page.close();
    }
    fs.writeFileSync(
      path.join(out, "sprint-status-styles.json"),
      JSON.stringify({ boundary: "真实浏览器组件，合成 API 响应；非部署观察", evidence }, null, 2),
    );
    console.log("2 sprint status visual cases passed");
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

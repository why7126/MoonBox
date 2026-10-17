const { chromium } = require("@playwright/test");
const fs = require("node:fs");
const path = require("node:path");

const css = fs.readFileSync(path.resolve(__dirname, "../src/styles/chat-workbench.css"), "utf8");
const cases = [
  { name: "req-generate-running", command: "/req-generate REQ-0027", status: "REQ-0027 当前为 captured，正在生成 requirement.md。" },
  { name: "req-complete-running", command: "/req-complete REQ-0027-requirement-center-command-chain-realization", status: "本轮未完成，Readiness: **Not Ready**。\n\n工作区只有旧的 REQ-0027-capture，注册表状态为 captured，且缺少 requirement.md；未找到你指定的完整 REQ ID。引用快照为只读上下文，不能替代本地事实源。" },
  { name: "bug-generate-running", command: "/bug-generate BUG-0024-capture", status: "dry-run 在创建临时锁前失败，正在改用只读文件锁继续检查写入范围。" },
  { name: "bug-complete-running", command: "/bug-complete BUG-0024-capture", status: "正在补齐 root-cause、workaround、acceptance 与 trace，执行中输出应占满内容列。" },
  { name: "req-review-running", command: "/req-review REQ-0027-requirement-center-command-chain-realization", status: "正在评审需求进入已评审阶段，运行态状态文案不应受命令类型影响。" },
  { name: "bug-review-running", command: "/bug-review BUG-0025-requirement-center-command-chain-write-gap", status: "正在评审缺陷修复状态，assistant status 输出仍必须等于内容列宽度。" },
  { name: "sprint-propose-running", command: "/sprint-propose --req REQ-0027-requirement-center-command-chain-realization", status: "正在读取 Sprint 范围和容量，状态输出按 assistant 渲染形态满宽。" },
  { name: "opsx-running", command: "/opsx-apply BUG-0025-requirement-center-command-chain-write-gap", status: "正在执行 OpenSpec Change，工具调用状态和正文输出的布局规则不依赖命令族。" },
  { name: "plain-chat-running", command: "帮我分析一下当前页面", status: "正在分析页面与历史上下文，普通 Chat 的 assistant running 输出也必须满宽。" },
  { name: "plain-assistant-completed", command: "普通 Chat", markdown: "已完成分析，下一步无需人工确认。" },
  { name: "history-restored", command: "历史恢复", status: "从历史入口恢复会话时，执行态输出仍占满消息历史可用宽度。" },
];

const closeEnough = (a, b) => Math.abs(a - b) <= 2;

(async () => {
  const browser = await chromium.launch({ headless: true });
  const errors = [];
  const samples = [];
  const evidenceDir = process.env.CHAT_WIDTH_EVIDENCE_DIR;
  if (evidenceDir) fs.mkdirSync(evidenceDir, { recursive: true });
  try {
    for (const sample of cases) {
      const page = await browser.newPage({ viewport: { width: 1440, height: 920 } });
      await page.setContent(`<!doctype html>
        <meta charset="utf-8">
        <style>${css}</style>
        <main class="chat-shell">
          <section class="chat-conversation">
            <div class="chat-message-history" data-testid="chat-message-history">
              <div class="chat-message-block turn-user">
                <article class="chat-message chat-message-user">
                  <strong>你</strong>
                  <div class="chat-turn-content">
                    <div class="chat-message-bubble">${sample.command}</div>
                  </div>
                </article>
              </div>
              <div class="chat-message-block turn-assistant">
                <article class="chat-message">
                  <strong>助手</strong>
                  <span class="chat-assistant-avatar" aria-hidden="true"></span>
                  <div class="chat-assistant-col">
                    <div class="chat-turn-activity">
                      <button class="chat-tool-summary"><span class="status-dot"></span>已读 9 次 工具调用 · 执行中<span class="chat-effective-config">Codex · GPT-6 Astra · Low</span></button>
                      ${sample.status ? `<p role="status">${sample.status}</p>` : ""}
                    </div>
                    <div class="chat-message-bubble">
                      ${sample.markdown ? `<div class="chat-markdown"><p>${sample.markdown}</p></div>` : ""}
                    </div>
                    <div class="chat-message-meta chat-assistant-meta">Codex · GPT-6 Astra · Low</div>
                  </div>
                </article>
              </div>
            </div>
          </section>
        </main>`);
      const result = await page.evaluate(() => {
        const rect = (selector) => {
          const element = document.querySelector(selector);
          const style = element ? getComputedStyle(element) : null;
          const box = element ? element.getBoundingClientRect() : null;
          return element && style && box ? {
            left: box.left,
            width: box.width,
            maxWidth: style.maxWidth,
            cssWidth: style.width,
            boxSizing: style.boxSizing,
            alignSelf: style.alignSelf,
            justifyContent: style.justifyContent,
            backgroundColor: style.backgroundColor,
            overflowWrap: style.overflowWrap,
          } : null;
        };
        return {
          history: rect(".chat-message-history"),
          assistantBlock: rect(".turn-assistant"),
          assistantArticle: rect(".turn-assistant .chat-message"),
          assistantColumn: rect(".chat-assistant-col"),
          activity: rect(".turn-assistant .chat-turn-activity"),
          summary: rect(".turn-assistant .chat-tool-summary"),
          status: rect(".turn-assistant .chat-turn-activity p[role='status']"),
          bubble: rect(".turn-assistant .chat-message-bubble"),
          markdown: rect(".turn-assistant .chat-markdown"),
          meta: rect(".chat-assistant-meta"),
          user: rect(".chat-message-user"),
        };
      });
      samples.push({ name: sample.name, ...result });
      const historyWidth = result.history.width;
      for (const selector of ["assistantBlock", "assistantArticle"]) {
        if (!closeEnough(result[selector].width, historyWidth)) errors.push(`${sample.name}:${selector} ${result[selector].width} != history ${historyWidth}`);
      }
      const columnWidth = result.assistantColumn.width;
      for (const selector of ["activity", "bubble"]) {
        if (!closeEnough(result[selector].width, columnWidth)) errors.push(`${sample.name}:${selector} ${result[selector].width} != column ${columnWidth}`);
      }
      if (result.assistantColumn.cssWidth !== `${columnWidth}px` && result.assistantColumn.cssWidth !== "100%") errors.push(`${sample.name}:unexpected column css width ${result.assistantColumn.cssWidth}`);
      if (result.assistantColumn.maxWidth !== "none") errors.push(`${sample.name}:column max-width ${result.assistantColumn.maxWidth} != none`);
      if (!closeEnough(result.summary.left, result.assistantColumn.left)) errors.push(`${sample.name}:summary left ${result.summary.left} != column left ${result.assistantColumn.left}`);
      if (!(result.summary.width < columnWidth)) errors.push(`${sample.name}:summary ${result.summary.width} should stay lightweight under column ${columnWidth}`);
      if (result.summary.alignSelf !== "flex-start") errors.push(`${sample.name}:summary align-self ${result.summary.alignSelf} != flex-start`);
      if (result.summary.justifyContent !== "flex-start") errors.push(`${sample.name}:summary justify-content ${result.summary.justifyContent} != flex-start`);
      if (result.summary.backgroundColor !== "rgba(0, 0, 0, 0)") errors.push(`${sample.name}:summary background ${result.summary.backgroundColor} should be transparent`);
      if (result.status && !closeEnough(result.status.width, columnWidth)) errors.push(`${sample.name}:status ${result.status.width} != column ${columnWidth}`);
      if (result.markdown && !closeEnough(result.markdown.width, columnWidth)) errors.push(`${sample.name}:markdown ${result.markdown.width} != column ${columnWidth}`);
      if (result.user.width >= historyWidth) errors.push(`${sample.name}:user bubble is not constrained`);
      if (evidenceDir && sample.name === "req-complete-running") {
        await page.screenshot({ path: path.join(evidenceDir, "AC-030-req-complete-running-1440x920.png") });
        fs.writeFileSync(path.join(evidenceDir, "AC-030-req-complete-running-1440x920-style.json"), JSON.stringify({ source: "Playwright synthetic DOM using production Chat CSS", scenario: sample.name, ...result }, null, 2));
      }
      await page.close();
    }
  } finally {
    await browser.close();
  }
  console.log(JSON.stringify({ cases: cases.length, errors, samples }, null, 2));
  if (errors.length) process.exitCode = 1;
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

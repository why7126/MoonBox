import playwright from "../../../../../src/web/node_modules/@playwright/test/index.js";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const evidenceDir = path.dirname(new URL(import.meta.url).pathname);
await mkdir(evidenceDir, { recursive: true });

const { chromium } = playwright;
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });

await page.addInitScript(() => {
  window.localStorage.setItem(
    "moonbox.session",
    JSON.stringify({
      username: "frontuser",
      started_at: "2026-08-19T00:00:00.000Z",
      access_token: "front-token",
      expires_at: "2026-08-20 00:00:00",
    }),
  );
  Object.defineProperty(navigator, "clipboard", {
    configurable: true,
    value: {
      writeText: async (value) => {
        window.__copiedCodeBlock = value;
      },
    },
  });
});

const fixture = {
  issues: [
    {
      id: "REQ-0021",
      type: "requirement",
      title: "Markdown 编辑器 Vditor 增强",
      priority: "P1",
      owner: "产品团队",
      source: "capture",
      stage: "capture",
      documents: ["capture.md", "trace.md"],
      document_entries: [
        { name: "capture.md", type: "markdown", open_mode: "drawer", label: "capture.md", editable: true, url: "/api/v1/requirement-center/issues/REQ-0021/documents/capture.md" },
        { name: "trace.md", type: "markdown", open_mode: "drawer", label: "trace.md", editable: false, url: "/api/v1/requirement-center/issues/REQ-0021/documents/trace.md" },
      ],
      updated_at: "12:30",
    },
  ],
  workspaces: [
    {
      organization_name: "MoonBox Lab",
      workspace_id: "moonbox-platform",
      name: "Platform Operations",
      slug: "platform-ops",
      description: "需求中心视觉验收",
      timezone: "Asia/Shanghai",
      member_count: 12,
      role: "拥有者",
      status: "ACTIVE",
      readonly: false,
    },
  ],
  current_user: { name: "许同学", avatar_initial: "许", can_access_admin: true, permissions: ["requirement:read"] },
  selected_workspace_id: "moonbox-platform",
  stats: { total: 1, requirements: 1, bugs: 0, blocked: 0, drift: 0 },
};

await page.route("**/api/v1/requirement-center/context**", (route) =>
  route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ data: fixture }) }),
);
await page.route("**/api/v1/requirement-center/issues/REQ-0021/documents/capture.md", (route) =>
  route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify({
      data: {
        content:
          "---\nreq_id: REQ-0021\nstatus: captured\nsource: explore\n---\n\n# capture.md\n\n需要支持图片上传、表格工具、代码高亮、数学公式。\n\n| 能力 | 状态 |\n|---|---|\n| 预览 | 阅读态 |\n\n```bash\npnpm test\npnpm build\n```\n",
      },
    }),
  }),
);
await page.route("**/api/v1/requirement-center/issues/REQ-0021/documents/trace.md", (route) =>
  route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify({
      data: {
        content:
          "---\nreq_id: REQ-0021\nstatus: captured\nsource: explore\n---\n\n# REQ-0021 Trace\n\n## 当前状态\n\n- 状态：captured\n- 优先级：P1\n\n```bash\n/req-generate REQ-0021\n```\n\n## Readiness Report\n\n| 项 | 结果 | 说明 |\n|---|---|---|\n| Readiness | Not Ready | 当前仅完成 capture，尚未生成 requirement、user-stories、business-flow 和 acceptance |\n| 下一步 | /req-generate | 建议先探索 MVP 边界，再生成 PRD |\n\n## 变更记录\n\n| 时间 | 事件 | 说明 |\n|---|---|---|\n| 2026-08-19 15:24:24 | req.capture | 记录需求：本地存量项目导入 MoonBox 并支持产品内迭代闭环。 |\n",
      },
    }),
  }),
);

await page.goto("http://127.0.0.1:4173/requirements", { waitUntil: "networkidle" });
await page.getByRole("button", { name: /capture.md/ }).click();
await page.screenshot({ path: path.join(evidenceDir, "03-drawer-prototype-preview-1440.png"), fullPage: true });
const previewComputed = await page.evaluate(() => {
  const drawer = document.querySelector(".rc-drawer");
  const toolbar = document.querySelector(".rc-vditor-toolbar");
  const rendered = document.querySelector('[data-testid="markdown-rendered-preview"]');
  const renderedStyles = rendered ? getComputedStyle(rendered) : null;
  const renderedHeading = rendered?.querySelector("h3.level-1");
  const renderedHeadingStyles = renderedHeading ? getComputedStyle(renderedHeading) : null;
  const renderedCode = rendered?.querySelector("code");
  const renderedCodeStyles = renderedCode ? getComputedStyle(renderedCode) : null;
  const copyButton = rendered?.querySelector(".copy-code");
  const copyButtonStyles = copyButton ? getComputedStyle(copyButton) : null;
  const copyButtonLabel = rendered?.querySelector(".copy-code span");
  const copyButtonLabelStyles = copyButtonLabel ? getComputedStyle(copyButtonLabel) : null;
  const codePre = rendered?.querySelector("pre.code");
  const codePreStyles = codePre ? getComputedStyle(codePre) : null;
  const frontmatterSummary = document.querySelector(".rc-markdown-frontmatter-summary");
  const frontmatterToggle = document.querySelector(".rc-markdown-frontmatter-toggle");
  const specStrip = document.querySelector(".rc-markdown-spec-strip");
  const drawerSubtitle = document.querySelector(".rc-drawer-title-block > span");
  const sourceFenceVisible = document.body.textContent?.includes("---\nreq_id: REQ-0021") ?? false;
  return {
    drawerWidth: drawer ? getComputedStyle(drawer).width : "",
    drawerSubtitleText: drawerSubtitle?.textContent ?? "",
    toolbarVisible: Boolean(toolbar),
    renderedPreviewExists: Boolean(rendered),
    renderedPreviewFontSize: renderedStyles?.fontSize ?? "",
    renderedPreviewLineHeight: renderedStyles?.lineHeight ?? "",
    renderedPreviewFontFamily: renderedStyles?.fontFamily ?? "",
    renderedHeadingFontSize: renderedHeadingStyles?.fontSize ?? "",
    renderedHeadingFontFamily: renderedHeadingStyles?.fontFamily ?? "",
    renderedCodeFontFamily: renderedCodeStyles?.fontFamily ?? "",
    codeCopyButtonExists: Boolean(copyButton),
    codeCopyButtonText: copyButton?.textContent ?? "",
    codeCopyButtonWidth: copyButtonStyles?.width ?? "",
    codeCopyButtonOpacity: copyButtonStyles?.opacity ?? "",
    codeCopyLabelWidth: copyButtonLabelStyles?.width ?? "",
    codeCopyLabelOpacity: copyButtonLabelStyles?.opacity ?? "",
    renderedCodePadding: codePreStyles?.padding ?? "",
    renderedPreviewText: rendered?.textContent ?? "",
    captureBriefVisible: document.body.textContent?.includes("Capture Brief") ?? false,
    documentContentLabelVisible: document.body.textContent?.includes("文档内容") ?? false,
    frontmatterSummaryExists: Boolean(frontmatterSummary),
    frontmatterToggleExists: Boolean(frontmatterToggle),
    frontmatterToggleExpanded: frontmatterToggle?.getAttribute("aria-expanded") ?? "",
    frontmatterToggleText: frontmatterToggle?.textContent ?? "",
    specStripExists: Boolean(specStrip),
    fullscreenButtonExists: Boolean(document.querySelector('[aria-label="放大右侧抽屉"]')),
    frontmatterSummaryText: frontmatterSummary?.textContent ?? "",
    rawFrontmatterFenceVisible: sourceFenceVisible,
  };
});
await page.getByRole("button", { name: "复制代码块" }).first().click();
const codeCopyComputed = await page.evaluate(() => {
  const copyButton = document.querySelector(".copy-code");
  return {
    copiedCode: window.__copiedCodeBlock ?? "",
    copyButtonTextAfterClick: copyButton?.textContent ?? "",
  };
});
await page.getByRole("button", { name: "放大右侧抽屉" }).click();
const fullscreenComputed = await page.evaluate(() => {
  const drawer = document.querySelector(".rc-drawer");
  return {
    drawerFullscreen: drawer?.classList.contains("fullscreen") ?? false,
    drawerWidthStyle: drawer?.getAttribute("style") ?? "",
    resizerExists: Boolean(document.querySelector(".rc-drawer-resizer")),
    restoreButtonExists: Boolean(document.querySelector('[aria-label="恢复右侧抽屉"]')),
  };
});
await page.getByRole("button", { name: "恢复右侧抽屉" }).click();
const restoredDrawerComputed = await page.evaluate(() => {
  const drawer = document.querySelector(".rc-drawer");
  return {
    drawerFullscreen: drawer?.classList.contains("fullscreen") ?? false,
    drawerWidthStyle: drawer?.getAttribute("style") ?? "",
    resizerExists: Boolean(document.querySelector(".rc-drawer-resizer")),
    fullscreenButtonExists: Boolean(document.querySelector('[aria-label="放大右侧抽屉"]')),
  };
});
await page.getByRole("button", { name: /文档属性.*展开/ }).click();
const expandedMetadataComputed = await page.evaluate(() => {
  const frontmatterSummary = document.querySelector(".rc-markdown-frontmatter-summary");
  const frontmatterToggle = document.querySelector(".rc-markdown-frontmatter-toggle");
  const specStrip = document.querySelector(".rc-markdown-spec-strip");
  return {
    frontmatterSummaryExists: Boolean(frontmatterSummary),
    frontmatterSummaryText: frontmatterSummary?.textContent ?? "",
    frontmatterToggleExpanded: frontmatterToggle?.getAttribute("aria-expanded") ?? "",
    frontmatterToggleText: frontmatterToggle?.textContent ?? "",
    specStripExists: Boolean(specStrip),
  };
});
await page.getByRole("button", { name: "关闭右侧抽屉", exact: true }).click();
await page.getByRole("button", { name: /trace.md/ }).click();
await page.screenshot({ path: path.join(evidenceDir, "07-drawer-trace-readonly-density-1440.png"), fullPage: true });
const traceReadonlyComputed = await page.evaluate(() => {
  const rendered = document.querySelector('[data-testid="markdown-rendered-preview"]');
  const renderedStyles = rendered ? getComputedStyle(rendered) : null;
  const heading = rendered?.querySelector("h3.level-1");
  const headingStyles = heading ? getComputedStyle(heading) : null;
  const tableCell = rendered?.querySelector("td");
  const tableCellStyles = tableCell ? getComputedStyle(tableCell) : null;
  const code = rendered?.querySelector("code");
  const codeStyles = code ? getComputedStyle(code) : null;
  const copyButton = rendered?.querySelector(".copy-code");
  return {
    renderedPreviewExists: Boolean(rendered),
    renderedPreviewFontSize: renderedStyles?.fontSize ?? "",
    renderedPreviewLineHeight: renderedStyles?.lineHeight ?? "",
    renderedHeadingFontSize: headingStyles?.fontSize ?? "",
    renderedTableCellFontSize: tableCellStyles?.fontSize ?? "",
    renderedTableCellLineHeight: tableCellStyles?.lineHeight ?? "",
    renderedTableCellPadding: tableCellStyles?.padding ?? "",
    renderedCodeFontFamily: codeStyles?.fontFamily ?? "",
    codeCopyButtonExists: Boolean(copyButton),
    codeCopyButtonText: copyButton?.textContent ?? "",
    modeBarExists: Boolean(document.querySelector(".rc-markdown-mode-bar")),
    specStripExists: Boolean(document.querySelector(".rc-markdown-spec-strip")),
  };
});
await page.getByRole("button", { name: "关闭右侧抽屉", exact: true }).click();
await page.getByRole("button", { name: /capture.md/ }).click();
await page.getByRole("group", { name: "Markdown 查看模式" }).getByRole("button", { name: "编辑" }).click();
await page.getByRole("button", { name: "插入表格" }).click();
await page.getByRole("button", { name: "插入代码块" }).click();
await page.getByRole("button", { name: "插入数学公式" }).click();
await page.screenshot({ path: path.join(evidenceDir, "04-drawer-prototype-edit-1440.png"), fullPage: true });
await page.getByRole("button", { name: "分栏" }).click();
const editorLocator = page.getByTestId("markdown-source-fallback");
await editorLocator.fill("alpha\nomega");
await editorLocator.focus();
await editorLocator.evaluate((editor) => {
  if (!(editor instanceof HTMLTextAreaElement)) return;
  editor.setSelectionRange(6, 6);
});
await page.getByRole("button", { name: "插入表格" }).click();
await page.waitForFunction(() => {
  const editor = document.querySelector('[data-testid="markdown-source-fallback"]');
  return editor instanceof HTMLTextAreaElement && editor.value.includes("| 列 1 | 列 2 |");
});
await editorLocator.focus();
await editorLocator.evaluate((editor) => {
  if (!(editor instanceof HTMLTextAreaElement)) return;
  const omegaStart = editor.value.indexOf("omega");
  if (omegaStart < 0) return;
  editor.setSelectionRange(omegaStart, omegaStart + "omega".length);
});
await page.getByRole("button", { name: "插入代码块" }).click();
await page.waitForFunction(() => {
  const editor = document.querySelector('[data-testid="markdown-source-fallback"]');
  return editor instanceof HTMLTextAreaElement && editor.value.includes("```ts\nomega\n```");
});
await editorLocator.focus();
await editorLocator.evaluate((editor) => {
  if (!(editor instanceof HTMLTextAreaElement)) return;
  editor.setSelectionRange(editor.value.length, editor.value.length);
});
await page.getByRole("button", { name: "插入数学公式" }).click();
await page.waitForFunction(() => {
  const editor = document.querySelector('[data-testid="markdown-source-fallback"]');
  return editor instanceof HTMLTextAreaElement && editor.value.includes("$$\n") && editor.value.includes("\n$$");
});
await page.screenshot({ path: path.join(evidenceDir, "05-drawer-prototype-split-1440.png"), fullPage: true });
const splitLabelComputed = await page.evaluate(() => {
  const editorPane = document.querySelector(".rc-vditor-pane.editor");
  const previewPane = document.querySelector(".rc-vditor-pane.preview");
  const editor = document.querySelector('[data-testid="markdown-source-fallback"]');
  const rendered = document.querySelector('[data-testid="markdown-rendered-preview"]');
  const renderedStyles = rendered ? getComputedStyle(rendered) : null;
  const renderedHeading = rendered?.querySelector("h3.level-1");
  const renderedHeadingStyles = renderedHeading ? getComputedStyle(renderedHeading) : null;
  const renderedCode = rendered?.querySelector("code");
  const renderedCodeStyles = renderedCode ? getComputedStyle(renderedCode) : null;
  const editorRect = editorPane?.getBoundingClientRect();
  const previewRect = previewPane?.getBoundingClientRect();
  const editorValue = editor instanceof HTMLTextAreaElement ? editor.value : "";
  return {
    markdownSourceLabelVisible: document.body.textContent?.includes("Markdown Source") ?? false,
    livePreviewLabelVisible: document.body.textContent?.includes("Live Preview") ?? false,
    editorPaneTop: editorRect?.top ?? null,
    previewPaneTop: previewRect?.top ?? null,
    paneTopDelta: editorRect && previewRect ? Math.abs(editorRect.top - previewRect.top) : null,
    focusedEditor: document.activeElement === editor,
    selectionStart: editor instanceof HTMLTextAreaElement ? editor.selectionStart : null,
    selectionEnd: editor instanceof HTMLTextAreaElement ? editor.selectionEnd : null,
    tableInsertedAtCursor: editorValue.includes("alpha\n| 列 1 | 列 2 |"),
    codeWrappedSelection: editorValue.includes("```ts\nomega\n```"),
    formulaInserted: editorValue.includes("$$\n") && editorValue.includes("\n$$"),
    livePreviewUpdated: rendered?.textContent?.includes("列 1") ?? false,
    renderedPreviewFontSize: renderedStyles?.fontSize ?? "",
    renderedPreviewLineHeight: renderedStyles?.lineHeight ?? "",
    renderedPreviewFontFamily: renderedStyles?.fontFamily ?? "",
    renderedHeadingFontSize: renderedHeadingStyles?.fontSize ?? "",
    renderedHeadingFontFamily: renderedHeadingStyles?.fontFamily ?? "",
    renderedCodeFontFamily: renderedCodeStyles?.fontFamily ?? "",
  };
});

const beforeUploadComputed = await page.evaluate(() => ({
  uploadStateExists: Boolean(document.querySelector(".rc-vditor-upload-state")),
  uploadStateText: document.querySelector(".rc-vditor-upload-state")?.textContent ?? "",
}));

await page.getByRole("button", { name: "插入图片" }).click();
await page.screenshot({ path: path.join(evidenceDir, "06-drawer-prototype-upload-failed-1440.png"), fullPage: true });

const computed = await page.evaluate(() => {
  const shell = document.querySelector(".rc-vditor-shell");
  const toolbar = document.querySelector(".rc-vditor-toolbar");
  const workspace = document.querySelector(".rc-vditor-workspace");
  const state = document.querySelector(".rc-vditor-upload-state");
  const drawer = document.querySelector(".rc-drawer");
  const spec = document.querySelector(".rc-markdown-spec-strip");
  const modeBar = document.querySelector(".rc-markdown-mode-bar");
  const footer = document.querySelector(".rc-markdown-footer");
  const editor = document.querySelector('[data-testid="markdown-source-fallback"]');
  const frontmatterSummary = document.querySelector(".rc-markdown-frontmatter-summary");
  const rect = shell?.getBoundingClientRect();
  const styles = shell ? getComputedStyle(shell) : null;
  return {
    shellExists: Boolean(shell),
    toolbarButtons: toolbar?.querySelectorAll("button").length ?? 0,
    uploadStateText: state?.textContent ?? "",
    workspaceGridTemplateColumns: workspace ? getComputedStyle(workspace).gridTemplateColumns : "",
    drawerWidth: drawer ? getComputedStyle(drawer).width : "",
    specStripExists: Boolean(spec),
    modeButtonTexts: Array.from(modeBar?.querySelectorAll("button") || []).map((button) => button.textContent),
    footerExists: Boolean(footer),
    footerHeight: footer ? getComputedStyle(footer).height : "",
    editorValueIncludesFrontmatterFence: editor instanceof HTMLTextAreaElement ? editor.value.includes("---\nreq_id: REQ-0021") : null,
    editorValuePreview: editor instanceof HTMLTextAreaElement ? editor.value.slice(0, 80) : "",
    metadataSummarySeparatedFromEditor: editor instanceof HTMLTextAreaElement && !editor.value.includes("req_id: REQ-0021"),
    shellRect: rect ? { x: rect.x, y: rect.y, width: rect.width, height: rect.height } : null,
    shellDisplay: styles?.display ?? "",
    bodyScrollWidth: document.body.scrollWidth,
    viewportWidth: window.innerWidth,
  };
});

computed.preview = previewComputed;
computed.codeCopy = codeCopyComputed;
computed.fullscreen = fullscreenComputed;
computed.restoredDrawer = restoredDrawerComputed;
computed.expandedMetadata = expandedMetadataComputed;
computed.beforeUpload = beforeUploadComputed;
computed.traceReadonly = traceReadonlyComputed;
computed.splitLabels = splitLabelComputed;
computed.toolbarInsertion = {
  tableInsertedAtCursor: splitLabelComputed.tableInsertedAtCursor,
  codeWrappedSelection: splitLabelComputed.codeWrappedSelection,
  formulaInserted: splitLabelComputed.formulaInserted,
  focusedEditor: splitLabelComputed.focusedEditor,
  selectionStart: splitLabelComputed.selectionStart,
  selectionEnd: splitLabelComputed.selectionEnd,
  livePreviewUpdated: splitLabelComputed.livePreviewUpdated,
};

await writeFile(path.join(evidenceDir, "computed-vditor-editor-1440.json"), JSON.stringify(computed, null, 2));
await browser.close();
console.log(JSON.stringify({ evidenceDir, computed }, null, 2));

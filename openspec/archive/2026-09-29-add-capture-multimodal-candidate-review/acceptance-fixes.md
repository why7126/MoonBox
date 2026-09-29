---
title: Capture 附件原型复刻验收返修
created_at: '2026-09-16 09:40:00'
updated_at: '2026-09-16 23:12:00'
---
# Capture 附件原型复刻验收返修

## 反馈批次

- 来源：用户在 `/opsx-modify REQ-0029-capture-multimodal-candidate-review` 中确认按附件 `layout-4-console-workbench.html` 一比一复刻布局，UI 设计系统保持与当前一致。
- 范围：仅调整 Web Capture 弹窗布局、局部交互外壳、视觉验收脚本和文档契约；API、DB、对象存储、编号、幂等确认和正式采集记录写入契约不变。
- 目标：单一 MD 编辑器 + 内嵌图片/文本文件材料块保持正式方向，外壳与审阅阶段复刻附件的三阶段工作台。

## 附件截图逐项视觉对照表

| 区域 | 附件期望 | 返修前实际 | 处置结论 | 检查方式 |
|---|---|---|---|---|
| 弹窗工作台 | 约 900px 输入态/审阅/结果态居中卡片，顶部为“新建 CAPTURE”和关闭动作 | 1200px 双栏工作区，材料在左侧 aside | 已改为居中工作台，保留 MoonBox token、圆角和阴影 | `capture-skeleton.cjs` 采样 `.capture-workspace` |
| 阶段提示 | 三个圆点 + “第 N 步 · …”文本 | 横向 ol 步骤条 | 已改为圆点进度和阶段标签 | 1440/390 骨架截图 |
| 原始材料 | 卡片内 `details` 抽屉，“来源材料 · N 项”，内部 chip 展示 MD、图片和添加入口 | 左侧材料摘要区，上传入口在编辑器下方 | 已改为材料抽屉与 chip row，上传入口在抽屉内 | `.capture-material-drawer`、`.capture-material-card` |
| MD 编辑器 | 一个大 textarea，260px 以上，高行距，用于图文整理原始输入 | 已有单一 textarea，但外部布局不一致 | 保持单一 textarea，更新提示和卡片层级 | `capture-dialog.test.tsx` |
| 候选审阅 | 单列 board，候选卡片左侧编号栏，右侧内容和动作 | 普通全宽卡片，无编号栏 | 已改为 `52px + 1fr` grid，移动端隐藏编号栏 | `.capture-board`、`.capture-candidate-number` |
| 编辑/改类型 | 在候选卡片内展开 field panel，类型变化不丢来源 | modal 编辑 | 已改为卡片内联编辑，保留候选 ID 与来源说明 | `capture-inline-edit` |
| 结果态 | 居中完成 icon、结果卡片、幂等说明 | 简单列表 | 已改为结果卡片和幂等提示 | `.capture-resultcard`、`.capture-idempotent` |

## UI Reference Replication Contract

- 设计系统映射：不复制附件的 Manrope、蓝色和浅色背景变量；映射到 `--mb-*`、`--ops-*`、`--mb-accent`，保持当前 MoonBox 深浅主题一致。
- 布局边界：输入态、审阅态和结果态均按附件控制在 `width <= 900px`，外层最大高度 `100dvh - 32/48px`，内部滚动。
- 材料结构：正式 DOM 入口为 `.capture-material-drawer`，内部 chip 使用 `.capture-material-card`，图片保留 `data-testid="capture-image-card"` 以维持真实上传取证脚本。
- 审阅结构：`.capture-board` 承载候选，`.capture-candidate` 采用 `52px minmax(0,1fr)`，`.capture-candidate-number` 显示条目序号，`max-width:640px` 以下隐藏编号栏。
- 动作矩阵：编辑/改类型为内联 field panel；拆分、删除、来源、确认沿用已有 modal 安全确认；确认前不显示或预占 REQ/BUG 编号。

## 根因证据

返修前实现满足“单一 MD 编辑器”和候选审阅能力，但 UI 骨架仍沿用治理工作台的 1200px 双栏结构；附件原型是单列居中三阶段 Capture flow。偏差直接体现在 `.capture-layout` 的 `320px minmax(0,1fr)`、`.capture-materials` aside 和候选卡片无编号栏。返修将这些 selector 重构为附件结构，同时保持现有数据契约。

## 验证记录

- `node node_modules/typescript/bin/tsc --noEmit -p tsconfig.json`：通过。
- `node node_modules/vitest/vitest.mjs run src/capture-dialog.test.tsx src/capture-api.test.ts src/requirement-center.test.tsx -t "unified markdown capture editor|opens full task documents|CaptureDialog|captureApi"`：通过，6 passed / 107 skipped。
- `CAPTURE_SKELETON_BASE=http://127.0.0.1:5190 node tests/capture-skeleton.cjs`：通过，生成 1440 dark、1440 light、390 light 截图与 `skeleton-styles.json`。
- `capture-ui-states.cjs`：未纳入通过证据。本地需求中心真实项目上下文仍将 Capture 入口置为只读，合成 Capture API 已 mock 但页面编辑器禁用；该问题属于本地验收环境连接状态限制，非本次布局组件 TypeScript 或骨架取证失败。

## REQ 子文档一致性扫尾

- `requirement.md`：本次只收敛 UI 布局表达，不改变业务需求、编号延后、候选稳定 ID、幂等确认和采集记录边界。
- `acceptance.md`：补充附件原型复刻布局验收说明。
- `trace.md`：记录本次 `/opsx-modify` 反馈批次和验证摘要。
- `prototype/**`：原 REQ prototype 仍作为需求链路产物保留；本次验收附件是返修参考，契约落在本文件与 Change design/spec 中。


## 反馈批次：字体层级收敛

- 来源：用户截图反馈“整体的字体大小差别有点大”，页面状态为 Capture 审阅候选深色主题。
- 范围：仅收敛 Capture 弹窗 typography；不调整布局宽度、材料抽屉、候选结构、API、DB、确认幂等或编号契约。
- 证据状态：confirmed。用户截图可见主标题、阶段文本、候选标题、候选正文和按钮整体偏大；当前 CSS 中主标题 30px、审阅标题 20px、基础字号 14px、候选编号 18px，与附件原型密度不匹配。

### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-a80481b8-bb03-424b-94ee-771210a43207.png` | Capture 弹窗 / 审阅候选 / 深色主题 / 桌面视口 | 当前实现截图与 `capture.css` | 字体层级接近附件原型，主标题突出但不压迫，候选正文和按钮保持紧凑 | 主标题、审阅标题、候选标题、正文、按钮和候选编号整体偏大，视觉密度偏低 | 字号、字重、行高、按钮文本密度 | 用户截图 + CSS selector 对照 + Playwright 骨架 computed style | 本次修复 | `src/web/src/components/requirement-center/capture/capture.css`、`evidence/skeleton-styles.json` |

### 调整明细

- `.capture-workspace` 基础字号从 14px 收敛为 13px。
- 主标题从 30px 收敛为 26px，移动端从 24px 收敛为 22px。
- 审阅标题从 20px 收敛为 18px，候选标题从 16px 收敛为 15px。
- 阶段文本、材料抽屉、编辑器 label、按钮、候选选择文本统一收敛到 13px 左右。
- 候选正文与澄清列表收敛到 12.5px 并明确行高；候选编号从 18px 收敛为 15px。
- Badge 轻微收敛到 10.5px，保留识别度。

### 验证记录

- `node node_modules/typescript/bin/tsc --noEmit -p tsconfig.json`：通过。
- `node node_modules/vitest/vitest.mjs run src/capture-dialog.test.tsx src/capture-api.test.ts src/requirement-center.test.tsx -t "unified markdown capture editor|opens full task documents|CaptureDialog|captureApi"`：通过，6 passed / 107 skipped。
- `CAPTURE_SKELETON_BASE=http://127.0.0.1:5190 node tests/capture-skeleton.cjs`：通过，已刷新 1440 dark、1440 light、390 light 截图和 `skeleton-styles.json`。

### REQ 子文档一致性扫尾

- `requirement.md`：无需更新，原因是本次仅收敛视觉字号，不改变产品流程、编号延后、候选审阅能力或幂等确认边界。
- `acceptance.md`：补充字体层级验收说明。
- `trace.md`：通过 Workflow Sync 回写验收返修状态；本 Change trace 记录本批返修。
- `prototype/**`：无需更新，原因是原型意图保持不变，本次是当前实现对原型视觉密度的贴近。


## 反馈批次：按附件比例回调字体层级

- 来源：用户在探索后确认下一轮返修方向为“更像附件”。
- 范围：按附件 `layout-4-console-workbench.html` 的 typography ratio 回调字号、字重、行高和按钮体量；保留 MoonBox 当前字体族、颜色 token、布局结构、材料抽屉、候选审阅动作和确认编号契约。
- 证据状态：confirmed。附件原型中主标题 26px/800、审阅标题 19px/800、候选标题 16px/800、候选正文 13.5px/1.7、候选编号 18px/800、Badge 12px、主按钮 14px；第二轮收敛后当前实现的候选区、Badge 和按钮局部偏小。

### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 附件 HTML `layout-4-console-workbench.html` | Capture 输入/审阅/结果三阶段 | 附件 CSS 与当前 `capture.css` | 保持附件 typography ratio，同时保留 MoonBox DS token | 第二轮后主标题接近附件，但副标题、候选编号、候选标题、描述、Badge、主按钮局部偏小或偏轻 | 字号、字重、行高、按钮 padding、Badge padding | 附件 CSS 对照 + 当前 CSS selector + Playwright computed style | 本次修复 | `src/web/src/components/requirement-center/capture/capture.css`、`evidence/skeleton-styles.json` |

### 调整明细

- 主标题保持 26px，字重提升到 800，贴近附件 `h1`。
- 副标题恢复到 14.5px / 1.6；审阅标题调整到 19px / 800。
- 候选标题恢复到 16px / 800，候选描述恢复到 13.5px / 1.7，候选列表保持 12.5px 但 line-height 恢复到 1.9。
- 候选编号恢复到 18px / 800；Badge 恢复到 12px、`5px 12px`。
- 主按钮恢复到 14px、`11px 20px`；普通操作按钮保持 13px、`8px 14px`。
- MD 编辑器文本恢复到 14.5px / 1.75，并使用当前 DS 字体族，避免等宽字体造成“代码化”观感。

### 验证记录

- `node node_modules/typescript/bin/tsc --noEmit -p tsconfig.json`：通过。
- `node node_modules/vitest/vitest.mjs run src/capture-dialog.test.tsx src/capture-api.test.ts src/requirement-center.test.tsx -t "unified markdown capture editor|opens full task documents|CaptureDialog|captureApi"`：通过，6 passed / 107 skipped。
- `CAPTURE_SKELETON_BASE=http://127.0.0.1:5190 node tests/capture-skeleton.cjs`：通过，已刷新 1440 dark、1440 light、390 light 截图和 `skeleton-styles.json`。

### REQ 子文档一致性扫尾

- `requirement.md`：无需更新，原因是本次仅调整参考稿视觉比例，不改变产品能力、业务流程或数据边界。
- `acceptance.md`：保留此前字体层级贴近附件的验收说明，语义仍适用。
- `trace.md`：通过 Workflow Sync 回写验收返修状态；本 Change trace 记录本批返修。
- `prototype/**`：无需更新，原因是附件原型本身就是本次对照事实源。


## 反馈批次：输入态附件结构复刻

- 来源：用户要求输入态严格按附件复刻，来源材料从大卡片改为紧凑 pill chip；材料抽屉、MD 编辑器、草稿状态和删除草稿放回同一张 card；`AI 整理候选` 改为 card 外全宽主按钮；关闭按钮改为轻量文字按钮；保持 MoonBox token，但布局、尺寸、间距按附件。
- 范围：仅调整 Capture 输入态布局结构、材料 chip 视觉、关闭/删除/主按钮位置、骨架 fixture 与取样脚本；审阅态、确认编号、API、DB、对象存储、幂等写入和正式采集记录边界不变。
- 证据状态：confirmed。用户对比图中当前实现仍为深色大材料卡片、底部 sticky action bar 和重按钮关闭；附件参考为同一白色 card 内的紧凑 pill chip、编辑区、草稿状态与删除草稿，card 外底部全宽主按钮。

### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 返修前实际 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-0e33e8a3-ae9b-4088-a516-aab55af57139.png` | Capture 输入态 / 附件参考 | 来源材料区 | 来源材料标题为抽屉 header，材料以横向紧凑 pill chip 展示，chip 高度接近一行控件 | 来源材料为 210px × 92px 大卡片网格 | 材料 item 尺寸、圆角、排列密度 | 附件截图 + `.capture-material-chip` computed style | 已改为 pill chip | `evidence/skeleton-styles.json`、`evidence/skeleton-1440-light.png` |
| 用户截图 `codex-clipboard-0e33e8a3-ae9b-4088-a516-aab55af57139.png` | Capture 输入态 / 附件参考 | 输入 card | 材料抽屉、MD 编辑器、草稿状态、删除草稿属于同一张 card | 材料区在独立 card，草稿状态和删除草稿在 sticky footer | 层级归属、footer 位置 | DOM selector 对照 + 骨架截图 | 已移入 `.capture-editor-panel` | `src/web/src/components/requirement-center/capture/CaptureDialog.tsx` |
| 用户截图 `codex-clipboard-0e33e8a3-ae9b-4088-a516-aab55af57139.png` | Capture 输入态 / 附件参考 | 主动作 | `AI 整理候选 →` 位于 card 外，横向撑满内容宽度 | 主动作在弹窗 footer 右侧，与删除草稿并列 | 按钮位置、宽度、层级 | `.capture-input-submit` computed style | 已改为 card 外全宽主按钮 | `evidence/skeleton-styles.json` |
| 用户截图 `codex-clipboard-94eaf343-4315-4400-900d-e1d28b32ad3d.png` | 当前深色实现 | 关闭按钮 | 轻量文字“关闭 ×”，不使用强调边框按钮 | 右上角为重边框按钮 | 按钮重量 | selector 对照 | 已改为轻量文字按钮 | `CaptureWorkspace.tsx`、`capture.css` |

### 调整明细

- `CaptureDialog` 输入态不再通过 `CaptureWorkspace.actions` 渲染底部 sticky action bar；输入态 `actions=null`。
- 来源材料 `details.capture-material-drawer` 移入 `capture-editor-panel`，与 MD 编辑器、保存状态和删除草稿同属一张 card。
- `.capture-material-chip` 从大卡片网格改为紧凑 pill chip；图片缩略图缩到 18px，文本文件与图片材料保持同一材料流。
- 删除草稿改为 card 内右下角轻量文本按钮；`AI 整理候选 →` 改为 `.capture-input-submit`，位于 card 外并全宽显示。
- 关闭按钮改为“关闭 ×”轻量文字按钮；保留当前 MoonBox token 和深浅主题变量。
- `capture-skeleton` fixture 与 computed style 采样从旧 `capture-actions`/大卡片更新到 `capture-input-submit`/pill chip。

### 验证记录

- `node node_modules/typescript/bin/tsc --noEmit -p tsconfig.json`：通过。
- `node node_modules/vitest/vitest.mjs run src/capture-api.test.ts src/capture-dialog.test.tsx src/requirement-center.test.tsx --pool=threads`：通过，113 passed。
- `CAPTURE_SKELETON_BASE=http://127.0.0.1:5190 node tests/capture-skeleton.cjs`：通过，刷新 1440 dark、1440 light、390 light 截图和 `skeleton-styles.json`。
- `capture-persistence.test.tsx`：未纳入本轮通过证据。该文件仍覆盖 BUG-0014 时代的旧“Capture 标题/一句话描述/直接创建”表单，和 REQ-0029 的候选审阅新流程不一致；本轮不为兼容废弃表单回滚产品实现。

### REQ 子文档一致性扫尾

- `requirement.md`：无需更新，原因是本次收敛输入态布局，不改变用户流程、候选审阅、编号延后、幂等确认或正式采集记录边界。
- `acceptance.md`：补充“紧凑 pill chip、同 card、card 外全宽主按钮、轻量关闭”验收表述。
- `trace.md`：记录本轮 `/opsx-modify` 反馈、验证摘要和待复验状态。
- `prototype/**`：无需更新，原因是本轮附件参考即为验收事实源，契约落在本文件、Change design/spec 和骨架证据中。


## 反馈批次：按 Markdown 右侧抽屉收敛字体密度

- 来源：用户要求“按 Markdown 右侧抽屉的阅读/编辑密度收敛 Capture 弹窗字体”，并确认 MD 输入区改成右侧抽屉同款 `monospace 12.5px`。
- 范围：仅调整 Capture 弹窗 typography；不改变输入态布局、材料流、草稿保存、候选审阅、确认编号、API、DB、对象存储、幂等写入和正式采集记录边界。
- 证据状态：confirmed。只读对比显示右侧 Markdown 抽屉正文为 `12.5px/1.68`，编辑 textarea 为 `12.5px/1.85 monospace`，pill 为 `11px`，footer button 为 `12.5px`；Capture 返修前主标题 26px、输入 textarea 14.5px 正文字体、主按钮 14px、候选正文 13.5px，整体视觉密度高于抽屉。

### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 返修前实际 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 项目现有 Markdown 右侧抽屉 | 需求中心 / Markdown drawer / 查看与编辑模式 | `.rc-rendered-markdown`、`.rc-markdown-view textarea`、`.rc-markdown-pill`、`.rc-markdown-footer-actions button` | Capture 的正文、MD 输入区、pill、状态和按钮密度贴近抽屉；主标题保留略高层级 | Capture 主标题 26px，输入区 14.5px 正文字体，chip 12.5px，主按钮 14px，候选正文 13.5px | 字号、字体族、行高、字重 | CSS selector 对照 + `capture-skeleton.cjs` computed style + 1440/390 截图 | 本次修复 | `src/web/src/components/requirement-center/capture/capture.css`、`evidence/skeleton-styles.json`、`evidence/skeleton-1440-light.png` |

### 调整明细

- 主标题从 26px 降到 24px，移动端从 24px 降到 22px，保留 Capture 入口层级。
- 顶部副标题从 14.5px 收敛到 13px；来源材料抽屉 header 从 13.5px 收敛到 12.5px。
- 材料 chip、图片/文本材料名称与计数从 12.5px 收敛到 11.5px，接近右侧抽屉 pill 密度。
- MD 输入区改为 `12.5px/1.85 ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace`，对齐右侧 Markdown 抽屉编辑 textarea。
- 草稿状态从 12.5px 收敛到 11.5px；普通按钮从 13px 收敛到 12.5px；主按钮从 14px/700 收敛到 13px/650。
- 候选正文从 13.5px/1.7 收敛到 12.5px/1.68；Badge 从 12px/700 收敛到 11.5px/650。

### 验证记录

- `node node_modules/typescript/bin/tsc --noEmit -p tsconfig.json`：通过。
- `node node_modules/vitest/vitest.mjs run src/capture-api.test.ts src/capture-dialog.test.tsx src/requirement-center.test.tsx --pool=threads`：通过，113 passed。
- `CAPTURE_SKELETON_BASE=http://127.0.0.1:5190 node tests/capture-skeleton.cjs`：通过，刷新 1440 dark、1440 light、390 light 截图和 `skeleton-styles.json`。

### REQ 子文档一致性扫尾

- `requirement.md`：无需更新，原因是本次仅调整字体密度，不改变产品流程、材料输入、候选审阅、编号延后、来源追溯或确认写入边界。
- `acceptance.md`：补充按 Markdown 右侧抽屉阅读/编辑密度收敛字体的验收说明。
- `trace.md`：记录本轮 `/opsx-modify` 反馈、证据入口和验证摘要。
- `prototype/**`：无需更新，原因是本次为实现与既有产品 Markdown 抽屉密度对齐，不改变原型结构或 Mock/API 边界。


## 反馈批次：Markdown 抽屉标题与审阅标签对齐

- 来源：用户要求 Capture 弹窗全局字体 family、主标题、顶部 kicker、审阅态文案和候选标签与需求中心 Markdown 右侧抽屉一致；主标题按抽屉标题样式 19px，第 2 步标题改为“AI 审阅结果”，副标题改为候选/需求/缺陷统计，删除候选说明 notice 模块。
- 范围：仅调整 Capture 弹窗 typography、审阅态文案、候选卡片顶部标签和删除按钮语义色；不改变输入态布局、材料流、草稿保存、候选稳定 ID、编辑/合并/拆分/删除数据流程、确认幂等、编号延后或正式采集记录生成边界。
- 证据状态：confirmed。上一轮实现仍保留 Capture 专属标题层级：主标题 24px，kicker 为弱化样式，审阅标题文案为“AI 已整理出 x 条候选”，候选卡片仍展示“条目 n”和合并类型/分级 badge，并保留候选说明 notice；与 Markdown 右侧抽屉的 19px 标题、crumb 色彩和紧凑审阅密度不一致。

### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 返修前实际 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 项目现有 Markdown 右侧抽屉 | 需求中心 / Markdown drawer | 弹窗全局字体 family | Capture body/heading/mono family 与抽屉使用同一 token 体系 | Capture 使用局部 `--cap-*` 但标题层级仍带入口差异 | font-family、字号层级 | CSS selector 对照 + computed style | 已改为 `--rc-font-body`、`--rc-font-heading`、`--rc-font-mono` 优先 | `capture.css`、`evidence/skeleton-styles.json` |
| 项目现有 Markdown 右侧抽屉 | 顶部标题 | `.capture-workspace h1` | 主标题使用抽屉标题样式，19px / 650 | 主标题 24px，仍高于抽屉标题 | font-size、line-height、weight | `capture-skeleton.cjs` 采样 `.capture-workspace h1` | 已改为 19px / 1.25 / 650 | `skeleton-styles.json` |
| 项目现有 Markdown 右侧抽屉 | 顶部 crumb | `.capture-kicker` | “新建 CAPTURE”使用抽屉 crumb 样式和颜色 | Kicker 为弱化说明色，存在额外字距/大写处理 | color、font、letter-spacing | `capture-skeleton.cjs` 采样 `.capture-kicker` | 已改为 accent 色、11.5px monospace、无额外字距 | `skeleton-styles.json` |
| 用户本轮文字反馈 | Capture 审阅态 | 审阅标题/副标题 | 标题为“AI 审阅结果”，18px；副标题为“x 条候选 · x 条需求 / x 条缺陷” | 标题为“AI 已整理出 x 条候选”，副标题为操作说明 | 文案、字号、信息层级 | `capture-dialog.test.tsx` DOM 断言 | 已调整 | `src/web/src/components/requirement-center/capture/CaptureDialog.tsx` |
| 用户本轮文字反馈 | Capture 审阅态候选卡 | 候选 card 顶部 | 不显示“条目 n”；展示类型标签与分级标签；删除按钮为危险色 | 左侧/顶部仍以“条目 n”为主标签，删除为普通按钮色 | 标签语义、危险动作颜色 | DOM 断言 + CSS selector 对照 | 已改为“需求/BUG”标签 + priority/severity 标签，删除使用 `.capture-danger-action` | `capture-dialog.test.tsx`、`capture.css` |
| 用户本轮文字反馈 | Capture 审阅态 notice | 候选说明模块 | 删除“这些仍是候选……” notice 模块 | 保留说明 notice | 冗余提示模块 | DOM 断言 `queryByText(/这些仍是候选/)` | 已删除渲染 | `capture-dialog.test.tsx` |

### 调整明细

- `.capture-workspace` 全局字体通过 `--rc-font-body` / `--rc-font-heading` / `--rc-font-mono` 对齐需求中心 Markdown 抽屉；按钮、标题、编辑器和材料 chip 统一继承该体系。
- 主标题从 24px 收敛到 19px / 650；第 2 步标题使用 18px / 650。
- “新建 CAPTURE”从弱化大写说明改为抽屉 crumb 风格：11.5px monospace、accent 色、无额外 letter spacing。
- 审阅态标题改为“AI 审阅结果”；副标题由静态操作说明改为 `{候选数} 条候选 · {需求数} 条需求 / {缺陷数} 条缺陷`。
- 候选卡片不再可见展示“条目 n”，保留 checkbox 的 `aria-label=选择条目 n` 作为可访问选择语义；卡片顶部展示类型标签和分级标签。
- 删除候选按钮改为 `.capture-danger-action`，使用危险色 token；候选说明 notice 模块从审阅态渲染中移除。

### 验证记录

- `node node_modules/typescript/bin/tsc --noEmit -p tsconfig.json`：通过。
- `node node_modules/vitest/vitest.mjs run src/capture-api.test.ts src/capture-dialog.test.tsx src/requirement-center.test.tsx --pool=threads`：通过，113 passed。
- `CAPTURE_SKELETON_BASE=http://127.0.0.1:5190 node tests/capture-skeleton.cjs`：通过，刷新 1440 dark、1440 light、390 light 截图和 `skeleton-styles.json`；其中 1440 dark/light 的 `.capture-workspace h1` 均为 19px，`.capture-kicker` 均为 11.5px monospace。

### REQ 子文档一致性扫尾

- `requirement.md`：无需更新，原因是本次只调整 UI 字体、文案和候选标签，不改变产品能力、候选编辑、编号延后、来源追溯或确认写入边界。
- `acceptance.md`：补充 Markdown 抽屉标题、kicker、审阅标题/统计、候选双标签、危险删除和 notice 移除的验收说明。
- `trace.md`：记录本轮 `/opsx-modify` 反馈、证据入口和验证摘要。
- `prototype/**`：无需更新，原因是本轮以现有 Markdown 右侧抽屉为产品内视觉基线，不改变附件原型结构、Mock/API 边界或数据流程。


## 反馈批次：删除弹窗顶部主标题与副标题

- 来源：用户在 `/explore` 后确认 `/opsx-modify`：删除 Capture 弹窗顶部主标题和副标题，仅保留顶部 crumb、步骤条和内容区标题；输入说明移入 MD 编辑器 placeholder 或 card 内轻提示；不改布局和数据流程。
- 范围：仅调整 Capture 弹窗顶部信息层级、MD 编辑器 placeholder、视觉采样 selector 和相关验收文档；不改变输入态 card 布局、材料抽屉、材料 chip、草稿保存、候选整理/审阅、确认幂等、编号延后、API、DB 或对象存储契约。
- 证据状态：confirmed。当前弹窗顶部同时存在 `新建 CAPTURE`、主标题“写下需求或问题”、副标题、步骤条和内容区标题；主标题/副标题与 crumb、步骤条、输入区 placeholder 可承载的说明重复，降低 Markdown 抽屉式密度。

### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 返修前实际 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户本轮文字反馈 | Capture 弹窗 / 输入态与审阅态通用顶部 | 弹窗 topbar、标题区和步骤条 | 顶部只保留 `新建 CAPTURE` crumb、关闭按钮和三点式步骤条；不展示独立主标题/副标题 | 顶部除 crumb 和步骤条外仍展示“写下需求或问题”和说明副标题 | 信息重复、视觉层级过重、顶部占高 | DOM 选择器、单测 `queryByText`、1440/390 skeleton 截图 | 本次修复 | `CaptureWorkspace.tsx`、`capture-dialog.test.tsx`、`evidence/skeleton-1440-light.png` |
| 用户本轮文字反馈 | Capture 输入态 | MD 编辑器 placeholder | 输入说明移入 MD 编辑器 placeholder 或 card 内轻提示 | placeholder 仅展示示例和材料添加说明，顶部副标题承担主要解释 | 引导文案位置 | DOM 断言 + textarea placeholder | 本次修复，placeholder 增加“写下需求、问题或补充背景” | `CaptureDialog.tsx`、`capture-dialog.test.tsx` |
| 当前视觉证据 | Capture skeleton / 1440 light & dark / 390 light | computed style 采样 | 不再采样 `.capture-workspace h1`，改采样 `.capture-kicker` 与 `.capture-progress strong` | 采样仍包含已删除的 h1 selector | 验收证据 selector 过期 | `capture-skeleton.cjs` + `skeleton-styles.json` | 已更新 selector 并刷新证据 | `src/web/tests/capture-skeleton.cjs`、`evidence/skeleton-styles.json` |

### 调整明细

- `CaptureWorkspace` 删除 `.capture-heading` 区块，不再渲染“写下需求或问题”和顶部说明副标题。
- `CaptureDialog` 的 MD 编辑器 placeholder 增加“写下需求、问题或补充背景”，继续保留示例和图片/文本文件材料入口说明。
- `capture.css` 删除未使用的 `.capture-heading` 和 `h1` 专属样式，顶部只保留 crumb、关闭按钮和步骤条；步骤条间距轻微收紧。
- `capture-skeleton.cjs` 将 computed style 采样从 `.capture-workspace h1` 改为 `.capture-progress strong`，与当前 DOM 对齐。
- `capture-dialog.test.tsx` 增加顶部主标题/副标题不存在、placeholder 包含输入说明的断言。

### 验证记录

- `node node_modules/typescript/bin/tsc --noEmit -p tsconfig.json`：通过。
- `node node_modules/vitest/vitest.mjs run src/capture-api.test.ts src/capture-dialog.test.tsx src/requirement-center.test.tsx --pool=threads`：通过，113 passed。
- `CAPTURE_SKELETON_BASE=http://127.0.0.1:5190 node tests/capture-skeleton.cjs`：通过，刷新 1440 dark、1440 light、390 light 截图和 `skeleton-styles.json`；1440 light/dark 下 `.capture-kicker` 为 11.5px，`.capture-progress strong` 为 13px，MD textarea 为 12.5px monospace。

### REQ 子文档一致性扫尾

- `requirement.md`：无需更新，原因是本次不改变产品能力、输入/审阅流程、编号延后、来源追溯或确认写入边界。
- `acceptance.md`：补充顶部标题/副标题删除、输入说明迁移到 placeholder 的验收说明。
- `trace.md`：记录本轮 `/opsx-modify` 反馈、证据入口和验证摘要。
- `prototype/**`：无需更新，原因是本轮是基于当前验收反馈对实现信息层级做精简，未改变原型结构、Mock/API 边界或材料/候选数据流程。


## 反馈批次：候选标题行、材料文案与二次弹窗可读性

- 来源：用户提供最新深色主题审阅态截图 `codex-clipboard-b0c4d748-308e-4232-b7c6-dc0e74058977.png` 并明确反馈：第 2 步结果标题与复选框应该在同一行；来源依据、拆分、删除二次弹窗无法查看；第 1 步来源材料删除“确认前仅保存草稿、图片材料、123/20000”和“原始材料”标签；删除第 1 步输入 card/来源材料外部边框。
- 范围：仅调整 Capture 弹窗视觉层级、候选卡片标题行、材料 chip 文案、输入态外框和二次 modal 可读性；不改变草稿保存、材料上传、候选稳定 ID、来源追溯、合并/拆分/删除数据流程、确认幂等或编号分配。
- 证据状态：confirmed。截图显示二次 modal 内容与候选卡文本叠加，可读性不足；当前 DOM/CSS 显示来源材料 summary 仍包含“确认前仅保存草稿”，MD 文本 chip 仍展示字符计数，图片 chip 副文案可能显示“图片材料”，输入区仍有 `.capture-editor-panel` 外框，候选标题位于复选框下一行。

### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 返修前实际 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-b0c4d748-308e-4232-b7c6-dc0e74058977.png` | Capture / 第 2 步审阅候选 / 深色主题 / 来源依据 modal 打开 | 二次 modal 层级与可读性 | 来源依据、拆分、删除等二次弹窗应作为独立高层级 modal，内容和按钮清晰可读 | modal 与候选卡文本叠加，遮罩和背景文本干扰阅读 | z-index、backdrop、背景、滚动、footer 可见性 | 截图 + CSS selector 对照 + DOM 单测 | 本次修复：提高 modal z-index、加深遮罩与 blur、modal 实底色/强阴影、body 滚动、footer 边界固定可见 | `capture.css`、`capture-dialog.test.tsx` |
| 用户截图 `codex-clipboard-b0c4d748-308e-4232-b7c6-dc0e74058977.png` | Capture / 第 2 步候选卡 | 候选卡顶部 | 复选框与结果标题同一行，类型/分级标签位于右侧 | 复选框单独一行，标题另起一行 | 对齐、信息绑定、标题位置 | DOM 单测 + selector 对照 | 本次修复：`.capture-candidate-title` 包含 checkbox 与标题，右侧保留标签 | `CaptureDialog.tsx`、`capture-dialog.test.tsx` |
| 用户截图文字反馈 | Capture / 第 1 步输入态 | 来源材料区域 | 删除“确认前仅保存草稿”“图片材料”“123/20000”等辅助文案；保留简洁材料 chip | summary 副文案、MD 计数和图片副文案仍显示 | 文案冗余、材料 chip 密度 | DOM 单测 + skeleton 截图 | 本次修复：summary 仅保留“来源材料 · x 项”，MD chip 仅“MD 文本”，图片 chip 仅“图片 n” | `CaptureDialog.tsx`、`skeleton-1440-light.png` |
| 用户截图文字反馈 | Capture / 第 1 步输入态 | 输入 card / 来源材料外框 | 去掉输入 card/来源材料外部边框，仅保留编辑器和控件必要边界 | `.capture-editor-panel` 仍有 border、radius、shadow | 外框、层级、卡片感过重 | computed style + skeleton 截图 | 本次修复：`.capture-editor-panel` border/background/shadow 清零，来源材料抽屉透明无 padding | `capture.css`、`skeleton-styles.json` |

### 调整明细

- 来源材料 summary 删除右侧“确认前仅保存草稿”；MD chip 删除字符计数；图片 chip 删除副文案，默认图片名不再使用“图片材料”。
- 删除输入态可见 “原始材料” label，textarea 保留 `aria-label="原始材料"` 以维持测试、可访问性和表单语义。
- `.capture-editor-panel` 外框、圆角、背景和阴影清零；来源材料 drawer 保持透明，textarea 自身保留边框作为主要编辑边界。
- 候选卡顶部改为 `.capture-candidate-title`：checkbox 与候选标题位于同一行，类型和分级标签继续在右侧。
- 二次 modal backdrop 提升到独立高层级，遮罩加深并 blur；modal 改为实底色 flex 布局，body 独立滚动，footer 与内容分隔并保持清晰。

### 验证记录

- `node node_modules/typescript/bin/tsc --noEmit -p tsconfig.json`：通过。
- `node node_modules/vitest/vitest.mjs run src/capture-api.test.ts src/capture-dialog.test.tsx src/requirement-center.test.tsx --pool=threads`：通过，113 passed。
- `CAPTURE_SKELETON_BASE=http://127.0.0.1:5190 node tests/capture-skeleton.cjs`：通过，刷新 1440 dark、1440 light、390 light 截图和 `skeleton-styles.json`；1440 light/dark 下 `.capture-material-drawer` padding 为 0、background 为透明，textarea 仍保留 12.5px monospace 与自身边界。

### REQ 子文档一致性扫尾

- `requirement.md`：无需更新，原因是本次仍属于既有 UI 验收精简和可读性返修，不改变需求目标、业务流程、确认规则或数据边界。
- `acceptance.md`：补充候选标题行、二次 modal 可读性、来源材料文案精简和输入外框精简验收说明。
- `trace.md`：记录本轮 `/opsx-modify` 反馈、证据入口和验证摘要。
- `prototype/**`：无需更新，原因是本轮反馈来自实际验收截图，未改变原型的单一 MD 编辑器、材料流、候选审阅和确认写入边界。


## 反馈批次：附件拆分删除与来源依据行内化

- 来源：用户提供 `layout-5-split-delete.html` 并明确要求第 2 步删除 `AI 审阅结果` 标题；来源依据改为候选卡内 label 加具体依据文本；拆分和删除改为候选卡内展开面板；确认创建不再二次弹窗。
- 范围：仅调整 Capture 审阅态信息结构与交互承载；不改变候选稳定 ID、来源追溯、确认版本绑定、服务端幂等、编号延后、按最终类型分配编号或正式 capture.md/trace.md 生成边界。
- 证据状态：confirmed。上一轮为了修复可读性将来源依据、拆分、删除保留为高层级 modal，但最新反馈要求这些动作回到卡内，避免审阅态被多层弹窗打断。

### 附件截图逐项视觉对照表

| 附件/反馈 | 页面/状态 | 对照对象 | 期望表现 | 返修前实际 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| `layout-5-split-delete.html` 与用户文字反馈 | Capture / 第 2 步审阅态 | 审阅头部 | 不显示 `AI 审阅结果`，只显示候选统计与合并所选 | 仍显示 `AI 审阅结果` 标题 | 信息层级冗余 | DOM 单测 `queryByText` | 本次修复 | `CaptureDialog.tsx`、`capture-dialog.test.tsx` |
| `layout-5-split-delete.html` 与用户文字反馈 | Capture / 候选卡 | 来源依据 | 卡内 label `来源依据` 后直接展示具体依据文本 | 来源依据通过按钮和弹窗查看，按钮只显示数量 | 信息不可直接阅读 | DOM 单测 + CSS selector | 本次修复：用 `classification_reason` 等具体文本行内展示 | `CaptureDialog.tsx`、`capture.css` |
| `layout-5-split-delete.html` 与用户文字反馈 | Capture / 候选卡 / 拆分 | 拆分交互 | 卡内展开面板，编辑两个子条目的标题和描述后确认 | 打开二次弹窗，且只适合弹窗式编辑 | 承载方式、编辑字段 | DOM 单测 + TypeScript | 本次修复：`capture-split-panel` 卡内展开 | `CaptureDialog.tsx`、`capture-dialog.test.tsx` |
| `layout-5-split-delete.html` 与用户文字反馈 | Capture / 候选卡 / 删除 | 删除交互 | 卡内展开危险确认面板 | 打开删除二次弹窗 | 承载方式 | DOM 单测 + danger 色断言 | 本次修复：`capture-delete-panel` 卡内展开 | `CaptureDialog.tsx`、`capture.css` |
| 用户文字反馈 | Capture / footer 主动作 | 确认创建 | 点击后直接提交确认流程 | 先打开“确认创建这批记录”二次弹窗 | 多余确认步骤 | DOM 单测 `queryByRole` | 本次修复：按钮直接调用 `confirm()` | `CaptureDialog.tsx`、`capture-dialog.test.tsx` |

### 调整明细

- 审阅头部删除 `AI 审阅结果` 标题，只保留 `{候选数} 条候选 · {需求数} 条需求 / {缺陷数} 条缺陷` 与 `合并所选`。
- 候选卡新增 `.capture-source-evidence`，以 label + 正文方式展示具体依据；优先使用 `classification_reason`。
- 拆分按钮打开卡内 `.capture-split-panel`，支持两个子条目的标题与描述编辑，确认后仍由现有拆分逻辑生成子候选并保留父来源。
- 删除按钮打开卡内 `.capture-delete-panel`，显式取消或确认删除；删除动作仍只移出确认集合，不删除共享材料。
- `确认创建 N 条` 直接提交确认流程；不再打开确认二次弹窗，服务端仍以 expected_revision 与幂等键绑定最终候选版本。

### 验证记录

- `node node_modules/typescript/bin/tsc --noEmit -p tsconfig.json`：通过。
- `node node_modules/vitest/vitest.mjs run src/capture-api.test.ts src/capture-dialog.test.tsx src/requirement-center.test.tsx --pool=threads`：通过，113 passed。
- `CAPTURE_SKELETON_BASE=http://127.0.0.1:5190 node tests/capture-skeleton.cjs`：通过，1440px dark/light 与 390px 合成骨架通过；本轮未改变输入态骨架尺寸。

### REQ 子文档一致性扫尾

- `requirement.md`：无需更新，原因是本次仅改变审阅态动作承载方式，不改变 REQ-0029 的业务流程、确认规则、编号延后、来源追溯或产物边界。
- `acceptance.md`：同步删除 `AI 审阅结果` 标题、来源依据行内化、拆分/删除卡内展开和确认创建直接提交的验收说明。
- `trace.md`：记录本轮 `/opsx-modify` 反馈、证据入口和验证摘要。
- `prototype/**`：无需更新，原因是附件 `layout-5-split-delete.html` 属于本轮验收参考，当前实现和 OpenSpec 契约已承接其关键交互；既有原型历史文件作为需求准备资料保留。


## 反馈批次：拆分删除面板向下展开

- 来源：用户确认 `/opsx-modify`：Capture 第 2 步候选卡拆分/删除展开面板改为向下展开；拆分面板左右两栏，每栏都是完整子条目，包含类目、标题、描述，两个子条目可分别选择需求或 BUG。
- 范围：仅调整 Capture 审阅态卡内展开位置和拆分面板字段结构；不改变候选 ID、父来源边、来源追溯、确认幂等、编号分配或服务端数据流程。
- 证据状态：confirmed。代码证据显示拆分/删除面板原本插在 `.capture-card-actions` 之前，因此打开后按钮位于面板下方，用户感知为向上展开；拆分面板原本是四个字段平铺，未呈现左右两个完整子条目。

### 附件截图逐项视觉对照表

| 附件/反馈 | 页面/状态 | 对照对象 | 期望表现 | 返修前实际 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户文字反馈 | Capture / 第 2 步候选卡 / 拆分或删除展开 | 面板展开方向 | 面板在操作按钮行之后向下展开 | 面板在操作按钮行之前渲染，按钮被推到面板下方 | DOM 顺序、视觉展开方向 | DOM 单测 `compareDocumentPosition` | 本次修复：面板移动到 `.capture-card-actions` 之后 | `CaptureDialog.tsx`、`capture-dialog.test.tsx` |
| 用户文字反馈 | Capture / 第 2 步候选卡 / 拆分展开 | 拆分面板结构 | 左右两栏，每栏完整包含类目、标题、描述 | 四个字段平铺，仅标题/描述，没有子条目类目选择 | 字段结构、信息组织、类目选择 | DOM 单测 role/label 断言 + TypeScript | 本次修复：新增 `capture-split-item` 左右两栏，每栏含类目、标题、描述 | `CaptureDialog.tsx`、`capture.css` |
| 用户文字反馈 | Capture / 第 2 步候选卡 / 删除展开 | 删除面板位置 | 删除面板也在删除按钮下方向下展开 | 删除面板位于按钮行上方 | DOM 顺序、操作关联 | DOM 单测 | 本次修复 | `CaptureDialog.tsx`、`capture-dialog.test.tsx` |

### 调整明细

- 将拆分/删除面板 JSX 从候选操作按钮行之前移动到按钮行之后，视觉上向下展开。
- `splitDraft` 增加 `typeA` 与 `typeB`，打开拆分面板时条目 A 默认沿用原候选类型，条目 B 默认取另一类目，用户可分别调整。
- `splitCandidate` 支持两个子条目的独立类目，并按类目写入默认 priority/severity；父候选来源、parents、source_refs、classification_reason 继续保留。
- 拆分面板新增 `.capture-split-item` 两栏结构，每栏包含类目、标题和描述；窄屏仍沿用既有 media query 单列降级。
- 删除面板保留原危险确认语义，仅调整到按钮行之后展开。

### 验证记录

- `node node_modules/typescript/bin/tsc --noEmit -p tsconfig.json`：通过。
- `node node_modules/vitest/vitest.mjs run src/capture-api.test.ts src/capture-dialog.test.tsx src/requirement-center.test.tsx --pool=threads`：通过，113 passed。
- `CAPTURE_SKELETON_BASE=http://127.0.0.1:5190 node tests/capture-skeleton.cjs`：通过，1440px dark/light 与 390px 合成骨架通过；本轮不改变输入态骨架。

### REQ 子文档一致性扫尾

- `requirement.md`：无需更新，原因是本次仅改变审阅态面板位置和拆分面板字段组织，不改变 REQ-0029 的业务流程、确认规则、编号延后、来源追溯或产物边界。
- `acceptance.md`：同步拆分/删除面板向下展开、拆分左右两栏完整子条目的验收说明。
- `trace.md`：记录本轮 `/opsx-modify` 反馈、证据入口和验证摘要。
- `prototype/**`：无需更新，原因是本轮是实际验收反馈对当前实现交互结构的细化，未改变单一 MD 编辑器、材料流、候选审阅和确认写入边界。


## 反馈批次：上传文本文件可删除

- 来源：用户确认 `/opsx-modify`：第 1 步来源材料中的上传文本文件需要支持删除；文本文件上传后在来源材料中显示独立 chip，包含文件名和删除按钮；删除文本文件 chip 时同步移除 MD 编辑器中对应来源文件块；图片删除保持现有逻辑。
- 范围：仅调整 Capture 输入态来源材料 chip 与 MD 来源块删除交互；不改变图片上传、草稿保存、AI 整理、候选 ID、来源追溯、确认幂等、编号分配或服务端数据流程。
- 证据状态：confirmed。代码证据显示图片材料已有 `removeImage` 和移除按钮；文本文件当前只通过 `sourceFileBlock()` 追加到 MD 正文，没有独立 chip，也没有删除入口。

### 附件截图逐项视觉对照表

| 附件/反馈 | 页面/状态 | 对照对象 | 期望表现 | 返修前实际 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户文字反馈 | Capture / 第 1 步输入态 / 来源材料 | 上传文本文件 chip | 文本文件上传后显示独立 chip，包含文件名和删除按钮 | 文本文件只追加进 MD 正文，来源材料区不显示文件 chip | 材料可见性、删除入口 | DOM 单测 + 文本块解析 | 本次修复：从来源文件块派生 `capture-text-file-card` | `CaptureDialog.tsx`、`capture-dialog.test.tsx` |
| 用户文字反馈 | Capture / 第 1 步输入态 / 删除文本文件 | MD 编辑器正文 | 删除文本文件 chip 时同步移除对应来源文件块 | 无删除入口，用户只能手动编辑正文 | 删除行为、正文同步 | DOM 单测：点击删除后正文不含来源文件块 | 本次修复 | `capture-dialog.test.tsx` |
| 用户文字反馈 | Capture / 第 1 步输入态 / 图片材料 | 图片删除 | 保持现有图片删除逻辑 | 已有 `removeImage` 删除图片 chip 与 `media_ids` | 无偏差 | 回归测试 | 无需修改 | `CaptureDialog.tsx` |

### 调整明细

- 新增 `sourceFileBlocks()`，从 MD 正文解析 `### 来源文件：...` fenced block，作为文本文件 chip 的派生数据源。
- 来源材料 summary 计数改为 `MD 文本 + 文本文件 chip + 图片 chip`。
- 文本文件 chip 展示文件名和删除按钮；点击删除按钮时按当前 block 边界从 MD 正文删除对应来源文件块。
- 图片删除逻辑不变，仍通过 `removeImage()` 移除本地预览与 `media_ids`。
- 不新增服务端字段；文本来源事实仍保存在单一 MD 编辑器正文中。

### 验证记录

- `node node_modules/typescript/bin/tsc --noEmit -p tsconfig.json`：通过。
- `node node_modules/vitest/vitest.mjs run src/capture-api.test.ts src/capture-dialog.test.tsx src/requirement-center.test.tsx --pool=threads`：通过，113 passed。
- `CAPTURE_SKELETON_BASE=http://127.0.0.1:5190 node tests/capture-skeleton.cjs`：通过，1440px dark/light 与 390px 合成骨架通过。

### REQ 子文档一致性扫尾

- `requirement.md`：无需更新，原因是本次属于既有“单一 MD 编辑器 + 文本文件材料块”的删除能力补齐，不改变需求目标、业务流程、确认规则、编号延后、来源追溯或产物边界。
- `acceptance.md`：同步上传文本文件 chip 与删除同步移除来源文件块的验收说明。
- `trace.md`：记录本轮 `/opsx-modify` 反馈、证据入口和验证摘要。
- `prototype/**`：无需更新，原因是本轮只补齐实际实现中的材料 chip 删除交互，未改变原型结构、Mock/API 边界或材料/候选数据流程。


## 反馈批次：编辑按钮图标与编辑面板向下展开

- 来源：用户确认 `/opsx-modify`：第 2 步候选卡操作区将 `编辑 / 改类型` 文案改为 `编辑` 并添加编辑图标；删除按钮添加删除图标；编辑面板改为在候选卡操作按钮行之后向下展开，与拆分/删除面板方向一致；编辑面板内容和行为保持不变。
- 范围：仅调整 Capture 审阅态候选卡操作按钮文案、图标和编辑面板渲染位置；不改变候选 ID、来源追溯、确认幂等、编号分配或服务端数据流程。
- 证据状态：confirmed。代码证据显示 `capture-inline-edit` 原本渲染在 `.capture-card-actions` 之前，`编辑 / 改类型` 和 `删除` 按钮没有对应图标。

### 附件截图逐项视觉对照表

| 附件/反馈 | 页面/状态 | 对照对象 | 期望表现 | 返修前实际 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户文字反馈 | Capture / 第 2 步候选卡 / 操作区 | 编辑按钮 | 文案为 `编辑`，带编辑图标 | 文案为 `编辑 / 改类型`，无图标 | 文案、图标 | DOM 单测 + 代码检查 | 本次修复 | `CaptureDialog.tsx`、`capture-dialog.test.tsx` |
| 用户文字反馈 | Capture / 第 2 步候选卡 / 操作区 | 删除按钮 | 带删除图标 | 只有文字 `删除` | 图标 | DOM 单测 + 代码检查 | 本次修复 | `CaptureDialog.tsx` |
| 用户文字反馈 | Capture / 第 2 步候选卡 / 编辑展开 | 编辑面板方向 | 面板在操作按钮行之后向下展开 | 面板在操作按钮行之前渲染，打开后按钮被推到面板下方 | DOM 顺序、视觉展开方向 | DOM 单测 `compareDocumentPosition` | 本次修复 | `CaptureDialog.tsx`、`capture-dialog.test.tsx` |

### 调整明细

- 引入 `Pencil` 图标，编辑按钮从 `编辑 / 改类型` 改为 `Pencil + 编辑`。
- 删除按钮增加 `Trash2` 图标，并保留危险色。
- 将 `capture-inline-edit` 从操作按钮行之前移动到按钮行之后，与拆分/删除面板统一为向下展开。
- 编辑面板内部字段、保存逻辑和改类型保留来源关系的提示均不变。

### 验证记录

- `node node_modules/typescript/bin/tsc --noEmit -p tsconfig.json`：通过。
- `node node_modules/vitest/vitest.mjs run src/capture-api.test.ts src/capture-dialog.test.tsx src/requirement-center.test.tsx --pool=threads`：通过，113 passed。
- `CAPTURE_SKELETON_BASE=http://127.0.0.1:5190 node tests/capture-skeleton.cjs`：通过，1440px dark/light 与 390px 合成骨架通过。

### REQ 子文档一致性扫尾

- `requirement.md`：无需更新，原因是本次仅改变审阅态按钮文案、图标和编辑面板展开位置，不改变需求目标、业务流程、确认规则、编号延后、来源追溯或产物边界。
- `acceptance.md`：同步编辑按钮文案/图标、删除图标和编辑面板向下展开的验收说明。
- `trace.md`：记录本轮 `/opsx-modify` 反馈、证据入口和验证摘要。
- `prototype/**`：无需更新，原因是本轮只细化实际实现的卡内操作交互，未改变原型结构、Mock/API 边界或材料/候选数据流程。


## 反馈批次：第 3 步创建结果按附件收敛

- 来源：用户确认 `/opsx-modify`：第 3 步创建结果按附件收敛，结果区改为左对齐大卡片内容；早期按附件结构包含成功图标、标题和副标题，成功图标已被后续验收反馈覆盖移除；结果列表改为每条采集记录一张卡片，使用 REQ/BUG 编号 badge 作为主身份，展示候选标题、目录、capture.md / trace.md 文件信息和来源摘要，不再把 candidate UUID 作为主要展示；幂等保护和产品边界说明合并为附件样式的实底说明块。
- 范围：仅调整 Capture 第 3 步结果态展示结构与文案；不改变确认幂等、编号分配、来源追溯、服务端 `issue_links` 契约或数据流程。
- 证据状态：confirmed。用户附件对比显示当前结果态与参考结果态差异明显；代码证据显示原实现 `.capture-result` 为 640px 居中摘要，并把 `candidate_id` 与 `issue_id` 作为简单两列映射展示。

### 附件截图逐项视觉对照表

| 附件/反馈 | 页面/状态 | 对照对象 | 期望表现 | 返修前实际 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-eb55a351-7891-488b-8d1e-f00602a8a1e2.png` | Capture / 第 3 步创建结果 / 附件参考 | 结果主区域 | 左对齐标题、副标题和大卡片内容；早期成功图标方案已被后续反馈覆盖 | 当前深色截图中结果内容居中，顶部到结果区留白大 | 对齐、容器宽度、信息密度 | 截图对照 + DOM/CSS 检查 | 本次修复：`.capture-result` 改为左对齐内容流 | `CaptureDialog.tsx`、`capture.css`、`capture-dialog.test.tsx` |
| 用户截图参考 | Capture / 单条结果记录 | 结果卡片 | 每条采集记录卡片展示 REQ/BUG badge、标题、目录、文件、来源 | 只展示左侧 `candidate_id` 与右侧 `issue_id` | 主身份错误、信息不足、UUID 暴露过重 | DOM 单测断言 | 本次修复：使用 `issue_id` badge 作为主身份，并从当前候选快照补标题和来源 | `capture-dialog.test.tsx` |
| 用户截图参考 | Capture / 幂等与产物说明 | 说明块 | 实底说明块，包含幂等保护与产物边界 | 虚线单句提示，只说明重复点击不重复创建 | 说明层级、文案完整性 | DOM 单测 + CSS selector | 本次修复：合并为 `幂等保护` 和 `产物边界` 两段 | `CaptureDialog.tsx`、`capture.css` |
| 用户文字约束 | Capture / 确认完成流程 | 服务端数据流程 | 保留现有 MoonBox token、深浅主题适配、确认幂等、编号分配、来源追溯和服务端数据流程 | 无服务端契约变更需求 | 边界控制 | TypeScript + 单测 | 无需改 API/DB | `captureApi.ts` 未变更 |

### 调整明细

- `CaptureDialog` 结果态从居中摘要改为左对齐结果内容：标题、副标题、结果卡片和说明块按当前验收反馈排列；早期成功图标方案已被后续反馈覆盖移除。
- 结果卡片不再把 `candidate_id` 作为主要展示；`candidate_id` 仅作为服务端映射 key 使用，用户界面主身份改为最终 `REQ/BUG` 编号 badge。
- 结果卡片通过当前确认候选快照补充标题、来源引用和分类依据；目录与 `capture.md` / `trace.md` 文件信息按最终编号生成展示。
- 幂等说明从虚线单句改为实底说明块，分为 `幂等保护` 与 `产物边界`。
- 未修改确认请求、轮询、重试、编号分配、来源追溯、`issue_links` DTO 或服务端写入流程。

### 验证记录

- `node node_modules/typescript/bin/tsc --noEmit`：通过。
- `node node_modules/vitest/vitest.mjs run src/capture-dialog.test.tsx -t CaptureDialog`：通过，4 passed。新增断言覆盖结果态左对齐信息结构、REQ badge、标题、目录、capture.md / trace.md、来源说明、幂等/产物边界说明，以及 `candidate_id` 不作为主要展示。
- `node node_modules/vitest/vitest.mjs run src/capture-api.test.ts src/capture-dialog.test.tsx src/requirement-center.test.tsx -t "unified markdown capture editor|opens full task documents|CaptureDialog|captureApi"`：通过，6 passed / 107 skipped。
- `CAPTURE_SKELETON_BASE=http://127.0.0.1:5190 node tests/capture-skeleton.cjs`：通过，input/result 1440px dark/light 与 390px 合成骨架通过；刷新 `skeleton-result-1440-dark.png`、`skeleton-result-1440-light.png`、`skeleton-result-390-light.png` 和 `skeleton-styles.json`，边界为合成 fixture，不调用 AI、不保存草稿、不创建记录。

### REQ 子文档一致性扫尾

- `requirement.md`：无需更新，原因是本次仅调整第 3 步结果态信息展示，不改变 REQ-0029 的业务目标、用户流程、确认规则、编号延后或产物边界。
- `acceptance.md`：无需更新，原因是既有验收已覆盖确认后生成采集记录、幂等、来源追溯和产物边界；本轮属于 UI 呈现收敛。
- `trace.md`：记录本轮 `/opsx-modify` 反馈、证据入口和验证摘要。
- `prototype/**`：无需更新，原因是本轮按验收附件对实际结果态做 UI 收敛，不改变原型结构、Mock/API 边界或候选确认数据流程。



## 反馈批次：项目内相似 REQ/BUG 检索与重复提示

- 来源：用户追问“Capture 的 AI 解析时有没有判断问题/需求是否已经存在项目中了？”随后明确要求在 AI 整理候选后、用户确认创建前，对候选与项目内已有 REQ/BUG 做相似匹配并提示重复风险。
- 范围：在当前 Change 内补齐确认前审阅层重复提示和处置入口；不新增 API、DB、服务端写入补充材料、权限、部署或对象存储边界。
- 证据状态：confirmed。只读代码核对显示 `capture_organizer.py` 整理时只传入 OpenSpec spec 摘要和原始材料，`capture_confirmations.py` / `capture.py` 仅处理路径/编号占用和确认幂等，未对现有 Issue 标题、摘要、状态或 trace 做语义重复检索。

### 偏差与处置表

| 项 | 期望 | 返修前实际 | 偏差 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|
| 相似项检索 | AI 整理后、确认创建前展示可能相关 REQ/BUG | 候选只展示类型、标题、描述、来源依据和编辑动作 | 用户无法在编号前发现重复或已有记录 | 本次在候选卡内增加 `可能相关` 面板 | `src/web/src/components/requirement-center/capture/CaptureDialog.tsx` |
| 处置选择 | 用户可选择继续创建、合并到已有记录、作为已有记录补充材料或删除候选 | 仅能编辑/合并候选、拆分或删除；没有已有记录处置 | 重复风险只能靠用户手动退出 | 本次提供候选级合并/补充标记；删除沿用现有候选删除 | `capture-dialog.test.tsx` |
| 编号边界 | 合并/补充已有项不分配新 REQ/BUG 编号，继续创建才进入确认批次 | 所有候选默认进入确认集合 | 标记已有项后仍可能被确认创建 | 本次将合并/补充候选排除出 `createCandidates`，确认按钮显示待创建数量 | `CaptureDialog.tsx` |
| 服务端契约 | 确认幂等、最终类型编号和来源追溯不受影响 | 服务端确认以保存后的候选集合为准 | 需要避免前端处置破坏快照语义 | 选择已有项时先保存筛选后的候选集合，再调用既有确认 API；不改确认服务 | `captureApi` 回归未改 |

### 调整明细

- `RequirementCenterPage` 将当前需求中心已加载的 `issues` 作为只读 `existingIssues` 传入 Capture 弹窗，用于候选审阅态相似提示。
- `CaptureDialog` 新增轻量相似度计算：候选标题、描述和分类依据与已有 Issue 的 ID、标题、阶段、来源和文档摘要做词项重叠，最多展示 3 条可能相关项。
- 候选卡新增 `可能相关` 面板，展示已有项 ID、标题、阶段/来源，并提供 `合并`、`补充材料` 和恢复创建操作；旧版默认态 `继续创建新记录` 文案已被后续“相似项提示空态隐藏”反馈覆盖。
- 用户选择 `合并` 或 `补充材料` 后，该候选保留在审阅界面但不进入确认创建集合；统计文案改为待创建需求/缺陷数量，并提示已标记为已有项数量。
- 确认创建仍调用既有保存与确认流程。若存在被标记为已有项的候选，先将最终待创建候选集合写回草稿，再用既有 idempotency key 确认，避免新分配编号。
- 本轮不实现“将补充材料写入已有 REQ/BUG 的 capture.md/trace.md”的服务端落盘；当前语义是确认前审阅处置与避免重复创建。正式追加材料写入可作为后续独立 REQ。

### 验证记录

- `node node_modules/typescript/bin/tsc --noEmit`（`src/web`）：通过。
- `node node_modules/vitest/vitest.mjs run src/capture-dialog.test.tsx -t CaptureDialog`：通过，4 tests passed；覆盖可能相关项展示、标记补充材料后确认创建数量变 0 且禁用、恢复创建后按原流程确认。

### REQ 子文档一致性扫尾

- `requirement.md`：无需更新，原因是主 PRD 已覆盖“用户审阅调整、确认前不分配编号、确认后按最终类型编号”的核心边界，本轮是确认前重复风险提示的验收细化，不改变正式采集产物边界。
- `acceptance.md`：已补充“相似 REQ/BUG 提示、合并/补充标记不进入确认创建批次、不分配新编号”的验收项。
- `trace.md`：记录本轮 `/opsx-modify` 反馈、证据入口和验证摘要。
- `business-flow.md` / `user-stories.md`：无需更新，原因是流程仍为“原始材料 → AI 整理 → 用户审阅 → 确认创建”，本轮新增的是审阅态重复提示分支，不改变主流程、角色或正式产物阶段。



## 反馈批次：MD 文本材料块可删除（已被后续反馈覆盖）

- 来源：用户截图 `codex-clipboard-3c6c3899-a78c-4fdc-a887-d05190170c63.png` 标注第 1 步来源材料中的 `MD 文本` chip，并反馈“这个删除不了，需要支持删除”。
- 当时范围：仅调整 Capture 输入态来源材料 chip 的可见性、删除入口和计数；不改变草稿保存、图片删除、上传文本文件删除、AI 整理、候选 ID、来源追溯、确认幂等或编号分配流程。
- 覆盖结论：该批次已被后续用户反馈“下方 Markdown 编辑器默认存在即可，不需要显示出来”覆盖。当前生效契约见下一批次“默认 Markdown 编辑器不显示来源 chip”：不再展示 `MD 文本` / `编辑器正文` chip，也不把手写或粘贴正文计入来源材料数量。

### 历史证据

| 附件/截图编号 | 页面/状态 | 对照对象 | 当时反馈 | 后续处置 |
|---|---|---|---|---|
| `codex-clipboard-3c6c3899-a78c-4fdc-a887-d05190170c63.png` | Capture / 第 1 步原始材料 / 深色主题 | `MD 文本` 来源材料 chip | 希望可删除 | 后续反馈确认该 chip 不应显示，因此本轮移除 chip 与计数 |

### REQ 子文档一致性扫尾

- 以后一批次“默认 Markdown 编辑器不显示来源 chip”为最终验收依据。


## 反馈批次：默认 Markdown 编辑器不显示来源 chip

- 来源：用户在继续验收中明确“这个 MD 文件是指下方 markdown 编辑框？”并确认“这个就默认存在即可，不需要显示出来，避免误会”。
- 范围：仅调整 Capture 第 1 步来源材料区的 chip 展示与计数；不改变草稿保存、上传文本文件删除、图片删除、AI 整理、候选 ID、来源追溯、确认幂等或编号分配流程。
- 证据状态：confirmed。上一轮实现将手写/粘贴正文展示为 `MD 文本` chip 并计入来源材料数量；用户已明确该编辑器正文应作为默认输入区隐含存在，不作为来源材料 chip。

### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 返修前实际 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户文字反馈 | Capture / 第 1 步原始材料 / 来源材料区 | 默认 Markdown 编辑器正文 | 下方 Markdown 编辑器默认存在，不显示 `MD 文本` 或 `编辑器正文` chip；来源材料只展示额外图片和上传文本文件 | 存在正文时显示 `MD 文本` chip 并计入来源材料 | chip 可见性、计数语义 | DOM 单测 + 代码检查 | 本次修复 | `CaptureDialog.tsx`、`capture-dialog.test.tsx` |

### 调整明细

- 移除 `MD 文本` / `编辑器正文` 来源材料 chip、删除按钮及手写正文拆分清空逻辑。
- 来源材料计数改为 `上传文本文件数 + 图片数`，不再把默认编辑器正文计入材料数量。
- 手写或粘贴正文继续保存在唯一 Markdown 编辑器中，并继续参与草稿保存、AI 整理和候选来源追溯。
- 上传 `.txt` / `.md` 文件形成的文本文件 chip 和图片 chip 删除逻辑保持不变。

### 验证记录

- `node node_modules/typescript/bin/tsc --noEmit`（`src/web`）：通过。
- `node node_modules/vitest/vitest.mjs run src/capture-api.test.ts src/capture-dialog.test.tsx`（`src/web`）：通过，2 files / 7 tests passed；覆盖默认编辑器正文不显示来源 chip、来源材料计数只统计上传文本文件、删除上传文本文件后保留手写正文。
- `openspec validate add-capture-multimodal-candidate-review --strict`：通过。
- `python scripts/validate-openspec-language.py --change add-capture-multimodal-candidate-review`：通过。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。

### REQ 子文档一致性扫尾

- `requirement.md`：无需更新，原因是本次只调整输入态材料 chip 呈现，不改变“单一 MD 编辑器 + 图文材料输入、AI 整理、候选审阅、确认创建”的业务目标和产物边界。
- `acceptance.md`：已更新为“默认 Markdown 编辑器不显示来源 chip，来源材料只统计额外图片和上传文本文件”的验收项。
- `trace.md`：记录本轮 `/opsx-modify` 反馈、证据入口和验证摘要。
- `business-flow.md` / `user-stories.md`：无需更新，原因是主流程、角色、状态转换、候选审阅与确认创建规则均未变化。


## 反馈批次：相似项提示空态隐藏

- 来源：用户截图 `codex-clipboard-5fde3798-14a2-42c6-a69c-c520112c2d00.png` 标注第 2 步候选卡，反馈“如果没有发现相关的，【可能相关模块】不显示。文案【继续创建新记录】不显示”。
- 范围：仅调整 Capture 第 2 步候选卡相似项提示的展示条件和恢复入口文案；不改变相似匹配算法、候选 ID、确认幂等、编号分配或服务端数据流程。
- 证据状态：confirmed。代码证据显示相似项面板按 `candidate.id` 渲染，即使 `matches.length === 0` 也显示空态；默认 `resolutionLabel` 返回 `继续创建新记录`，导致默认创建状态也展示该文案。

### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 返修前实际 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| `codex-clipboard-5fde3798-14a2-42c6-a69c-c520112c2d00.png` | Capture / 第 2 步审阅候选 / 深色主题 | 候选卡相似项提示 | 未发现相关项时不显示 `可能相关` 模块；默认创建状态不显示 `继续创建新记录` | 无匹配时仍显示 `可能相关` 空态和默认创建文案 | 模块可见性、默认文案 | 截图 + DOM 单测 + 代码检查 | 本次修复 | `CaptureDialog.tsx`、`capture-dialog.test.tsx` |

### 调整明细

- 相似项面板渲染条件从 `candidate.id` 收敛为存在相似匹配时才显示。
- 删除无匹配时的空态文案 `未发现高相似的现有 REQ/BUG，可继续创建。`。
- 默认创建状态不再展示 `继续创建新记录`；候选被标记为合并或补充材料后，恢复入口改为 `恢复创建`。
- 合并、补充材料、待创建统计、确认创建幂等和编号分配流程未改。

### 验证记录

- `node node_modules/typescript/bin/tsc --noEmit`（`src/web`）：通过。
- `node node_modules/vitest/vitest.mjs run src/capture-api.test.ts src/capture-dialog.test.tsx`（`src/web`）：通过，2 files / 7 tests passed；覆盖无匹配时不显示可能相关面板和空态，有匹配时仍支持补充材料，并通过 `恢复创建` 回到待创建批次。

### REQ 子文档一致性扫尾

- `requirement.md`：无需更新，原因是本次只调整候选卡相似项提示的空态呈现和默认文案，不改变需求目标、主流程、候选审阅能力或产物边界。
- `acceptance.md`：已补充“无匹配不显示可能相关模块，默认创建状态不显示继续创建新记录”的验收项。
- `trace.md`：记录本轮 `/opsx-modify` 反馈、证据入口和验证摘要。
- `business-flow.md` / `user-stories.md`：无需更新，原因是用户流程仍为 AI 整理候选后审阅、处置和确认创建，本轮只是审阅态展示规则收敛。


## 反馈批次：创建结果态去掉结果图标

- 来源：用户截图 `codex-clipboard-7a28f2ef-b353-4f73-bd8b-a56c518588b1.png` 标注第 3 步创建结果态顶部圆形勾选图标，并反馈“不需要这个图标”；随后追问失败结果是否也会有图标，确认失败/中断不应显示成功图标。
- 范围：仅调整 Capture 第 3 步结果态图标展示；不改变创建结果、确认幂等、编号分配、来源追溯或服务端数据流程。
- 证据状态：confirmed。代码证据显示结果态非 confirming 分支统一渲染 `capture-doneicon` + `Check`，成功、失败和中断结果都会显示圆形成功图标。

### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 返修前实际 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| `codex-clipboard-7a28f2ef-b353-4f73-bd8b-a56c518588b1.png` | Capture / 第 3 步创建结果 / 深色主题 | 顶部圆形勾选图标 | 成功结果、失败或中断结果均不显示结果图标；保留标题、副标题、结果卡片和说明块 | 非 confirming 结果态统一显示圆形成功勾选图标 | 图标可见性、状态语义 | 截图 + DOM 单测 + 代码检查 | 本次修复 | `CaptureDialog.tsx`、`capture.css`、`capture-dialog.test.tsx` |

### 调整明细

- 移除 `Check` 图标导入和非 confirming 结果态的 `capture-doneicon` 渲染。
- 删除 `.capture-doneicon` 样式，并将结果态标题 margin 收敛为无图标布局。
- confirming 状态继续显示 loading 图标，成功/失败/中断结果态只显示标题、副标题、结果卡片、错误提示和对应操作入口。
- 创建结果、确认幂等、编号分配、来源追溯和服务端数据流程未改。

### 验证记录

- `node node_modules/typescript/bin/tsc --noEmit`（`src/web`）：通过。
- `node node_modules/vitest/vitest.mjs run src/capture-api.test.ts src/capture-dialog.test.tsx`（`src/web`）：通过，2 files / 7 tests passed；覆盖完成结果不渲染 `.capture-doneicon`。

### REQ 子文档一致性扫尾

- `requirement.md`：无需更新，原因是本次只调整第 3 步结果态装饰性图标，不改变业务目标、候选确认、采集记录产物或追溯边界。
- `acceptance.md`：已补充“创建结果态不显示结果图标，confirming loading 保留”的验收项。
- `trace.md`：记录本轮 `/opsx-modify` 反馈、证据入口和验证摘要。
- `business-flow.md` / `user-stories.md`：无需更新，原因是主流程、角色、状态转换和失败重试语义均未变化。

---
change_id: add-chat-workbench-image-skill-context
source_requirement: REQ-0028-chat-skill-codex
source_sprint: sprint-006
title: Chat 工作台多材料与 Skill 快速引用验收返修台账
created_at: 2026-09-17 09:20:00
updated_at: 2026-09-20 18:00:48
status: pending_recheck
---

# Chat 工作台多材料与 Skill 快速引用验收返修台账

## 返修批次 2026-09-20 Chat 轨迹 Tab 实际内容边缘对齐

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 实际内容边缘 | 标红区域显示 `trace-toolbar`、`trace-status`、`trace-card` 等实际内容边缘仍未与输入框外边缘对齐。 | 已移除 `trace-wrap` 左右 padding，使内部实际内容边缘直接落在与 Composer 相同的内容轨道上。 |
| 窄屏安全边距 | 窄屏仍需保留页面安全边距。 | `trace-wrap` 窄屏宽度保持 `calc(100% - 24px)`，仅清除内部水平 padding。 |

### 附件/参考稿逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| `codex-clipboard-b9c6a548-ed18-43c2-8b52-e8c28facaa1e.png` | Chat 轨迹 Tab，桌面深色主题，轨迹面板打开 | `trace-wrap` 内部实际内容边缘与 Composer 输入框外边缘 | 轨迹内容左边缘和右边缘应与输入框外边缘同轨。 | 外层宽度已接近输入框，但内容因 `trace-wrap` 左右 padding 内缩。 | 左右边缘对齐偏差。 | 截图标注、CSS selector 检查、前端测试 | 本次修复 | `src/web/src/styles/chat-workbench.css`、`src/web/src/chat-workbench.test.tsx` |

### 根因证据

- 上一批返修将 `.trace-wrap` 宽度改为与 Composer 一致，但仍保留 `padding: 4px 28px 40px`。
- 因 `box-sizing: border-box`，这 28px 左右 padding 会压缩内部内容区，导致 `trace-toolbar`、`trace-status`、`trace-card` 和 `section-block` 的实际边缘相对输入框外边缘内缩。

### 调整详情

- `chat-workbench.css` 将桌面 `.trace-wrap` padding 调整为 `4px 0 40px`。
- 窄屏 `.trace-wrap` 保持 `width: calc(100% - 24px)` 页面安全边距，同时将 padding 调整为 `4px 0 28px`。
- `chat-workbench.test.tsx` 扩展 CSS 断言，锁定桌面与窄屏 `trace-wrap` 的水平 padding 为 0，避免内容边缘再次内缩。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批属于轨迹 Tab 视觉对齐返修，不改变主 PRD 范围；无需更新。 |
| `business-flow.md` | 不改变会话创建、发送、执行、历史或关联流程；无需更新。 |
| `user-stories.md` | 不新增用户故事；无需更新。 |
| `acceptance.md` | 已补充轨迹实际内容边缘对齐验收口径。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 本批以当前截图验收反馈收敛轨迹 Tab，不改变原 REQ prototype 结构；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-workbench.test.tsx src/chat-execution.test.tsx src/chat-trajectory.test.tsx` | pass | 14 passed；覆盖 trace-wrap 清除左右 padding、桌面内容边缘与 Composer 对齐、窄屏保留 24px 页面安全边距和 v3 trace shell 回归。 |

## 返修批次 2026-09-20 Chat 轨迹 Tab 宽度与说明文案收敛

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 轨迹内容宽度 | 轨迹 Tab 内容区整体宽度与底部 Composer 输入框一致。 | 已将 `trace-wrap` 与 Composer 统一到 `1120px / calc(100% - 48px)` 内容轨道，窄屏统一为 `calc(100% - 24px)`。 |
| 说明文案 | 不展示“仅展示实际执行产生的事件与文件变更”。 | 已移除 Chat 轨迹面板 footer 文案；轨迹状态区仅保留轮次状态和事件数据本身。 |

### 附件/参考稿逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户文字反馈 | Chat 轨迹 Tab，桌面与窄屏 | `trace-wrap`、Composer | 轨迹内容区与输入框左/右边缘共享同一内容轨道。 | 返修前 `trace-wrap` 使用 1080px 轨道，Composer 使用 1120px 轨道。 | 内容宽度不一致。 | CSS selector 检查、前端测试 | 本次修复 | `src/web/src/styles/chat-workbench.css`、`src/web/src/chat-workbench.test.tsx` |
| 用户文字反馈 | Chat 轨迹 Tab footer | 轨迹面板底部说明文案 | 不展示解释性 footer 文案。 | 返修前 `ChatWorkbenchPage` 在轨迹 aside 底部渲染“仅展示实际执行产生的事件与文件变更”。 | 多余文案。 | DOM 测试、源码检查 | 本次修复 | `src/web/src/pages/catalog/ChatWorkbenchPage.tsx`、`src/web/src/chat-workbench.test.tsx` |

### 根因证据

- `chat-workbench.css` v3 轨迹复刻样式中 `.trace-wrap` 使用 `max-width: 1080px; width: 100%`，而 Composer 使用 `width: min(100% - 48px, 1120px); max-width: 1120px`，导致两者内容轨道不一致。
- `ChatWorkbenchPage.tsx` 在 `chat-execution-panel` 的 `ExecutionPanel` 后额外渲染 footer 文案，该文案不属于当前 v3 参考稿复刻后的必要业务信息。

### 调整详情

- `chat-workbench.css` 将 `.chat-main > .chat-execution-panel .trace-wrap` 与独立 `.chat-trajectory.trace-wrap` 调整为与 Composer 同一 `1120px / calc(100% - 48px)` 轨道，并在窄屏使用 `calc(100% - 24px)`。
- `ChatWorkbenchPage.tsx` 移除轨迹 aside 底部说明 footer。
- `chat-workbench.test.tsx` 增加轨迹 footer 文案不存在断言，并锁定 trace-wrap 与 Composer 的同宽 CSS 规则。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批属于轨迹 Tab 视觉对齐与说明文案返修，不改变主 PRD 范围；无需更新。 |
| `business-flow.md` | 不改变会话创建、发送、执行、历史或关联流程；无需更新。 |
| `user-stories.md` | 不新增用户故事；无需更新。 |
| `acceptance.md` | 已补充轨迹宽度与说明文案移除验收口径。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 本批以 v3 参考稿与验收反馈收敛当前轨迹 Tab，不改变原 REQ prototype 结构；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-workbench.test.tsx src/chat-execution.test.tsx src/chat-trajectory.test.tsx` | pass | 14 passed；覆盖轨迹面板 footer 文案移除、trace-wrap 与 Composer 共享 1120px 内容轨道、v3 trace shell 回归。 |

## 返修批次 2026-09-20 Chat 轨迹 Tab v3 复刻

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| v3 参考稿一对一复刻 | 按 `moonbox-chat-redesign-v3.html` 的 selector/DOM 分层复刻轨迹 Tab。 | 已将轨迹页收敛为 `trace-wrap`、`trace-toolbar`、`trace-status`、`trace-card`、`trace-controls`、`scrub`、`event-list`、`disclosure/raw-events-box`、`section-block` 分层。 |
| 真实数据与语义 | 使用现有真实 trace 数据，不写入附件 demo 文案，不改变 API/DB/payload。 | 事件仍来自 `traceNodes(events)`、`readChatEvents`、context 快照和 diff 接口；仅调整展示结构与样式。 |
| 保留轨迹能力 | 搜索、scrub、事件详情、原始事件、引用快照、文件变更、停止、重试等能力不回退。 | 搜索、compact/timed、事件选择详情、raw events disclosure、context snapshot、DiffView、停止和重试均保留。 |

### 附件/参考稿逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| `moonbox-chat-redesign-v3.html` | Chat 轨迹 Tab，1440px 与窄屏 | `.trace-wrap` | 顶层内容宽度约 1080px，居中，内部包含 toolbar/status/card/section-block。 | 返修前 toolbar/status/card 分散在 ExecutionPanel 与 TrajectoryView，`trace-wrap` 只包事件列表区域。 | DOM 分层和容器归属不一致。 | selector 映射、组件测试、computed style 计划 | 本次修复 | `src/web/src/components/chat/ExecutionPanel.tsx`、`src/web/src/components/chat/TrajectoryView.tsx` |
| `moonbox-chat-redesign-v3.html` | Trace toolbar/status | `.trace-toolbar`、`.trace-status` | 顶部运行状态、停止、执行轮次；下方状态摘要和事件读取说明。 | 返修前 toolbar 位于 `trace-wrap` 外，status 与 card 不是同一视觉系统。 | 间距、边框、层级、分组不一致。 | DOM 结构测试、样式 selector 检查 | 本次修复 | `src/web/src/chat-execution.test.tsx` |
| `moonbox-chat-redesign-v3.html` | Trace card | `.trace-card`、`.trace-controls`、`.scrub`、`.event-row` | 搜索/控制、scrub 和事件行被同一卡片承载，事件行三列展示。 | 返修前 card wrapper 缺失，scrub 与 event-list 更接近旧轨迹组件。 | 卡片边界、事件行密度、scrub 高度不一致。 | 前端测试、CSS selector 检查 | 本次修复 | `src/web/src/styles/chat-workbench.css` |
| `moonbox-chat-redesign-v3.html` | 原始事件、引用快照、文件变更 | `.disclosure`、`.raw-events-box`、`.section-block` | 原始事件为 disclosure；引用快照和文件变更为下方 section-block。 | 返修前 raw events 在 TrajectoryView 外，引用快照和 Diff 为普通 panel section。 | 默认层级与参考稿不一致。 | 组件测试、DOM 结构检查 | 本次修复 | `src/web/src/components/chat/TrajectoryView.tsx`、`src/web/src/components/chat/DiffView.tsx` |

### 根因证据

- `ExecutionPanel.tsx` 返修前将 `trace-toolbar` 放在执行事件 section 外，`trace-status` 放在 section 内，`TrajectoryView` 自己再渲染 `trace-wrap`，导致 v3 参考稿中的单一轨迹容器被拆散。
- `TrajectoryView.tsx` 返修前只包含控制条、scrub、事件列表和详情侧栏，缺少 `trace-card` 与 raw events disclosure 内聚结构。
- `DiffView.tsx` 和 context snapshot 返修前仍沿用普通 `chat-panel-section`，未进入 v3 的 `section-block` 层级。

### 调整详情

- `ExecutionPanel.tsx` 将 toolbar、状态摘要、TrajectoryView、引用快照和文件变更统一收进 `trace-wrap`。
- `TrajectoryView.tsx` 增加 `withinTraceWrap` 复用模式；在执行面板内输出 `trace-card`，独立渲染时仍保留 `trace-wrap`，避免破坏组件测试和复用。
- `TrajectoryView.tsx` 将原始事件移动到 `trace-card` 内，以 `disclosure/raw-events-box` 展示，并保留事件详情增强态。
- `DiffView.tsx` 改为 `section-block` / `section-title` / `file-diff-list` 风格，不改变比较范围和 diff payload。
- `chat-workbench.css` 增加 v3 trace selector 样式覆盖，收敛 toolbar、status、card、controls、search、scrub、event row、raw events、snapshot 和 file diff 的字号、间距、边框、圆角、背景和窄屏布局。
- `src/web/scripts/check-chat-event-display.cjs` 更新为轨迹 v3 视觉验收脚本，面向 `.trace-wrap`、`.trace-card`、`.event-row`、`.raw-events-box` 和 `.section-block` 采样。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批属于 Chat 轨迹 Tab UI 复刻返修，不改变主 PRD 范围；无需更新。 |
| `business-flow.md` | 不改变会话创建、发送、执行、历史或关联流程；无需更新。 |
| `user-stories.md` | 不新增用户故事；无需更新。 |
| `acceptance.md` | 已补充轨迹 Tab v3 一对一复刻验收口径和验证缺口说明。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 本批以外部 HTML 参考稿收敛现有轨迹 Tab，不改变原 REQ prototype 结构；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-execution.test.tsx src/chat-trajectory.test.tsx` | pass | 6 passed；覆盖 v3 trace shell、toolbar/status/card/scrub/raw events、引用快照、文件变更和既有事件详情。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-execution.test.tsx src/chat-trajectory.test.tsx src/chat-workbench.test.tsx src/chat-sessions.test.tsx src/chat-composer.test.tsx src/chat-messages.test.tsx src/chat-activity.test.tsx` | pass | 43 passed；覆盖 Chat 页面壳、会话、Composer、消息、运行状态、执行面板和轨迹回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

## 返修批次 2026-09-22 轨迹文件变更快照语义

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 文件变更事实源 | 轨迹里的“文件变更”不能让用户误以为本地文件已经实时修改。 | `DiffView` 将范围文案改为“本轮执行快照 / 会话累计快照”，并提示这是执行结束时保存的差异快照，当前状态来自本地工作区实时校验。 |
| 未跟踪文件 | 执行快照里新增但当前 Git 仍未跟踪的文件需明确展示。 | 后端 `read_diff()` 为 diff 文件附加 `workspace_status=untracked`，前端 badge 显示“新增（未跟踪）”。 |
| 快照与磁盘不一致 | 当执行快照内容与当前磁盘内容不一致时，需要明确提示。 | 后端比对 diff 的 `after_sha256` 与当前文件 sha；不一致时返回 `workspace_status=mismatch`，前端展示“快照内容与当前磁盘内容不一致，页面展示的是执行快照。” |

### 根因证据

- 用户截图显示 `issues/bugs/plan/BUG-0024-capture/capture.md` 在轨迹 Diff 中标记为“新增”，但本地文件内容与截图中的快照内容不一致，且 Git 状态为 untracked。
- 返修前 `DiffView` 只展示 `chat_diffs.payload` 中保存的 diff 快照，比较范围文案为“本轮变更”，没有说明该数据是历史执行快照，也没有当前 workspace 状态。
- 返修前 `read_diff()` 只返回 `files` / `cumulative_files`，没有把当前磁盘状态、未跟踪状态或快照不一致状态作为前端可展示事实返回。

### 调整详情

- `read_diff()` 在返回保存的 diff payload 后，会基于会话绑定的 `workspace_root` 与 `workspace_id` 读取当前工作区快照，并为每个 diff 文件附加 `workspace_status`。
- 当前 Git porcelain 为 `??` 的文件标记为 `untracked`；当前文件缺失标记为 `missing`；有 `after_sha256` 且与当前文件 sha 不一致时标记为 `mismatch`；无法确认时降级为 `unknown`。
- `DiffView` 将比较范围文案改为快照语义，新增快照说明、当前工作区状态行和 mismatch 警示；不再把保存快照直接呈现为实时本地状态。
- 前端测试覆盖“新增（未跟踪）”、当前工作区状态提示和快照不一致提示；后端测试覆盖未跟踪文件与快照内容不一致文件的 `workspace_status` 返回。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 不改变 Chat 工作台目标和业务流程；无需更新主 PRD。 |
| `business-flow.md` | 不改变会话执行、轨迹读取或 Diff 生成流程；仅澄清展示语义。 |
| `user-stories.md` | 不新增用户故事；无需更新。 |
| `acceptance.md` | 已补充轨迹文件变更快照与当前工作区状态的验收口径。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变 UI 原型结构；无需更新。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `uv run pytest src/backend/tests/test_chat.py::test_diff_marks_workspace_snapshot_status -q` | pass | 覆盖 `workspace_status=untracked`、`workspace_status=mismatch` 和不暴露当前文件 hash。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-rendering.test.tsx src/chat-execution.test.tsx` | pass | 覆盖 DiffView 快照文案、未跟踪 badge、快照不一致提示和轨迹文件变更回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |
| `node scripts/check-chat-event-display.cjs http://127.0.0.1:18112` | blocked | Playwright 脚本已更新为 v3 轨迹验收，但本地 Vite dev server 因当前环境 corepack/pnpm 缓存缺失和 `data/runtime` 工作区副本依赖解析 warning 未能稳定提供页面；未生成本轮截图，需在修复本地 dev server 后补跑。 |

## 返修批次 2026-09-20 Chat Composer 空白区域关闭面板

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 空白区域关闭 | Skill、模型、推理面板打开后，点击输入框空白、Composer 工具栏空白或页面空白均自动隐藏。 | 已将外部点击保护范围从整个 Composer 收窄为当前 popover 与三个触发按钮；Composer 内空白点击会关闭面板。 |
| 触发器与面板内点击 | 点击当前面板内部或对应触发按钮不按外部点击处理。 | 当前 popover、Skill 按钮、模型按钮和推理按钮保留点击保护；按钮仍可 toggle，面板选项仍可正常选择。 |
| 既有语义 | Skill slash 搜索、键盘选择、模型/推理单选语义不回退。 | 原有 slash、Arrow、Enter、Escape 和 menuitemradio 行为保留；发送 payload 不变。 |

### 根因证据

- 返修前 `Composer.tsx` 的 document `mousedown` 判断使用 `composerRoot.current?.contains(event.target)`，导致整个 Composer 内部都被视为“内部点击”。
- 因此点击输入框空白、Composer 底部工具栏空白等用户感知上的空白区域时，关闭逻辑直接返回，面板保持显示。
- 既有测试只覆盖 `document.body` 外部点击关闭，未覆盖 Composer 内空白点击关闭。

### 调整详情

- `Composer.tsx` 将外部点击保护范围收窄为 `.chat-composer-popover`、Skill 触发按钮、模型触发按钮和推理触发按钮。
- 点击输入区空白、Composer 根节点空白或页面空白均调用 `closeAllPopovers()`。
- `chat-composer.test.tsx` 补充 Skill、模型、推理三类面板在 Composer 内空白点击时自动关闭的断言。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批属于 Composer 下拉面板关闭逻辑返修，不改变主 PRD 范围；无需更新。 |
| `business-flow.md` | 不改变会话创建、发送、执行或历史流程；无需更新。 |
| `user-stories.md` | 不新增用户故事；无需更新。 |
| `acceptance.md` | 已补充三类面板点击输入区/Composer/页面空白自动关闭的验收口径。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变原型结构；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-composer.test.tsx` | pass | 13 passed；覆盖 Skill、模型、推理面板点击 Composer 内空白和输入区空白自动关闭。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-execution-labels.test.ts src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-relations.test.tsx src/chat-workbench.test.tsx` | pass | 32 passed；覆盖 Chat 消息、Composer、运行状态、管理关联和页面壳回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

## 返修批次 2026-09-20 Chat Composer 下拉面板统一

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 面板样式一致 | 输入框中 Skill 下拉、模型下拉和推理下拉使用统一 UI 样式，包括面板、字号密度、hover、active 和 disabled 状态。 | 已抽取统一 `chat-composer-popover` 与 `chat-composer-option` 基础样式；Skill、模型、推理仅保留必要宽度和语义差异。 |
| 关闭逻辑一致 | 三类下拉均支持失焦或外部点击不显示，并保持 Escape、选中关闭和切换互斥。 | 已统一外部点击关闭、全局 Escape 关闭、切换触发器互斥；Skill 保留 slash 删除关闭和键盘上下/Enter 选择。 |
| 语义不回退 | Skill 保留搜索与键盘选择；模型/推理保留单选语义和 raw value payload。 | Skill 仍为 `listbox/option`，模型/推理仍为 `menu/menuitemradio`；发送 payload 与 `chat.config_select` 事件不变。 |

### 根因证据

- `Composer.tsx` 返修前 Skill 使用独立 `chat-skill-menu` 渲染在输入区下方，模型/推理使用 `chat-config-menu` 渲染在配置按钮区域，结构和定位不同。
- `chat-workbench.css` 中 Skill 菜单和 config 菜单分别维护 hover、字号、边框和 active 样式，容易产生视觉漂移。
- 关闭逻辑返修前只对 `configMenu` 绑定 document `mousedown` 外部关闭，Skill 菜单主要依赖 slash 删除、Escape 或选择关闭。

### 调整详情

- `Composer.tsx` 新增 Composer 根节点外部点击和 Escape 统一关闭逻辑；打开 Skill 时关闭模型/推理，打开模型/推理时关闭 Skill。
- Skill、模型、推理面板统一挂载 `chat-composer-popover`，候选项统一挂载 `chat-composer-option`；Skill 保留 `role=listbox` 与键盘导航，模型/推理保留 `menuitemradio`。
- `chat-workbench.css` 合并三类面板基础样式，统一字号、密度、圆角、阴影、hover、active 和 disabled 状态；Skill 与 config 只保留宽度差异。
- `chat-composer.test.tsx` 增加统一 popover 行为测试，覆盖外部点击关闭、Escape 关闭、切换面板互斥、选中后关闭和样式类一致性。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批属于 Chat 输入区下拉面板体验返修，不改变主 PRD 范围；无需更新。 |
| `business-flow.md` | 不改变会话创建、发送、执行或历史流程；无需更新。 |
| `user-stories.md` | 不新增用户故事；无需更新。 |
| `acceptance.md` | 已补充 Composer 下拉面板统一样式和关闭逻辑验收口径。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变原型结构；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-composer.test.tsx` | pass | 13 passed；覆盖 Skill、模型、推理统一 popover 样式类、外部点击关闭、Escape 关闭、互斥切换、选中关闭和发送 payload。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-execution-labels.test.ts src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-relations.test.tsx src/chat-workbench.test.tsx` | pass | 32 passed；覆盖 Chat 消息、Composer、运行状态、管理关联和页面壳回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |
| `node scripts/check-chat-materials.cjs http://127.0.0.1:18112 ../../openspec/changes/add-chat-workbench-image-skill-context/evidence/ui` | pass | 2 screenshots + computed style；synthetic Chat API mocks，真实前端组件和样式；覆盖统一 popover 后 Chat 页面视觉回归。 |

## 返修批次 2026-09-20 Chat 模型列表顺序收敛

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 模型列表顺序 | Composer 模型下拉按 `GPT-6 Astra`、`GPT-5.6 Sol`、`GPT-5.6 Terra`、`GPT-5.6 Luna`、`GPT-5.5` 展示。 | 已调整后端 execution capabilities 默认模型数组顺序；前端继续按接口顺序渲染，不在展示层二次排序。 |
| 底层 value | 模型展示顺序调整不改变发送 payload、API、DB 和执行配置快照中的 raw value。 | 默认模型仍为 `gpt-6-astra`；发送时仍提交 `gpt-6-astra` / `gpt-5.6-sol` 等稳定 value。 |

### 根因证据

- `src/backend/app/chat/settings.py` 中默认 `models` 数组返修前把 `gpt-5.6-sol` 放在 `gpt-6-astra` 前方。
- `Composer` 模型菜单按 capabilities 返回顺序渲染，因此后端默认顺序会直接成为用户可见顺序。

### 调整详情

- `src/backend/app/chat/settings.py` 将默认模型顺序调整为：`gpt-6-astra`、`gpt-5.6-sol`、`gpt-5.6-terra`、`gpt-5.6-luna`、`gpt-5.5`。
- `src/backend/tests/test_chat.py` 锁定 `/api/v1/chat/capabilities` 返回的模型 value 与 display_name 顺序。
- `src/web/src/chat-composer.test.tsx` 锁定 Composer 模型菜单前 5 项展示顺序。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批属于 Chat 执行配置 UI 顺序返修，不改变主 PRD 范围；无需更新。 |
| `business-flow.md` | 不改变会话创建、发送、执行或历史流程；无需更新。 |
| `user-stories.md` | 不新增用户故事；无需更新。 |
| `acceptance.md` | 已补充模型列表展示顺序验收口径。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变原型结构；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `uv run --project src/backend pytest src/backend/tests/test_chat.py -q` | pass | 36 passed, 1 skipped；覆盖 Chat capabilities 中模型 value/display_name 顺序。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-composer.test.tsx` | pass | 12 passed；覆盖 Composer 模型菜单展示顺序和发送 payload raw value。 |

## 返修批次 2026-09-20 AI meta 与管理关联弹窗收敛

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| AI tool-summary 思考耗时 | `已完成` 若存在已采集的思考/推理耗时字段，则显示 `已完成（思考 x）`；字段不存在不展示，不从总耗时或 Token 推断。 | 已在 `execution.usage` 事件存在 `reasoning_duration_ms` 或 `thinking_duration_ms` 时展示思考耗时，按毫秒/秒/分钟秒格式化；无字段保持原状态文案。 |
| AI meta 顺序 | AI 消息复制图标放在 meta 第一位。 | 已将 `CopyMessageButton` 移到 AI meta 首位；Skill 图标、时间、首 token、思考耗时、总耗时和 Token 统计依次跟随。 |
| 管理关联加载跳变 | 打开弹窗不应从整块“正在读取授权对象…”明显跳变为完整列表。 | 会话栏预取候选对象；弹窗复用预取结果，搜索刷新时保留既有列表并用轻量“正在更新候选…”提示，避免列表区域闪空。 |
| 搜索与下拉整合 | 搜索对象与主对象下拉可以整合为一个更自然的控件。 | 已将搜索框、主对象选择和引用选择整合为一个可搜索候选列表；每行同时支持设为主对象和引用对象，保存 payload 仍为 `primary` 与 `references[]`。 |
| REQ/BUG 类型区分 | 下拉/候选面板中的 REQ 和 BUG 需要颜色区分。 | 候选行增加 `REQ` / `BUG` 文本 badge，并使用不同低饱和颜色；不只依赖颜色表达类型。 |

### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户附件 Image #1 | Chat 对话区，AI 消息 meta 与 tool-summary | AI tool-summary 与 AI meta | `已完成` 在有思考耗时时补充思考耗时；复制图标位于 AI meta 第一位 | tool-summary 不展示思考耗时；AI meta 复制图标位于时间之后 | 信息顺序、耗时展示缺失 | 代码路径检查、前端组件测试 | 本次修复 | `src/web/src/components/chat/TurnActivity.tsx`、`src/web/src/components/chat/ConversationMessages.tsx`、`src/web/src/chat-activity.test.tsx`、`src/web/src/chat-messages.test.tsx` |
| 用户附件 Image #1 / Image #2 | Chat 管理关联弹窗，打开与加载后状态 | 管理关联 modal | 弹窗打开后候选区稳定，搜索、主对象和引用对象选择整合，REQ/BUG 有明确类型区分 | 弹窗先显示整块 loading 文案，随后跳变为列表；搜索框与主对象 select 分离；候选类型仅从 ID 文本判断 | 加载态跳变、控件分散、类型视觉区分不足 | 代码路径检查、前端组件测试、ARIA/DOM 结构检查 | 本次修复 | `src/web/src/components/chat/RelationsBar.tsx`、`src/web/src/styles/chat-workbench.css`、`src/web/src/chat-relations.test.tsx` |

### 根因证据

- `ConversationMessages.tsx` 的 AI meta 返修前按时间、复制、Skill、统计字段顺序渲染，复制图标不是首位。
- `TurnActivity.tsx` 只按 turn status 映射 `已完成` 等状态文案，未读取 `execution.usage` 中明确的思考/推理耗时字段。
- `RelationsBar.tsx` 返修前在弹窗内部独立请求候选对象，初始 `loading=true` 时用整块 loading 文案替代候选区；搜索框、主对象原生 `select` 和引用 `checkbox` 列表分散为三段控件。

### 调整详情

- `ConversationMessages.tsx` 扩展 `UsagePayload`，支持 `reasoning_duration_ms` / `thinking_duration_ms` 展示；AI meta 将复制图标作为第一个可交互项。
- `TurnActivity.tsx` 读取同一轮 `execution.usage` 事件，只有已完成且存在思考耗时字段时展示 `已完成（思考 x）`，不从 `duration_ms` 或 `reasoning_tokens` 推断。
- `RelationsBar.tsx` 在会话层预取 `/conversations/{id}/objects`；弹窗接收 `initialCandidates`，搜索刷新时保持已知候选列表稳定。
- 管理关联弹窗改为一个 searchable combobox/listbox：每行包含类型 badge、ID、标题、主对象 radio 和引用 checkbox；REQ/BUG 类型由后端返回 kind 或前端按 ID 前缀安全推断。
- `chat-workbench.css` 补齐关系候选列表、类型 badge、轻量刷新态和已选摘要样式；保存接口 payload、权限校验和后端关系语义不变。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批仍属于 Chat 消息 meta 与关联弹窗体验验收返修，不改变主 PRD 范围；无需更新。 |
| `business-flow.md` | 不改变会话创建、关联保存、发送或执行流程；无需更新。 |
| `user-stories.md` | 不新增用户故事；无需更新。 |
| `acceptance.md` | 已补充 AI meta 首位复制、思考耗时展示和管理关联弹窗稳定候选/REQ-BUG badge 验收口径。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变原型结构；本批为参考稿与截图反馈下的局部收敛，无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-activity.test.tsx src/chat-relations.test.tsx` | pass | 11 passed；覆盖 AI meta 复制图标首位、思考耗时展示、管理关联合并列表、列表稳定刷新和 REQ/BUG badge。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-execution-labels.test.ts src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-relations.test.tsx src/chat-workbench.test.tsx` | pass | 31 passed；覆盖 Chat 消息、Composer、运行状态、管理关联和页面壳回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |
| `node scripts/check-chat-materials.cjs http://127.0.0.1:18112 ../../openspec/changes/add-chat-workbench-image-skill-context/evidence/ui` | pass | 2 screenshots + computed style；synthetic Chat API mocks，真实前端组件和样式；本轮复验重新生成 Chat 页面视觉证据。 |

## 返修批次 2026-09-20 Chat 执行配置展示名统一

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 名词大小写和格式 | Chat 中涉及 Agent、模型和推理强度的展示名统一为 `Codex`、`GPT-6 Astra`、`GPT-5.6 Luna`、`GPT-5.6 Terra`、`GPT-5.6 Sol`、`GPT-5.5`、`XHigh`、`High`、`Medium`、`Low`。 | 已抽取共享执行配置展示名 formatter，并接入消息 meta、AI tool-summary 和 Composer 配置控件兜底展示。 |
| 底层 value | payload、API、DB 和执行配置快照仍使用原始 value，例如 `codex`、`gpt-6-astra`、`high`。 | 仅改变展示层 label；发送 payload 和后端能力配置不变。 |

### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户文字反馈 | Chat 对话区和输入区，消息 meta、AI tool-summary、Composer 配置控件 | 执行配置展示名 | 展示 `Codex · GPT-6 Astra · High` 等规范名称 | 部分位置展示 `codex · gpt-6-astra · high` raw value | 大小写、连字符、模型品牌格式不统一 | 代码路径检查、前端组件测试、展示名 formatter 单测 | 本次修复 | `src/web/src/components/chat/executionLabels.ts`、`src/web/src/components/chat/ConversationMessages.tsx`、`src/web/src/components/chat/TurnActivity.tsx`、`src/web/src/components/chat/Composer.tsx`、`src/web/src/chat-execution-labels.test.ts` |

### 根因证据

- 后端 `chat/settings.py` 能力配置中的 `display_name` 已包含规范展示名，但消息历史和运行状态读取到的是 `effective_config` raw value。
- `ConversationMessages.configLabel()` 和 `TurnActivity` 直接拼接 `config.agent`、`config.model`、`config.reasoning`，绕过了能力配置展示名。
- Composer 下拉候选使用 `display_name`，但配置控件兜底展示在能力配置缺失或 display_name 缺失时仍可能回到 raw value。

### 调整详情

- 新增 `executionLabels.ts`，集中维护 Agent、模型和推理强度展示名映射，并保留从 `ExecutionOption.display_name` 优先取值的能力。
- `ConversationMessages` 用户消息 meta 改用 `executionConfigLabel()`，历史 raw value 也会展示为规范名称。
- `TurnActivity` tool-summary 执行配置摘要改用同一 formatter。
- `Composer` 配置控件在能力配置缺失或候选 display_name 缺失时使用同一展示名兜底；发送 payload 继续提交原始 `execution_config` value。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批为展示名一致性验收返修，不改变主 PRD 目标；无需更新。 |
| `business-flow.md` | 不改变会话创建、发送、执行或历史读取流程；无需更新。 |
| `user-stories.md` | 不新增用户故事；无需更新。 |
| `acceptance.md` | 已更新 AC-025 和前端验证证据，明确展示名与 raw value 边界。 |
| `trace.md` | 本批摘要与验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变布局结构，仅修正文案格式；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-execution-labels.test.ts src/chat-messages.test.tsx src/chat-activity.test.tsx src/chat-composer.test.tsx` | pass | 20 passed；覆盖全部规范展示名、消息 meta、AI tool-summary、Composer 兜底展示和发送 payload raw value。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-execution-labels.test.ts src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 27 passed；覆盖执行配置展示名、消息、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |
| `node scripts/check-chat-materials.cjs http://127.0.0.1:18112 ../../openspec/changes/add-chat-workbench-image-skill-context/evidence/ui` | pass | 2 screenshots + computed style；synthetic Chat API mocks，真实前端组件和样式；Vite 停止阶段 requirement-center proxy `ECONNREFUSED` 为非 Chat mock 噪声。 |

## 返修批次 2026-09-20 用户消息 Skill 与正文 inline flow 修正

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 用户消息 Skill 与正文同行 | 用户消息首段正文必须与 Skill chip 在同一 inline 内容流内显示，文本从 Skill chip 后继续排版并自然换行。 | 已将用户消息首段拆为 `chat-user-inline-flow`，Skill chip 与首段正文同处一个 inline flow；长文本按文本流自然换行。 |
| 复杂 Markdown 层级 | 第二段及复杂 Markdown 不应被强行塞进同一纯文本行，仍需保持块级阅读层级。 | 首段之后的内容继续交给 `SafeMarkdown` 渲染，保留段落、列表、代码块等块级结构。 |

### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户附件 Image #1 | Chat 对话区，用户消息含图片、Skill chip 和长文本 | 用户消息气泡内 Skill chip 与首段正文 | Skill chip 与文本在同一行起排，文本从 chip 后继续并自然换行 | Skill chip 单独位于第一行，正文从下一行开始 | DOM 虽同属 bubble，但正文 `SafeMarkdown` 外层为独立块/弹性项，不是真正 inline 内容流 | DOM 结构检查、前端组件测试、视觉对照 | 本次修复 | `src/web/src/components/chat/ConversationMessages.tsx`、`src/web/src/styles/chat-workbench.css`、`src/web/src/chat-messages.test.tsx` |

### 根因证据

- 当前用户消息气泡中 Skill chip 与正文同属 `.chat-message-bubble`，但正文由 `SafeMarkdown` 渲染为 `.chat-markdown` 块级容器。
- `.chat-message-user .chat-message-bubble` 采用 flex 布局时，`.chat-message-skills` 与 `.chat-markdown` 成为两个 flex item；在当前宽度和长文本场景下，正文自然换到下一行，未满足“文本从 Skill chip 后继续”的 inline flow 预期。
- 验收标准 AC-022 已要求 Skill pill 与正文同一行；本次反馈进一步澄清“同一行”不是同一 bubble，而是首段正文与 Skill chip 的同一 inline 内容流。

### 调整详情

- `ConversationMessages` 新增用户消息专用 `UserMessageBody`，先过滤派生材料说明，再将首个 Markdown block 拆入 `chat-user-inline-flow`。
- Skill chip 与首段正文位于同一个 inline flow：Skill chip 保持 inline-flex，首段正文使用 inline 文本节点并保留自然换行。
- 首段之后的剩余内容继续由 `SafeMarkdown` 渲染，避免列表、代码块、表格等复杂 Markdown 退化为纯文本。
- 用户消息复制仍使用过滤后的完整可见正文，不受首段拆分影响。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批为既有 Chat 消息阅读层级的视觉验收细化，不改变主 PRD 目标；无需更新。 |
| `business-flow.md` | 不改变会话创建、上传、发送、执行或历史读取流程；无需更新。 |
| `user-stories.md` | 不新增用户故事；无需更新。 |
| `acceptance.md` | 已更新 AC-022 和前端消息布局验证证据，明确首段 inline flow 与后续 Markdown 块级渲染。 |
| `trace.md` | 本批摘要与验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变原型结构，仅修正实现对参考图的同行排版复刻；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx` | pass | 4 passed；覆盖 Skill chip 与首段正文同一 inline flow、第二段 Markdown 块级渲染、复制正文、图片 object URL、assistant 布局和 meta 回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 26 passed；覆盖消息、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |
| `node scripts/check-chat-materials.cjs http://127.0.0.1:18112 ../../openspec/changes/add-chat-workbench-image-skill-context/evidence/ui` | pass | 2 screenshots + computed style；synthetic Chat API mocks，真实前端组件和样式；Vite 停止阶段 requirement-center proxy `ECONNREFUSED` 为非 Chat mock 噪声。 |

## 返修批次 2026-09-20 图片鉴权显示与 Skill 菜单触发态修正

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 用户消息图片真实显示 | 用户消息图片缩略图和预览弹窗都必须展示真实图片；受控材料接口需要鉴权时不能让 `<img>` 直接请求 Bearer 接口。 | 前端新增材料内容读取动作，使用当前登录态 `Authorization` fetch 真实 bytes，再生成 object URL 给缩略图和预览弹窗使用；组件卸载或切换时释放 object URL。 |
| Skill 面板关闭 | 输入框通过 `/` 或 `/keyword` 打开 Skill 面板后，删除触发字符或查询内容时面板应自动关闭；按钮打开的 Skill 面板不受普通输入影响。 | Composer 增加 `slash` / `button` 触发态；slash 触发时无匹配查询会自动关闭，按钮触发时保持显式打开语义。 |
| Skill 候选密度 | Skill 面板字号偏大，应贴近 Chat 13px 输入体系。 | 候选主标题收敛为 13px，摘要收敛为 11.5px，行高、gap 和 padding 同步减密。 |

### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户附件 Image #1 | Chat 对话区，用户消息图片缩略图 | 用户消息材料缩略图 | 缩略图展示真实图片内容，hover 不应只暴露材料摘要 | 缩略图仍是 `PNG` 占位卡，且 hover 显示 `图片.png · bytes` | 缩略图未渲染真实 `<img>` 内容 | 前端组件测试断言 blob URL、代码路径检查 | 本次修复；缩略图使用授权 fetch 后生成的 object URL | `src/web/src/components/chat/ConversationMessages.tsx`、`src/web/src/chat-messages.test.tsx` |
| 用户附件 Image #2 | Chat 对话区，图片预览弹窗 | 材料预览弹窗 | 点击缩略图后弹窗展示真实图片 | 弹窗只展示文件名或占位信息 | 原实现把受控内容地址直接交给 `<img>`，浏览器不会附带 Bearer 令牌 | 前端组件测试断言材料 content 请求带 Authorization，预览 `<img>` 使用 blob URL | 本次修复；弹窗同样使用 object URL | `src/web/src/components/chat/chatApi.ts`、`src/web/src/components/chat/ConversationMessages.tsx` |
| 用户附件 Image #3 | Composer 输入 `/bug` 打开 Skill 菜单 | Skill 候选列表与触发态 | 删除 `/` 或 `/keyword` 后菜单关闭；按钮打开时保持；候选字号更紧凑 | 删除触发字符后面板仍保留；候选字体偏大 | Composer 未区分 slash 与按钮打开来源；候选列表沿用较大字号 | 前端组件测试覆盖 slash 自动关闭、按钮保持、键盘选择；CSS 检查 | 本次修复 | `src/web/src/components/chat/Composer.tsx`、`src/web/src/styles/chat-workbench.css`、`src/web/src/chat-composer.test.tsx` |

### 根因证据

- 图片缩略图根因：用户消息材料缩略图只渲染文件类型占位，没有对 image 材料创建真实图片预览源。
- 图片弹窗根因：受控材料内容接口需要 `Authorization`，而 `<img src="/api/v1/chat/materials/.../content">` 无法自动携带 Bearer 令牌，导致前端拿到地址也无法真实显示图片。
- Skill 面板关闭根因：`onPromptChange` 在不再匹配 `/keyword` 时仅清空查询，没有关闭 slash 触发的 `skillMenu`。
- Skill 面板密度根因：候选列表未按 Chat 13px 输入体系单独收敛字号、行高和间距。

### 调整详情

- `chatApi.ts` 新增 `fetchChatMaterialBlob()`，通过当前前端会话令牌带 `Authorization` 读取受控材料内容，失败时使用既有 Chat API 错误口径。
- `ConversationMessages` 新增 `useMaterialObjectUrl()`，对图片材料按需 fetch blob、创建 object URL，并在组件卸载、材料切换或预览关闭时释放 URL。
- 用户消息图片缩略图和预览弹窗均使用 object URL；非图片材料继续展示文件摘要，不伪造预览地址。
- `Composer` 增加 `skillMenuTrigger`，区分按钮打开和 slash 输入打开；删除 slash 触发内容时自动关闭面板，保留按钮打开、上下键选择、Enter 选中、Escape 关闭和普通 Enter 发送语义。
- `chat-workbench.css` 收敛 Skill 候选列表字体和密度：主标题 13px，摘要 11.5px，行高 1.45，行高与间距贴近 13px 输入体系。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批仍属于 Chat 多材料输入、Skill 快速引用和 Codex 基线体验的验收修正，不改变主 PRD 目标；无需更新。 |
| `business-flow.md` | 不改变会话创建、上传、发送或历史读取主流程；无需更新。 |
| `user-stories.md` | 不新增用户故事；无需更新。 |
| `acceptance.md` | 已补充 AC-011B、AC-029、AC-033 和实现验收证据。 |
| `trace.md` | 本批摘要、观测声明和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变原型结构，仅修复现有展示与交互细节；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx` | pass | 16 passed；覆盖图片缩略图和预览通过 Authorization fetch 转 object URL、object URL 释放、slash 触发菜单删除关闭、按钮触发菜单保持和既有键盘选择。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 26 passed；覆盖消息、Composer、运行状态和 Chat 页面壳回归。 |
| `uv run --project src/backend pytest src/backend/tests/test_chat.py -q` | pass | 36 passed, 1 skipped；确认材料上传、受控内容读取和既有 Chat 后端回归未受影响。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |
| `node scripts/check-chat-materials.cjs http://127.0.0.1:18112 ../../openspec/changes/add-chat-workbench-image-skill-context/evidence/ui` | pass | 2 screenshots + computed style；synthetic Chat API mocks，真实前端组件和样式；Vite 停止阶段 requirement-center proxy `ECONNREFUSED` 为非 Chat mock 噪声。 |

## 返修批次 2026-09-20 用户消息与 Skill 交互细节修正

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 图片点击预览 | 用户消息图片缩略图点击后应展示真实图片；历史材料缺少 `preview_url` 时复用现有材料内容或下载事实源生成可预览地址，不伪造地址。 | 后端新增受控材料内容读取接口；历史图片材料存在授权 `ref_id` 时补 `preview_url`，前端图片预览优先使用 metadata URL，缺失时回退到受控内容地址。 |
| Skill 图标统一 | Composer skill 按钮、输入框 inline chip、候选列表、用户消息 Skill chip 和 AI meta Skill 图标使用同一图标。 | 前端统一使用 `Sparkles` 作为 Skill 图标；assistant avatar 继续保留执行体图标，不作为 Skill 图标。 |
| 用户消息 Skill chip | 用户消息 Skill chip 只显示图标 + Skill 英文名，不展示尾部 `skill` 文案。 | 已移除 `.chat-message-skill small` 展示和样式，仅保留统一 Skill 图标与英文名。 |
| `/` Skill 菜单键盘操作 | Skill 菜单默认选中第一项，支持上下键选择、Enter 填入输入框、Escape 关闭。 | Composer 在 Skill 菜单打开时拦截 ArrowUp / ArrowDown / Enter / Escape；Enter 选中候选，菜单关闭后普通 Enter 发送语义保持不变。 |
| 复制反馈 | 用户和 AI 消息复制成功或失败后，图标应临时变化，让用户能感知结果。 | `CopyMessageButton` 成功切换为 `Check`，失败切换为 `CircleAlert`，1.5 秒后恢复 `Copy`，并保留 aria-label / title。 |

### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户附件 Image #1 | Chat 对话区，用户点击图片预览弹窗 | 用户消息材料缩略图与预览弹窗 | 点击图片后弹窗展示真实图片内容 | 弹窗只展示 `PNG` 占位和“当前历史摘要未包含可预览地址”说明 | 历史材料缺少可预览 URL 时未使用已持久化 `ref_id` 回读对象内容 | 后端接口测试、前端组件测试、代码路径检查 | 本次修复；缺少授权 `ref_id` 的旧摘要仍只展示材料摘要，不伪造地址 | `src/backend/app/chat/api.py`、`src/backend/app/chat/service.py`、`src/web/src/components/chat/ConversationMessages.tsx`、`src/backend/tests/test_chat.py`、`src/web/src/chat-messages.test.tsx` |
| 用户附件 Image #1 | Chat 对话区，用户消息气泡 | 用户消息 Skill chip | Skill chip 显示统一图标 + `Explore`，不显示尾部 `skill` 文案 | 当前显示为 `Explore skill`，且图标与其他区域不统一 | 文案冗余、图标不一致 | DOM 断言与样式检查 | 本次修复 | `src/web/src/components/chat/ConversationMessages.tsx`、`src/web/src/styles/chat-workbench.css`、`src/web/src/chat-messages.test.tsx` |
| 用户附件 Image #1 | Chat 对话区，复制按钮点击后 | 用户消息与 AI 消息复制图标 | 点击成功/失败后图标临时切换，用户可感知状态 | 点击后 aria 状态有变化但图标缺少结果反馈 | 状态反馈不够直观 | 前端组件测试模拟 clipboard 成功与失败 | 本次修复 | `src/web/src/components/chat/ConversationMessages.tsx`、`src/web/src/chat-messages.test.tsx` |
| 用户附件 Image #2 | Composer 输入 `/ex` 打开 Skill 菜单 | Skill 候选列表 | 默认选中第一条候选，支持上下键切换和 Enter 选中 | 鼠标可选，键盘选择缺失 | 键盘可达性不足 | Testing Library role=option / selected 断言 | 本次修复 | `src/web/src/components/chat/Composer.tsx`、`src/web/src/chat-composer.test.tsx` |

### 根因证据

- 图片预览根因：`materialPreviewUrl()` 只消费历史 metadata 中已经存在的 `url` / `preview_url` / `download_url` / `content_url`，但历史材料摘要常只有 `ref_id` 和脱敏 metadata，导致弹窗无法回读对象存储中的真实图片。
- 服务端根因：上传材料已有 `uploaded_materials.object_key` 与所有者、状态事实源，但缺少一个当前登录态授权读取内容的受控接口，前端不能安全构造真实对象地址。
- Skill 展示根因：用户消息 Skill chip 保留了辅助 `small` 文案，AI meta 曾使用 `Box` 作为 Skill 图标，Composer 与候选列表使用 `Sparkles`，造成同一能力图标漂移。
- Skill 菜单根因：Composer 只实现鼠标点击选择和普通 Enter 发送，未在菜单打开态建立 active option 状态与键盘事件分支。
- 复制反馈根因：复制状态通过 `aria-label` / `title` 和 class 表达，图标本身未随 `copied` / `failed` 状态变化，用户视觉上难以确认操作结果。

### 调整详情

- 后端新增 `GET /api/v1/chat/materials/{material_id}/content`，使用当前登录态读取 `uploaded_materials`，校验材料所有者、ready 状态与删除状态后经对象存储适配层返回真实 bytes；失败时沿用 2510 受控错误，不返回内部对象 key。
- `read_turn_materials()` 对历史图片材料在存在授权 `ref_id` 且缺少可预览 URL 时补 `/api/v1/chat/materials/{ref_id}/content`；`revalidate_uploaded_materials()` 对新上传图片材料同步写入受控 `preview_url` metadata。
- 前端 `materialPreviewUrl()` 在 metadata URL 缺失但存在 image `ref_id` 时回退到受控内容读取地址；预览弹窗因此可展示真实图片。
- `ConversationMessages` 将用户消息 Skill chip 与 AI meta Skill 图标统一为 `Sparkles`，用户消息 Skill chip 只显示图标与英文名，移除尾部 `skill` 文案。
- `Composer` 为 Skill 菜单增加 active index、`role=listbox/option`、`aria-selected`、上下键循环选择、Enter 选择和 Escape 关闭，菜单关闭后保留原 Enter 发送与 Shift+Enter 换行。
- `CopyMessageButton` 根据状态渲染 `Copy` / `Check` / `CircleAlert`，成功、失败状态数秒后恢复，并继续保留可访问文案。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批为既有 Chat 多材料、Skill 快速引用和 Codex 基线体验的验收细化，不改变主 PRD 目标；无需更新。 |
| `business-flow.md` | 不改变会话创建、上传、发送或历史读取主流程；无需更新。 |
| `user-stories.md` | 不新增用户故事；无需更新。 |
| `acceptance.md` | 已补充 AC-011B、AC-029、AC-031、AC-032，并刷新实现验收证据口径。 |
| `trace.md` | 本批摘要、观测声明和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变原型结构，仅修复已有交互和展示细节；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `uv run --project src/backend pytest src/backend/tests/test_chat.py -q` | pass | 36 passed, 1 skipped；覆盖上传材料内容读取、对象存储回读、材料重验和既有 Chat 回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx` | pass | 15 passed；覆盖图片 preview URL fallback、Skill 图标统一、用户消息 Skill chip 去尾部 `skill` 文案、AI meta Skill 图标、复制成功/失败图标和 Skill 菜单键盘选择。 |
| `./scripts/generate-openapi-client.sh` | partial | 已导出 `src/web/openapi.json`；包装脚本在本机 Corepack pnpm 缓存缺失处退出，未影响 OpenAPI JSON 导出。 |
| `./src/web/node_modules/.bin/orval --config src/web/orval.config.ts` | pass | 使用本地 Orval 从更新后的 OpenAPI 生成 Chat 客户端。 |
| `node scripts/check-chat-materials.cjs http://127.0.0.1:18112 ../../openspec/changes/add-chat-workbench-image-skill-context/evidence/ui` | pass | 2 screenshots + computed style；synthetic Chat API mocks，真实前端组件和样式；Vite 停止阶段的 requirement-center proxy `ECONNREFUSED` 为非 Chat mock 噪声，不影响本次证据。 |

## 返修批次 2026-09-17 输入框优化

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 会话创建前分支选择 | 仓库位置应表达分支选择；默认 `main`，无 `main` 时使用 `master`；分支列表从 Git 仓库读取。 | 已调整为会话创建前选择分支，创建后锁定；能力接口返回仓库分支列表与默认分支。 |
| Agent / 模型 / 推理位置 | 执行配置放在发送按钮左侧。 | 已移动到输入区右侧动作组，顺序为 Skill、Agent、模型、推理、发送。 |
| Skill 命令选择 | 输入 `/` 或点击右下角 Skill 按钮均展示 `.agents/skills` 命令；选中后以标签显示。 | 已复用同一 Skill 选择器，选中后生成 Skill token，不自动执行命令。 |
| 文件上传入口 | 左下角改为上传文件图标，支持图片与文件、多选、粘贴。 | 已改为 paperclip 图标；上传接口支持图片、PDF、文本、Markdown、CSV、JSON，多文件和剪贴板文件。 |
| 上传后展示 | 上传后的图片或文件显示在输入框上方。 | 已在材料条展示图片与文件 token，包含名称、大小、状态和移除入口。 |
| 发送动作 | 发送按钮只显示图标，并支持回车发送。 | 已改为图标按钮；保留 Enter 发送、Shift+Enter 换行。 |

### 附件截图逐项视觉对照表

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户附件 Image #1。 |
| 页面/状态 | Codex 对话完成态截图，作为 Chat 输入与命令标签交互的风格参考。 |
| 对照对象 | 当前 Change 的 Chat Composer、Skill token、材料条、执行配置和发送动作。 |
| 期望表现 | 命令可作为标签进入上下文；文件/图片材料显示在输入框上方；发送动作用图标；操作区紧凑。 |
| 实际表现 | 上一版实现主要为图片引用登记，未覆盖会话创建前分支、通用文件上传、粘贴上传和 `/` 命令入口。 |
| 偏差项 | 分支字段缺失；上传范围偏窄；对象存储只登记引用；Skill 选择只能按钮触发；发送按钮含文字；执行配置位置不符合验收反馈。 |
| 检查方式 | 前端组件测试、TypeScript、后端 Chat 测试、OpenAPI/Orval、文档一致性扫尾。 |
| 处置结论 | 本次修复，仍保持截图只作为交互与阅读层级参考，不复制其中具体历史命令或路径。 |
| 证据入口 | 本台账、`trace.md` 验证记录、REQ `acceptance.md` 实现验收证据。 |

### 调整详情

- 后端新增 `chat_conversations.branch_name` 与 `chat_uploaded_materials`，会话创建时校验仓库分支，上传材料写入对象存储并以 opaque `ref_id` 绑定轮次。
- `GET /api/v1/chat/capabilities` 的仓库列表返回 `branches` 与默认分支；`POST /api/v1/chat/conversations` 接收 `branch_name`。
- 新增 `POST /api/v1/chat/materials?space_id=&repository_id=`，服务端验证空间、仓库、文件类型、单文件大小和总量，日志与历史只保存脱敏摘要。
- 轮次 `attachments[]` 支持 `kind: image|file`，发送前重验上传材料所有者、空间、仓库、状态和范围；空文本允许文件或图片上下文。
- Web Composer 支持分支选择、paperclip 多文件上传、剪贴板文件上传、材料条回显、`/` 命令选择、Skill 按钮选择、Skill token、图标发送和执行配置右侧聚合。
- 行为事件和请求日志增加 `file_count`，允许 `chat.file_add` 与 `chat.file_remove`，观测仍禁止保存对象 key、签名 URL、Prompt、回复或本机路径。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 行为仍在原“多图片输入与 Skill 快速引用”范围内；本次补充分支和通用文件上传属于验收反馈对同一 Composer 能力的细化，不新增独立 REQ。 |
| `business-flow.md` | 不改变 Chat 主流程；无需更新。 |
| `user-stories.md` | 用户故事仍覆盖添加材料、引用 Skill 和发送；无需更新。 |
| `acceptance.md` | 已更新为图片/文件、分支选择、粘贴上传和真实上传验收口径。 |
| `trace.md` | 由 Workflow Sync 维护阶段与关联摘要。 |
| `prototype/**` | 原型仍作为输入区与阅读层级参考；本次未新增需要重绘的原型页面。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `uv run --project src/backend pytest src/backend/tests/test_chat.py -q` | pass | 覆盖分支候选、分支会话创建、对象存储上传材料、上传材料重验、文件材料入轮次和既有 Chat 回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom src/chat-composer.test.tsx` | pass | 覆盖多材料 Composer、Skill 选择、上传入口、命令 token 和前端交互回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

## 返修批次 2026-09-20 Chat 消息复制功能修复

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 用户消息复制 | 点击用户消息复制图标后，应复制用户可见正文，不包含被展示层过滤的 `Skill 引用：xxx` 派生说明。 | 已共用 `CopyMessageButton`，用户消息复制 `messageContentForDisplay()` 过滤后的正文。 |
| AI 消息复制 | 点击 AI 消息复制图标后，应复制 AI 正文，不包含 meta、Skill 图标、耗时或 Token 统计。 | 已共用 `CopyMessageButton`，AI 消息复制正文内容。 |
| 可靠复制 | 优先使用 `navigator.clipboard.writeText`；失败或不可用时提供 fallback。 | 已实现 clipboard 优先，失败后回退隐藏 textarea + `document.execCommand("copy")`。 |
| 状态反馈 | 复制成功显示短暂已复制状态，失败显示可访问失败状态。 | 已通过 `aria-label` / `title` 与 `.copied` / `.failed` 状态样式展示成功和失败反馈，1.5 秒后恢复。 |

### 根因证据

- 用户消息和 AI 消息的复制图标此前主要完成视觉呈现，缺少可复用的点击复制动作与状态反馈。
- 浏览器剪贴板 API 受权限与安全上下文影响，单一路径可能失败；此前未覆盖 `navigator.clipboard` 不可用或拒绝时的 fallback。
- 前端测试未覆盖点击复制、复制失败和 fallback 路径，导致该交互缺口未被回归发现。

### 调整详情

- `ConversationMessages.tsx` 新增共用 `copyText()`，先调用 `navigator.clipboard.writeText`，异常或不可用时创建隐藏 textarea 并调用 `document.execCommand("copy")`。
- 新增 `CopyMessageButton` 状态机，成功显示 `已复制`，失败显示 `复制失败`，保留图标按钮和可访问标签。
- 用户消息复制使用过滤后的可见正文，避免把历史旧数据中的 `Skill 引用：xxx` 派生说明复制出去；AI 消息复制仅取 AI 正文。
- CSS 补充复制成功和失败颜色反馈，不改变现有 Skill、附件、payload、trace 或消息布局语义。
- 前端测试覆盖 clipboard 成功路径、textarea fallback 成功路径和 fallback 失败路径。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 不改变产品范围；仍属于 Chat 工作台消息操作体验修复，无需更新。 |
| `business-flow.md` | 不改变会话创建、发送、执行或轨迹读取流程；无需更新。 |
| `user-stories.md` | 不新增用户故事；复制是既有消息动作可靠性修复，无需更新。 |
| `acceptance.md` | 已补充消息复制可靠性、fallback 和成功/失败状态验收口径。 |
| `trace.md` | 本批摘要与验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变布局和视觉结构；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 24 passed；覆盖用户消息/AI 消息复制、clipboard 成功、textarea fallback 成功、fallback 失败、消息布局、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

## 返修批次 2026-09-20 输入框与消息呈现继续复刻

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 输入框分隔线 | 输入区内部不应多一条分隔线；工具栏上边界也不需要分隔线。 | 已移除 `chat-input-row` 内部分隔线和 `chat-composer-actions` 顶部分隔线。 |
| 输入字体 | 输入框文字偏大，应贴近附件 `composer-input`。 | 已将 rich composer 字号调整为 14px、line-height 1.6，输入区高度和 padding 贴近附件。 |
| 用户消息呈现 | 用户消息应按附件 `turn-user` 结构呈现，附件缩略图在气泡上方，Skill pill 与正文同一行，meta 在气泡下方。 | 已新增 `chat-turn-content`，收敛用户消息气泡、附件缩略图、Skill pill 和 meta 结构与样式。 |
| AI 消息呈现 | AI 消息应按附件 `turn-assistant` 结构呈现，包含 avatar、assistant-col、tool-summary 和 bubble-assistant 阅读层级。 | 已为 assistant 消息增加 avatar + assistant-col；`TurnActivity` 改为 tool-summary 风格，AI 正文使用 bubble-assistant 阅读层级。 |

### 附件截图逐项视觉对照表

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户附件 Image #1 与 `moonbox-chat-redesign-v2.html`。 |
| 页面/状态 | Chat 输入框空态；对话区存在用户消息、附件、Skill 引用、AI 消息与运行状态摘要。 |
| 对照对象 | 当前 `Composer`、`ConversationMessages`、`TurnActivity` 与 `chat-workbench.css`。 |
| 期望表现 | Composer 输入本体无中部横线，输入区与底部工具栏之间无额外分隔线；输入字号为 14px/1.6；用户消息为附件缩略图 + 右侧气泡 + 下方 meta；AI 消息为 avatar + assistant-col + tool-summary + 正文 + meta。 |
| 实际表现 | 返修前 `.chat-input-row` 自带 `border-bottom`，形成输入区内部横线；`.chat-rich-composer` 使用 15px/1.75；用户和 AI 消息仍有部分 MoonBox 自有块状结构，AI 缺少 avatar 与 assistant-col。 |
| 偏差项 | 多余分隔线、字体大小、行高、用户消息 DOM 层级、AI 消息 avatar/列布局、运行摘要视觉。 |
| 检查方式 | 附件 HTML 反向工程、截图视觉对照、DOM 结构检查、前端组件测试、TypeScript 编译。 |
| 处置结论 | 本次修复；不改变后端 API、DB、对象存储、权限、会话切换、轨迹读取、历史 actions、ARIA、Enter 发送、附件上传或发送 payload。 |
| 证据入口 | `src/web/src/components/chat/ConversationMessages.tsx`、`src/web/src/components/chat/TurnActivity.tsx`、`src/web/src/styles/chat-workbench.css`、`src/web/src/chat-messages.test.tsx`、`src/web/src/chat-activity.test.tsx`、本台账和 `trace.md`。 |

### 根因证据

- 附件 `composer-input` 为 `font-size:14px; line-height:1.6; min-height:44px`，而当前 `.chat-rich-composer` 为 `font-size:15px; line-height:1.75; min-height:64px`。
- 用户标注截图显示输入区与底部工具栏之间不需要横线；上一轮虽然移除了 `.chat-input-row` 的 `border-bottom`，但 `.chat-composer-actions` 仍保留 `border-top`，形成新的多余分隔线。
- 附件用户消息使用 `turn-user`：附件缩略图、`bubble-user`、`turn-meta` 分层；当前用户消息缺少独立 `chat-turn-content`，附件 token 也更偏信息块。
- 附件 AI 消息使用 `turn-assistant`：avatar、assistant-col、tool-summary、bubble-assistant；当前 AI 消息没有 avatar/assistant-col，运行状态按钮不是 tool-summary 风格。

### 调整详情

- `.chat-input-row` 移除 `border-bottom`，只保留输入区域 padding；`.chat-composer-actions` 移除 `border-top`，使 Composer 输入区与底部工具栏保持同一 Dock 面。
- `.chat-rich-composer` 调整为 14px、line-height 1.6、min-height 44px，并收敛 padding。
- `ConversationMessages` 为用户消息新增 `chat-turn-content` 容器，附件缩略图、Skill pill、正文和 meta 按 turn-user 结构组织。
- Assistant 消息新增 `chat-assistant-avatar` 和 `chat-assistant-col`；正文沿用 `chat-message-bubble` 但按 bubble-assistant 字号与行高展示。
- `TurnActivity` 增加 `chat-tool-summary`、status dot、chevron 和内联执行配置摘要，保留点击查看轨迹、失败提示与运行状态文案。
- 前端测试补充用户消息 turn-user、assistant avatar/column、tool-summary 和执行配置摘要断言。

## 返修批次 2026-09-20 Composer 工具栏分隔线移除

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| Composer 工具栏分隔线 | 用户标注的输入区与底部工具栏之间不需要横线。 | 已删除 `.chat-composer-actions` 的 `border-top`，保留 Dock 外边框和工具栏间距。 |

### 附件截图逐项视觉对照表

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户附件 Image #1，红框标注 Composer 中部横线。 |
| 页面/状态 | Chat 输入框空态，深色 Dock Composer，底部工具栏可见。 |
| 对照对象 | 当前 `.chat-composer-actions` 顶部边框。 |
| 期望表现 | 输入区与底部工具栏之间无额外分隔线，仅通过间距、Dock 背景和整体边框区分层级。 |
| 实际表现 | `.chat-composer-actions` 存在 `border-top: 1px solid var(--rc-border-soft)`，形成红框标注的横线。 |
| 偏差项 | 多余工具栏上边界分隔线。 |
| 检查方式 | 截图标注对照、CSS selector 检查、前端组件测试、TypeScript 编译。 |
| 处置结论 | 本次修复；移除该边框，不改变附件、Skill、发送、运行状态、payload 或窄屏语义。 |
| 证据入口 | `src/web/src/styles/chat-workbench.css`、本台账、`trace.md`。 |

### 根因证据

- 上一批返修将分隔线从 `chat-input-row` 迁移到 `chat-composer-actions` 顶部，但用户复验截图确认该位置同样不需要横线。
- CSS 中 `.chat-composer-actions` 的 `border-top` 与红框标注位置一致，因此根因确认为工具栏顶部边框未移除。

### 调整详情

- 删除 `.chat-composer-actions` 的 `border-top`。
- 保留 Composer Dock 外边框、底部工具栏间距、输入文本 14px/1.6、附件/Skill payload 和发送语义。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批仅移除工具栏分隔线，不新增业务能力，无需更新。 |
| `acceptance.md` | 需要更新 AC-UI-012，将“工具栏上边界显示分隔线”修正为“输入区与工具栏之间不显示分隔线”。 |
| `trace.md` | 通过 Workflow Sync 维护，不手动编辑 linked Issue marker。 |
| prototype | 原型意图仍为 Chat 输入区视觉复刻，无需更新静态 prototype。 |

### 验证证据

| 命令 | 结果 | 说明 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-composer.test.tsx src/chat-messages.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 4 files / 22 tests；覆盖 Composer、消息、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |
| `openspec validate add-chat-workbench-image-skill-context --strict` | pass | 当前 Change 规格校验通过。 |

## 返修批次 2026-09-20 用户消息 Skill 重复展示修正

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 用户消息 Skill 展示 | 用户消息气泡按附件预期仅显示 Skill pill 与用户原始输入正文同一行，不再额外展示 `Skill 引用：xxx`。 | 已在用户消息展示层过滤历史旧数据中的 `Skill 引用：xxx` 派生行；`skills[]` / `materials[]` payload 和 trace 不变。 |

### 附件截图逐项视觉对照表

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户附件 Image #1 当前效果、Image #2 预期效果。 |
| 页面/状态 | Chat 对话区用户消息，存在 Skill pill、正文、执行配置 meta、复制和查看本轮轨迹。 |
| 对照对象 | `ConversationMessages` 用户消息气泡、`chat-message-skills`、`SafeMarkdown` 正文渲染。 |
| 期望表现 | 用户消息气泡中 Skill pill 与正文位于同一内容流；不展示额外 `Skill 引用：explore` 派生说明。 |
| 实际表现 | 当前效果同时显示 Skill pill 和正文中的 `Skill 引用：explore`，造成重复且纵向层级变重。 |
| 偏差项 | 重复文案、消息气泡内容层级、用户原始正文与派生上下文摘要混杂。 |
| 检查方式 | 截图视觉对照、DOM 渲染路径检查、前端组件测试、TypeScript 编译。 |
| 处置结论 | 本次修复；仅过滤用户消息展示层中的派生行，不改变发送 payload、Skill material、trace、附件、复制和查看本轮轨迹语义。 |
| 证据入口 | `src/web/src/components/chat/ConversationMessages.tsx`、`src/web/src/chat-messages.test.tsx`、本台账和 `trace.md`。 |

### 根因证据

- `ConversationMessages` 已基于 `materials.kind === "skill"` 渲染 Skill pill。
- 部分历史或执行返回的 `row.content` 中仍包含 `Skill 引用：explore` 派生说明，`SafeMarkdown` 会原样渲染，导致与 Skill pill 重复。
- 用户预期图显示用户气泡只需要 Skill pill 与正文，Skill 引用说明属于派生上下文摘要，不应进入用户消息可读正文。

### 调整详情

- 新增用户消息展示内容过滤：当消息存在 Skill material 时，移除正文中匹配 `Skill 引用：...` 的派生行。
- 用户消息复制使用过滤后的展示正文；当过滤后为空时回退原始内容，避免复制空内容。
- 保留 `skills[]`、`materials[]`、trace、附件位于气泡上方、复制按钮和查看本轮轨迹入口。
- 前端测试补充历史旧数据场景：正文包含 `Skill 引用：explore` 时，气泡仍显示 Skill pill 和用户正文，但不显示派生行。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批属于消息展示层去重，不新增业务能力，无需更新。 |
| `acceptance.md` | 需要补充用户消息气泡不展示 `Skill 引用：xxx` 派生说明的验收标准。 |
| `trace.md` | 通过 Workflow Sync 维护，不手动编辑 linked Issue marker。 |
| prototype | 原型意图仍为 Chat 输入区和消息流视觉复刻，无需更新静态 prototype。 |

### 验证证据

| 命令 | 结果 | 说明 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 4 files / 22 tests；覆盖用户消息 Skill 去重、附件、Skill pill、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

## 返修批次 2026-09-20 用户消息 meta 行收敛

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 用户消息 meta | 模型信息与时间信息放在同一行，模型信息位于最前并使用更亮的 mono 弱强调色；复制为图标；用户消息不需要查看本轮轨迹入口。 | 已将用户消息 `effective_config` 合入 `chat-message-meta` 最前方，复制按钮改为 `Copy` 图标并保留 `aria-label`，用户消息不再渲染查看本轮轨迹；AI 消息轨迹入口保留。 |

### 附件截图逐项视觉对照表

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | `moonbox-chat-redesign-v2.html` 用户消息 `.turn-meta`。 |
| 页面/状态 | Chat 对话区用户消息，包含附件、Skill pill、正文、模型信息、时间和复制动作。 |
| 对照对象 | `ConversationMessages` 用户消息 `chat-message-meta` 与 `chat-message-config`。 |
| 期望表现 | `codex · gpt-6-astra · high · 时间 · 复制图标` 位于同一行；模型信息在最前，颜色比时间更亮；用户消息不展示查看本轮轨迹。 |
| 实际表现 | 返修前模型信息单独渲染为 `chat-message-config`，时间、复制和查看本轮轨迹位于另一行；复制为文字按钮。 |
| 偏差项 | meta 层级拆分、颜色层级、复制按钮形态、用户消息轨迹入口冗余。 |
| 检查方式 | 参考 HTML selector 对照、DOM 结构检查、前端组件测试、TypeScript 编译。 |
| 处置结论 | 本次修复；保留附件、Skill pill、复制内容、AI 消息查看本轮轨迹和现有 payload 语义。 |
| 证据入口 | `src/web/src/components/chat/ConversationMessages.tsx`、`src/web/src/styles/chat-workbench.css`、`src/web/src/chat-messages.test.tsx`、本台账和 `trace.md`。 |

### 根因证据

- 参考稿 `.turn-meta` 将 `.model-tag`、时间与动作放在同一 flex 行，`.model-tag` 使用 mono 字体和更亮弱强调色。
- 当前实现把用户模型信息放在独立 `.chat-message-config` 段落中，再另起 `.chat-message-meta` 展示时间、复制和查看本轮轨迹，导致布局与层级不一致。
- 用户反馈明确取消用户消息“查看本轮轨迹”入口，但保留 AI 消息轨迹入口，属于展示层收敛，不影响执行 trace 数据。

### 调整详情

- 用户消息不再单独渲染 `.chat-message-config`。
- 用户消息 meta 最前渲染 `.chat-message-model`，内容为 `agent · model · reasoning`，并与时间和复制图标同一行。
- 复制按钮改为 lucide `Copy` 图标，保留 `aria-label="复制消息"` 和原复制内容。
- 用户消息不渲染“查看本轮轨迹”；AI 消息仍保留该入口。
- 前端测试补充用户 meta 模型信息、复制图标和无用户轨迹入口断言。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批属于用户消息 meta 视觉和动作收敛，不新增业务能力，无需更新。 |
| `acceptance.md` | 需要补充用户消息 meta 行、复制图标和不展示用户轨迹入口的验收标准。 |
| `trace.md` | 通过 Workflow Sync 维护，不手动编辑 linked Issue marker。 |
| prototype | 原型意图仍为 Chat 消息流视觉复刻，无需更新静态 prototype。 |

### 验证证据

| 命令 | 结果 | 说明 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 4 files / 22 tests；覆盖用户消息 meta、复制图标、无用户轨迹入口、附件、Skill pill、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

## 返修批次 2026-09-20 AI 消息 meta 与统计收敛

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| AI 消息间距 | `tool-summary` 与 AI 正文之间间距过大。 | 已缩小 `chat-turn-activity` 与 assistant 内容间距，并收敛 assistant column gap。 |
| AI Skill 展示 | AI 正文不重复显示 `Explore skill`，复制图标后新增 Skill 图标，hover 显示使用的 Skill。 | 已限制 Skill pill 仅在用户消息气泡渲染；AI meta 复制图标后显示 Skill 图标，使用 `title` / `aria-label` 暴露 Skill 名称。 |
| AI meta 对齐 | 时间、复制、Skill 与 AI 正文左对齐。 | 已新增 `chat-assistant-meta` 并左对齐。 |
| AI meta 动作 | 复制改为图标；底部 `查看本轮轨迹` 与上方 `tool-summary` 点击重复，不再显示。 | 已将 AI 复制改为图标按钮并移除底部查看本轮轨迹；上方 `tool-summary` 仍保留点击进入轨迹。 |
| tool-summary | `已完成 + 模型信息` 参照附件加边框。 | 已增强 `chat-tool-summary` 边框与背景，保留状态、工具调用和模型信息。 |
| AI 耗时与 Token | 时间、复制、Skill 后展示首 token、整体耗时和 Token 数；没有字段不得伪造。 | 已从现有 `execution.usage` 事件展示已采集 `total_tokens`、`duration_ms` 或 turn `created_at/updated_at` 推导的整体耗时；当前接口未提供首 token、输入/输出/思考 token 时不展示。 |

### 附件截图逐项视觉对照表

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户附件 Image #1 当前 AI 消息标注、Image #2 Codex Skill hover 参考、`moonbox-chat-redesign-v2.html` assistant turn。 |
| 页面/状态 | Chat 对话区 AI 消息，包含 tool-summary、AI 正文、meta、Skill 引用与统计字段。 |
| 对照对象 | `TurnActivity`、`ConversationMessages` assistant 分支、`chat-message-meta`、`chat-tool-summary`。 |
| 期望表现 | tool-summary 与正文间距紧凑；AI 正文不重复 Skill pill；AI meta 左对齐，包含时间、复制图标、Skill 图标及可采集统计；底部不再展示查看本轮轨迹。 |
| 实际表现 | 返修前 tool-summary 与正文间距过大；AI 正文重复显示 Skill pill；AI meta 居中偏移、复制为文字、底部轨迹入口与 tool-summary 重复；统计字段未集中展示。 |
| 偏差项 | 间距、Skill 重复、meta 对齐、动作图标、冗余轨迹入口、统计展示策略。 |
| 检查方式 | 附件/HTML 视觉对照、DOM 结构检查、事件事实源检查、前端组件测试、TypeScript 编译。 |
| 处置结论 | 本次修复；统计只展示当前 API/事件中可信字段，不伪造首 token 与分项 token。 |
| 证据入口 | `src/web/src/components/chat/ConversationMessages.tsx`、`src/web/src/components/chat/TurnActivity.tsx`、`src/web/src/styles/chat-workbench.css`、`src/web/src/chat-messages.test.tsx`、本台账和 `trace.md`。 |

### 根因证据

- 参考稿 assistant turn 不重复展示 Skill pill；Skill 更适合落在 meta 动作区。
- 当前 `ConversationMessages` 在所有角色消息气泡内渲染 `chat-message-skills`，导致 assistant 正文也显示 Skill pill。
- 当前事件 API 已能读取 `execution.usage.total_tokens`，工具事件也可能携带 `duration_ms`；但现有 `TurnRead` / message API 未直接提供首 token 延时、输入 token、输出 token、思考 token 字段。
- `read_events` 只返回 `sequence`、`type`、`payload`，不返回事件 `created_at`，因此首 token 延时不能从前端可靠推导。

### 调整详情

- Assistant 正文不再渲染 Skill pill；用户消息仍保留 Skill pill 与正文同一行。
- 新增 AI meta 读取同一 turn 的事件与状态，只展示可信字段：`execution.usage.total_tokens`、`execution.usage.duration_ms`，或在无 usage duration 时用 terminal turn 的 `updated_at - created_at` 作为整体耗时近似。
- 首 token 延时、输入/输出/思考 token 当前无字段时不展示。
- AI 复制按钮改为图标，Skill 图标使用 hover title 和 aria-label 展示本轮 Skill。
- 移除 AI meta 中底部 `查看本轮轨迹`，保留 `tool-summary` 点击进入轨迹。
- 缩小 `.chat-turn-activity` 与正文间距，增强 `chat-tool-summary` 边框和背景。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批属于 AI 消息展示层收敛，不新增后端能力，无需更新。 |
| `acceptance.md` | 需要补充 AI meta、Skill 图标、统计字段不伪造和轨迹入口去重的验收标准。 |
| `trace.md` | 通过 Workflow Sync 维护，不手动编辑 linked Issue marker。 |
| prototype | 原型意图仍为 Chat 消息流视觉复刻，无需更新静态 prototype。 |

### 验证证据

| 命令 | 结果 | 说明 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 4 files / 22 tests；覆盖 AI Skill 去重、复制图标、Skill 图标、无底部轨迹入口、Token/耗时展示、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批属于 Chat 输入框和对话阅读层级视觉细化；未新增独立业务能力，无需更新。 |
| `business-flow.md` | 不改变 Chat 创建、上传、引用 Skill、运行或轨迹查看流程；无需更新。 |
| `user-stories.md` | 用户故事仍覆盖发送消息、查看执行状态和查看轨迹；无需更新。 |
| `acceptance.md` | 已补充输入框分隔线、字号、用户消息和 AI 消息呈现验收口径。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 原 prototype 不变；附件 HTML 与用户截图作为视觉参考，无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-activity.test.tsx src/chat-composer.test.tsx src/chat-workbench.test.tsx` | pass | 22 passed；覆盖用户消息 turn-user、assistant avatar/column、tool-summary、Composer 与 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

## 返修批次 2026-09-18 AI 运行状态块左对齐

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| AI 运行状态块对齐 | “连接中 / 执行中 / 正在等待执行结果”等 AI 状态块应与输入框左边缘对齐。 | 已将 `chat-turn-activity` 外层轨道调整为与 Composer 相同的 1120px 内容轨道并居中。 |
| 内部正文可读性 | 状态块内部正文不应因外层轨道变宽而变成长行。 | 已保留内部子元素 `max-width: min(720px, 72%)`，维持运行状态内容的可读宽度。 |
| 既有能力不回退 | 不影响右侧用户消息、附件、Skill chip、轨迹入口、窄屏布局和 payload 语义。 | 仅调整 CSS 轨道宽度；DOM、API、payload、轨迹入口和消息结构不变。 |

### 附件截图逐项视觉对照表

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户附件 Image #1。 |
| 页面/状态 | `/chat` 深色主题，对话页中存在右侧用户消息和左侧 AI 运行状态块；底部 Composer 可见。 |
| 对照对象 | 当前 `TurnActivity` / `.chat-turn-activity`、底部 `.chat-composer` 与消息区布局。 |
| 期望表现 | AI 运行状态块外层左边缘与输入框左边缘同轨道对齐；内部文字仍保持较窄阅读宽度。 |
| 实际表现 | 返修前 `.chat-turn-activity` 使用 `width: min(720px, 72%)` 和 `margin: auto`，导致其左边缘比 1120px Composer 轨道明显右缩。 |
| 偏差项 | 内容轨道宽度、左边缘对齐、运行状态块与 Composer 的视觉关系。 |
| 检查方式 | 截图视觉对照、CSS selector 检查、前端组件测试、TypeScript 编译。 |
| 处置结论 | 本次修复；不改变后端 API、DB、对象存储、权限、会话切换、轨迹读取、历史 actions、ARIA、Enter 发送、附件上传或发送 payload。 |
| 证据入口 | `src/web/src/styles/chat-workbench.css`、`src/web/src/chat-activity.test.tsx`、本台账和 `trace.md`。 |

### 根因证据

- Composer 轨道为 `.chat-main > .chat-composer { width: min(100% - 48px, 1120px); margin: 14px auto 22px; }`。
- AI 运行状态块原先为 `.chat-turn-activity { width: min(720px, 72%); margin: 22px auto 0; }`。
- 在宽视口下两个元素都居中，但宽度不同，720px 状态块左边缘会相对 1120px Composer 左边缘向右缩进，形成截图中的不对齐。

### 调整详情

- 将 `.chat-turn-activity` 外层改为 `width: min(100%, 1120px); max-width: 1120px; margin: 22px auto 0;`，与 Composer 共享同一内容轨道。
- 新增 `.chat-turn-activity > * { max-width: min(720px, 72%); }`，保持按钮、执行配置和状态正文的可读宽度。
- 窄屏下将 `.chat-turn-activity > *` 恢复为 `max-width: 100%`，避免横向溢出。
- 前端测试补充运行中活动块渲染覆盖，确认状态块仍展示执行配置与状态正文。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批属于对话阅读层级 UI 对齐细化；未新增独立业务能力，无需更新。 |
| `business-flow.md` | 不改变 Chat 创建、运行、轨迹读取或消息回显流程；无需更新。 |
| `user-stories.md` | 用户故事仍覆盖发送后查看 AI 执行状态和轨迹；无需更新。 |
| `acceptance.md` | 已补充 AI 运行状态块与 Composer 内容轨道对齐验收口径。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变原型结构；用户截图作为视觉对齐证据，无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-activity.test.tsx src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-workbench.test.tsx` | pass | 21 passed；覆盖运行状态块、消息布局、Composer 和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

## 返修批次 2026-09-18 Composer 与消息流视觉复核

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 输入框背景 | Composer 输入框背景应贴近参考图深色 Dock 风格，不应呈现为偏亮普通面板。 | 已调整 `chat-composer` 为深色 Dock 容器，强化边框、圆角、底部工具栏分隔和输入区域层级。 |
| 项目选择 | 会话创建前不应显示项目/仓库选择；一个空间对应一个产品和仓库，用户只选择分支。 | 已移除可见“项目/仓库”选择器，前端自动使用当前空间绑定仓库注入会话创建与上传 payload，UI 仅保留分支选择。 |
| 历史弹窗操作按钮 | 历史弹窗行内操作应更轻量，默认弱化，hover/focus 清晰，删除保持危险态。 | 已调整历史行内 action 视觉，保留置顶、重命名、归档/恢复、删除权限与禁用语义。 |
| 聊天信息布局 | 用户消息、Skill chip、附件和 meta 应按参考图消息流层级展示。 | 已重构历史消息 DOM：附件在用户泡上方，Skill chip 与用户正文位于同一用户消息泡内，meta 与执行配置跟随消息组；助手正文保持左侧主体阅读区。 |

### 附件截图逐项视觉对照表

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户附件 Image #1 和 Image #2。 |
| 页面/状态 | Image #1 为当前实际页面：Composer 偏亮、显示项目选择、消息布局与参考稿不一致；Image #2 为参考页面：深色输入 Dock、历史顶栏入口、对话阅读流。 |
| 对照对象 | 当前 `/chat` 的 `Composer`、`ConversationMessages`、`SessionDialogs` 和 `chat-workbench.css`。 |
| 期望表现 | Composer 为深色 Dock；创建前仅可选分支；历史行内动作轻量；用户消息靠右成组，附件预览在消息泡上方，Skill chip 与文本在同一消息内容流。 |
| 实际表现 | 上一批返修后 Composer 背景仍偏面板色；单仓库场景显示“项目”选择；历史 action 视觉仍较实；消息回显仍把 Skill/附件/配置作为正文后的材料块展示。 |
| 偏差项 | 背景色、可见控件、按钮视觉权重、消息 DOM 层级、Skill chip 与用户正文归属、附件预览位置。 |
| 检查方式 | 附件视觉对照、DOM 结构检查、前端组件测试、TypeScript 编译、OpenSpec 校验。 |
| 处置结论 | 本次修复；不改变 API、DB、对象存储、权限、会话切换、轨迹读取、历史 actions、ARIA、Enter 发送、附件上传或发送 payload schema。 |
| 证据入口 | `src/web/src/components/chat/Composer.tsx`、`src/web/src/components/chat/ConversationMessages.tsx`、`src/web/src/components/chat/SessionDialogs.tsx`、`src/web/src/styles/chat-workbench.css`、`src/web/src/chat-messages.test.tsx` 和本台账。 |

### 根因证据

- `Composer` 在未创建会话时仍渲染 `chat-draft-repository` 下的“项目”选择器，且仓库只在单仓库时自动选中；这与“空间绑定仓库，用户只选分支”的验收结论冲突。
- `.chat-composer` 继承 `var(--rc-panel-2)` 背景，视觉上更像普通卡片，未形成参考图的深色底部 Dock。
- `ConversationMessages` 原实现将正文、执行配置、Skill/附件材料和 meta 分块顺序渲染，导致 Skill chip 不属于用户消息内容流。
- `SessionDialogs` 历史动作已改成图标，但默认权重和 hover/focus 状态仍不够贴近参考稿轻量行内 action。

### 调整详情

- `Composer` 移除可见仓库选择器，`repository` 始终从当前空间能力列表自动取第一个绑定仓库；会话创建、材料上传和 Skill 读取仍使用同一 repository 值。
- `chat-composer` 样式改为深色 Dock：扩大最大宽度、强化圆角和阴影、输入区底部分隔、工具区贴近参考稿。
- `ConversationMessages` 新增消息组结构：`chat-message-attachments` 展示图片/文件摘要，`chat-message-bubble` 内展示 Skill chip 与正文，`chat-message-meta` 跟随消息组。
- `chat-message-skill` 使用轻量 chip 展示 `Skill + 英文名`，不展示 `context_reference_only` 等内部说明；附件仍只展示脱敏摘要。
- 历史弹窗 `chat-history-actions` 默认弱化，行 hover/focus 时清晰展示；删除动作保留 danger 语义。
- 前端测试更新为自动仓库注入契约，并新增消息布局测试，固定附件、Skill chip、正文和消息泡的 DOM 归属。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 本批仍属于 Chat 输入区与对话阅读层级验收细化；未新增独立业务能力，无需更新。 |
| `business-flow.md` | 不改变 Chat 创建、上传、引用 Skill、历史或轨迹主流程；无需更新。 |
| `user-stories.md` | 用户故事仍覆盖创建会话前选择分支、添加材料、引用 Skill 和查看历史消息；无需更新。 |
| `acceptance.md` | 已补充自动仓库注入、深色 Dock、历史 action 和消息流布局验收口径。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 原 prototype 与用户附件继续作为视觉参考；本批不需要重绘原型。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-composer.test.tsx src/chat-messages.test.tsx src/chat-sessions.test.tsx src/chat-workbench.test.tsx src/chat-trajectory.test.tsx src/chat-execution.test.tsx` | pass | 32 passed；覆盖自动仓库注入、Composer、消息流、历史动作、subbar、轨迹与执行回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

### 文档同步

已同步 Change `tasks.md`、`trace.md`、`design.md`、delta spec、REQ `acceptance.md`、Sprint 验收报告、API 索引、数据库设计、对象存储策略和产品数据采集与链路观测说明。

## 返修批次 2026-09-17 Skill 入口与候选读取

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| Skill 图标位置 | Skill 图标按钮放在文件上传按钮右侧。 | 已将 Skill 按钮移动到上传文件按钮所在的左侧材料动作组。 |
| Skill 候选读取 | 仓库 `.agents/skills` 中存在多个 Skill，页面不应显示“当前仓库暂无可引用 Skill”。 | 已补齐部署挂载，让后端 `governance_root/.agents/skills` 可读到仓库 Skill。 |

### 附件截图逐项视觉对照表

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户附件 Image #1，显示仓库 `.agents/skills` 目录下存在多个 Skill。 |
| 页面/状态 | Chat Composer Skill 菜单空态；项目文件树展示 `.agents/skills` 非空。 |
| 对照对象 | 当前 Web Composer 左侧动作组、后端 `skill_candidates()`、Docker Compose 治理根目录挂载。 |
| 期望表现 | 上传文件图标右侧直接显示 Skill 图标；点击 Skill 或输入 `/` 能列出 `.agents/skills/*/SKILL.md` 候选。 |
| 实际表现 | Skill 按钮位于右侧执行配置组；Docker 后端的 `/app/governance` 未挂载 `.agents`，导致后端判断 Skill 目录不可用。 |
| 偏差项 | 按钮位置、部署挂载、Skill 候选事实源可见性。 |
| 检查方式 | DOM 组件测试、后端 Skill 候选测试、Compose 挂载单元测试。 |
| 处置结论 | 本次修复，仍保持 Skill 只作为上下文引用，不自动执行命令。 |
| 证据入口 | `src/web/src/chat-composer.test.tsx`、`src/backend/tests/test_chat.py`、`tests/unit/test_chat_platform_script.py`。 |

### 根因证据

- 前端 `Composer` 中上传按钮位于 `.chat-material-actions`，Skill 按钮位于 `.chat-composer-right`，因此视觉上不在上传按钮右侧。
- 后端 `skill_candidates()` 读取 `binding.governance_root/.agents/skills`；本地仓库 `.agents/skills` 存在 46 个 `SKILL.md`，但容器投影 `/app/governance/.agents/skills` 不存在。
- `deploy/docker-compose.chat-platform.yml` 与 `deploy/docker-compose.governance.yml` 原挂载清单未包含 `./.agents:/app/governance/.agents:ro`。

### 调整详情

- Web Composer 将 Skill 按钮移动到文件上传按钮右侧，仍复用同一候选菜单和 Skill token 行为。
- Chat 平台和治理覆盖 Compose 均增加 `.agents` 到 `/app/governance/.agents:ro` 的只读挂载，确保 API 后端与常驻控制器读取同一项目 Skill 事实源。
- 后端测试固定验证存在 `.agents/skills/<name>/SKILL.md` 时 `GET /api/v1/chat/skills` 返回候选。
- 前端测试固定验证文件上传入口与 Skill 按钮属于同一个材料动作组。
- 部署测试固定验证 Chat/Governance 覆盖服务均包含 `.agents` 只读挂载。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 仍属于原 Skill 快速引用和输入区布局验收细化；无需更新。 |
| `business-flow.md` | 不改变 Chat 主流程；无需更新。 |
| `user-stories.md` | 用户故事仍覆盖引用 Skill；无需更新。 |
| `acceptance.md` | 已补充 Skill 按钮位置和 `.agents/skills` 候选可见性验收口径。 |
| `trace.md` | 已记录本批返修摘要与验证结果。 |
| `prototype/**` | 原型仍作为输入区参考；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom src/chat-composer.test.tsx` | pass | 9 passed；覆盖 Skill 按钮在上传按钮右侧材料动作组内。 |
| `uv run --project src/backend pytest src/backend/tests/test_chat.py -q` | pass | 36 passed, 1 skipped；覆盖后端 Skill 候选从 `.agents/skills` 返回。 |
| `uv run pytest tests/unit/test_chat_platform_script.py -q` | pass | 5 passed；覆盖 Chat/Governance Compose `.agents` 只读挂载。 |

## 返修批次 2026-09-17 Skill 搜索与轻量展示

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| Skill 列表视觉 | 每一个 Skill 项不需要边框，右侧不需要显示 `---`，展示 Skill 英文名和中文描述。 | 已调整菜单项为无边框行，英文名使用 slug title-case 展示，中文描述来自 `SKILL.md` frontmatter `description`。 |
| `/bug` 模糊搜索 | 输入框输入 `/bug` 时应像参考图一样筛出匹配 Skill。 | 已将 `/xxx` 输入识别为 Skill 查询，并按 id、名称、摘要进行客户端模糊过滤。 |
| 选中后 token | 选中后输入框只显示完整图标 + Skill 英文名，不显示其他说明，不需要边框。 | 已将 Skill token 改为无边框轻量 token，仅显示图标、英文名和移除按钮。 |

### 附件截图逐项视觉对照表

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户附件 Image #1 和 Image #2。 |
| 页面/状态 | Image #1 为 Skill 候选列表与选中后 `Explore` token 参考；Image #2 为当前 Chat Composer 中 Skill token 展示参考。 |
| 对照对象 | Web Composer Skill 菜单、`/` 搜索触发、Skill token、后端 Skill 候选摘要。 |
| 期望表现 | Skill 列表行没有单项边框；行内展示英文名和中文描述；右侧不出现 `---`；输入 `/bug` 时模糊筛选 Bug 相关 Skill；选中后 token 仅保留图标和 Skill 英文名。 |
| 实际表现 | 返修前后端把 YAML frontmatter 第一行 `---` 当作 summary；前端列表项使用按钮边框样式且说明右对齐；`/bug` 触发菜单但不稳定过滤；选中 token 显示 `context_reference_only` 并继承材料 token 边框。 |
| 偏差项 | Skill 摘要解析、候选过滤、菜单行视觉、token 内容和边框。 |
| 检查方式 | 后端 Skill 候选测试、前端组件测试、TypeScript 编译、OpenSpec 校验。 |
| 处置结论 | 本次修复；截图只作为交互与视觉参考，不复制其中历史命令、路径或执行结果。 |
| 证据入口 | `src/backend/tests/test_chat.py`、`src/web/src/chat-composer.test.tsx`、`trace.md` 验证记录。 |

### 根因证据

- 后端 `skill_candidates()` 原先读取 `SKILL.md` 第一条非空行作为摘要；含 YAML frontmatter 的 Skill 第一行是 `---`，因此前端右侧展示 `---`。
- 前端 `onPromptChange()` 对 `/xxx` 调用 `openSkillMenu()`，而 `openSkillMenu()` 使用 toggle，连续输入会让菜单开关状态不稳定，且未保存查询词用于候选过滤。
- 前端 Skill token 复用 `.chat-material-token`，所以显示边框和 `injection_scope` 说明，不符合验收截图里的轻量 token。

### 调整详情

- 后端新增 Skill 摘要解析逻辑，优先读取 frontmatter `description`，再回退到正文标题或首段，避免把 `---` 当摘要。
- Web Composer 新增 Skill 查询状态，输入 `/bug` 时强制打开菜单并按 id、名称、中文描述模糊过滤；Skill 按钮入口仍展示全部候选。
- Skill 列表项改为无边框行，展示 title-case 英文名与中文描述；空态与无匹配态分离。
- Skill token 改为无边框轻量样式，仅显示图标、title-case 英文名和移除按钮，不展示 `context_reference_only`。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 仍属于原 Skill 快速引用输入体验细化；无需更新。 |
| `business-flow.md` | 不改变 Chat 主流程；无需更新。 |
| `user-stories.md` | 用户故事仍覆盖引用 Skill；无需更新。 |
| `acceptance.md` | 已补充 Skill 列表中文描述、`/keyword` 搜索和轻量 token 验收口径。 |
| `trace.md` | 由 Workflow Sync 维护阶段投影，本批摘要写入 Change trace。 |
| `prototype/**` | 原型仍作为输入区参考；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom src/chat-composer.test.tsx` | pass | 9 passed；覆盖 `/bug` 模糊搜索、中文描述展示、无 `---`、轻量 Skill token 和发送上下文。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |
| `uv run --project src/backend pytest src/backend/tests/test_chat.py -q` | pass | 36 passed, 1 skipped；覆盖 Skill frontmatter `description` 解析与 Chat 回归。 |

## 返修批次 2026-09-18 Skill token 与用户输入同一行

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| Skill token 布局 | Skill 不与附件放在同一行，而是与用户输入放在同一行。 | 已将 Skill token 从附件材料条移出，放入 `chat-input-row`，与文本输入框同一输入行展示。 |
| 附件材料条语义 | 附件材料条只展示图片或文件。 | `chat-attachment-strip` 仅在存在图片或文件材料时渲染，不再承载 Skill token。 |

### 附件截图逐项视觉对照表

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户附件 Image #1。 |
| 页面/状态 | Chat Composer 深色主题；输入框内同时存在文件附件、Skill token、用户输入和底部动作区。 |
| 对照对象 | Web Composer 当前 `chat-material-strip`、`chat-input-row`、`chat-skill-token` 和 `chat-prompt`。 |
| 期望表现 | 图片或文件附件显示在输入框上方材料区；Skill token 与用户输入位于同一输入行，不和附件同排。 |
| 实际表现 | 返修前 `Composer` 将 `materials` 和 `skills` 同时渲染在 `chat-material-strip`，导致文件 token 与 Skill token 位于同一材料行。 |
| 偏差项 | 组件层级、行内布局、材料条语义和可测试 selector 归属。 |
| 检查方式 | DOM 结构检查、前端组件测试、TypeScript 编译、Change spec 与 REQ acceptance 一致性检查。 |
| 处置结论 | 本次修复；截图仅作为视觉与交互期望参考，不复制其中具体文件名、输入内容或本机路径。 |
| 证据入口 | `src/web/src/components/chat/Composer.tsx`、`src/web/src/styles/chat-workbench.css`、`src/web/src/chat-composer.test.tsx`、本台账和 `trace.md`。 |

### 根因证据

- `Composer` 原 JSX 使用同一个 `chat-material-strip` 同时渲染 `materials.map(...)` 与 `skills.map(...)`。
- `.chat-material-strip` 是横向 flex 容器，因此在同时有文件附件与 Skill token 时自然把二者放在同一行。
- 验收反馈要求 Skill 与用户输入同一行，属于当前输入区 UI 行为修正，不扩大 API、DB、权限、部署或对象存储边界。

### 调整详情

- `Composer` 中 `chat-attachment-strip` 改为仅在 `materials.length > 0` 时渲染图片或文件 token。
- 新增 `chat-input-row` 包裹 Skill token 与 textarea，Skill token 仍保留无边框轻量样式、图标、英文名和移除入口。
- CSS 为 `chat-input-row` 增加 flex 布局，textarea 在桌面端与 Skill token 同行，窄屏下允许自然换行，避免横向溢出。
- 前端测试补充断言：选中 Skill 后 token 位于 `chat-input-row` 内，且 Skill-only 场景不渲染 `chat-attachment-strip`。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 仍属于原“输入区多材料与 Skill 快速引用”范围；本次只细化 token 归属行，无需更新。 |
| `business-flow.md` | 不改变 Chat 创建、上传、引用 Skill 或发送主流程；无需更新。 |
| `user-stories.md` | 用户故事仍覆盖引用 Skill 和添加附件；无需更新。 |
| `acceptance.md` | 已补充 Skill token 与用户输入同一行、且不进入附件材料条的验收口径。 |
| `trace.md` | 由 Workflow Sync 维护阶段投影；本批摘要写入 Change trace。 |
| `prototype/**` | 原型仍作为输入区层级参考；未新增需要重绘的页面或交互状态。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-composer.test.tsx` | pass | 9 passed；覆盖 Skill token 位于输入行且不进入附件材料条。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |
| `node scripts/check-chat-materials.cjs http://127.0.0.1:18112 ../../openspec/changes/add-chat-workbench-image-skill-context/evidence/ui` | pass | 2 screenshots + computed style；合成 API mocks，覆盖 `chat-input-row` 内存在 Skill token 且附件材料条不承载 Skill token。 |

## 返修批次 2026-09-18 Rich Composer inline Skill chip

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| Skill 与用户消息布局 | Skill token 不是 textarea 左侧独立列，而是像参考图一样成为用户消息编辑内容流里的 inline chip，文本从 chip 后继续输入并自然换行。 | 已将 textarea 替换为 rich composer：Skill token 为 `contentEditable=false` inline chip，文本编辑节点与 token 位于同一内容流。 |
| 既有输入语义 | 保留 Enter 发送、Shift+Enter 换行、`/skill` 搜索、粘贴上传和现有发送 payload 语义。 | 已保留原 `draft` 纯文本状态和 `skills[]` payload；前端测试覆盖 Enter、Skill 搜索、发送 payload 和粘贴上传入口。 |

### 附件截图逐项视觉对照表

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户附件 Image #1 和 Image #2。 |
| 页面/状态 | Image #1 为当前问题效果；Image #2 为预期效果，Skill chip 与用户消息文本处于同一编辑内容流。 |
| 对照对象 | Web Composer `chat-rich-composer`、`chat-skill-token`、`chat-prompt`、附件材料条和底部动作区。 |
| 期望表现 | Skill chip 像文本前缀一样嵌入消息编辑流；长文本从 chip 后继续并自然换行；附件仍位于输入框上方材料区。 |
| 实际表现 | 上一批返修把 Skill token 与 textarea 放进同一个 flex row；长文本仍在 textarea 独立盒子里排版，形成“左 token + 右文本块”的两列效果。 |
| 偏差项 | 编辑器组件模型、文本流归属、换行行为和视觉参考契约表达不够精确。 |
| 检查方式 | 代码结构检查、前端组件测试、Playwright 截图、computed style 和 DOM selector 验证。 |
| 处置结论 | 本次修复；不改变后端 API、DB、对象存储、权限或执行 payload。 |
| 证据入口 | `src/web/src/components/chat/Composer.tsx`、`src/web/src/styles/chat-workbench.css`、`src/web/src/chat-composer.test.tsx`、`src/web/scripts/check-chat-materials.cjs`、`trace.md`。 |

### 根因证据

- 上一版 `chat-input-row` 结构中，Skill token 与 `textarea` 是 flex sibling；这只能实现“同一容器行”，无法让 token 进入 textarea 的文本排版流。
- HTML `textarea` 不能嵌入 React token、图标或可删除 chip，因此继续调整 flex、padding 或定位只能伪装第一行，无法稳定支持长文本自然换行。
- 参考图表达的是 inline chip + text editor 的 rich composer 形态，需将输入控件升级为 contenteditable 编辑器模型。

### 调整详情

- Web Composer 将 `textarea` 替换为 `chat-rich-composer`，内部包含 `contentEditable=false` 的 Skill token 和 `contenteditable` 文本节点。
- `draft` 仍保存纯文本；`skills[]` 仍保存 Skill 快照；发送 payload、幂等签名、Skill 选择事件和材料上传语义不变。
- 文本节点使用非受控 contenteditable 与状态同步，避免每次输入重绘导致光标跳动；选择 Skill 后会清理 `/keyword` 并把焦点放回文本末尾。
- 样式将 `chat-prompt` 设置为 inline 文本流，Skill token 与用户输入共享 `chat-rich-composer` 的自然换行。
- 视觉脚本新增 `chat-rich-composer`、`chat-prompt` display 和 Skill token 归属断言，防止退回 flex sibling 布局。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 仍属于原“输入区多材料与 Skill 快速引用”范围；本次细化编辑器实现模型，无需更新。 |
| `business-flow.md` | 不改变 Chat 创建、上传、引用 Skill 或发送主流程；无需更新。 |
| `user-stories.md` | 用户故事仍覆盖引用 Skill 后继续输入消息；无需更新。 |
| `acceptance.md` | 已更新为 rich composer inline chip 验收口径。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 原型仍作为输入区层级参考；本次参考用户附件修正组件模型，无需重绘 prototype。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-composer.test.tsx` | pass | 9 passed；覆盖 rich composer 中 Skill token 与文本节点同属内容流、`/bug` 搜索、发送 payload 和 Enter 行为。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |
| `node scripts/check-chat-materials.cjs http://127.0.0.1:18112 ../../openspec/changes/add-chat-workbench-image-skill-context/evidence/ui` | pass | 2 screenshots + computed style；验证 Skill token 位于 `chat-rich-composer` 内、`chat-prompt` 为 inline 且附件材料条不承载 Skill token。 |

## 返修批次 2026-09-18 Skill inline chip 键盘删除

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| Delete 删除 Skill | 输入框 Skill inline chip 可通过 `Delete` 键删除。 | 已支持 chip 聚焦时按 `Delete` 或 `Backspace` 删除该 Skill。 |
| 光标附近删除 | 光标在 Skill chip 附近时按 `Delete` 或 `Backspace` 删除 Skill。 | 当文本光标位于 rich composer 文本开头时，`Delete` 或 `Backspace` 会删除紧邻文本的最后一个 Skill chip。 |
| 状态同步 | 删除后同步 `skills[]`、草稿状态和 `chat.skill_remove` 事件，发送 payload 不再包含已删除 Skill。 | 已复用统一 `removeSkill()` 路径；测试覆盖 DOM、事件与发送 payload。 |

### 附件截图逐项视觉对照表

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 无新增附件；沿用 rich composer inline chip 交互状态。 |
| 页面/状态 | Chat Composer rich composer，已选 Skill inline chip，焦点在 chip 或文本开头。 |
| 对照对象 | `chat-rich-composer`、`chat-skill-token`、`chat-prompt`、`skills[]` payload 和行为事件。 |
| 期望表现 | `Delete` / `Backspace` 与 chip 的 `x` 按钮具备等价删除能力；删除后 payload 不包含该 Skill。 |
| 实际表现 | 返修前 `onKeyDown` 只处理 Enter 发送；Skill 删除只绑定在 chip 内部 `x` 按钮。 |
| 偏差项 | 键盘可访问性、inline chip 编辑模型、状态同步路径。 |
| 检查方式 | 前端组件测试、TypeScript、代码路径检查、发送 payload 断言。 |
| 处置结论 | 本次修复；不改变后端 API、DB、对象存储、权限或执行 payload schema。 |
| 证据入口 | `src/web/src/components/chat/Composer.tsx`、`src/web/src/chat-composer.test.tsx`、本台账和 `trace.md`。 |

### 根因证据

- `chat-prompt` 的 `onKeyDown` 仅覆盖 Enter 发送和 IME 保护，未处理 `Delete` 或 `Backspace`。
- Skill token 删除逻辑内联在 `x` 按钮 `onClick` 中，键盘事件无法复用该路径。
- rich composer 中 Skill token 是 `contentEditable=false` inline chip；若不显式实现键盘删除，浏览器不会自动同步 React `skills[]` 状态和发送 payload。

### 调整详情

- 新增统一 `removeSkill(id)`，供 `x` 按钮、chip 键盘删除和文本开头删除复用。
- Skill chip 增加 `tabIndex=0` 和 `Delete` / `Backspace` 键盘处理，删除后焦点回到文本末尾。
- `chat-prompt` 在文本光标位于开头时，按 `Delete` 或 `Backspace` 删除紧邻文本的最后一个 Skill chip。
- 前端测试新增键盘删除覆盖：删除后 DOM token 消失，记录 `chat.skill_remove`，发送 payload 的 `skills` 为空。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 仍属于 Skill inline chip 编辑体验细化；无需更新。 |
| `business-flow.md` | 不改变 Chat 创建、上传、引用 Skill 或发送主流程；无需更新。 |
| `user-stories.md` | 用户故事仍覆盖引用与移除 Skill；无需更新。 |
| `acceptance.md` | 已补充 `Delete` / `Backspace` 键盘删除验收口径。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变原型布局；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-composer.test.tsx` | pass | 10 passed；覆盖 Skill inline chip `Delete` 删除、`chat.skill_remove` 事件和发送 payload 同步。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

## 返修批次 2026-09-20 Chat 消息材料与 assistant 阅读层级返修

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 用户消息材料派生行 | 用户消息正文不显示 `图片引用：图片.png · image/png · 54059 bytes`。 | 已在展示层过滤用户消息中的 `图片引用`、`文件引用`、`Skill 引用` 派生行，仅保留用户原始正文。 |
| 图片点击放大 | 图片缩略图支持点击放大查看。 | 已将用户消息附件缩略图改为按钮；存在 `metadata.preview_url/url/download_url/content_url` 时展示真实图片，否则打开材料摘要弹窗并明确当前历史摘要缺少可预览地址，不伪造 URL。 |
| AI 消息重复图片 | AI 消息不重复展示用户上传图片或附件。 | 已限定附件缩略图仅在用户消息渲染；AI 消息材料仍保留在 payload/trace，不在正文区重复展示。 |
| AI tool-summary 位置和样式 | `已读 x 次 工具调用 · 已完成 ...` 与 AI 图标同一行结构，作为 assistant-col 第一行，并按附件 `tool-summary` 边框样式呈现。 | 已将 assistant turn 的 `TurnActivity` 移入 `assistant-col` 首行；运行中无 assistant 消息时仍保留用户消息下方运行状态。 |
| AI 重点信息差异化 | 类似 `未修改代码或创建 Issue` 的关键结论需要高亮。 | 已在安全 Markdown 文本节点中高亮重点内容，不开放 HTML 注入；后续批次已将固定文案表升级为语义特征识别。 |

### 附件截图逐项视觉对照表

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户附件 Image #1、Image #2；参考附件 `moonbox-chat-redesign-v2.html`。 |
| 页面/状态 | Chat 对话页，包含用户图片材料、Skill pill、AI tool-summary、AI 正文和 meta。 |
| 对照对象 | 当前 `ConversationMessages`、`TurnActivity`、`SafeMarkdown` 与 `chat-workbench.css`；参考稿 `.turn-assistant`、`.tool-summary`、`.bubble-assistant .field-hint b`。 |
| 期望表现 | 用户气泡正文不显示材料派生行；用户图片缩略图可点击预览；AI 不重复附件；tool-summary 与 AI avatar/assistant-col 同组；关键结论金色强调。 |
| 实际表现 | 返修前用户正文仍显示 `图片引用`；AI 消息重复渲染图片材料；`TurnActivity` 挂在用户消息块后，视觉上位于 AI 图标上方；重点结论未差异化。 |
| 偏差项 | 材料摘要去重、附件预览交互、assistant turn DOM 层级、tool-summary 样式位置、重点文本视觉强调。 |
| 检查方式 | 代码路径检查、前端组件测试、TypeScript 编译；图片真实预览地址仅使用已有 material metadata，不新增 API 或伪造地址。 |
| 处置结论 | 本次修复；不改变后端 API、DB、对象存储、权限、payload 或 trace 语义。 |
| 证据入口 | `src/web/src/components/chat/ConversationMessages.tsx`、`src/web/src/components/chat/SafeMarkdown.tsx`、`src/web/src/styles/chat-workbench.css`、`src/web/src/chat-messages.test.tsx`、本台账和 `trace.md`。 |

### 根因证据

- 后端 `material_message()` 会将图片、文件和 Skill 摘要拼入消息正文，便于执行上下文和历史可追溯；展示层此前只过滤 `Skill 引用`，未过滤 `图片引用` / `文件引用`。
- `ConversationMessages` 对 `row.materials` 不区分角色，导致 assistant 消息也渲染用户上传图片附件。
- `TurnActivity` 仅挂在用户消息块之后；当 assistant 消息出现时，tool-summary 未成为 assistant turn 的第一行。
- `SafeMarkdown` 安全渲染仅处理普通文本、链接、粗体、代码、列表和表格，未提供重点内容高亮。

### 调整详情

- `messageContentForDisplay()` 扩展过滤规则，用户消息正文过滤 `图片引用`、`文件引用` 和 `Skill 引用` 派生行，复制动作继续复用过滤后的可见正文。
- 用户附件缩略图改为可点击按钮，打开材料预览弹窗；有真实预览 URL 时显示图片，无 URL 时展示材料摘要和“未包含可预览地址”提示。
- assistant 消息不再渲染非 Skill 附件，避免重复展示用户图片；保留 Skill meta 图标和 payload。
- assistant 消息存在时，将同 turn 的 `TurnActivity` 放入 `assistant-col` 首行；assistant 尚未生成时，用户消息下方仍展示运行状态，保证运行中反馈不丢失。
- `SafeMarkdown` 对重点内容进行 `mark.chat-important-highlight` 包裹，样式使用 accent 色强调，不允许 HTML 注入。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 仍属于 Chat 消息阅读层级与材料回显验收修复；无需更新主 PRD。 |
| `business-flow.md` | 不改变 Chat 创建、材料上传、发送、执行或轨迹读取流程；无需更新。 |
| `user-stories.md` | 不新增用户故事；材料预览与 assistant 阅读层级属于既有消息体验验收细化，无需更新。 |
| `acceptance.md` | 已补充材料派生行过滤、图片预览、AI 不重复附件、tool-summary 位置与重点高亮验收口径。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变 prototype 主布局；参考稿差异已通过本批对照表记录，无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 24 passed；覆盖用户材料派生行过滤、图片预览弹窗、AI 不重复附件、assistant 内 tool-summary、重点内容高亮、复制、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

## 返修批次 2026-09-20 Chat 消息字号收敛到 13px

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 聊天输入框字号 | Composer 输入文字从 14px 改为 13px。 | 已将 `.chat-rich-composer` 字号调整为 13px，保留 `line-height: 1.6`。 |
| 用户消息字号 | 用户消息正文从 14px 改为 13px。 | 已将 `.chat-message-user .chat-message-bubble` 字号调整为 13px。 |
| AI 消息字号 | AI 消息正文从 14px 改为 13px。 | 已将 `.turn-assistant .chat-message-bubble` 字号调整为 13px。 |

### 附件截图逐项视觉对照表

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 无新增附件；沿用本轮用户文本验收反馈。 |
| 页面/状态 | Chat 对话页，Composer、用户消息、AI 消息正文阅读态。 |
| 对照对象 | 当前 `chat-workbench.css` 中 `.chat-rich-composer`、`.chat-message-user .chat-message-bubble`、`.turn-assistant .chat-message-bubble`。 |
| 期望表现 | 三处正文类文本字号统一为 13px，meta、按钮、tool-summary 等辅助信息不随本次调整改变。 |
| 实际表现 | 返修前三处均为 14px。 |
| 偏差项 | 文本密度和字号。 |
| 检查方式 | CSS 片段检查、前端组件测试、TypeScript 编译。 |
| 处置结论 | 本次修复；不改变布局、payload、API、DB、权限、对象存储或 trace 语义。 |
| 证据入口 | `src/web/src/styles/chat-workbench.css`、本台账和 `trace.md`。 |

### 根因证据

- 上一批按参考稿将输入框和消息正文从更大字号收敛到 14px；本轮用户明确验收要求继续统一调整为 13px。
- 目标 CSS 选择器均为正文阅读层，不涉及 meta、配置 chip、tool-summary、按钮或弹窗标题。

### 调整详情

- `.chat-rich-composer`：`font-size: 13px`，保留 `line-height: 1.6`。
- `.chat-message-user .chat-message-bubble`：`font-size: 13px`，保留用户消息行高和气泡布局。
- `.turn-assistant .chat-message-bubble`：`font-size: 13px`，保留 AI 消息行高和 assistant 布局。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 仍属于 Chat 阅读密度验收细化；无需更新主 PRD。 |
| `business-flow.md` | 不改变业务流程；无需更新。 |
| `user-stories.md` | 不新增用户故事；无需更新。 |
| `acceptance.md` | 已将当前有效验收口径从 14px 更新为 13px。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变原型结构；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 24 passed；覆盖消息、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

## 返修批次 2026-09-20 AI 正文重点高亮语义化

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 重点高亮判断方式 | `未修改代码或创建 Issue` 只是示例，不应只按指定文案高亮。 | 已移除固定 `IMPORTANT_PHRASES` 文案表，改为基于句子语义特征识别关键结论、风险/阻塞、动作结果和下一步等重点内容。 |
| 安全边界 | 保留 SafeMarkdown 安全渲染，不允许 HTML 注入。 | 高亮仍只发生在普通文本节点；代码、链接、粗体、表格等既有安全子集保持原渲染规则，未开放原始 HTML。 |
| 测试覆盖 | 示例文案仅作为样例之一，多种表达均需覆盖。 | 前端测试覆盖“当前判断/根因未确认/需要补充”和“未修改代码或创建 Issue”两类表达，并验证普通说明不被高亮。 |

### 根因证据

- `SafeMarkdown.tsx` 返修前存在固定 `IMPORTANT_PHRASES = ["未修改代码或创建 Issue", "未修改代码", "未创建 Issue"]`，导致高亮能力绑定少量示例文案。
- `chat-messages.test.tsx` 返修前只断言固定样例 `未修改代码或创建 Issue`，未覆盖同类语义的不同表达。

### 调整详情

- 将固定文案匹配替换为 `IMPORTANT_SEGMENT_PATTERNS` 语义特征规则，覆盖结论/判断、风险/阻塞、失败/不可用、根因未确认、动作结果和下一步/补充动作等句子。
- `highlightText()` 改为按中文/英文句末符号切分普通文本片段，对命中语义特征的整句使用 `mark.chat-important-highlight` 包裹。
- `inline()` 仍先隔离代码、粗体和安全链接，普通文本片段才进入高亮逻辑，保持 SafeMarkdown 安全边界。
- `chat-messages.test.tsx` 将固定短语断言改为多高亮断言，确认示例文案不是唯一命中条件，同时普通说明不高亮。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 仍属于 AI 消息阅读层级验收细化；无需更新主 PRD。 |
| `business-flow.md` | 不改变业务流程；无需更新。 |
| `user-stories.md` | 不新增用户故事；无需更新。 |
| `acceptance.md` | 已将 AC-030 从固定示例文案口径更新为基于语义特征的重点内容高亮。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变原型结构或视觉布局；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 24 passed；覆盖语义高亮、普通说明不高亮、消息布局、复制、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

## 返修批次 2026-09-20 AI 正文重点高亮密度收敛

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 高亮密度 | 高亮内容不能太多，否则失去重点提示意义。 | 已在语义候选基础上增加优先级和数量限制，每条 AI 消息最多高亮 1-2 个短片段。 |
| 高亮范围 | 避免整句大面积高亮，普通礼貌句和泛化建议不高亮。 | 已从整句命中改为短片段抽取，优先 `根因未确认`、`未修改代码或创建 Issue` 等高信号片段。 |
| 候选优先级 | 多候选时优先高亮最终结论、阻塞原因和动作结果。 | 已按阻塞/失败/不可用、动作结果、已完成结果、下一步补充动作排序，低优先级候选在达到上限后不再高亮。 |

### 根因证据

- 上一批 `highlightText()` 对命中语义特征的整句使用 `mark.chat-important-highlight` 包裹；一旦句子中同时包含“当前判断”“根因未确认”“需要补充”等词，整句会被高亮。
- `chat-messages.test.tsx` 上一批断言整句 `当前判断：根因未确认，需要补充页面名称。` 高亮，未约束高亮数量和短片段范围。

### 调整详情

- 新增 `MAX_IMPORTANT_HIGHLIGHTS = 2`，每条 `SafeMarkdown` 内容最多消费 2 个高亮片段。
- 用 `IMPORTANT_FRAGMENT_RULES` 替代整句规则，按优先级抽取短片段：阻塞/失败/不可用与未完成动作优先，其次已完成动作，最后才是下一步补充动作。
- `buildHighlightPlan()` 在渲染前基于全文生成高亮计划，按优先级和位置选择非重叠片段，再由普通文本节点消费；代码、链接、粗体和表格安全边界保持不变。
- 前端测试断言高亮结果为 `根因未确认` 和 `未修改代码或创建 Issue`，并确认 `需要补充页面名称` 与普通说明不高亮。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 仍属于 AI 消息阅读层级验收细化；无需更新主 PRD。 |
| `business-flow.md` | 不改变业务流程；无需更新。 |
| `user-stories.md` | 不新增用户故事；无需更新。 |
| `acceptance.md` | 已将 AC-030 补充为最多 1-2 个高优先级短片段，避免整句大面积高亮。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变原型结构或视觉布局；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx` | pass | 4 passed；覆盖短片段高亮、最多 2 个高亮、低优先级候选不高亮、普通说明不高亮和消息布局回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

## 返修批次 2026-09-18 Chat 对话/轨迹/历史布局复刻

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 对话/轨迹 | 按附件 HTML 参考稿，将【对话】/【轨迹】改为 subbar 左侧 segmented tabs，并在同一行右侧展示连接与关联状态。 | 已将 tabs 与 `RelationsBar` 合并到 `chat-subbar`，保留 `role=tablist`、`chat-relations-bar`、项目连接刷新和管理关联行为。 |
| 历史 | 历史保持顶栏入口，但弹窗布局复刻附件的标题、说明、搜索、筛选、分组列表和行内动作。 | 已重构 `SessionDialogs` 历史视图，按置顶、最近 7 天、更早分组，动作改为置顶、重命名、归档/恢复、删除图标按钮。 |
| 轨迹 | 轨迹按附件的 `trace-wrap`、toolbar、状态摘要、搜索、scrub 和事件行布局展示。 | 已调整 `ExecutionPanel` 与 `TrajectoryView` 结构和样式，保留事件详情、原始事件、引用快照、Diff、停止、重试与读取逻辑。 |

### 附件截图逐项视觉对照表

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户附件 `moonbox-chat-redesign-v2.html`。 |
| 页面/状态 | Chat 工作台参考稿；覆盖顶栏、subbar、对话面板、轨迹面板、历史弹窗和 Composer。 |
| 对照对象 | 当前 `/chat` 的 `ChatWorkbenchPage`、`SessionDialogs`、`ExecutionPanel`、`TrajectoryView` 和 `chat-workbench.css`。 |
| 期望表现 | 顶栏右侧保留历史和新建会话；对话/轨迹为 compact segmented tabs；连接/主对象/管理关联在同一 subbar；历史 modal 有搜索、筛选、分组和行内图标动作；轨迹有 toolbar、状态摘要、搜索、scrub、event row。 |
| 实际表现 | 返修前对话/轨迹为下划线 tabs，关联状态单独占一行；历史为普通表格式弹窗；轨迹使用旧 toolbar、overview 和列表样式，视觉层级与参考稿差异较大。 |
| 偏差项 | 顶部行结构、tab 形态、关联状态位置、历史弹窗信息架构、轨迹 toolbar/status/scrub/event row 层级。 |
| 检查方式 | HTML 反向工程、代码结构检查、前端组件测试、TypeScript 编译；本批不复制参考稿静态示例内容。 |
| 处置结论 | 本次修复；共享侧边栏、Composer 既有 rich composer、真实会话数据、权限、历史 actions、轨迹读取与停止/重试语义保持不变。 |
| 证据入口 | `src/web/src/pages/catalog/ChatWorkbenchPage.tsx`、`src/web/src/components/chat/SessionDialogs.tsx`、`src/web/src/components/chat/ExecutionPanel.tsx`、`src/web/src/components/chat/TrajectoryView.tsx`、`src/web/src/styles/chat-workbench.css`、前端测试输出。 |

### 根因证据

- `ChatWorkbenchPage` 原结构将 `chat-view-tabs` 和 `RelationsBar` 分成两行，无法呈现参考稿 subbar 的左右结构。
- `SessionDialogs` 历史视图原先直接渲染线性 `chat-history-row`，没有分组、搜索框图标容器和行内图标动作。
- `TrajectoryView` 原先使用 `chat-trajectory-toolbar`、`chat-timeline-overview` 和普通 timeline row；`ExecutionPanel` 的运行状态、停止和轮次选择也分散在多个块中，无法形成参考稿的 trace toolbar/status/scrub/event row 层级。
- 用户附件为 UI 参考稿，不是业务指令；静态标题、时间、命令、用户信息和示例事件均未复制为产品数据。

### 调整详情

- `ChatWorkbenchPage` 新增 `chat-subbar`，将对话/轨迹 tabs 与 `RelationsBar` 放在同一行；CSS 将 tabs 改为 segmented control，将连接状态和关联入口改为轻量 status chip。
- `SessionDialogs` 历史弹窗保留 `ChatDialog`、分页、搜索、筛选、置顶、重命名、归档/恢复、删除逻辑，新增分组和 lucide 图标动作展示。
- `ExecutionPanel` 顶部改为 `trace-toolbar`，同区展示运行状态、停止按钮和执行轮次选择；状态摘要改为 `trace-status`。
- `TrajectoryView` 改为 `trace-wrap` 内的 `trace-controls`、`scrub` 和 `event-row`，继续支持搜索、收起/展开、耗时/顺序、事件详情 tab 和原始事件查看。
- `Composer` 为 rich composer 文本节点补充 `.value/.disabled` 与 `change` 事件兼容层，并在单仓库场景也显示会话仓库选择，保持既有测试和辅助查询稳定。
- 前端测试补充 segmented tabs 与 subbar、历史分组/行结构、trace-wrap/scrub/event-row DOM 契约断言。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 仍属于原“Chat 工作台图片/文件输入、Skill 快速引用与 Codex 基线体验增强”范围；本次扩展到对话/轨迹/历史布局复刻，未新增 API、DB、权限或部署边界，无需更新主 PRD。 |
| `business-flow.md` | 不改变 Chat 创建、会话历史、执行轨迹读取或关联对象流程；无需更新。 |
| `user-stories.md` | 用户故事仍覆盖 Chat 工作台对话输入、Skill 引用、历史和轨迹查看；无需更新。 |
| `acceptance.md` | 已补充对话/轨迹 segmented tabs、历史弹窗和轨迹 trace-wrap 验收口径。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 参考稿来自用户附件 HTML，原 prototype 仍作为输入区和阅读层级参考；无需重绘。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-workbench.test.tsx src/chat-sessions.test.tsx src/chat-trajectory.test.tsx src/chat-execution.test.tsx` | pass | 21 passed；覆盖 subbar segmented tabs、历史 modal 分组/行结构、trace-wrap/scrub/event-row、执行停止与历史动作回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

## 返修批次 2026-09-20 Chat Codex 写权限门禁拆分

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 写权限阶段 | REQ/BUG 早期阶段也需要写治理文档，不应要求主对象已 `in_sprint`。 | 已将写权限拆分为 `governance_write`、`implementation_write`、`read_only`；有主对象且用户具备空间写角色时，未归档 REQ/BUG 可获得治理目录写权限。 |
| 产品实现保护 | 修改 `src/`、`tests/`、API、DB、部署等实现文件时仍需严格门禁。 | `implementation_write` 仍要求主对象 `in_sprint`、关联 active Change trace 与 Sprint `sprint.yaml` 双向纳入；否则只降级为治理写或完全只读。 |
| 前端表达 | 用户需要明确知道当前会话是治理可写、实现只读还是完全只读。 | 会话响应新增 `write_scope` 与 `write_reason_code`；Composer 展示“治理可写 / 实现可写 / 完全只读”状态，`reason_code` 作为 hover 信息。 |

### 根因证据

- `src/backend/app/chat/policy.py` 返修前 `write_allowed()` 将写权限绑定到主对象 `in_sprint`、活动 Change trace 与 Sprint 双向纳入；早期 REQ/BUG 即使只需要写 `issues/**` 治理文档也会被降级为 read-only。
- `src/backend/app/chat/container_server.py` 返修前只有 `moonbox-read` 与 `moonbox-write` 两个 profile；若简单放宽 `write_allowed()`，会把整个 `/work` 打开，不符合“实现只读”的安全边界。
- 前端 `ConversationRead` 返修前不包含写权限原因字段，Composer 只能展示归档、运行中、执行服务未就绪等状态，无法解释治理写与实现写差异。

### 调整详情

- `policy.py` 新增 `write_policy()`，返回稳定 `write_scope` 与 `reason_code`；`write_allowed()` 继续作为兼容布尔入口。
- `container_server.py` 新增 `moonbox-governance` profile：`/work` 只读，仅 `issues/`、`openspec/changes/`、`iterations/`、`docs/spec-logs/` 等受控治理目录可写，`.git` 只读、网络禁用。
- `app_server.py` 与 `execution.py` 按 `write_scope` 选择 `moonbox-read`、`moonbox-governance` 或 `moonbox-write`；运行期间 scope 变化会按权限撤销处理。
- 会话读取、创建、列表和更新响应补充 `write_scope`、`write_reason_code`；前端手写 Chat API 类型扩展该字段并在 Composer 底部展示状态胶囊。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 仍属于 Chat Codex 会话执行权限与治理上下文增强；无需更新主 PRD。 |
| `business-flow.md` | 不改变会话创建、发送、关联或历史流程；只细化执行器写入门禁。 |
| `user-stories.md` | 不新增用户故事；无需更新。 |
| `acceptance.md` | 已补充治理可写、实现可写和完全只读的验收口径。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变 UI 原型结构；仅新增 Composer 权限状态胶囊。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `uv run pytest src/backend/tests/test_chat.py::test_write_policy_requires_current_role_and_sprint_change src/backend/tests/test_chat.py::test_conversation_read_includes_write_scope src/backend/tests/test_chat_app_server.py::test_named_profile_downgrades_write src/backend/tests/test_chat_app_server.py::test_named_profile_supports_governance_scope` | pass | 4 passed；覆盖无主对象完全只读、早期 REQ 治理可写、Sprint/Change 双向纳入后实现可写、角色撤销和 App Server governance profile。 |
| `./node_modules/.bin/vitest run src/chat-composer.test.tsx` | pass | 14 passed；覆盖 Composer 权限状态展示、既有提示、上传、Skill、下拉、发送回归。 |

### 残余风险

| 项 | 结论 |
|---|---|
| 子路径权限依赖 | `moonbox-governance` 依赖 Codex permissions profile 对更具体路径的写权限覆盖；聚焦测试覆盖 profile 选择，完整容器沙箱探针需在 Docker 本地验收时补跑。 |
| OpenAPI 生成 | `src/web/openapi.json` 已由生成脚本导出，本地 Orval 已生成客户端；脚本包装层仍因本机 pnpm/corepack 缓存缺失在版本检查处退出，后续环境恢复后可补跑完整脚本确认同等结果。 |

## 返修批次 2026-09-20 Chat 写权限状态刷新与只读原因提示

### 验收反馈

| 项 | 期望 | 返修结论 |
|---|---|---|
| 状态不可手动切换 | Composer 的写权限状态不是可点击开关，应由管理关联和后端 `write_policy` 自动刷新。 | 已保持状态胶囊为展示控件，并在管理关联保存后立即重新拉取会话，刷新 `write_scope` / `write_reason_code`。 |
| 无主对象提示 | `primary_object_required` 时应引导先设置主对象。 | `chat-write-scope` 的 `title` 与 `aria-label` 改为可读原因，提示“请先在管理关联中设置主对象”。 |
| 早期 REQ/BUG 治理可写 | 主对象为未终态 REQ/BUG 且用户具备写角色时，应显示治理可写，不要求 `in_sprint`。 | 后端策略保持上一批 `governance_write` 规则；本轮补充刷新链路，关联保存后前端能看到最新状态。 |
| 运行中权限语义 | 已有运行中的 Codex turn 保持原权限，新发送轮次才使用最新 scope。 | 保存提示明确“已有运行保持原权限”；后端测试覆盖 turn 启动后新增主对象仍不热升级。 |

### 根因证据

- `Composer` 的写权限胶囊是 `span`，并非按钮；用户无法通过点击切换权限，权限只来自会话响应中的 `write_scope`。
- `RelationsBar` 保存关联后只更新本地 `value` 并调用无参 `onSaved()`；页面层只展示 toast，没有调用 `model.refreshSelected()` 重新读取会话，因此 `write_scope` 可能停留在保存前的 `read_only`。
- `run_claim()` 在 turn 启动时读取一次 `write_policy()` 并设置 App Server scope；运行期间只检查已获写权限是否被撤销，不会把 read-only turn 热升级为写权限。

### 调整详情

- `Composer.tsx` 新增 `writeScopeReason()`，将 `primary_object_required`、`actor_not_writer`、`governance_object_writable` 等 reason code 映射为可读提示，并绑定到 `title` / `aria-label`。
- `RelationsBar.tsx` 将 `onSaved` 扩展为携带保存后的 `Relations`，便于父层触发会话刷新或后续状态更新。
- `ChatWorkbenchPage.tsx` 在关联保存后调用 `model.refreshSelected()`，刷新当前会话的 `write_scope` 与 `write_reason_code`，并提示已有运行保持原权限、下一轮使用最新范围。
- `test_chat.py` 补充运行中不热升级测试；`chat-composer.test.tsx` 覆盖可读只读原因；`chat-relations.test.tsx` 覆盖保存后回传关联结果供父层刷新。

### REQ 子文档一致性扫尾检查

| 子文档 | 结论 |
|---|---|
| `requirement.md` | 仍属于 Chat Codex 会话执行权限与治理上下文增强；无需更新主 PRD。 |
| `business-flow.md` | 不改变会话创建、发送或管理关联流程；仅补齐保存后的状态刷新与提示。 |
| `user-stories.md` | 不新增用户故事；无需更新。 |
| `acceptance.md` | 已更新 AC-OBS-007 和实现验收证据，补充关联保存刷新、只读原因提示和运行中权限不热切换。 |
| `trace.md` | 本批摘要和验证证据写入 Change trace；REQ trace 继续由 Workflow Sync 维护。 |
| `prototype/**` | 不改变 UI 原型结构；仅增强状态胶囊提示和保存后的数据刷新。 |

### 验证证据

| 命令 | 结果 | 摘要 |
|---|---|---|
| `uv run pytest src/backend/tests/test_chat.py::test_write_policy_requires_current_role_and_sprint_change src/backend/tests/test_chat.py::test_conversation_read_includes_write_scope src/backend/tests/test_chat.py::test_running_turn_keeps_original_read_only_scope_after_primary_object_added -q` | pass | 3 passed；覆盖无主对象只读、关联后治理可写、实现写门禁、角色撤销和运行中不热升级。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-composer.test.tsx src/chat-relations.test.tsx` | pass | 18 passed；覆盖写权限状态提示、只读原因 hover/aria、管理关联保存后回传刷新事实和既有 Composer/Relations 回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

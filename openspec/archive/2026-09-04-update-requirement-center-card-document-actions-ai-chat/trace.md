---
change_id: update-requirement-center-card-document-actions-ai-chat
status: in_progress
type: update
source_requirement: REQ-0020-requirement-center-card-document-actions-ai-chat
sprint: sprint-003
created_at: 2026-08-18 09:58:34
updated_at: 2026-09-03 08:30:40
prototype_sources:
  - issues/requirements/review/REQ-0020-requirement-center-card-document-actions-ai-chat/prototype/web/prototype.html
  - issues/requirements/review/REQ-0020-requirement-center-card-document-actions-ai-chat/prototype/web/prototype.png
  - issues/requirements/review/REQ-0020-requirement-center-card-document-actions-ai-chat/prototype/web/context.md
conflict_resolution:
  status: documented
ui_contract:
  status: documented
ui_skeleton:
  status: implemented
visual_acceptance_1440:
  status: pass
computed_style:
  status: pass
mock_api_boundary:
  status: documented
req_final_consistency:
  status: pass
---

# Trace

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-18 09:58:34 | req.opsx | 创建 REQ-0020 对应 OpenSpec Change，状态为 proposed。 |
| 2026-08-18 10:20:24 | opsx.apply | 完成需求中心卡片文档入口、Capture、AI 聊天、阶段动作、选择弹窗、tasks 抽屉、后端受控文档接口与测试；1440px 视觉和 computed style 证据待补。 |
| 2026-08-18 10:37:04 | opsx.modify | 按验收反馈修正未入迭代阶段 Sprint 标签显示语义：采集池、规划中、待评审、已评审不展示历史 Sprint，也不进入 Sprint 筛选来源。 |
| 2026-08-18 10:44:08 | opsx.modify | 按用户截图反馈优化 Capture 弹窗为轻量紧凑表单，补充 segmented 类型选择、pill 优先级选择、标题 autofocus、校验错误态和统一按钮风格。 |
| 2026-08-18 10:52:00 | opsx.apply | 补齐 1440px 视觉验收、关键交互截图、computed style 证据和 REQ 最终一致性检查，Change 任务完成。 |
| 2026-08-18 11:35:26 | opsx.modify | 按二次验收反馈修正阶段文档白名单、采集池探索辅助动作、未入开发隐藏研发进度，并继续优化 Capture 弹窗必填同行、分割线、留白和校验态。 |
| 2026-08-18 11:50:38 | opsx.modify | 按原型继续收口采集池卡片视觉：文档入口改为金色文本链接，辅助分析动作移入 footer 右侧并使用“需求分析 / Bug 分析”，缺失提示和卡片留白轻量化。 |
| 2026-08-18 12:10:49 | opsx.modify | 按最新验收反馈细化采集池卡片：修复文档分隔符乱码为真实空格，文档链接字重对齐缺失提示，压缩缺失提示间距，footer 主次动作取消加粗并区分金色/蓝灰层级。 |
| 2026-08-18 13:04:39 | opsx.modify | 按验收反馈增强 Markdown 抽屉：补充背景蒙层、桌面可拖拽宽度、移动端全屏规则，并限制采集池 `capture.md` 受控编辑保存，`trace.md` 保持只读。 |
| 2026-08-18 13:17:12 | opsx.modify | 按验收确认细化采集池 `capture.md` 抽屉：默认预览，点击“编辑”进入编辑态，保存成功后回到预览态并回显最新内容；`trace.md` 继续只读。 |
| 2026-08-30 22:12:55 | opsx.modify | 按验收反馈新增受控 workflow demo 模式：显式 `?mock=workflow` / `?demo=workflow` 覆盖 9 阶段每列至少 1 张 `DEMO-` 卡片，默认真实 API 数据不受影响。 |
| 2026-08-30 22:55:41 | opsx.modify | 按验收反馈补齐 workflow demo 文档内容：Markdown demo 文档直接展示阶段匹配 mock 正文，HTML demo 文档通过 Blob 新 Tab 预览，默认真实 API 文档读取不受影响。 |
| 2026-09-01 19:45:55 | opsx.modify | 按验收反馈调整采集池卡片 footer 动作顺序：辅助分析动作排在主生成动作左侧，Requirement 展示“需求分析 / 生成需求”，Bug 展示“Bug 分析 / 生成 Bug”。 |
| 2026-09-01 20:14:30 | opsx.modify | 按验收反馈收紧采集池与规划中主动作门禁：生成/完善动作要求阶段必需文档存在且内容非空，采集池分析动作保持随时可用。 |
| 2026-09-01 20:32:00 | opsx.modify | 按验收反馈扩展未入迭代阶段必备文档门禁：待评审和已评审主动作也必须满足 Requirement / Bug 对应文档包存在且内容非空。 |
| 2026-09-01 23:25:30 | opsx.modify | 按验收反馈统一缺失文档 Tips 口径：优先展示 `action.disabled_reason`，前端 fallback 使用阶段 + 类型必备文档表，并区分缺少文档、空文档和数据漂移。 |
| 2026-09-01 23:40:00 | opsx.modify | 按验收反馈重做 workflow demo 数据为验收矩阵：覆盖 9 阶段 Requirement / Bug 正常、缺失、空文档、漂移、禁用、可编辑/只读、HTML、Sprint、tasks 和归档场景。 |
| 2026-09-02 08:48:39 | opsx.modify | 按验收反馈为待评审“发起评审 / 确认修复”增加二次确认；成功流转到已评审后重新计算 action 为“加入迭代 →”，并要求 Sprint 选择。 |
| 2026-09-03 08:02:54 | opsx.modify | 按验收反馈将验收中研发、测试、人工验收进度统一为可点击入口，点击后打开右侧统一进度抽屉并按来源高亮对应分区。 |
| 2026-09-03 08:19:00 | opsx.modify | 按验收反馈先补齐人工验收 `已完成/总数` 格式；该轮对进度区颜色层级的理解已由 2026-09-03 08:30:40 记录纠正。 |
| 2026-09-03 08:30:40 | opsx.modify | 纠正 Image #2 参考关系后重新对齐验收中进度区：默认视觉改为灰蓝色次级内联文本，恢复点分隔并取消金色和加粗，人工验收继续保持 `已完成/总数` 格式。 |

## Readiness Report

| 项 | 结果 | 证据 |
|---|---|---|
| Review Gate | pass | REQ trace status 为 `in_sprint`，iteration 为 `sprint-003` |
| Requirement Readiness | ready | requirement、acceptance、trace、user-stories、business-flow 齐全 |
| Prototype Gate | pass | prototype_refs、prototype_gate、AC-PROTOTYPE 与 context.md 已存在 |
| Knowledge Gate | pass | 读取 prototype-driven-ui-gate、sprint-002 retrospective、prototype-ui-acceptance |

## 影响范围

```yaml
backend: true
web: true
api: true
database: false
storage: false
admin: false
miniapp: false
```

## 实现证据

| 项 | 结果 | 证据 |
|---|---|---|
| UI Skeleton | implemented | `src/web/src/pages/catalog/RequirementCenterPage.tsx` 新增卡片文档入口、阶段动作容器、AI FAB、Markdown/tasks/AI 抽屉、Capture/执行方式/Sprint 弹窗 |
| 文档接口 | implemented | `src/backend/app/api/v1/requirement_center.py` 新增 Markdown JSON 读取与 HTML 预览接口 |
| API 字段 | implemented | `RequirementCenterIssue` 新增 `document_entries`、`detail_url`、`archive_url`、`action`、`tasks`；context 新增 `sprint_options` |
| 安全边界 | implemented | 文档读取限制在 issue 目录内，文件名禁止路径穿越，仅允许 `.md` / `.html`，错误响应脱敏 |
| Mock/API 边界 | documented | 默认看板 issue/workspace/user/document/action/tasks/sprint options 来自 API；仅显式 `?mock=workflow` / `?demo=workflow` 使用前端内置语义化 `DEMO-` 验收矩阵卡片、Markdown 正文和 HTML Blob 预览覆盖 9 阶段视觉验收；浏览器内 Slash Command 执行为可审计前端反馈模拟，不直接执行本机命令 |
| 主动作门禁 | implemented | `action.disabled_reason` 按阶段检查必需文档存在且内容非空：采集池为 `capture.md` + `trace.md`；规划中按类型补充 `requirement.md` 或 `bug.md`；待评审需求为 `capture.md` + `trace.md` + `requirement.md` + `acceptance.md` + `business-flow.md` + `user-stories.md`，待评审 Bug 为 `capture.md` + `trace.md` + `bug.md` + `root-cause.md` + `workaround.md` + `acceptance.md`；已评审在对应待评审文档包基础上要求 `review.md` |
| 缺失文档 Tips | implemented | `src/web/src/pages/catalog/RequirementCenterPage.tsx` 优先展示 `action.disabled_reason`，无后端原因时按 `requiredDocsForIssue(stage, type)` 兜底计算缺失文档，避免 Tips 与主动作禁用原因不一致 |
| workflow demo 矩阵 | implemented | `?mock=workflow` / `?demo=workflow` 使用 24 张语义化 `DEMO-` 卡片覆盖 9 阶段与已知验收场景；证据见 `evidence/20260901-workflow-demo-matrix/01-workflow-demo-matrix-1440.png` 和 `computed-workflow-demo-matrix-1440.json` |
| 待评审确认与 action 重算 | implemented | 待评审 Requirement / Bug 主动作点击先展示二次确认；确认成功后按目标阶段重算 action，已评审卡片展示“加入迭代 →”，命令映射 `/sprint-propose --req|--bug <ID>` 并进入 Sprint 选择；证据见 `evidence/20260902-review-confirmation-action-refresh/` |
| 验收中统一进度抽屉 | implemented | 验收中 Requirement / Bug 的研发、测试、人工验收进度均为可点击入口；右侧抽屉同时展示研发任务、自动化测试、人工验收三类进度，并按点击来源高亮；证据见 `evidence/20260903-unified-progress-drawer/` |
| 验收中进度区视觉与人工验收格式 | implemented | 卡片进度区默认呈现灰蓝色次级内联文本按钮，移除金色、加粗和 `10px` 等宽小字观感，并恢复点分隔；人工验收与研发、测试一致显示为 `已完成/总数`；证据见 `evidence/20260903-progress-muted-inline/` |

## 验证证据

| 命令 | 结果 |
|---|---|
| `pnpm --dir src/web exec vitest run src/requirement-center.test.tsx` | pass，37 tests |
| `uv run pytest tests/integration/api/test_requirement_center.py` | pass，9 tests |
| `pnpm --dir src/web exec vitest run src/requirement-center.test.tsx` | pass，38 tests，覆盖未入迭代阶段隐藏 Sprint 标签和筛选来源 |
| `uv run pytest tests/integration/api/test_requirement_center.py` | pass，10 tests，覆盖 `approved + target_iteration` 不输出 `sprint_id` |
| `pnpm --dir src/web exec vitest run src/requirement-center.test.tsx` | pass，38 tests，覆盖 Capture 轻量选择控件、标题 autofocus、必填 invalid 错误态和创建插入 |
| `Playwright chromium 1440x1000` | pass，生成 7 张视觉截图、5 份分状态 computed style JSON、1 份重叠检查摘要 |
| `corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx` | pass，54 tests，覆盖待评审二次确认、需求/Bug 已评审 action 重算和 Sprint 选择门禁 |
| `corepack pnpm@11.2.2 --dir src/web build` | pass，TypeScript build 与 Vite production build 通过 |
| `Playwright chromium 1440x1100` | pass，生成待评审确认弹窗、已评审 action 重算、Bug 加入迭代 Sprint 选择视觉证据 |
| `corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx` | pass，57 tests，覆盖验收中 Requirement / Bug 测试与人工验收进度入口打开统一右侧抽屉 |
| `corepack pnpm@11.2.2 --dir src/web build` | pass，TypeScript build 与 Vite production build 通过 |
| `Playwright chromium 1440x1100` | pass，生成验收中测试进度、人工验收进度打开右侧统一进度抽屉视觉证据 |
| `corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx` | pass，57 tests，覆盖进度区灰蓝次级内联文本、点分隔和人工验收 `x/x` 格式 |
| `corepack pnpm@11.2.2 --dir src/web build` | pass，TypeScript build 与 Vite production build 通过 |
| `Playwright chromium 1440x1100` | pass，生成验收中灰蓝次级进度区视觉与 computed style 证据 |

## 验收返修记录

| 项 | 内容 |
|---|---|
| 反馈 | 采集池、规划中、待评审、已评审尚未纳入迭代，不应显示 Sprint 标签，也不应进入 Sprint 筛选来源 |
| 根因证据 | 后端无条件派生 `sprint_id`；前端无条件渲染 `.rc-sprint-tag` 并从所有 `issue.sprintId` 汇总筛选项 |
| 调整 | 后端按阶段过滤可展示 `sprint_id`；前端 `visibleSprintId` 统一控制标签、筛选项和筛选匹配 |
| 文档 | 同步 Change `design.md`、spec delta、linked REQ `requirement.md` 与 `acceptance.md` |

| 项 | 内容 |
|---|---|
| 反馈 | Capture 弹窗字段分割线和纵向留白偏重，标题必填表达割裂，类型/优先级下拉不够轻量，取消/创建按钮风格不统一 |
| 根因证据 | 用户截图显示字段间多条分割线、独立 `*` 行、下拉控件和默认样式取消按钮；当前实现使用 select 和通用 `.rc-flow-dialog` 样式 |
| 调整 | 增加 `.rc-capture-dialog` 紧凑变体；类型和优先级改为 button group；标题输入 autofocus；校验失败设置 `aria-invalid` 与 invalid class；取消按钮改为统一次级按钮 |
| 文档 | 同步 Change `design.md`、spec delta、linked REQ `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md`、`prototype/**` 无需更新 |

| 项 | 内容 |
|---|---|
| 反馈 | 查看 Markdown 文档时右侧抽屉没有背景蒙层，不利于阅读；右侧抽屉希望可调整宽度；采集池 `capture.md` 需要支持编辑，`trace.md` 保持只读 |
| 根因证据 | 代码中抽屉直接渲染裸 `aside.rc-drawer`，无 backdrop layer；CSS 固定 `width: min(520px, 100vw)`，无拖拽状态；Markdown 内容以 `<pre>` 只读展示；后端仅提供 GET 文档读取/HTML 预览接口，无受控保存接口 |
| 调整 | 前端新增 `.rc-drawer-layer` 和 `.rc-drawer-backdrop` 蒙层、桌面 420px-760px 拖拽宽度、移动端全屏宽度、`capture.md` 编辑器、保存状态和未保存关闭确认；后端新增 `PUT /api/v1/requirement-center/issues/{issue_id}/documents/{document_name}`，仅允许采集池 `capture.md` 写入并阻断 `trace.md` 与非采集池阶段 |
| 文档 | 同步 Change `design.md`、spec delta、linked REQ `requirement.md` 与 `acceptance.md`、`docs/03-api-index.md` 和 Sprint 验收报告；`business-flow.md`、`user-stories.md`、`prototype/**` 无需更新 |

| 项 | 内容 |
|---|---|
| 反馈 | 采集池卡片只应展示 `capture.md` 和 `trace.md`；不应展示“研发 18/18”；需求探索/BUG探索辅助按钮缺失；Capture 弹窗必填星号仍未与标题同行且视觉仍偏重 |
| 根因证据 | 用户截图显示采集池历史文档与研发进度泄漏；代码中 `issueDocumentEntries(issue).map(...)` 无阶段裁剪、`issue.taskProgress` 无阶段守卫，`_stage_action` 只返回主生成动作；Capture 表单标签文本与 `*` 未使用稳定行内标签结构 |
| 调整 | 前端新增阶段可展示文档白名单、`visibleTaskProgress` 阶段守卫和采集池 `auxiliaryActions`；Capture 标题标签改为 `.rc-field-label` 行内结构，并继续压缩弹窗间距、弱化分割线与校验 ring |
| 文档 | 同步 Change `design.md`、spec delta、linked REQ `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md`、`prototype/**` 无需更新 |

| 项 | 内容 |
|---|---|
| 反馈 | 实现效果与原型存在视觉偏差：文档入口 chip 化、辅助动作在左侧且文案不一致、缺失提示和卡片留白偏重 |
| 根因证据 | 用户原型对照截图显示可用文档为金色文本链接并使用轻量分隔，主动作与“需求分析 / Bug 分析”位于 footer 右侧；当前实现截图显示文档为带图标 chip、辅助动作为左侧描边按钮 |
| 调整 | 文档入口去图标和 chip 样式，改为原型式金色文本链接；采集池辅助分析动作移入 footer 右侧，文案改为“需求分析 / Bug 分析”；缺失提示轻量化并压缩卡片间距 |
| 文档 | 同步 Change `design.md`、spec delta、linked REQ `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md`、`prototype/**` 无需更新 |

| 项 | 内容 |
|---|---|
| 反馈 | `capture.md` 与 `trace.md` 之间出现乱码分隔符；文档链接字重应与“缺失 capture.md、trace.md”提示一致；缺失提示与上方分割线间距偏高；footer 文字按钮不应加粗，主动作金色，需求分析/Bug 分析应为原型蓝灰色辅助动作 |
| 根因证据 | 代码中分隔符由 CSS 伪元素 `content` 生成，容易在截图/字体链路中呈现异常；`.rc-docs button` 与 `.rc-card-actions button` 使用 500 字重；`.rc-card footer button` 的通用金色规则覆盖了 `.secondary` 辅助动作颜色；缺失提示使用独立块级间距 |
| 调整 | 文档入口改为显式 `.rc-doc-separator` 空格节点；文档链接、缺失提示和 footer 文字按钮统一轻量 400 字重；缺失提示 `margin-top` 压缩为 4px；`.secondary` 通过更具体选择器固定为蓝灰色，`.primary` 保持金色 |
| 文档 | 同步 Change `design.md`、spec delta、linked REQ `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md`、`prototype/**` 无需更新 |

## 二次验收视觉证据

| 状态 | 证据 |
|---|---|
| 采集池阶段文档裁剪与隐藏研发进度 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-capture-filter-actions/01-capture-card-filter-1440.png` |
| 采集池需求探索辅助动作与 AI 抽屉反馈 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-capture-filter-actions/02-capture-explore-ai-drawer-1440.png` |
| Capture 弹窗紧凑态 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-capture-filter-actions/03-capture-dialog-compact-1440.png` |
| Capture 标题校验态 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-capture-filter-actions/04-capture-validation-1440.png` |
| DOM / computed 摘要 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-capture-filter-actions/computed-capture-filter-actions-1440.json`；`visibleDocs=["capture.md","trace.md"]`，`hasTaskProgress=false`，辅助命令 `/req-explore REQ-0199`，标题 `aria-invalid=true` |

## 原型卡片视觉返修证据

| 状态 | 证据 |
|---|---|
| 采集池卡片文档文本链接、footer 动作与轻量缺失提示 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-prototype-card-visual/01-capture-cards-prototype-actions-1440.png` |
| “需求分析”辅助动作进入 AI 抽屉反馈 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-prototype-card-visual/02-capture-analysis-ai-drawer-1440.png` |
| DOM / computed 摘要 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-prototype-card-visual/computed-prototype-card-visual-1440.json`；`reqDocs=["capture.md","trace.md"]`，footer 包含“生成需求”和“需求分析”，缺失提示为“缺失 capture.md、trace.md” |

## 卡片字体与分隔符返修证据

| 状态 | 证据 |
|---|---|
| 采集池卡片空格分隔、文档链接轻量字重、缺失提示紧凑间距和 footer 主次动作层级 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-card-typography-spacing/01-capture-card-typography-spacing-1440.png` |
| “需求分析”辅助动作进入 AI 抽屉反馈 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-card-typography-spacing/02-capture-analysis-secondary-action-1440.png` |
| DOM / computed 摘要 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-card-typography-spacing/computed-card-typography-spacing-1440.json`；`docs.textContent="capture.md trace.md"`，`docSeparator.textContent=" "`，文档链接和缺失提示 `fontWeight=400`，主动作金色，辅助动作蓝灰色 |

## Markdown 抽屉编辑返修证据

| 状态 | 证据 |
|---|---|
| Markdown 抽屉背景蒙层与采集池 `capture.md` 编辑态 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-markdown-drawer-edit/01-markdown-drawer-backdrop-edit-1440.png` |
| `capture.md` 保存成功反馈 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-markdown-drawer-edit/02-capture-save-success-1440.png` |
| 桌面抽屉拖拽宽度 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-markdown-drawer-edit/03-drawer-resized-1440.png` |
| `trace.md` 只读态 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-markdown-drawer-edit/04-trace-readonly-1440.png` |
| DOM / computed 摘要 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-markdown-drawer-edit/computed-markdown-drawer-edit-1440.json`；backdrop `background=rgba(5, 7, 18, 0.58)`，drawer `minWidth=420px` / `maxWidth=760px`，拖拽后 `width≈682px`，`trace.md` badge 为“只读文档” |

## capture.md 默认预览返修证据

| 状态 | 证据 |
|---|---|
| `capture.md` 默认预览态，有“编辑”按钮且无编辑器 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-capture-preview-edit/01-capture-md-preview-default-1440.png` |
| 点击“编辑”后进入受控编辑态 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-capture-preview-edit/02-capture-md-edit-mode-1440.png` |
| 保存成功后回到预览态并回显最新内容 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-capture-preview-edit/03-capture-md-save-back-preview-1440.png` |
| `trace.md` 只读且无编辑按钮 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-capture-preview-edit/04-trace-md-readonly-1440.png` |
| DOM / computed 摘要 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-capture-preview-edit/computed-capture-preview-edit-1440.json`；`previewBefore.hasTextarea=false`，`editMode.hasTextarea=true`，`afterSave.headerBadge="预览 capture.md"`，`trace.hasEditButton=false` |

## workflow demo 模式返修证据

| 状态 | 证据 |
|---|---|
| `?mock=workflow` 下 9 阶段均有 demo 卡片 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260830-workflow-demo-mode/01-workflow-demo-9-stage-1440.png` |
| demo 模式 Bug 筛选仍保留 9 阶段且展示 Bug demo 状态 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260830-workflow-demo-mode/02-workflow-demo-bug-filter-1440.png` |
| DOM / computed 摘要 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260830-workflow-demo-mode/computed-workflow-demo-mode-1440.json`；`stageCounts` 每列均大于 0，`defaultMode.fetchCalled=true`，`mockMode.fetchCalled=false` |

## workflow demo 文档内容返修证据

| 状态 | 证据 |
|---|---|
| demo Markdown 抽屉展示阶段匹配 mock 正文且不请求真实文档 API | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260830-workflow-demo-documents/01-demo-markdown-document-1440.png` |
| demo HTML 入口通过 Blob 新 Tab 打开受控预览 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260830-workflow-demo-documents/02-demo-html-preview-1440.png` |
| 默认真实模式仍通过真实文档 API 读取 Markdown | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260830-workflow-demo-documents/03-default-real-document-api-1440.png` |
| DOM / computed 摘要 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260830-workflow-demo-documents/computed-workflow-demo-documents-1440.json`；`mockMode.documentApiCalls=0`，`mockMode.htmlUrl` 使用 `blob:`，`defaultMode.documentApiCalls=1` |

## 采集池 footer 动作顺序返修证据

| 状态 | 证据 |
|---|---|
| 采集池 Requirement footer 中“需求分析”位于“生成需求”左侧 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260901-capture-action-order/01-capture-action-order-1440.png` |
| DOM / computed 摘要 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260901-capture-action-order/computed-capture-action-order-1440.json`；`reqOrder=["需求分析","生成需求"]`，`bugOrder=["Bug 分析","生成 Bug"]` |

## 待补证

- 无。1440px 视觉验收、computed style 和 REQ 最终一致性检查已补齐。

## 1440px 视觉验收

| 状态 | 证据 |
|---|---|
| 首屏 9 阶段看板 | `data/visual-evidence/REQ-0020-requirement-center-card-document-actions-ai-chat/01-board-1440.png` |
| Capture 弹窗 | `data/visual-evidence/REQ-0020-requirement-center-card-document-actions-ai-chat/02-capture-dialog-1440.png` |
| Capture 标题校验态 | `data/visual-evidence/REQ-0020-requirement-center-card-document-actions-ai-chat/03-capture-validation-1440.png` |
| Markdown 右侧抽屉 | `data/visual-evidence/REQ-0020-requirement-center-card-document-actions-ai-chat/04-markdown-drawer-1440.png` |
| AI 聊天右侧抽屉 | `data/visual-evidence/REQ-0020-requirement-center-card-document-actions-ai-chat/05-ai-chat-drawer-1440.png` |
| tasks 只读进度抽屉 | `data/visual-evidence/REQ-0020-requirement-center-card-document-actions-ai-chat/06-tasks-drawer-1440.png` |
| 创建成功 toast | `data/visual-evidence/REQ-0020-requirement-center-card-document-actions-ai-chat/07-toast-success-1440.png` |
| 重叠检查 | `data/visual-evidence/REQ-0020-requirement-center-card-document-actions-ai-chat/visual-check-summary.json`，`overlapWarnings=[]`，9 列、5 张卡片、AI FAB 存在 |

## Computed Style 验收

| 对象 | 证据 | 摘要 |
|---|---|---|
| 看板、列头、卡片标题、文档入口、阶段按钮、AI FAB | `data/visual-evidence/REQ-0020-requirement-center-card-document-actions-ai-chat/computed-board-1440.json` | 9 列 grid、列头 sticky、AI FAB `position=fixed`、`right=22px`、`bottom=22px`、`z-index=65` |
| Capture 弹窗与错误态 | `data/visual-evidence/REQ-0020-requirement-center-card-document-actions-ai-chat/computed-capture-1440.json` | 弹窗 `width=560px`、`border-radius=8px`；类型/优先级选择控件 `display=grid`；标题错误态 `borderColor=rgb(212, 116, 118)` |
| Markdown 抽屉 | `data/visual-evidence/REQ-0020-requirement-center-card-document-actions-ai-chat/computed-markdown-drawer-1440.json` | 右侧抽屉 `width=520px`、`height=1000px`、`position=fixed`、`right=0px`、`z-index=70` |
| AI 聊天抽屉 | `data/visual-evidence/REQ-0020-requirement-center-card-document-actions-ai-chat/computed-ai-drawer-1440.json` | 聊天抽屉与输入区可滚动、输入框和发送按钮维持固定布局 |
| tasks 抽屉 | `data/visual-evidence/REQ-0020-requirement-center-card-document-actions-ai-chat/computed-tasks-drawer-1440.json` | 只读任务进度区在右侧抽屉内展示，阻塞提示不溢出 |

## REQ 最终一致性检查

| 文档 | 结论 |
|---|---|
| `requirement.md` | 已包含 Capture 表单、文档入口、AI 聊天、阶段动作、Sprint 标签语义、tasks 抽屉和安全边界要求 |
| `acceptance.md` | 已包含 AC-001A、AC-017A、AC-PROTOTYPE 和最终视觉验收要求 |
| `trace.md` | Workflow Sync 维护状态，Change trace 已记录实现、返修、视觉证据和 Mock/API 边界 |
| `business-flow.md` | 无需更新；最终实现未改变业务状态流转 |
| `user-stories.md` | 无需更新；最终实现未改变角色目标和主路径 |
| `prototype/**` | 无需更新；原型作为初始结构事实源，后续截图反馈已在 Change 返修记录和视觉证据中覆盖 |

## Next

`/opsx-archive REQ-0020-requirement-center-card-document-actions-ai-chat`

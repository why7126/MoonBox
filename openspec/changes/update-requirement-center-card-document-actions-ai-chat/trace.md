---
change_id: update-requirement-center-card-document-actions-ai-chat
status: in_progress
type: update
source_requirement: REQ-0020-requirement-center-card-document-actions-ai-chat
sprint: sprint-003
created_at: 2026-08-18 09:58:34
updated_at: 2026-08-18 13:17:12
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
| Mock/API 边界 | documented | 看板 issue/workspace/user/document/action/tasks/sprint options 来自 API；浏览器内 Slash Command 执行为可审计前端反馈模拟，不直接执行本机命令 |

## 验证证据

| 命令 | 结果 |
|---|---|
| `pnpm --dir src/web exec vitest run src/requirement-center.test.tsx` | pass，37 tests |
| `uv run pytest tests/integration/api/test_requirement_center.py` | pass，9 tests |
| `pnpm --dir src/web exec vitest run src/requirement-center.test.tsx` | pass，38 tests，覆盖未入迭代阶段隐藏 Sprint 标签和筛选来源 |
| `uv run pytest tests/integration/api/test_requirement_center.py` | pass，10 tests，覆盖 `approved + target_iteration` 不输出 `sprint_id` |
| `pnpm --dir src/web exec vitest run src/requirement-center.test.tsx` | pass，38 tests，覆盖 Capture 轻量选择控件、标题 autofocus、必填 invalid 错误态和创建插入 |
| `Playwright chromium 1440x1000` | pass，生成 7 张视觉截图、5 份分状态 computed style JSON、1 份重叠检查摘要 |

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

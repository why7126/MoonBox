---
requirement_id: REQ-0036-requirement-center-document-drawer-simplification
title: 需求中心文档抽屉简化与 Change 属性模块移除 - 验收标准
acceptance_status: passed
created_at: 2026-09-15 23:11:38
updated_at: 2026-09-29 14:44:19
owner: product
source: requirement.md
---

# 需求中心文档抽屉简化与 Change 属性模块移除 - 验收标准

## 功能 AC

- [ ] AC-001 文档抽屉在 REQ、BUG 和独立 Change 场景下均不显示“Change 追溯属性”模块，包括标题、边框、左侧色条、任务进度、告警分隔符、关联 Change 列表和 Change 文档按钮。
- [ ] AC-002 删除模块后，文档属性直接位于正文之前；展开/收起、键盘焦点、滚动、关闭和全屏或展开状态正常。
- [ ] AC-003 删除模块后没有空白占位、残留边框、重复分隔线、贴边文本或正文顶部断层。
- [ ] AC-004 单个关联 Change 的 REQ/BUG 仍能从抽屉外紧凑入口打开该 Change 的 proposal、design、tasks 和 trace 等可读文档，卡片不展开完整 Change ID；与 Issue 自身文档合并时按文件名和语义去重。
- [ ] AC-005 多个关联 Change 的 REQ/BUG 能通过直接紧凑文档入口逐个辨认并打开各自 trace；`proposal.md`、`spec.md`、`design.md`、`tasks.md`、`sprint.md` 不重复出现；不得默认选择第一个 Change，不得把多个 Change 的任务进度汇总成单个 Change。
- [ ] AC-006 独立 Change 的文档入口继续可用；缺失文档、只读、编辑、脏数据保护和加载失败提示不回归。
- [ ] AC-007 Issue trace 与 Change trace 在入口标签或上下文中可区分，用户不会因模块删除而打开错误 trace。
- [ ] AC-008 无权对象、只读成员、冻结空间、跨项目同 ID 和直接文档 URL 回归通过；删除 UI 模块不能放宽授权或泄露受限内容。
- [ ] AC-009 既有需求中心卡片、筛选、搜索、刷新、阶段按钮和文档按钮行为不因抽屉模块删除而退化。

## 原型驱动 UI AC

- [ ] AC-PROTOTYPE-001 原型拆解完成，包含页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
- [ ] AC-PROTOTYPE-002 UI Skeleton 在后续 Change 设计中先行确认，至少覆盖抽屉标题区、文档属性区、正文区、加载态、错误态和多 Change 入口承接位置。
- [ ] AC-PROTOTYPE-003 1440px 桌面视口完成视觉验收，验证抽屉顶部间距、边框、圆角、滚动、深浅主题、长标题、长 ID 和长正文不溢出。
- [ ] AC-PROTOTYPE-004 窄视口完成关键交互验收，验证文档属性折叠、正文阅读、关闭/展开和抽屉外紧凑 Change 文档入口仍可操作。
- [ ] AC-PROTOTYPE-005 实施完成前执行 REQ 最终一致性检查，确认 requirement、user-stories、business-flow、acceptance、trace 与实际 Change 设计和验证证据一致。

## 横切 AC（knowledge-base）

本 REQ 不命中 `admin-list`、`admin-form`、`admin-modal` 或 `media-upload` 标签；无需写入管理后台列表、表单、弹窗或上传类横切 AC。

## 验收证据要求

- 需要提供 1440px 与窄视口截图。
- 需要覆盖深浅主题。
- 需要记录关键 computed style 或等价检查：文档属性区 `padding`、`border`、`gap`、`font-size`、`line-height`、正文顶部间距、抽屉滚动容器 `overflow`。
- 需要说明浏览器证据是部署观察、真实组件合成 API 观察，还是单元测试/组件测试；不得混淆证据层级。

## 实施验证记录

- 2026-09-15 23:44:29 `/opsx-apply`：已删除需求中心 Markdown 抽屉内“Change 追溯属性”模块；抽屉只保留标题区、文档属性区、正文阅读/编辑区。
- 抽屉外入口：卡片直接显示紧凑文档入口进入目标文档；`proposal.md`、`spec.md`、`design.md`、`tasks.md`、`sprint.md` 按文件名和语义去重不重复出现，Change trace 以 `Change 1 Change trace.md`、`Change 2 Change trace.md` 等短文案进入目标 Change 文档；多 Change 不默认选择第一项，不汇总多个 Change 任务进度。
- 视觉证据：`openspec/archive/2026-09-17-remove-requirement-center-document-drawer-change-attributes/evidence/ui/`，包含 1440px 深/浅主题、390px 窄视口、REQ 文档、关联 Change 文档和独立 Change 文档截图，并复验同名文档入口去重。
- computed style：`openspec/archive/2026-09-17-remove-requirement-center-document-drawer-change-attributes/evidence/ui/computed-style.json`，记录文档属性区与滚动容器样式，`changeModuleCount=0`。
- 自动化验证：`cd src/web && ./node_modules/.bin/vitest run src/requirement-center.test.tsx` 通过 106 tests；`cd src/web && ./node_modules/.bin/tsc -b` 通过。
- 数据边界：synthetic API + 真实 Web bundle 验证；未新增 API、DB、OpenAPI、Orval、请求封装、埋点或对象存储变更。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-29 14:44:19
accepted_by: workflow-sync
source_change: remove-requirement-center-document-drawer-change-attributes
source_sprint: sprint-007
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```


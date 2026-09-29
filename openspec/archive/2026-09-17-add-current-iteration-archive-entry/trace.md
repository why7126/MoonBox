---
change_id: add-current-iteration-archive-entry
source: req-opsx
source_requirement: REQ-0037-current-iteration-archive-entry
sprint: sprint-007
status: applied
created_at: 2026-09-15 00:00:00
updated_at: 2026-09-15 09:33:51
acceptance_refs:
  - acceptance-fixes.md
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
    - task_traces
    - task_trace_spans
  reason: 当前迭代归档入口是 Web 端触发的高风险多步骤 Sprint archive 写操作，涉及入口点击、权限拒绝、readiness 门禁、归档执行请求和 Workflow Sync 结果刷新。
  validation: 实施阶段验证行为事件、请求日志、Task Trace 或复用链路能覆盖入口点击、确认取消、门禁失败、权限拒绝、归档成功和 Workflow Sync 失败，并确认不记录完整文档正文、本机路径、Authorization、Cookie、密钥、真实 .env 或未脱敏错误堆栈。
execution:
  schema_version: 1
  started_at: 2026-09-15 00:20:09
  completed_at: 2026-09-15 00:43:06
  last_event: opsx.modify
---

# Trace

## 来源

- REQ: `REQ-0037-current-iteration-archive-entry`
- Sprint: `sprint-007`
- 命令: `/req-opsx REQ-0037-current-iteration-archive-entry`

## Requirement Readiness Report

- 状态: ready
- REQ 状态: `in_sprint`
- 六件套: requirement、user-stories、business-flow、acceptance、trace、prototype 已存在
- Prototype gate: 已有 `prototype_refs`、`prototype_gate`、`AC-PROTOTYPE-*`，需要在 apply 阶段完成 1440px 与 computed style 证据

## 影响分析

```yaml
impact:
  backend: true
  web: true
  miniapp: false
  admin: false
  database: false
  storage: false
  api: true
capabilities:
  new: []
  modified:
    - web-catalog-requirement-center
    - web-catalog-requirement-center-real-data
```

## 冲突处理

- `used_capacity > 0` 只作为归档入口候选条件，最终入口启用状态必须基于 Sprint archive readiness 汇总。
- 前端 readiness 与后端 Sprint archive 执行结果冲突时，以后端/治理命令最终门禁为准。
- `prototype.html` 是 UI 设计输入，最终验收以 Change design、acceptance、1440px/关键交互视觉证据、computed style、Mock/API 边界和 REQ 最终一致性回填共同为准。

## UI 合同与骨架状态

| 项 | 状态 | 说明 |
|---|---|---|
| UI Contract | proposed | 已写入 design.md，覆盖事实源、入口、视觉 token、权限、Mock/API 边界和一致性参照 |
| UI Skeleton | done | 已落地容量条入口、确认弹窗、门禁 checklist、取消和确认 selector |
| 1440px 视觉证据 | done | `/private/tmp/req0037-desktop.png`、`/private/tmp/req0037-desktop-dialog.png` |
| computed style | done | Playwright 1440px/390px 边界检查通过，入口、摘要与弹窗均在视口内；看板列体顶部 padding 与空列虚线框 top inset 收紧为 10px；归档长期证据已转存到 `evidence/` |
| Mock/API 边界 | done | workflow demo 仅作视觉夹具；生产 readiness 来自需求中心上下文，真实归档复用 `/sprint-archive` |
| 最终一致性 | done | `requirement.md`、`acceptance.md`、`trace.md`、`prototype/web/*` 与实现范围和复用边界一致 |

## 实现回填

- 后端：`RequirementCenterCurrentIterationCapacity.archive_readiness` 新增 Sprint archive readiness 投影，汇总 used_capacity、未归档 REQ/BUG/Change、验收 sign-off 与安全摘要。
- 前端：当前迭代容量条显示归档 icon-only 入口；状态 badge 保留在容量卡片右上角；readiness 长摘要只通过 hover/title 暴露。disabled 时不可进入确认；enabled 时进入 `ArchiveSprintConfirmDialog`，确认按钮仅引导 `/sprint-archive <sprint>`。
- 看板视觉：列头与首张卡片或空列虚线框之间的顶部留白从 20px 收紧到 10px，保持 9 列宽度、sticky 列头、卡片间距和阶段状态不变。
- API / OpenAPI：已刷新 `src/web/openapi.json` 与 Orval 生成类型；本机 `pnpm` Corepack 缓存缺失，脚本导出 OpenAPI 后使用本地 Orval 二进制完成客户端生成。
- DB：不新增 schema、索引或迁移。
- 观测复用边界：本 Change 不新增归档执行 API；归档执行请求日志、Task Trace、权限和 Workflow Sync 失败仍由 Sprint archive 既有链路承担。

## 验证证据

- `uv run pytest tests/integration/api/test_requirement_center.py`
- `./node_modules/.bin/vitest run src/requirement-center.test.tsx -t "workflow demo|current iteration|archive readiness"`
- `./node_modules/.bin/tsc -b --pretty false`
- `openspec validate add-current-iteration-archive-entry --strict`
- Playwright 视觉证据：`/private/tmp/req0037-desktop.png`、`/private/tmp/req0037-desktop-dialog.png`、`/private/tmp/req0037-mobile.png`、`/private/tmp/req0037-mobile-dialog.png`

## 验证记录

| 时间 | 验证项 | 结果 |
|---|---|---|
| 2026-09-15 09:33:51 | 需求中心交付验证来源入口 | pass；`acceptance_refs` 指向 `acceptance-fixes.md`，本节作为非空验证来源章节，避免卡片误报“未找到交付验证记录”。 |
| 2026-09-15 08:35:49 | 当前迭代归档入口实现与返修验证 | pass；详见 `## 验证证据`、`### 返修验证`、视觉证据和 `acceptance-fixes.md`。 |

## 验收返修回填

| 时间 | 事件 | 附件反馈 | 处理 | 证据 |
|---|---|---|---|---|
| 2026-09-15 08:35:49 | opsx.modify | CapacityItem 需按左侧 sprint id + 状态 badge、中间容量数值 + 进度条、右侧归档 icon button 三列呈现；归档 icon button 不要边框 | `rc-capacity-main` 改为身份/容量网格，`rc-capacity-item` 保持右侧操作列；状态 badge 进入左侧 meta 并通过 title 展示容量来源/说明；归档 icon button border 改为 0，title 保留归档或无法归档说明与 readiness safe_summary；390px 下改为安全堆叠 | `evidence/req0037-capacity-tricol-1440.png`、`evidence/req0037-capacity-tricol-390.png`；Playwright 断言桌面三列顺序、按钮无边框、状态 title 和归档 title |
| 2026-09-15 08:27:06 | opsx.modify | Image #1 红框标出看板列头与列体之间约 57px 空带；研发中卡片与验收中卡片起点观感不一致 | `.rc-column-body` 与 `.rc-column-body.empty` 顶部 padding 从 20px 收紧到 10px，空列虚线框 top inset 从 20px 收紧到 10px；不改变卡片、列头、列宽或业务流转 | `evidence/req0037-board-gap-1440-scrolled.png`、`evidence/req0037-board-gap-1440-scrolled-computed.json`；computed style 显示 `bodyPaddingTop: 10px`、`emptyBeforeTop: 10px`、`developmentGap: 16`；前端样式契约测试、TypeScript 与 OpenSpec strict 通过 |
| 2026-09-15 08:22:45 | opsx.modify | 当前迭代容量条右侧的“归档当前迭代”和 readiness 长摘要占用过多空间；需要保留原状态并将归档入口改为图标按钮 | `current-iteration-archive-action` 改为 34px `Archive` icon-only 按钮；状态 badge 固定在卡片右上角；readiness 长摘要移入 `title`/hover；390px 下移除桌面 flex-basis 空白 | `src/tmp/visual-evidence/req0037-modify-1440.png`、`src/tmp/visual-evidence/req0037-modify-390.png`；Playwright 断言按钮无可见文本、title 含安全摘要、状态右上对齐 |

### 返修验证

- `./node_modules/.bin/vitest run src/requirement-center.test.tsx -t "current iteration|archive readiness"`
- `./node_modules/.bin/vitest run src/requirement-center.test.tsx -t "board columns"`
- `./node_modules/.bin/tsc -b --pretty false`
- `openspec validate add-current-iteration-archive-entry --strict`
- Playwright 1440px 看板间距视觉断言：聚焦 9 列 DOM 夹具复用生产 `globals.css`，横向滚动到研发中/验收中列；computed style 显示 `bodyPaddingTop: 10px`、`emptyBeforeTop: 10px`、`developmentGap: 16`。
- Playwright 1440px/390px 三列布局视觉断言：桌面 meta、track、archive 从左到右排列；390px meta、track、archive 安全堆叠；归档按钮 34x34、border 为 0、可见文本为空；状态 badge title 含容量来源和说明；归档按钮 title 含 readiness safe_summary。
- Playwright 1440px/390px 视觉断言：按钮 34x34、可见文本为空、卡片常态不显示 readiness 长摘要、禁用态 title 含 “Sprint archive readiness 未通过”、状态 badge 与卡片右上角对齐。

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-09-15 08:35:49 | opsx.modify | 根据验收反馈将 CapacityItem 调整为桌面三列、移动端安全堆叠；状态 badge 进入左侧并提供容量来源/说明 title；归档 icon button 去除边框并保留 readiness title。 |
| 2026-09-15 09:33:51 | opsx.modify | 补齐需求中心可识别交付验证来源：`acceptance_refs` 指向 `acceptance-fixes.md`，并新增非空 `## 验证记录`。 |
| 2026-09-15 08:27:06 | opsx.modify | 根据附件红框反馈收紧看板列头到卡片/空列框的顶部留白；列体 padding-top 和空列框 top inset 调整为 10px，并补充 1440px 聚焦视觉证据。 |
| 2026-09-15 08:22:45 | opsx.modify | 根据验收反馈将容量条归档入口改为 icon-only，状态 badge 固定右上，readiness 长摘要改为 hover/title，并补充 1440px/390px 视觉证据。 |
| 2026-09-15 00:39:03 | opsx.apply | 实现当前迭代归档入口 readiness 投影、禁用/启用状态、确认弹窗、OpenAPI/Orval 同步和验证回填；等待 Workflow Sync 写入完成事实。 |
| 2026-09-15 00:00:00 | req.opsx | 创建 OpenSpec Change，生成 proposal、design、delta specs、tasks 和 trace。 |

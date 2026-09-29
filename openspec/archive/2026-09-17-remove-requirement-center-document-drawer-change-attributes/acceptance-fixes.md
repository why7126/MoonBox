---
change_id: remove-requirement-center-document-drawer-change-attributes
title: 需求中心文档抽屉移除 Change 属性模块 - 验收返修台账
status: applied
created_at: 2026-09-16 08:15:51
updated_at: 2026-09-16 08:45:49
source_requirement: REQ-0036-requirement-center-document-drawer-simplification
source_sprint: sprint-007
---

# 需求中心文档抽屉移除 Change 属性模块 - 验收返修台账

## 返修批次 R1：卡片关联 Change 文档入口紧凑化

| 字段 | 内容 |
|---|---|
| 验收反馈 | 卡片只保留紧凑文档入口，不在卡片上展开完整 Change ID；关联 Change 文档入口改为直接紧凑文档入口，并保留 Issue trace 与 Change trace 可区分。 |
| 范围判定 | 属于当前 Change 范围内的抽屉外入口承接方式调整；不新增 API、DB、权限、部署、对象存储或新业务能力。 |
| 证据状态 | confirmed；上一版卡片直接显示 `first-change / Change trace.md` 与 `second-change / Change trace.md`，不符合紧凑入口反馈。 |
| 偏差项 | 关联 Change 文档入口在卡片上展开完整 Change ID；卡片额外展示关联 Change ID 行，增加阅读噪音。 |
| 调整内容 | 移除卡片上的关联 Change ID 展开行；将关联 Change 文档收进卡片内直接紧凑文档入口；文档按钮直接显示为 `Change 1 Change trace.md` 等短文案，避免展开完整 Change ID。 |
| Issue trace / Change trace 区分 | Issue 自身文档入口仍显示 `trace.md`；关联 Change trace 直接显示 `Change 1 Change trace.md`、`Change 2 Change trace.md` 等短文案，打开抽屉后标题沿用同一短上下文。 |
| 验证 | `cd src/web && ./node_modules/.bin/vitest run src/requirement-center.test.tsx` 通过 106 tests；`cd src/web && ./node_modules/.bin/tsc -b` 通过；Playwright synthetic API + 真实 Web bundle 视觉验收通过并刷新 `evidence/ui/`。 |
| 证据入口 | `openspec/archive/2026-09-17-remove-requirement-center-document-drawer-change-attributes/evidence/ui/`、`openspec/archive/2026-09-17-remove-requirement-center-document-drawer-change-attributes/evidence/ui/computed-style.json`。 |


## 返修批次 R2：移除额外 Change 文档交互层

| 字段 | 内容 |
|---|---|
| 验收反馈 | 卡片移除额外的 Change 文档/更多交互层；仅保留现有紧凑文档入口，`tasks.md`、`spec.md`、`design.md`、`proposal.md` 等直接作为 Change 文档入口展示；不展开完整 Change ID，并保持 Issue trace 与 Change trace 通过短文案可区分。 |
| 范围判定 | 属于当前 Change 范围内的抽屉外入口承接方式进一步收敛；不新增 API、DB、权限、部署、对象存储或新业务能力。 |
| 证据状态 | confirmed；R1 的 `Change 文档` details 仍是额外交互层，而关联 Change 的 `tasks.md`、`spec.md` 等本身已是文档入口。 |
| 调整内容 | 删除 `Change 文档` / `更多` 交互层及对应样式；将关联 Change 的文档直接显示为卡片紧凑文档按钮，多 Change 使用 `Change 1`、`Change 2` 短前缀，不展示完整 Change ID。 |
| Issue trace / Change trace 区分 | Issue 自身文档入口仍显示 `trace.md`；关联 Change trace 直接显示为 `Change 1 Change trace.md`、`Change 2 Change trace.md`。 |
| 验证 | `cd src/web && ./node_modules/.bin/vitest run src/requirement-center.test.tsx` 通过 106 tests；`cd src/web && ./node_modules/.bin/tsc -b` 通过；Playwright synthetic API + 真实 Web bundle 视觉验收通过并刷新 `evidence/ui/`。 |


## 返修批次 R3：卡片文档入口语义去重

| 字段 | 内容 |
|---|---|
| 验收反馈 | Change 文档入口与 Issue 自身文档合并展示时出现重复，`spec.md`、`design.md`、`tasks.md`、`sprint.md`、`proposal.md` 等不应重复出现；同时保留 Change trace 与 Issue trace 的短文案区分。 |
| 范围判定 | 属于当前 Change 范围内的卡片文档入口呈现修正；不新增 API、DB、权限、部署、对象存储或新业务能力。 |
| 证据状态 | confirmed；用户截图显示同一卡片内 `tasks.md`、`spec.md`、`design.md`、`proposal.md`、`sprint.md` 重复出现，影响紧凑入口阅读。 |
| 偏差项 | Issue 自身文档与关联 Change 文档直接合并后，非 trace 的同名文档未做跨来源语义去重，导致卡片文档入口重复堆叠。 |
| 调整内容 | 为卡片文档入口增加跨来源语义 key：Issue 文档先占位，关联 Change 文档再追加；非 `trace.md` 文档按文件名去重，`proposal.md`、`spec.md`、`design.md`、`tasks.md`、`sprint.md` 只展示一次；Change 的 `trace.md` 按 Change ID 保留独立入口。 |
| Issue trace / Change trace 区分 | Issue 自身文档入口仍显示 `trace.md`；关联 Change trace 保留为 `Change 1 Change trace.md`、`Change 2 Change trace.md` 等短文案，不与 Issue trace 合并。 |
| 验证 | `cd src/web && ./node_modules/.bin/vitest run src/requirement-center.test.tsx` 通过 106 tests；`cd src/web && ./node_modules/.bin/tsc -b` 通过；Playwright synthetic API + 真实 Web bundle 视觉复验通过并刷新 `evidence/ui/`。 |
| 证据入口 | 前端测试新增同名 `proposal.md`、`spec.md`、`design.md`、`tasks.md`、`sprint.md` 去重断言；`evidence/ui/drawer-related-change-*`、`evidence/ui/computed-style.json`；用户截图作为本批次偏差输入。 |
| REQ 子文档一致性扫尾 | 已更新 `requirement.md`、`acceptance.md`、`prototype/web/context.md`；无需更新 `user-stories.md`、`business-flow.md`、`prototype/web/prototype.html`，原因是用户目标与流程未变，本次仅细化卡片文档入口合并规则。 |

## 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户文字反馈 R1/R2 | 需求中心卡片，REQ 关联多 Change，默认卡片态与直接文档入口打开态 | 上一版实现与当前反馈 | 卡片直接显示紧凑文档入口，不展示额外 `Change 文档` 或 `更多` 交互，不展开完整 Change ID | 上一版卡片直接展开完整 Change ID 文档按钮；返修后卡片直接显示 `Change 1 Change trace.md`、`Change 2 Change trace.md` 等短文档入口 | 信息过长、卡片噪音、Issue trace 与 Change trace 需明确区分 | Testing Library 断言 + Playwright 1440px/390px 截图 + computed style JSON | 已修复 | `evidence/ui/drawer-related-change-*`、`evidence/ui/computed-style.json` |
| 用户截图 R3 | 需求中心卡片，REQ-0036 关联 Change 文档与 Issue 文档合并展示 | 用户附件截图与当前实现 | `proposal.md`、`spec.md`、`design.md`、`tasks.md`、`sprint.md` 在卡片上只出现一次；Issue trace 与 Change trace 保持可区分 | 截图中 `proposal.md`、`spec.md`、`design.md`、`tasks.md`、`sprint.md` 重复出现 | 同名文档未跨来源语义去重 | Testing Library 断言同名文档只出现一次，Change trace 仍可分别打开 | 本次已修复 | `src/web/src/requirement-center.test.tsx` |

## REQ 子文档一致性扫尾检查

- 已更新 `requirement.md`：明确抽屉外入口应为紧凑文档入口，不在卡片上展开完整 Change ID，并在 Issue 文档与关联 Change 文档合并时按文件名和语义去重。
- 已更新 `acceptance.md`：AC-004、AC-005、AC-PROTOTYPE-004 和实施验证记录补充紧凑入口与同名文档去重要求。
- 已更新 `prototype/web/context.md`：多 Change 入口状态与交互触发补充直接紧凑入口和同名文档去重规则。
- 无需更新 `user-stories.md`：用户目标仍是能找到关联 Change 文档且不混淆 trace，未改变角色目标。
- 无需更新 `business-flow.md`：流程仍是抽屉外选择目标 Change 文档，未改变业务状态流。
- 无需更新 `prototype/web/prototype.html`：该原型用于抽屉结构证明，本次返修只细化卡片侧入口呈现；视觉证据已由 Playwright 截图承接。

## 文档未更新项与原因

- API、DB、部署、安全、对象存储、OpenAPI、Orval 和公共产品手册无需更新：本返修仅调整 Web 卡片内文档入口呈现和测试断言。

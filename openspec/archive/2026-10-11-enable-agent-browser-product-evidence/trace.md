---
title: Agent 浏览器自主取证治理追溯记录
change_id: enable-agent-browser-product-evidence
type: governance
status: applied
sprint: sprint-008
created_at: 2026-10-05 22:50:08
updated_at: 2026-10-06 01:02:52
owner: MoonBox 产品团队
---

# Agent 浏览器自主取证治理追溯记录

## 链路

- Change：`enable-agent-browser-product-evidence`
- Sprint：`sprint-008`
- 来源：`/spec-opt` 纯治理变更
- 状态：已完成治理规则落地并通过验证

## 验收返修

用户指出自主取证规则需覆盖 `.agents/skills/` 下全部技能。当前返修已补齐全部技能入口，并调整旧有人工补证顺序；完整偏差与验证见 [返修台账](acceptance-fixes.md)。

验收返修验证：46/46 技能覆盖；上下文预算校验、8 项聚焦单元测试、OpenSpec strict、当前 Change 中文与文档标题、目录结构、Sprint scope、聚焦 diff 均通过。目录结构仅有既有 legacy 数据目录迁移警告。返修完成后保持 Change `applied` 事实，用户可见阶段为验收中、待复验。

Workflow Sync `opsx.modify` 解析到 `sprint-008` 并通过；AI Usage Hook 因无可归属 token_count 返回 `usage_mode: unavailable`，属于非阻断 warning。

第二轮验收反馈：`bug-explore`、`bug-generate`、`bug-complete` 在根因未确认时需在当前命令继续自主补证。规则、技能与验证门禁已调整；证据和最终校验见 [返修台账](acceptance-fixes.md)。

第二轮验证：9 项聚焦单元测试、上下文预算与三技能补证门禁、OpenSpec strict、当前 Change 中文与文档标题、目录结构、Sprint scope、聚焦 diff 均通过。Change 保持 `applied` 事实，用户可见阶段为验收中、待复验。

第二轮 Workflow Sync `opsx.modify` 解析到 `sprint-008` 并通过；AI Usage Hook 因无可归属 token_count 返回 `usage_mode: unavailable`，非阻断。

第三轮验收反馈：`explore` 与 `req-explore` 在现状判断需要产品运行态证据时也应主动取证。已补齐两个探索入口与只读边界；完整偏差及验证记录见 [返修台账](acceptance-fixes.md)。

第三轮验证：10 项聚焦单元测试、上下文预算和两个探索技能取证门禁、OpenSpec strict、当前 Change 中文与文档标题、目录结构、Sprint scope、聚焦 diff 均通过。Change 保持 `applied` 事实，用户可见阶段为验收中、待复验。

第三轮 Workflow Sync `opsx.modify` 解析到 `sprint-008` 并通过；AI Usage Hook 因无可归属 token_count 返回 `usage_mode: unavailable`，非阻断。

## 验证记录

| 校验 | 结果 |
|---|---|
| Agent 上下文预算 | 通过，45 个命令技能均满足门禁 |
| 当前 Change 中文优先与文档标题 | 通过，无其他活动 Change 残留 |
| 目录结构 | 通过；既有 legacy 数据目录保留迁移警告 |
| OpenSpec validate | 通过 |
| sprint-008 scope | 通过，Change 已纳入 Sprint |
| 聚焦 diff whitespace | 通过 |

本次仅修改治理资产与 Sprint/Change 文档；业务测试不适用。仓库中原有 `src/` 未提交改动属于并行工作，本次未触碰。

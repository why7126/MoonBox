---
title: Agent 浏览器自主取证治理迭代
created_at: 2026-10-05 22:50:08
updated_at: 2026-10-06 01:02:52
owner: MoonBox 产品团队
---

# Agent 浏览器自主取证治理迭代

## 迭代目标

允许 Agent 在必要的测试、验收和 BUG 补证中自行访问产品取得证据，减少等待人工补证。

## 变更摘要

以根因证据规则为事实源，明确先自主取证、通常优先 Firefox、无需二次确认，以及敏感信息和高影响操作边界。

验收返修将该入口同步到全部 46 份技能，并修正原有直接转人工补证的指引。

第二轮验收返修明确 BUG 探索、文档生成和完善命令即使已产出结论或文档，根因未确认时仍在当前命令内继续自主补证；实际证据不足时保持非确认状态并说明缺口。

第三轮验收返修明确通用探索与需求探索在现状判断依赖产品表现且材料不足时，应在当前轮主动浏览取证；默认只读，无法取得证据时说明结论不确定性。

## 影响范围与更新文件

`AGENTS.md`、`rules/root-cause-evidence.md`、`rules/bug-management.md`、`rules/testing.md`、`rules/agent-context-budget.md`、`docs/README.md`、`docs/spec-logs/CHANGELOG.md`、全部 46 份技能、上下文预算校验脚本及聚焦测试、当前 OpenSpec Change 和 sprint-008。

## 验证结果

46/46 技能覆盖；上下文预算校验、8 项聚焦单元测试、OpenSpec strict、当前 Change 中文与文档标题、目录结构、Sprint scope 和聚焦 diff 均通过。目录结构有既有 legacy 数据目录迁移警告。详细结果见当前 Change `acceptance-fixes.md` 与 `trace.md`。

Workflow Sync `opsx.modify` 通过；AI Usage 因无可归属会话计数为 `unavailable`，非阻断。

第二轮返修新增三个 BUG 技能连续补证防回退测试；9 项聚焦单元测试、上下文预算、当前 Change 中文与标题、OpenSpec strict、目录结构、Sprint scope 与聚焦 diff 均通过。详细见 Change 返修台账。

第二轮 Workflow Sync 通过；AI Usage 无可归属会话计数，状态为 `unavailable`，非阻断。

第三轮返修新增两个探索技能主动取证防回退测试；10 项聚焦单元测试、上下文预算、当前 Change 中文与标题、OpenSpec strict、目录结构、Sprint scope 与聚焦 diff 均通过。详细见 Change 返修台账。

第三轮 Workflow Sync 通过；AI Usage 无可归属会话计数，状态为 `unavailable`，非阻断。

## 交付层影响

API、DB、Web、客户端、管理端、Orval、Docker Compose：均无运行时改动。

## 后续建议

无。

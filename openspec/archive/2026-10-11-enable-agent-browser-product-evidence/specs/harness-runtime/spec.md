---
title: Agent 浏览器自主取证规格增量
change_id: enable-agent-browser-product-evidence
capability: harness-runtime
---

# Agent 浏览器自主取证规格增量

## ADDED Requirements

### Requirement: Agent 浏览器自主取证

Agent 在测试、验收、BUG 补证和问题排查需要产品运行态证据时，SHALL 在已有权限与任务范围内直接通过浏览器取证，通常优先 Firefox，不要求用户二次确认。只有自主取证不可行或关键证据仍不足时，才请求人工补证并说明障碍。

项目 `.agents/skills/` 下的每份技能 SHALL 引用同一自主取证契约；技能中的任务特定补证步骤不得跳过可用的浏览器自主取证。

`bug-explore`、`bug-generate` 和 `bug-complete` 在根因未确认时 SHALL 于当前命令内继续聚焦自主补证；文档已生成不得视作停止条件。只有直接证据可复核并解释现象与触发条件时才能标记 `confirmed`，否则保留真实状态与证据缺口。

`explore` 与 `req-explore` 的结论依赖当前产品表现且现有材料不足时，Agent SHALL 在本轮通过已有权限的浏览器主动取证，同时遵守只读探索边界；无法取证时 SHALL 标明事实缺口与结论不确定性。

#### Scenario: 可直接访问产品并复现

- **WHEN** Agent 已具备访问目标产品的浏览器和授权会话
- **THEN** Agent 直接复现并记录脱敏的可复核证据

#### Scenario: 任一技能进入运行态取证环节

- **WHEN** Agent 执行 `.agents/skills/` 中任一技能且需要产品运行态证据
- **THEN** 该技能遵循浏览器自主取证契约，并只在自主取证不可行或证据仍不足时请求用户补证

#### Scenario: 自主取证不可行

- **WHEN** 环境不可用、权限不足或操作会造成未授权的高影响结果
- **THEN** Agent 保持根因未确认，说明已尝试路径并提出具体人工补证步骤

#### Scenario: BUG 文档生成后根因仍未确认

- **WHEN** `bug-generate` 或 `bug-complete` 已写入文档，但根因仍为 `unknown`、`hypothesis` 或 `probable`
- **THEN** Agent 在当前命令中继续尝试最小关键证据并回填对应文档
- **AND** 若证据仍不足，保持非确认状态并记录已尝试路径与具体缺口，不推进修复评审

#### Scenario: 探索结论依赖当前产品表现

- **WHEN** `explore` 或 `req-explore` 需判断既有页面、流程、交互、状态或权限，而现有材料不足
- **THEN** Agent 在当前探索中自主浏览产品并记录最小相关的脱敏证据
- **AND** 如无法取证，标明已尝试路径与结论不确定性，不把推测表述为现状事实

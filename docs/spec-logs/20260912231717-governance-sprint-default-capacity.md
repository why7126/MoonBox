---
purpose: Sprint默认容量与覆盖治理
created_at: '2026-09-12 23:17:17'
updated_at: '2026-09-12 23:17:17'
owner: MoonBox 产品团队
---

# Sprint 默认容量30人天

## 迭代目标

明确缺省容量30人天并保留显式覆盖，按用户授权纠正sprint-005。

## 变更摘要与影响范围

容量CLI缺省30、显式正数优先、非法值拒绝，覆盖原因可追溯；重新计算缓冲和120%门禁，拒绝超额写入。sprint-005从20改30，本治理Change为S=1人天，当前23/30人天，缓冲7人天（23.33%）低于建议30%。其他Sprint不批量覆盖，原日期和人员不变。

## 更新文件

- rules/iterations-lifecycle.md、rules/agent-context-budget.md、AGENTS.md。
- .agents/skills/sprint-propose/SKILL.md、docs/08-command-execution-order.md。
- scripts/add-sprint-scope-item.py、tests/unit/test_sprint_capacity_default.py。
- iterations/change/sprint-005/sprint.yaml与Workflow Sync派生四件套。
- openspec/changes/standardize-sprint-default-capacity/。

## 验证结果

5项聚焦容量测试通过；上下文预算、目录、目标OpenSpec与Sprint Scope通过。全局中文校验被既有fix-requirement-center-apply-lifecycle-sync英文标题影响；本Change另做聚焦校验，不修改无关Change。

## 业务边界

API、DB、Web、客户端、管理端、Orval、Docker Compose均无实现变化，不需要客户端生成或数据库迁移。product_data_collection_observability: not_applicable；affected_layers: 治理CLI与规划文档；原因：不改变业务日志、事件、Task Trace和请求封装；validation: 容量与派生一致性校验。

## 后续建议

默认值不替代显式容量，不自动调整归档Sprint；继续按真实范围计入工作量。未创建follow-up Issue/Change，本治理Change为用户本轮明确授权产物。

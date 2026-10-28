---
title: 探索技能持续改进试点治理记录
created_at: 2026-10-26 12:18:18
updated_at: 2026-10-26 12:18:18
---

# 探索技能持续改进试点治理记录

## 目标与变更
保留 explore 默认只读，补齐五类反馈、项目知识隔离、统一候选去重、维护交接、行为评测与版本生效。复用统一治理机制，无新增私有台账。
## 更新范围
`.agents/skills/explore/SKILL.md`、其 `evals/cases.md`、spec-opt Skill、AGENTS、上下文预算规则、治理反馈标准、docs 索引、scripts README、上下文校验脚本与 `scripts/test_explore_feedback_contract.py`。
## 验证结果
4项单元测试通过；上下文预算、目标Change中文与残留分离、中文标题、OpenSpec CLI、Sprint scope、目录校验通过。目录保留既有 legacy SQLite 警告。完整验收入口在 `openspec/changes/improve-explore-feedback-loop/trace.md`；真实模型对照尚未执行，效果待观察。
## 影响边界
API/DB/Web/客户端/管理端/Orval/Docker Compose/安全权限均无变更，不需要生成客户端或迁移。product_data_collection_observability: N/A；affected_layers: []；仅治理契约，不更改产品采集。
## 后续建议
在真实后续任务收集可比证据，按统一门禁确认收益；不为指标制造任务。当前保留未归档，不自动提交。


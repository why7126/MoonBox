---
purpose: OpenSpec Change Proposal
content: 应用 ProjectTilesFST spec-study 单报告去重规则
created_at: 2026-08-07 00:00:00
updated_at: 2026-08-07 00:00:00
owner: MoonBox 产品团队
---

# Proposal

## 背景

MoonBox 在 `/spec-study apply ProjectTilesFST --focus A、B、C、D、E` 后同时生成了正式 `study` 报告和内容高度重叠的 `governance` 日志。ProjectTilesFST 已沉淀 `avoid-duplicate-spec-study-reports` 治理规则，要求同一次 `/spec-study` 学习应用流程只维护一份正式 `study` 报告。

## 目标

- `/spec-study` 同一次学习应用流程只生成一份正式 `YYYYMMDDhhmmss-study-xxx.md`。
- 学习阶段候选内容和应用结果汇总到最终回复、active Change 文档或同一份 study 报告。
- 删除 MoonBox 当前同一流程下重复的 governance 日志，并在 study 报告中保留修正记录。

## 非目标

- 不修改业务 `src/`。
- 不改变 `/spec-opt` 独立治理变更生成 governance 日志的规则。
- 不同步 ProjectTilesFST 业务域内容。

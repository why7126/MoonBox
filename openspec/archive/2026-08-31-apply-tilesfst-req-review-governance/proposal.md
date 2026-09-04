---
change_id: apply-tilesfst-req-review-governance
change_type: governance
status: applied
created_at: 2026-08-31 08:36:34
updated_at: 2026-08-31 08:36:34
---

# Proposal: 应用 TilesFST req-review 治理学习

## 背景

本次 `/spec-study apply TilesFST --focus req-review --items A,B,C,D` 已确认应用 TilesFST 在 `req-review` 正向路径、目录迁移、当前态派生、Workflow Sync 和 AI Usage 收尾上的治理实践。

MoonBox 当前 `req-review` 技能仍将无 flag 调用定义为输出评审检查清单并询问，正向链路示例也继续使用 `--approve`。这与高频评审通过路径不够一致，且容易让下一步输出重复参数。

## 目标

- 将 `/req-review REQ-xxxx-slug` 定义为默认评审通过，`--approve` 仅作为兼容别名保留。
- 将 reject/defer 继续保留为显式反向结果。
- 同步 `.agents/skills/req-review/SKILL.md`、需求生命周期规则、Issue 阶段规则和命令顺序文档中的正向命令提示。
- 明确默认 approve 后仍需在 Workflow Sync 前执行目录迁移，并刷新当前态看板索引。
- 在 `req-review` 技能中显式补齐 AI Usage Post-command Hook 收尾。
- 生成单份 `spec-study` 学习报告，记录采纳、未采纳、影响范围、验证和学习对象只读保护。

## 非目标

- 不修改业务 `src/` 运行时代码。
- 不改变 REQ/BUG 的底层状态枚举。
- 不绕过评审检查清单、产品数据采集与链路观测声明或 Sprint 纳入门禁。
- 不自动创建新的 REQ/BUG。

## 影响范围

```yaml
impact:
  api: false
  database: false
  web: false
  admin: false
  miniapp: false
  orval: false
  docker_compose: false
  governance_assets: true
```

## 风险

- 默认 approve 会降低命令输入成本，但高风险或材料缺失需求仍必须由前置检查和评审清单阻断或转入引导式反馈。
- `sprint-003` 当前容量已高于 100%，本 Change 纳入后会进一步提高容量占用；因其为纯治理小项，按 S=1 记录并在 Sprint 风险中体现。

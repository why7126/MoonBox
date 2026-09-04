---
change_id: apply-tilesfst-sprint-md-governance
type: update
status: proposed
created_at: 2026-08-27 01:02:45
updated_at: 2026-08-27 01:02:45
---

# 应用 TilesFST sprint.md 治理学习成果

## 背景

`/spec-study TilesFST --focus sprint.md` 已完成第一阶段只读学习。ProjectTilesFST（本地只读项目）的 Sprint 文档以 `sprint.yaml` 为机器事实源，以 `sprint.md` 为产品化规划面板，并通过 Workflow Sync、Scope 校验、Fact Sheet 和归档 readiness 保持一致。

MoonBox 当前已有 Sprint scope 主表、workflow-sync 派生表和 `validate-sprint-scope.py`，但 `sprint.md` 的目标区仍偏总述，缺少目标编号列表与逐项要点；容量、里程碑、风险、知识库承接、横切预防清单等章节主要依赖 `/sprint-propose` 约束，还没有脚本化生成/校验到同等强度。

## 目标

- 在 Workflow Sync 刷新 `sprint.md` 时维护 `Sprint 目标编号列表` 与每个范围项的要点段落。
- 强化 `validate-sprint-scope.py`，校验目标编号列表、Scope 主表和 workflow-sync 派生表共同覆盖正式范围。
- 同步 `/sprint-propose`、`/sprint-apply`、`/sprint-archive`、`/sprint-exps` 与 `rules/iterations-lifecycle.md`，明确 `sprint.md` 的产品化规划面板结构和 Fact Sheet 读优先规则。
- 生成单份 `/spec-study` 学习报告，并登记到 `docs/spec-logs/CHANGELOG.md`。

## 非目标

- 不修改 `src/` 业务运行时代码。
- 不复制 ProjectTilesFST 的小程序、瓷砖、证书、SKU、媒体转码或业务专属 Sprint 内容。
- 不修改 `openspec/specs/` 正式规格。
- 不改变 Sprint 机器事实源仍以 `sprint.yaml` 为准的原则。

## 影响范围

```yaml
impact:
  backend: false
  web: false
  admin: false
  database: false
  api: false
  docker_compose: false
  governance: true
  sprint: true
  scripts: true
```

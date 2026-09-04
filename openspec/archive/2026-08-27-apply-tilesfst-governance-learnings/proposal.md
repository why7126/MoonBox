---
change_id: apply-tilesfst-governance-learnings
type: update
status: proposed
created_at: 2026-08-27 00:03:08
updated_at: 2026-08-27 00:03:08
---

# 应用 TilesFST 治理学习成果

## 背景

`/spec-study TilesFST` 已完成第一阶段只读学习，并确认四类可迁移治理能力：命令最终输出契约卫生、Sprint 选择与连续编号门禁、版本升级/回滚计划治理、AI Usage 矩阵 unknown 语义。

MoonBox 当前已有 `.agents/skills/`、OpenSpec、Sprint、Workflow Sync、发布镜像和 Mintlify 产品手册治理。本变更将 TilesFST 的治理经验改写为 MoonBox 语境下的规则、脚本、技能和学习报告，不复制学习对象业务专属内容。

## 目标

- 强化命令最终输出契约校验，减少尖括号占位模板、通用示例和规范语气泄漏到用户可见回复的风险。
- 新增 Sprint 选择门禁脚本，校验 active Sprint 数量、默认选择和连续编号。
- 新增版本升级/回滚计划命令入口与校验脚本，覆盖首次部署、相邻升级和跨版本人工复核。
- 优化 Sprint AI Usage 矩阵语义，区分未观测阶段与真实 `0`。
- 生成单份 `study` 学习报告，并登记到 `docs/spec-logs/CHANGELOG.md`。

## 非目标

- 不修改业务 `src/` 代码、API、数据库 schema、Web 或管理端运行时实现。
- 不恢复 `.claude/`、`.codex/`、`.cursor/`、`.kiro/`、`.opencode/` 等目录。
- 不自动执行生产升级、数据库 restore、对象存储写入维护或真实环境变量修改。
- 不复制 TilesFST 的小程序、瓷砖业务媒体治理或产品数据采集专属规则。
- 不修改 `openspec/specs/` 正式规格。

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
```

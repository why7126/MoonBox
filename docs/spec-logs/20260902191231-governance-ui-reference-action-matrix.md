---
purpose: UI 参考稿复刻动作按钮矩阵治理日志
content: 记录 UI 参考稿复刻中动作按钮、modal 类型、selector、状态和验收证据矩阵的治理优化
created_at: 2026-09-02 19:12:31
updated_at: 2026-09-02 19:12:31
owner: MoonBox 产品团队
---

# UI 参考稿复刻动作按钮矩阵治理日志

## 迭代目标

在 UI 参考稿复刻流程中前置“动作按钮 → modal 类型 → selector → 状态 → 验收证据”矩阵，并要求同一动作族一次性实现按钮与 modal 组件族，避免继续出现逐按钮问答返修。

## 变更摘要

- 新增动作按钮与 modal 组件族矩阵字段、适用条件和处置结论。
- 将矩阵接入 `req-complete`、`req-opsx`、`opsx-apply`、`opsx-modify`、`opsx-archive`。
- 强化 UI Reference Replication Gate：单按钮反馈先回扣所属动作族矩阵，再做组件族返修。
- 新增 OpenSpec `harness-runtime` delta，覆盖实现前矩阵、组件族一次性实现、返修回补和归档复核。

## 影响范围

- 入口：AI Agent 工作指南。
- 规则：UI 设计规则、Agent 上下文预算规则。
- 标准：原型驱动 UI 验收标准。
- 技能：REQ 完善、REQ 转 OpenSpec、OpenSpec apply/modify/archive。
- OpenSpec：`add-ui-reference-replication-governance`。

## 更新文件

- `AGENTS.md`
- `rules/ui-design.md`
- `rules/agent-context-budget.md`
- `docs/standards/prototype-ui-acceptance.md`
- `.agents/skills/req-complete/SKILL.md`
- `.agents/skills/req-opsx/SKILL.md`
- `.agents/skills/opsx-apply/SKILL.md`
- `.agents/skills/opsx-modify/SKILL.md`
- `.agents/skills/opsx-archive/SKILL.md`
- `openspec/changes/add-ui-reference-replication-governance/`
- `docs/spec-logs/CHANGELOG.md`

## 验证结果

已通过：上下文预算、OpenSpec 语言、目录结构、目标 Change、Sprint scope、Workflow Sync 和 AI Usage hook。Workflow Sync 更新 1 项、无错误；AI Usage hook 为 actual 模式，warning_count 为 0。

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

- API：N/A，未修改接口契约。
- DB：N/A，未修改 schema、迁移、索引或保留周期。
- Web：N/A，未修改运行时代码。
- 客户端生成 / Orval：N/A，未修改 OpenAPI 或生成配置。
- 管理端：N/A，未修改运行时代码。
- Docker Compose：N/A，未修改部署拓扑、端口或环境变量。

## 后续建议

后续可将动作按钮矩阵字段完整性接入 UI Contract 或 OpenSpec 文档校验脚本。

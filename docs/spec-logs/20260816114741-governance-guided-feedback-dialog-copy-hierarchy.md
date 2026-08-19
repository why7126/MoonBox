---
purpose: 治理迭代日志
content: 记录引导式反馈弹窗顶部说明层级约束
created_at: 2026-08-16 11:47:41
updated_at: 2026-08-16 11:47:41
owner: MoonBox 产品团队
---

# 引导式反馈弹窗顶部说明层级

## 迭代目标

补充原生交互卡片的顶部说明文案层级约束：同类弹窗顶部只保留一处主说明，避免“副标题 + hint”重复承载同一流程信息。

## 变更摘要

- 在上下文预算规则中补充交互卡片顶部说明只保留一处主说明。
- 在 `/spec-opt` Skill 的引导式反馈契约中补充同一约束。
- 新增 OpenSpec Change `add-guided-feedback-dialog-copy-hierarchy`，记录可归档的 harness-runtime delta。

## 影响范围

- Agent 命令输出契约。
- 原生交互卡片与文本降级输出的说明文案组织。
- 不影响业务 API、数据库、Web 页面运行时、客户端生成或部署。

## 更新文件

- `.agents/skills/spec-opt/SKILL.md`
- `rules/agent-context-budget.md`
- `openspec/changes/add-guided-feedback-dialog-copy-hierarchy/`
- `docs/spec-logs/20260816114741-governance-guided-feedback-dialog-copy-hierarchy.md`

## 验证结果

- 通过：`python scripts/validate-agent-context-budget.py`
- 通过：`python scripts/validate-openspec-language.py`
- 通过：`openspec validate add-guided-feedback-dialog-copy-hierarchy`
- 通过：`python scripts/validate-sprint-scope.py sprint-003 --item add-guided-feedback-dialog-copy-hierarchy`
- 通过：`python scripts/sync-workflow-status.py --event opsx.apply --change add-guided-feedback-dialog-copy-hierarchy --sprint auto`
- 通过：`python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change add-guided-feedback-dialog-copy-hierarchy --sprint sprint-003 --json`
- Warning：`python scripts/validate-directory-structure.py` 失败，原因是根目录存在既有未登记目录 `tmp`。

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

- API：不适用。
- DB：不适用。
- Web：不修改运行时页面，仅影响 Agent 命令交互文案治理。
- 客户端生成：不适用。
- 管理端：不适用。
- Orval：不适用。
- Docker Compose：不适用。

## 后续建议

后续如发现其他命令 Skill 复制了旧版反馈契约，可在独立治理变更中批量同步顶部说明层级约束与校验脚本覆盖。

---
purpose: 治理迭代日志
content: 记录 explore 命令原生交互卡片不可用时声明降级原因的规范补充
created_at: 2026-08-10 08:40:21
updated_at: 2026-08-10 08:40:21
owner: MoonBox 产品团队
---

# Explore 交互卡片降级原因声明

## 迭代目标

补齐 `/explore` 的交互降级透明度：当原生交互卡片不可用时，命令必须先声明降级原因，再输出文本结构化选项，避免用户误判为没有执行交互卡片优先规范。

## 变更摘要

- `/explore` Skill 明确：原生交互卡片不可用时必须先声明降级原因。
- `rules/agent-context-budget.md` 将“声明降级原因”纳入通用命令反馈契约。
- `standardize-guided-command-feedback` Change 的 design 和 tasks 同步返修。
- `scripts/validate-agent-context-budget.py` 将“声明降级原因”纳入引导式反馈契约校验。

## 影响范围

- 影响 `/explore` 以及复用通用反馈契约的命令输出规范。
- 不修改业务 `src/`、API、数据库、Web、客户端生成物、管理端或部署拓扑。

## 更新文件

- `.agents/skills/explore/SKILL.md`
- `rules/agent-context-budget.md`
- `openspec/changes/standardize-guided-command-feedback/design.md`
- `openspec/changes/standardize-guided-command-feedback/tasks.md`
- `scripts/validate-agent-context-budget.py`
- `docs/spec-logs/20260810084021-governance-explore-card-fallback-reason.md`

## 验证结果

- 通过：`python scripts/validate-agent-context-budget.py`
- 通过：`python scripts/validate-openspec-language.py`
- 通过：`python scripts/validate-directory-structure.py`
- 通过：`openspec validate standardize-guided-command-feedback`
- 通过：`python scripts/sync-workflow-status.py --event opsx.apply --change standardize-guided-command-feedback --sprint auto`
- 通过：`python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change standardize-guided-command-feedback --sprint sprint-002 --dry-run --json`

## API / DB / Web / 客户端 / 管理端 / Orval / Docker Compose 影响

- API：无影响。
- DB：无影响。
- Web：无业务 UI 实现影响。
- 客户端：无生成物更新；仅要求当前命令在卡片能力不可用时说明降级原因。
- 管理端：无影响。
- Orval：无影响。
- Docker Compose：无影响。

## 后续建议

- 若后续客户端提供原生选择卡片工具，应优先渲染卡片，不输出降级说明。
- 若当前运行环境不提供交互工具，统一使用短句说明降级原因，再输出文本结构化选项。

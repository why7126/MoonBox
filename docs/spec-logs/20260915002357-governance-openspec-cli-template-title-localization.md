---
purpose: OpenSpec CLI 模板标题中文化治理日志
content: 记录 req-opsx 与 bug-opsx 对 OpenSpec CLI template 英文标题的中文化契约和校验
created_at: 2026-09-15 00:23:57
updated_at: 2026-09-15 08:27:26
owner: MoonBox 产品团队
---

# OpenSpec CLI 模板标题中文化治理日志

## 迭代目标

减少 `/req-opsx` 和 `/bug-opsx` 生成 OpenSpec Change 后反复修正英文脚手架标题的成本，让 CLI template 结构可复用，但最终项目文档标题保持中文优先。

## 变更摘要

- `/req-opsx` 增加 OpenSpec CLI 模板标题中文化映射。
- `/bug-opsx` 增加同一类中文化映射。
- `scripts/validate-agent-context-budget.py` 增加契约片段检查，防止两个 opsx 技能回退。
- 同步 `AGENTS.md`、`rules/language.md`、`rules/agent-context-budget.md` 和目标 OpenSpec Change。

## 影响范围

- 技能命令：`req-opsx`、`bug-opsx`。
- 治理规则：语言规范、上下文预算、Agent 入口红线。
- OpenSpec：`agent-workflow-tooling` delta spec。
- 业务代码：不涉及。

## 更新文件

- `.agents/skills/req-opsx/SKILL.md`
- `.agents/skills/bug-opsx/SKILL.md`
- `scripts/validate-agent-context-budget.py`
- `AGENTS.md`
- `rules/language.md`
- `rules/agent-context-budget.md`
- `openspec/archive/2026-09-15-localize-openspec-cli-template-titles/`
- `iterations/change/sprint-006/`
- `docs/spec-logs/CHANGELOG.md`

## 验证结果

- 通过：`python scripts/validate-agent-context-budget.py`
- 通过：`python scripts/validate-openspec-language.py --change localize-openspec-cli-template-titles --residual-report`
- 通过：`openspec validate localize-openspec-cli-template-titles --strict`
- 通过：`python -m py_compile scripts/validate-agent-context-budget.py`
- 通过：`python scripts/validate-sprint-scope.py sprint-006 --item localize-openspec-cli-template-titles`
- 通过：`python scripts/sync-workflow-status.py --event opsx.apply --change localize-openspec-cli-template-titles --sprint auto`
- 通过：`bash scripts/archive-change.sh localize-openspec-cli-template-titles`
- 通过：`python scripts/validate-archive-evidence.py --change localize-openspec-cli-template-titles --archive-path openspec/archive/2026-09-15-localize-openspec-cli-template-titles`
- 通过：`python scripts/sync-workflow-status.py --event opsx.archive --change localize-openspec-cli-template-titles --sprint auto`
- 通过：`python scripts/promote-issues-for-archive.py --change localize-openspec-cli-template-titles --reason "/opsx-archive localize-openspec-cli-template-titles"`
- 通过：`openspec validate --all --strict`
- 通过：`python scripts/validate-directory-structure.py`
- Warning：AI Usage hook 未发现可归因 command-run token 事件，`usage_mode: unavailable`。
- 已解除：此前 `python scripts/validate-directory-structure.py` 因既有根目录 `.vite` 未登记失败；后续 `ignore-local-vite-cache-directory` 已完成治理归档，本 Change 归档收尾时目录结构校验通过。

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

不适用。本次只调整治理命令模板、校验脚本和文档规范，不改变运行时业务实现、接口契约、数据库 schema、前端页面、管理端、客户端生成、Orval 或 Docker Compose。

## 后续建议

观察后续 `/req-opsx` 和 `/bug-opsx` 生成的 Change 是否仍出现英文脚手架标题；若出现新的标题变体，再扩展标题映射或中文优先校验词表。

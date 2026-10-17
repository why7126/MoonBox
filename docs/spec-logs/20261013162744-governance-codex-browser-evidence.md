---
title: 产品取证浏览器优先级治理日志
created_at: 2026-10-13 16:27:44
updated_at: 2026-10-13 16:27:44
---
# 产品取证浏览器优先级治理日志

## 迭代目标

产品运行态取证优先使用 Codex 侧边浏览器，减少对用户 Firefox 会话的占用，同时保持证据完整性。

## 变更摘要与影响范围

统一调整 Agent 入口、根因证据规则、上下文预算规则和技能短契约。侧边浏览器无法取得本次所需证据时，使用其他已提供的浏览器或等价自动化工具，Firefox 作为后备。校验脚本改为检查侧边浏览器优先级。

## 更新文件

- `AGENTS.md`
- `rules/root-cause-evidence.md`、`rules/agent-context-budget.md`
- `.agents/skills/*/SKILL.md` 中涉及浏览器优先级的文案
- `scripts/validate-agent-context-budget.py`
- `openspec/changes/prefer-codex-browser-for-evidence/` 与 `iterations/change/sprint-008/sprint.yaml`

## 验证结果

上下文预算校验及 OpenSpec Change 校验通过；其余验证结果见 Change `trace.md`。

## 产品与部署影响

API、数据库、Web、客户端、管理端、Orval、Docker Compose 均无运行时变更。

## 后续建议

后续新增技能时沿用根因证据规则中的浏览器优先级，并继续分别记录页面展示与当前服务连通性。

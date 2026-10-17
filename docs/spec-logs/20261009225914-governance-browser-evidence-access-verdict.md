---
title: 浏览器取证失败重试与访问判定治理迭代日志
created_at: 2026-10-09 22:59:14
updated_at: 2026-10-09 23:07:27
owner: MoonBox 产品团队
---

# 浏览器取证失败重试与访问判定治理迭代日志

## 迭代目标

防止一次浏览器工具超时或终端连接失败被误判为产品无法访问。

## 变更摘要与影响范围

规定先检查现有浏览器窗口和标签页，清单失败后直接连接浏览器应用，再尝试可行替代入口；区分已加载页面展示、当前服务连通性和根因证据。人工补证前记录尝试路径及具体缺口。影响治理规则、技能和索引，不改变产品行为。

## 更新文件

`rules/root-cause-evidence.md`、`AGENTS.md`、`rules/agent-context-budget.md`、全部 47 份 `.agents/skills/*/SKILL.md`、`scripts/validate-agent-context-budget.py`、`tests/unit/test_validate_agent_context_budget.py`、`docs/README.md`、`openspec/changes/harden-browser-evidence-access-verdict/`、`iterations/change/sprint-009/sprint.yaml`。

## 验证结果

聚焦契约断言 7/7、Agent 上下文预算、当前 Change 中文优先、文档标题、目录结构、OpenSpec strict 与聚焦 diff whitespace 均通过；Workflow Sync `opsx.apply` 成功，`sprint-009` scope 复验通过。AI Usage 自动发现无可归属 token_count，为非阻断 warning。结果同时回填 Change `trace.md`。

## 横向影响

API、DB、Web、客户端、管理端、Orval 和 Docker Compose 均无运行时代码或配置变更；业务测试不适用。

## 后续建议

后续 BUG 补证以可复核的浏览器页面和请求证据验证规则执行效果；本次不自动创建 follow-up Issue。

## 覆盖范围返修

用户指出初次仅同步两个技能入口。现已覆盖全部 47 份浏览器自主取证技能，集中校验器检查每份技能的 `§5.0` 引用，并增加缺失引用反例测试。聚焦单元测试 11/11 通过，`opsx.modify` Workflow Sync 退出码 0；AI Usage 无可归属用量，属于非阻断 warning。完整复验结果见 Change 追溯记录。

---
title: 实现写权限修复阶段验证记录
created_at: 2026-10-07 16:55:05
updated_at: 2026-10-07 16:55:05
---

# 实现写权限修复阶段验证记录

## 已验证

命令：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src/backend DATABASE_URL=sqlite:///:memory: /usr/local/bin/python -m unittest discover -s src/backend/tests -p test_permission_governance_contract.py -v`。8 组测试通过；测试使用临时治理文件和隔离 SQLite，真实调用完整 write_policy，并验证既有事件存储/去重与 AppServer 请求 profile。REQ/BUG 别名组合通过，冲突、类型非法、来源/Sprint 不匹配、只读成员、缺失成员及非实现阶段没有获得实现权限。治理候选不被提升。

源码语法检查与目标 git diff --check 通过。根因和 Sprint 门禁通过，opsx.start 已同步。本次变更触达 policy.py、execution.py、app_server.py 及新增测试；保留工作区既有修改。

## 本轮隔离环境验证

- 在已有虚拟环境中从本机缓存补齐 pytest/httpx；SQLite 相关四组套件 73 passed、1 skipped，21 subtests passed。
- 一次性回环 MySQL 测试库运行 Chat 集成 45 passed、1 skipped，以及权限契约 8 passed、21 subtests passed。权限测试入口拒绝非回环、非 `_test` 数据库。
- 显式离线 Docker 探针 3 passed，覆盖容器工具链、profile 以及只读根目录、Git 和隔离挂载。
- 一次性仓库与数据库中，真实 Codex 容器执行 BUG-0029 字段形态 `bug_id/iteration` 的源码写入测试通过：`counter.txt` 从 `0` 变为 `1`，同一 turn 持久事件记录 `implementation_write`、`moonbox-write` selected/acknowledged profile。测试清理仓库和 runtime；这不是原部署的 BUG-0029 会话复验。
- `bash scripts/validate-openspec.sh --change fix-opsx-apply-governance-scope-source-readonly --residual-report` 通过；`python scripts/validate-sprint-scope.py sprint-008` 通过。原文档中的 `--sprint` 示例与脚本参数不一致，实际使用位置参数。

## 仍待部署复验

原产品部署未更新到本次代码，故不能宣称原 BUG-0029 会话或部署版本已通过 AC-009。请求确认事件代表执行器接收 profile；与真实容器源码写入共同构成测试环境证据，单独的请求确认不代表 OS 边界。历史 turn 缺失的 reason_code 不补造。

## 影响面

product_data_collection_observability: applicable；affected_layers: Agent Workflow、既有 Chat 事件；事件使用原 turn 关联 Task Trace，未新增 trace 表结构或 usage_events。API 路由/响应 schema、DB schema、UI、部署配置和客户端生成不变，N/A 原因是复用既有通用事件 payload；安全规则和观测/API 文档已同步。原部署复验待发布后执行。

补充红绿对照：从 Git HEAD 抽取旧 `_implementation_ready`，在同一隔离 SQLite 会话和同一 bug_id/iteration 输入下，完整 write_policy 旧实现为 governance_write，新实现为 implementation_write，断言通过；只在测试进程替换函数，不改工作区旧版本或数据库事实。

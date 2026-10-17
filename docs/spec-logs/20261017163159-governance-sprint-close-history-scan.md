---
title: Sprint 关闭扫描历史证据识别治理日志
created_at: 2026-10-17 16:31:59
updated_at: 2026-10-17 16:31:59
---

# Sprint 关闭扫描历史证据识别治理日志

## 迭代目标

让 Sprint 关闭扫描保留历史验收与排障证据，同时准确阻断结构化当前状态残留和失效归档证据链接。

## 变更摘要与影响范围

Issue 子文档扫描以主文档、trace、验收文档的结构化当前态字段为状态事实；历史正文不再按中间态词语触发阻塞。已归档 Change 的证据链接继续校验。同步 Sprint 归档技能和迭代生命周期规则，Change 纳入 sprint-009。

## 更新文件

- `scripts/sprint_close_stale_scan.py`、`tests/unit/test_sprint_close_stale_history.py`
- `rules/iterations-lifecycle.md`、`.agents/skills/sprint-archive/SKILL.md`
- `openspec/changes/fix-sprint-close-stale-history-scan/`、`iterations/change/sprint-009/`

## 验证结果

聚焦测试 4 项通过；sprint-008 关闭扫描 0 blocker、0 warning；归档就绪、中文优先、目录结构和 Change 校验通过。完整 pytest 入口因环境缺少 FastAPI 未运行。

## 产品与部署影响

API、数据库、Web、客户端、管理端、Orval、Docker Compose 均无运行时变更；安全边界不变。

## 后续建议

后续治理扫描优先读取结构化当前事实，对历史表格、轮次、样本和技术状态保留原始语义。

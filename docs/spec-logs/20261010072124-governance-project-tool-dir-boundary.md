---
title: 全仓自有目录工具路径边界治理记录
created_at: 2026-10-10 07:21:24
updated_at: 2026-10-10 07:33:22
---

# 全仓自有目录工具路径边界治理记录

## 迭代目标

承接 BUG-0026 AF-011，将空 `.agents`、`.codex` 残留治理从两个治理根扩展到仓库自有目录，同时保留根目录 `.agents` 技能入口。

## 变更摘要与影响范围

目录校验递归发现仓库自有目录中的工具路径；Chat worker 在写入型轮次前后清理确认无内容的宿主残留。沙箱运行期间只识别已配置写入根的精确空路径。非空目录、文件和符号链接保留并阻断；Git 元数据、虚拟环境、依赖、构建缓存和本地运行数据不自动清理。已安全移除八个已确认空目录。

更新文件：`AGENTS.md`、`rules/directory-structure.md`、`docs/README.md`、`scripts/runtime_tool_mounts.py`、`scripts/validate-directory-structure.py`、`src/backend/app/chat/execution.py`、聚焦测试、BUG-0026 文档、其 active Change 和 sprint-008 验收记录。

## 验证结果

工具路径单元测试 3 项、Chat 后端全套 48 passed/1 skipped、同款执行器镜像离线隔离探针 1 项通过。探针确认归档 profile 的 12 个执行时空路径，退出后宿主清理使其全部不存在。目录结构、Agent 上下文预算、OpenSpec strict、中文优先、Sprint Scope 与产品数据采集和链路观测聚焦校验通过。Workflow Sync `opsx.modify` 0 errors/0 blockers；AI Usage hook warning/unavailable。真实产品新轮次仍需单独观察，不以隔离探针替代。

## 跨层影响

API、DB、Web、管理端、客户端生成、Orval、Docker Compose 均无接口或部署拓扑变更。Chat worker 的宿主目录检查行为与治理校验行为发生变化；无新增产品数据采集、请求日志或 Task Trace 字段。

## 后续建议

在隔离 Chat 写入轮次和真实产品轮次分别观察宿主残留，确认新写入根目录不会再次留下空工具路径；通过后再评估 BUG-0026 的最终归档验收。

---
title: 统一主源码目录与交付链路工作区及模块化执行架构变更提案
created_at: '2026-10-29 06:49:00'
updated_at: '2026-10-29 06:49:00'
---

# 统一主源码目录与交付链路工作区及模块化执行架构变更提案

## 背景

现有 Chat 工作区身份与会话目录、source/copy 模式耦合。源码目录、治理投影与副本之间的版本关系增加执行和成果回写复杂度。用户确认以唯一主源码目录为默认执行入口，按交付链路使用 Git worktree 隔离并行任务，同时保留原需求的不可变环境版本、多空间隔离和诊断能力。此处依据此前静态代码分析，不声明当前线上已完成改造。

## 变更内容

落实 REQ-0042-agent-runtime-version-space-isolation 全部功能要求和验收项。BREAKING：停止新建会话 copy，旧数据保留并迁移，前端改为绑定 workspace_id；兼容窗口内旧输入受控映射。

## 能力影响

### 新增能力

- `unified-workspace-runtime`：统一主源码目录与交付链路工作区及模块化执行架构。

### 修改能力

- codex-session-execution：会话与工作区绑定、工作区级互斥。
- web-catalog-chat-workbench：默认主目录与按需 worktree，旧 copy 仅保留兼容。

## 影响范围

Web、后端执行/治理、API、数据库、部署挂载与安全权限；无移动端/桌面端或新 TUI。模块全部使用 moonbox- 前缀。接口变更同步 OpenAPI/Orval，数据库兼容 SQLite/MySQL。恢复点不替代数据库备份；合入不自动推送、发布或正式归档。

来源：`issues/requirements/review/REQ-0042-agent-runtime-version-space-isolation/requirement.md`、`issues/requirements/review/REQ-0042-agent-runtime-version-space-isolation/acceptance.md`。Sprint：sprint-015。当前仅设计，不写 src、不启动实现。

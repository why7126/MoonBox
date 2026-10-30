---
title: 工作区恢复点复用保留与冲突恢复变更提案
created_at: '2026-10-29 06:49:00'
updated_at: '2026-10-29 06:49:00'
---

# 工作区恢复点复用保留与冲突恢复变更提案

## 背景

多轮对话和多个会话共享工作区后，每条消息机械生成永久全量快照会增加扫描与存储成本；仅依赖 Git 又无法保护未提交成果。用户确认每轮保留历史、写入有可信基线、内容变化才生成版本，并以保护引用和有限中间版本实现恢复。复用已归档 REQ-0053 的分批内容存储能力，不重做其规模化执行。

## 变更内容

落实 REQ-0054-workspace-recovery-points 全部功能要求和验收项。新增受控业务操作，保留现有历史、权限和失败恢复边界。

## 能力影响

### 新增能力

- `workspace-recovery-points`：工作区恢复点复用保留与冲突恢复。

### 修改能力

- chat-scalable-storage：按授权写范围采集与恢复点复用，保留原规模化安全边界。

## 影响范围

Web、后端执行/治理、API、数据库、部署挂载与安全权限；无移动端/桌面端或新 TUI。模块全部使用 moonbox- 前缀。接口变更同步 OpenAPI/Orval，数据库兼容 SQLite/MySQL。恢复点不替代数据库备份；合入不自动推送、发布或正式归档。

来源：`issues/requirements/review/REQ-0054-workspace-recovery-points/requirement.md`、`issues/requirements/review/REQ-0054-workspace-recovery-points/acceptance.md`。Sprint：sprint-015。当前仅设计，不写 src、不启动实现。

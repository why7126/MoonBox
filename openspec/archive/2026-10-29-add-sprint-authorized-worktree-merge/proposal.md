---
title: 继承迭代操作权限的工作区成果确认合入变更提案
created_at: '2026-10-29 06:49:00'
updated_at: '2026-10-29 06:49:00'
---

# 继承迭代操作权限的工作区成果确认合入变更提案

## 背景

多 worktree 成果需要进入同一主线，单纯显示开发完成或仅凭 Agent 声明不足以证明可以交付。用户最终选择验收和候选合并验证通过后，由具有所属迭代操作权限的人确认，替换此前自动合入提议；系统随后完成受控合入与记录续接。

## 变更内容

落实 REQ-0055-sprint-authorized-worktree-merge 全部功能要求和验收项。新增受控业务操作，保留现有历史、权限和失败恢复边界。

## 能力影响

### 新增能力

- `sprint-authorized-worktree-merge`：继承迭代操作权限的工作区成果确认合入。

### 修改能力

无既有条款替换；新增合入业务能力，复用现有验收和治理流程。

## 影响范围

Web、后端执行/治理、API、数据库、部署挂载与安全权限；无移动端/桌面端或新 TUI。模块全部使用 moonbox- 前缀。接口变更同步 OpenAPI/Orval，数据库兼容 SQLite/MySQL。恢复点不替代数据库备份；合入不自动推送、发布或正式归档。

来源：`issues/requirements/review/REQ-0055-sprint-authorized-worktree-merge/requirement.md`、`issues/requirements/review/REQ-0055-sprint-authorized-worktree-merge/acceptance.md`。Sprint：sprint-015。当前仅设计，不写 src、不启动实现。

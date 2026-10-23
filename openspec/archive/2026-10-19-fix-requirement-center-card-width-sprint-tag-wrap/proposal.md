---
title: 需求中心九阶段卡片扩宽与迭代标签修复提案
created_at: "2026-10-19 09:31:29"
updated_at: "2026-10-19 09:31:29"
---

# 需求中心九阶段卡片扩宽与迭代标签修复提案

## 背景

[BUG-0043](../../../issues/bugs/review/BUG-0043-requirement-center-card-width-sprint-tag-wrap/bug.md) 已评审并纳入 sprint-010。九列固定 320px，长 Change ID 与 Sprint 同排时标签被挤压换行，影响扫描阅读。严重度 low，按正常迭代修复。

## 变更内容

- 九阶段共用列宽统一为 380px，卡片随列扩宽。
- Sprint 标签保持单行且不收缩；长 ID 在剩余空间合理换行。
- 保持横向滚动、阶段语义、字体、文档入口及动作行为，补充真实浏览器布局回归。

## 能力影响

### 新增能力

无。

### 修改能力

- web-catalog-requirement-center：补充生命周期看板的等宽列与标签布局约束。

## 影响范围

主要为 src/web/src/styles/globals.css 的共用看板和卡片样式，以及聚焦布局测试。无需 API、数据库、安全、部署配置或客户端生成变更。按 BUG 五项 AC 验证。

## 回滚方案

回退本 Change 的样式与配套测试改动，恢复原布局；无数据迁移。回退会恢复原标签换行缺陷，需重新记录验收状态。

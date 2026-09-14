---
created_at: 2026-09-12 17:38:39
updated_at: 2026-09-12 17:38:39
---

## 背景与动机

REQ 优先级与 BUG 严重度在 Capture、事实源和 Sprint 展示中混用，可能被旧主文档覆盖。

## 变更内容

- 统一 REQ priority、BUG severity 的 Frontmatter 范围与 trace 优先读取。
- 同步已有 capture、主文档和注册表，修正 Sprint BUG 表头。
- 兼容旧 hint 读取，缺失或非法值不自动猜测等级；不批量迁移历史归档。

## 能力范围

### 新增能力

- `issue-classification-metadata`: Issue 分级元数据归属及同步。

### 修改能力

无。

## 影响范围

仅治理规则、技能、文档及 Workflow Sync 脚本。不修改业务 src、API、DB、Web、管理端、Orval 或部署。

---
title: Issue 阶段同步修复设计
created_at: 2026-10-27 09:17:15
updated_at: 2026-10-27 09:17:15
---

# Issue 阶段同步修复设计

## 方案
以物理 plan/review/archive 目录为事实源，迁移准备时以目标目录为投影。只处理 trace.md、capture.md 和对应主文档中已有的 Frontmatter lifecycle_stage；缺失字段不扩散创建，未知值阻断自动修复。正文历史、其他语义 status、验收证据保持不变。

## 执行边界
共享纯函数生成阶段补丁；迁移预览展示补丁，日常同步投影，残留扫描检出阶段差异，reconcile 按字段修复避免触碰其他状态。已归档修复先预览。

## 取证与验证
旧版 BUG-0068 状态残留扫描返回零但主文档和 capture 阶段仍为 plan，trace 与 registry 为 archive。验证 REQ/BUG 各阶段、迁移、非法值阻断、正文保留、重复幂等和定向两字段修复。

## 采集声明
product_data_collection_observability: N/A
affected_layers: governance_scripts
validation: 脚本级隔离回归和静态门禁；不改变 API、DB、UI、部署、安全、客户端、Orval 或运行态数据采集。

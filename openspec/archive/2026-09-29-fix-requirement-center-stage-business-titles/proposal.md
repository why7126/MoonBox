---
title: 修复需求中心阶段业务标题并统一文档中文标题生成
created_at: '2026-09-15 23:04:19'
updated_at: '2026-09-15 23:04:19'
---

# 修复需求中心阶段业务标题并统一文档中文标题生成

## 背景

[BUG-0019-requirement-center-issue-title-overridden](../../../issues/bugs/review/BUG-0019-requirement-center-issue-title-overridden/bug.md) 已批准并纳入 sprint-007。现有卡片跨阶段优先 Change 标题，且提取范围包含追溯文档，导致业务标题错取；用户确定了按阶段读取注册表、主文档、proposal 的新契约及所有生成文档中文标题要求。

## 变更内容

- 按九阶段选择业务标题，唯一 Change 仅从 proposal 读取，历史缺失安全降级。
- 全部生成 Markdown 具有中文 title 和一致一级标题，注册表每条具有中文业务 title；统一生成入口校验与错误定位。
- 保留对象身份、权限、OpenSpec 解析语法，新增回归与真实页面证据。

## 能力影响

### 新增能力

无新增能力目录。

### 修改能力

- web-catalog-requirement-center-real-data：阶段标题来源、关联对象与显示标题的身份边界。
- harness-runtime：生成文档中文标题与完成门禁。

## 影响范围

后端治理读取/响应投影、Web 卡片、生成模板/技能/规则、生成结果应用前校验及对应测试。保持 Sprint 既有 L=5 人天估算，不重复计费。无需数据库迁移或生产维护。

## 回滚方案

回滚本 Change 的代码与规则变更，保留已写入的合法中文标题；不删除已有文档、不恢复真实数据、不修改历史归档状态。字段扩展保持向后兼容，前后端协调部署。

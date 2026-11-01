---
title: Change 来源人力估算修复提案
created_at: '2026-10-31 23:29:25'
updated_at: '2026-10-31 23:29:25'
---

# Change 来源人力估算修复提案

## 背景
来源[BUG-0073](../../../issues/bugs/review/BUG-0073-change-source-issue-estimate-missing/bug.md)已有真实Sprint输入复现：Issue返回3人天，Change返回缺失。已评审、纳入sprint-018。
## 变更内容
保留Change自身估算优先；明确唯一归属时引用来源Issue估算，冲突与共享估算不复制。
## 能力影响
修改web-catalog-requirement-center-real-data的单卡预估人天投影，无新增能力。
## 影响范围
card_metadata、change_index、API投影及卡片标签；无需数据库、部署或对象存储变更。若增加来源字段，更新schema、OpenAPI、Orval及API文档。
## 回滚方案
回退本次估算引用逻辑恢复待估算提示，不回写Sprint数据，不改变容量历史。

---
title: 纯 Change 卡片阻塞诊断修复提案
created_at: '2026-10-20 19:09:48'
updated_at: '2026-10-20 19:09:48'
---

# 纯 Change 卡片阻塞诊断修复提案

## 背景

来源 [BUG-0054-change-card-blocked-reason-missing](../../../issues/bugs/review/BUG-0054-change-card-blocked-reason-missing/bug.md)，根因已确认、评审通过，已纳入 sprint-011。上游已有 stale AC 信息，但准入层 reason=status 丢失详情，卡片和禁用动作只显示 blocked。

## 变更内容

保持 readiness 的准入布尔值与归档门禁不变，增加可安全传播的诊断结构：原因码、受影响 AC、必要的仓库相对输入路径、可操作建议。先核对现有接口 schema，优先兼容扩展，不移除既有 status/reason 消费契约。归档准入和 reader 投影不再将所有诊断压成 blocked。

中文展示区分未执行、输入缺失、输入变化及未知错误；未知情况不编造原因。按钮禁用提示与卡片摘要使用同一诊断语义，ready 时清除旧提示。后端输出前脱敏，不把绑定根、原始异常堆栈或配置传给前端；路径只允许授权范围内的仓库相对值。

## 能力影响

### 修改能力

- `web-catalog-requirement-center-real-data`：增加本次修复的行为契约与回归场景。

## 影响范围

acceptance_evidence、archive_admission、reader 及卡片显示；若新增响应字段，同步 API 索引、OpenAPI/生成客户端和接口测试，无数据库迁移。

估算沿用 1 人天，不新增重复容量项。本次只创建规格与任务，不执行实现或部署。

## 回滚方案

若修复引入回归，回退对应实现与部署版本，保留历史 manifest 和诊断证据；恢复原有阻断状态，不能以篡改证据或放宽准入回滚。无数据迁移和恢复操作。

---
title: 归档恢复边界治理优化
created_at: 2026-10-16 15:19:32
updated_at: 2026-10-16 15:19:32
---

# 归档恢复边界治理优化

## 迭代目标

阻止归档命令成功后直接修改正式规格，并让规格合并与 Change 迁移之间的重试依据已保存的文件事实继续。

## 变更摘要

- 归档脚本在临时副本预览 OpenSpec 合并，保存原规格、预期规格与活动 Change 的指纹；重试时按指纹选择继续合并、只迁移 Change 或阻断未知修改。
- 私有指纹放在归档权限允许且 Git 忽略的目录；真实隔离产品轮次证实普通诊断目录不可写。
- 归档技能明确归档脚本成功后不得直接改正式规格；发现意外差异时保留现场并报告阻断。

## 影响范围与更新文件

涉及 `.agents/skills/opsx-archive/SKILL.md`、`scripts/archive-change.sh`、`scripts/archive-recovery-guard.py`、`.gitignore`、`docs/08-command-execution-order.md`、归档回归测试及 REQ-0027 Change 验收材料。API、数据库结构、Web、管理端、客户端生成、Orval、Docker Compose 和安全权限边界均未改变。`product_data_collection_observability` 不适用：未新增采集、请求日志或 Task Trace 字段。

## 验证结果

归档/Issue 迁移相关回归 27 项通过；真实 OpenSpec CLI 分段复验确认已合并规格只迁移一次；真实隔离产品归档轮次发现后置直接编辑正式规格，重试被指纹护栏阻断并保留文件。AC-012 尚缺完整产品中断轮次，保持未签认。

## 后续建议

继续采集完整对象 Chat 的四个指定中断窗口；若后置直接编辑仍发生，进一步收紧产品执行器在归档命令完成后的写权限或完成态校验。

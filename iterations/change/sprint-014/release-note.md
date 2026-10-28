---
title: 临时验证资源治理交付说明
created_at: 2026-10-26 12:12:25
updated_at: 2026-10-27 16:39:42
sprint_id: sprint-014
---

# 临时验证资源治理交付说明

## 交付范围
- add-temporary-docker-lifecycle：创建前登记、标签隔离、任务结束清理与到期回收门禁。
## 影响与限制
此前已归档交付仅涉及治理文件和脚本，无产品部署变更；历史未登记容器不自动清理。没有常驻定时任务，到期由后续入口触发。
## 验证入口
[Change追踪](../../../openspec/changes/add-temporary-docker-lifecycle/trace.md)

## BUG-0064 计划交付

新增已评审缺陷BUG-0064-chat-unknown-recovery-container-churn，计划修复unknown恢复无界重试。覆盖持久化退避与暂停、预检成本优化和恢复观测；当前仅纳入，未开发、未验收、未发布。预计涉及后端与恢复元数据，API/UI边界由Change设计明确，正式部署另行按流程执行。

## BUG-0067 计划交付

BUG-0067-chat-stream-preview-premature-truncation 已正式纳入，计划修复短正文按片段数量过早截断和误导性缺失提示；估算3人天。状态in_sprint，已关联 fix-chat-stream-preview-premature-truncation，尚未实施或发布。保留有界读取、权限隔离与最终答案去重；具体接口变化以Change设计为准。规划与依赖见 sprint.md 第13节。

## BUG-0068 计划交付

BUG-0068-chat-database-lock-execution-interruption 已纳入sprint-014，估算5人天。计划修复需求中心治理核验在写事务内扫描文件引起的共享数据库竞争，保留权限、核验保护与幂等。尚未创建Change、实施、验收或发布；不重启服务、不重跑原apply。共享reader路径与BUG-0056协同集成，详见sprint.md第14节。

## BUG-0069 计划交付

BUG-0069-chat-interrupted-successor-proof-missing已评审并纳入sprint-014，计划保留旧停止轮次历史，核验外部接续完成证据后安全解除限制。复用BUG-0061本次复发根因与评审，旧BUG保持归档。当前未开发、未验收、未发布，估算5人天，容量风险见sprint.md。

## BUG-0056 验收返修进展

需求中心返修进一步减少重复文档解析及状态核对，并让后台自动备份分步释放数据库读锁、在繁忙时有界延后；孤儿内容清理增加引用索引。已更新授权的本地服务，旧执行历史与权限保护保持有效。真实并发验收完成前不视为发布完成。详情见 [返修台账](../../../openspec/changes/fix-requirement-center-context-load-latency/acceptance-fixes.md)。

### BUG-0056 真实后台性能返修复验

后台三服务同时运行时，30次暖导航首卡P95 1.776秒、HTTP1.359秒，30次刷新HTTP P95 1.111秒，零错误、后台健康无重启。隔离冷暖、配对改善及资源预算通过，证据见[返修台账](../../../openspec/changes/fix-requirement-center-context-load-latency/acceptance-fixes.md)。首次重启及源版本变化初始化8.620秒单列，不将其称为暖读。保留历史执行保护与授权核验；本轮不自动归档。

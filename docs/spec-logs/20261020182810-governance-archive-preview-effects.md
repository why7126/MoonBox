---
title: 归档预演完成事实核验修复
created_at: 2026-10-20 18:28:10
updated_at: 2026-10-20 18:28:10
---

# 归档预演完成事实核验修复

## 目标与根因
REQ-0046 与 BUG-0052 联合返修。CLI 退出码为 0 但明示 MODIFIED failed/Aborted，旧预演误判；新增要求分类错误。

## 更新文件与影响
scripts/archive-recovery-guard.py；tests/unit/test_archive_preview_result.py、test_acceptance_orchestration.py、test_change_identity.py；docs/standards/opsx-acceptance.md；两条 Change 的 delta、设计、返修台账、任务、trace 与 acceptance-plan.json。
预演核对失败输出、归档唯一性、源目录消失、完整内容和规格效果。显式 reprepare 在原 baseline 未变时保留旧日志并重建，未知修改仍拒绝。

## 验证
聚焦正反例和两条链路真实 CLI 临时预演，最终逐项报告见 Change evidence/acceptance/；静态与临时副本验证不冒充产品真实模型归档。

## 边界与后续
API/DB/Web/客户端/管理端/Orval/Docker Compose 无变更；治理脚本由工作区执行，无需重建产品镜像。product_data_collection_observability: N/A；affected_layers: []；不新增产品事件采集。原型与产品行为未改，复用仍有效证据。正式对象不归档，不新增 Issue。

## 最终结果

46 项聚焦回归通过；REQ 33/33、BUG 17/17，完整清单与同步后 readiness 均通过。REQ 恢复日志显式重建并保留 previous_record，当前 classify=merge。两种临时归档顺序通过，正式对象未归档。Workflow Sync 无错误；BUG root-cause.status=confirmed 的既有语义警告经核对保留。用量自动发现 unavailable，不为用量重跑验收。

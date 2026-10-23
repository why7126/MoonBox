---
bug_id: BUG-0053-deployed-acceptance-input-resolution
title: 部署态验收输入解析不完整导致纯 Change 归档误阻塞临时方案
created_at: '2026-10-20 18:56:49'
updated_at: '2026-10-20 18:56:49'
owner: 产品团队
severity: high
---

# 部署态验收输入解析不完整导致纯 Change 归档误阻塞临时方案

## 可用临时方案

没有已验证、能够恢复部署态按钮且不改变门禁的临时方案。当前建议保留 blocked 状态，在本地只读核对同一 Change 的 readiness、验收 run_id 和输入指纹，以区分证据确实失效与部署读取偏差。

1. 运行 `src/backend/.venv/bin/python scripts/opsx_acceptance.py --change optimize-governance-feedback-loop --readiness`，记录状态、stale AC 与 run_id。
2. 使用现有授权的部署诊断入口，对同一绑定和 run_id 核对源码根是否配置、四个相对路径是否可读取；仅保留布尔结果、相对路径和指纹，不导出绑定绝对路径。
3. 将结果与 capture.md 已记录样本比较，若输入或 run_id 不同，重新调查而非套用旧结论。

## 限制与风险

该方案仅协助诊断，不解除阻塞。不要手改 ready、manifest、指纹或禁用状态，不把源码随意复制进治理投影，也不以本地 ready 自动授权归档。归档需在正式流程验证并取得相应授权后执行；本次未执行归档或部署。

## 退出条件

正式修复部署后通过 acceptance.md 的真实页面与负向门禁验证，再停止临时对照流程。诊断为只读，无持久变更需要回滚。

## 当前处置

关联修复 `fix-deployed-acceptance-input-resolution` 已在本地部署验证；上文临时诊断保留为历史处置方式。修复后的真实输入变化仍需增量复验，不能绕过门禁。

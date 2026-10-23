---
title: 同条文兼容追加与产品防复发修复提案
created_at: '2026-10-22 09:34:48'
updated_at: '2026-10-23 21:07:37'
---

# 同条文兼容追加与产品防复发修复提案

## 背景

来源 [BUG-0063-compatible-requirement-successor-blocked](../../../issues/bugs/review/BUG-0063-compatible-requirement-successor-blocked/bug.md)，已评审且纳入 sprint-012。当前归档后继遍历按模块与Requirement标题交集拒绝，BUG-0061保留BUG-0060三项原约束并追加场景仍阻断。当前现场可复现，根因8项证据通过；需在产品层面避免合法后继反复导致旧交付不可关闭。

## 变更内容

- 版本化、可验证的同条文兼容追加证明，支持多跳和跨Sprint，禁止ID特判。
- 后继验收/归档写入前检查历史保护影响，最终写入复读稳定指纹。
- 产品逐项展示对象、条文、分类和处理路径，保留草稿及独立签署门禁。
- 四入口统一判定和持续安全回归；历史证据不变，新增证明可追溯。

## 能力影响

### 新增能力

无新增独立模块；新增规则纳入现有治理恢复能力。

### 修改能力

- governance-command-durable-recovery：演进条文冲突范围，增加兼容证明、提前影响预检、产品诊断及防复发契约。

## 影响范围

archive_recovery、archive_admission、sprint_archive_admission、最终发送/归档准入、Workflow Sync消费者与Chat错误展示；测试、API错误契约及文档按实际影响同步。BUG-0062的历史验收不改写，本Change通过增量规格演进策略。

product_data_collection_observability: applicable；affected_layers: agent_workflow_governance、归档证明、API准入诊断、Web反馈、Sprint预检、Workflow Sync；reason: 证明分类与错误贯通影响治理观测；validation: AC-007—018覆盖证据、并发、共享原因、脱敏与真实部署。N/A：不计划新增DB schema、对象存储或权限；API结构实际变化需同步OpenAPI/Orval及文档；不新增原始Prompt、凭证或主机路径采集。

## 回滚方案

回退代码到保守拒绝策略并保留新增审计证明，不改旧manifest/journal或规格历史。旧版本不识别的新证明应安全拒绝而非放行；运行未完成操作保留恢复入口，禁止重放成功副作用。

## 规划与边界

sprint-012原估算XL/8人天不重复累加，总量34/30人天。18项AC全部待执行。此阶段仅生成设计与任务，不关闭Sprint、不替代人工签署、不处理无关历史链接。

## 2026-10-23 验收反馈调整（当前策略）

取消后继写入前兼容证明硬性限制：产品预检、CLI 和归档执行不再要求独立兼容或规则替代证明；已完成后继仍核验正常验收、唯一身份、连续归档哈希链、交付增量、最终规格效果和并发变化。历史 journal、manifest 与证明保留，不自动归档或代替独立签署。

本节取代前文将兼容证明作为硬门禁的描述；证明工具保留为可选审查工具。

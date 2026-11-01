---
title: 独立 Change 创建时自动分级与卡片只读展示用户故事
requirement_id: REQ-0059-standalone-change-auto-classification
created_at: '2026-11-01 00:25:42'
updated_at: '2026-11-01 00:57:00'
---

# 独立 Change 创建时自动分级与卡片只读展示用户故事

## US-001 创建后即可判断分级
作为创建独立 Change 的 Agent，我需要识别来源及修复类型，根据证据完成评估，让负责人无需在卡片补填。验收对应 AC-001、002、003。

## US-002 快速浏览交付风险
作为产品经理，我需要 fix 展示严重性、其他独立 Change 展示优先级，且卡片只读，避免把缺陷影响程度与排期混淆。验收对应 AC-004、005、006。

## US-003 保留历史及来源事实
作为研发负责人，我需要旧值可追溯、来源 Issue 不被覆盖、重试不产生重复变更，确保治理记录可信。验收对应 AC-007、008、009。

## US-004 安全维护评估结果
作为授权维护者，我需要通过治理流程调整等级并留下理由，旧 API 不绕过类型及版本校验。验收对应 AC-010、011。

## 实施一致性核对

2026-11-01 核对本文件与实现一致：创建Agent评估，完成门禁校验；卡片只读按维度展示；来源和历史保留。证据见 Change `update-standalone-change-auto-classification/evidence/acceptance/implementation-review.md`。无数据库迁移、部署拓扑调整或新增权限。

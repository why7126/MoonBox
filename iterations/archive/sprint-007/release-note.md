---
sprint_id: sprint-007
title: sprint-007 发布说明
status: published
lifecycle_stage: archive
created_at: '2026-09-15 00:03:01'
updated_at: '2026-09-29 14:42:54'
---

# sprint-007 发布说明

## 发布状态

published；Sprint 范围已完成归档闭环，可作为后续发布计划输入。本文件为迭代发布说明，不代表已执行生产升级或正式对外发布。

## 范围摘要

REQ-0029-capture-multimodal-candidate-review：图文输入、AI整理、候选审阅，确认后按最终类型分配编号并批量生成采集记录。

REQ-0037-current-iteration-archive-entry：当前迭代容量区域或操作区展示归档当前迭代入口；入口启用状态基于 Sprint archive readiness 汇总，未满足时隐藏或禁用并展示安全摘要。

BUG-0017-compose-container-name-suffix-one：修复 Docker/Compose 容器名自动追加 `-1` 后缀导致运维识别与脚本引用不稳定的问题；具体发布内容以关联 OpenSpec Change 的真实验收为准。

## 交付边界

只纳入已评审需求与缺陷范围；13 个 OpenSpec Change 已完成归档。正式对外发布、镜像构建、升级计划和产品手册投影仍需按发布链路单独执行。

## 发布前验证

已核对 REQ-0029 的36条AC、RC-001至003、图片实链与授权、批量恢复、UI视觉、API/DB/客户端和部署文档；已核对 REQ-0037 的 Sprint archive readiness、归档确认、权限和 Workflow Sync 门禁；已核对 BUG-0017 的 Compose 配置解析、运行态容器名和部署文档一致性。Sprint 关闭前 `validate-sprint-archive-readiness`、`check-sprint-close-stale-scan` 和 `validate-env-ignore-policy` 通过。

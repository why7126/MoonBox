---
bug_id: BUG-0053-deployed-acceptance-input-resolution
title: 部署态验收输入解析不完整导致纯 Change 归档误阻塞
status: done
created_at: '2026-10-20 18:50:18'
updated_at: 2026-10-20 19:36:07
owner: 产品团队
source: 用户授权与同会话只读取证
lifecycle_stage: plan
severity: high
environment: docker
related_requirement: null
related_bug: BUG-0054-change-card-blocked-reason-missing
related_change: null
iteration: null
---

# 部署态验收输入解析不完整导致纯 Change 归档误阻塞

## 现象与复现

1. 使用本地已通过自动验收的纯 Change `optimize-governance-feedback-loop`，来源迭代为 `sprint-011`。
2. 在 Docker 部署的需求中心刷新页面，定位“验收中”卡片。
3. 卡片研发任务为 6/6，却显示 `blocked`，“完成 / 归档”不可点击。

期望：同一验收清单、相同输入内容在本地与部署态得到一致 readiness；真实缺失或内容变化仍应阻断。
实际：本地 ready，部署态 blocked，合法归档入口被误禁用。

## 本轮已取得的证据

- 用户截图与刷新后的浏览器观察一致；截图未复制入仓库。
- 本地 `scripts/opsx_acceptance.py --change optimize-governance-feedback-loop --readiness` 返回 ready、stale=[]。
- 部署后端使用实际仓库绑定读取，source_root 已配置且可访问；同一 run_id 返回 blocked，stale 为 AC-001、AC-002、AC-004。
- 证据入口：`openspec/changes/optimize-governance-feedback-loop/evidence/acceptance/20261020183342423385-0a32c636/manifest.json`。
- 部署中的 `app.governance.acceptance_evidence.input_bytes` 只将 src、scripts 顶层路径路由至可信源码根，其余从治理投影根读取。
- 被误判缺失的输入：`tests/unit/test_governance_feedback.py`、`tests/unit/test_ai_usage.py`、`AGENTS.md`、`.gitignore`。
- 只读内存诊断改从已绑定源码根读取上述输入后，三个 AC 的指纹均与既有 manifest 一致；未改写证据或跳过校验。
- 取证时本地工作区已有并行修改，将 tests 纳入读取范围并增加目录处理；运行容器尚未包含该修改，且根级 AGENTS.md、.gitignore 仍需覆盖。修复时先核对当前版本，避免覆盖并行工作。

## 影响与初判

严重等级 high：阻断已有验收通过成果的完成/归档流程。已确认该样本存在部署态输入解析范围不足；其他输入类型与全部 Change 的影响范围待补充。

## 建议验收要点

- 覆盖 src、scripts、tests、根级治理文件及合法目录输入的部署态解析，保持绑定边界与路径安全。
- 相同输入在本地、治理投影与可信源码绑定组合下指纹一致；真正缺失、变化和越界路径仍被拒绝。
- 重新部署后真实页面显示 ready 并开放完成/归档，不能只凭本地回归宣布恢复。

## 判重与关联

BUG-0018 处理独立 Change 验收来源识别；BUG-0035 处理卡片验收进度/门禁不一致与文档入口。二者与本次部署态输入路由缺口弱相关，非重复。阻塞详情丢失单独记录为关联 BUG-0054。

## 范围边界

本次仅采集缺陷，未开发、未评审、未纳入 Sprint。来源 Change/Sprint 仅为复现场景，不是本 BUG 的交付归属。product_data_collection_observability: N/A；affected_layers: 治理验收读取与需求中心卡片；本次不改变产品采集或持久化，validation 为文档标题与 Workflow Sync。

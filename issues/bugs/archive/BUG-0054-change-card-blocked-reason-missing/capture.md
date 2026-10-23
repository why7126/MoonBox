---
bug_id: BUG-0054-change-card-blocked-reason-missing
title: 纯 Change 卡片验收阻塞缺少具体原因
status: done
created_at: '2026-10-20 18:50:18'
updated_at: 2026-10-20 19:36:42
owner: 产品团队
source: 用户授权与同会话只读取证
lifecycle_stage: plan
severity: medium
environment: docker
related_requirement: null
related_bug: BUG-0053-deployed-acceptance-input-resolution
related_change: null
iteration: null
---

# 纯 Change 卡片验收阻塞缺少具体原因

## 现象与复现

1. 打开需求中心，定位 `optimize-governance-feedback-loop` 的验收中卡片。
2. 观察红色阻塞提示及禁用的“完成 / 归档”动作。
3. 页面仅显示 `blocked`，按钮禁用原因也仅为 `blocked`，无法知道哪些 AC 或输入出了问题。

期望：卡片提供可理解的阻塞摘要，并能定位受影响 AC、具体缺失/变化输入及下一步处理；不得泄漏本机绝对路径或敏感内容。
实际：后端已有 stale AC 诊断，但投影仅保留状态字符串，前端无可操作原因。

## 本轮已取得的证据

- 用户截图与刷新后浏览器页面均只显示 blocked；禁用动作提示也为 blocked。
- 部署 readiness 返回 AC-001、AC-002、AC-004 失效；进一步只读诊断定位到四个输入读取失败，见关联 BUG-0053。
- `src/backend/app/governance/archive_admission.py` 的独立 Change 分支将 readiness 结果简化为 ready 布尔值与 reason=status，丢弃 stale AC 细节。
- `src/backend/app/governance/reader.py` 将该 reason 投影到 acceptance_blocked_reason 和 action.disabled_reason，最终页面只能显示 blocked。
- 验收证据入口：`openspec/changes/optimize-governance-feedback-loop/evidence/acceptance/20261020183342423385-0a32c636/manifest.json`。

## 影响与初判

严重等级 medium：缺少诊断信息使用户无法判断是真实缺证、指纹变化还是读取失败，增加重复验收和排查成本。即使 BUG-0053 修复，其他真实阻塞仍需要可理解原因，故独立闭环。

## 建议验收要点

- 真实缺失输入、内容变化、验收未执行等情形提供不同且可操作的中文原因。
- 从 readiness 经归档准入、卡片字段到页面提示保留诊断语义；摘要能关联具体 AC 和安全的仓库相对路径。
- 有原因时不以裸 blocked 代替；无可用诊断时提供明确兜底和证据入口。
- 验证禁用动作与提示一致，并保留原有验收门禁，不因改进文案放开归档。

## 判重与关联

BUG-0018 聚焦验收来源识别，BUG-0035 聚焦进度与归档门禁及文档入口；本条聚焦 readiness 诊断在准入投影中丢失，属于独立修复面。与 BUG-0053 共用样本但修复目标不同。

## 范围边界

本次仅采集缺陷，未开发、未评审、未纳入 Sprint。来源 Change/Sprint 仅为复现场景，不是本 BUG 的交付归属。product_data_collection_observability: N/A；affected_layers: 治理验收读取与需求中心卡片；本次不改变产品采集或持久化，validation 为文档标题与 Workflow Sync。

---
bug_id: BUG-0054-change-card-blocked-reason-missing
title: 纯 Change 卡片验收阻塞缺少具体原因
status: done
created_at: '2026-10-20 18:53:04'
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
discovered_at: '2026-10-20 18:50:18'
root_cause_status: confirmed
---

# 纯 Change 卡片验收阻塞缺少具体原因

## 现象与复现

1. 打开需求中心，定位 `optimize-governance-feedback-loop` 的验收中卡片。
2. 观察红色阻塞提示及禁用的“完成 / 归档”动作。
3. 页面仅显示 `blocked`，按钮禁用原因也仅为 `blocked`，无法知道哪些 AC 或输入出了问题。

期望：卡片提供可理解的阻塞摘要，并能定位受影响 AC、具体缺失/变化输入及下一步处理；不得泄漏本机绝对路径或敏感内容。
实际：后端已有 stale AC 诊断，但投影仅保留状态字符串，前端无可操作原因。

## 已有取证摘要

- 用户截图与刷新后浏览器页面均只显示 blocked；禁用动作提示也为 blocked。
- 部署 readiness 返回 AC-001、AC-002、AC-004 失效；进一步只读诊断定位到四个输入读取失败，见关联 BUG-0053。
- `src/backend/app/governance/archive_admission.py` 的独立 Change 分支将 readiness 结果简化为 ready 布尔值与 reason=status，丢弃 stale AC 细节。
- `src/backend/app/governance/reader.py` 将该 reason 投影到 acceptance_blocked_reason 和 action.disabled_reason，最终页面只能显示 blocked。
- 验收证据入口：`openspec/changes/optimize-governance-feedback-loop/evidence/acceptance/20261020183342423385-0a32c636/manifest.json`。

## 严重等级说明

严重等级 medium：缺少诊断信息使用户无法判断是真实缺证、指纹变化还是读取失败，增加重复验收和排查成本。即使 BUG-0053 修复，其他真实阻塞仍需要可理解原因，故独立闭环。

## 建议验收要点

- 真实缺失输入、内容变化、验收未执行等情形提供不同且可操作的中文原因。
- 从 readiness 经归档准入、卡片字段到页面提示保留诊断语义；摘要能关联具体 AC 和安全的仓库相对路径。
- 有原因时不以裸 blocked 代替；无可用诊断时提供明确兜底和证据入口。
- 验证禁用动作与提示一致，并保留原有验收门禁，不因改进文案放开归档。

## 判重与关联

BUG-0018 聚焦验收来源识别，BUG-0035 聚焦进度与归档门禁及文档入口；本条聚焦 readiness 诊断在准入投影中丢失，属于独立修复面。与 BUG-0053 共用样本但修复目标不同。


## 根因判断与证据链

根因状态：confirmed（针对纯 Change 验收计划分支）。归档准入层将包含 stale AC 的 readiness 结果压缩为 `reason=evidence["status"]`，卡片投影继续复用这一字段，诊断信息在到达页面前丢失，因此只有 blocked 而无具体原因。

| ID | 类型 | 来源 | 观察与支持的判断 |
|---|---|---|---|
| E1 | reproduction | 本会话刷新后的需求中心 `/requirements`、用户截图，摘要见 capture.md | 卡片与禁用动作均只显示 blocked |
| E2 | data_sample | 同一样本的部署 readiness，摘要见关联 BUG-0053 capture.md | 已包含 AC-001、AC-002、AC-004 的 stale 信息，说明上游并非完全没有诊断 |
| E3 | code_path | `src/backend/app/governance/archive_admission.py` 的 change_acceptance 独立 Change 分支 | 返回 ready 与 reason=status，未保留 stale AC；本次文档生成时再次只读核对该代码 |
| E4 | code_path | `src/backend/app/governance/reader.py` 的归档准入卡片投影，前序探索记录见 capture.md | 将同一 reason 用于 acceptance_blocked_reason/action.disabled_reason，与页面表现吻合 |

运行态证据复用本会话前序取证；本次不宣称重新部署或完成修复验收。BUG-0053 解释为何此样本进入 blocked，本条解释为何任何进入该分支的诊断只剩状态词，两者可以独立修复和验证。

## 影响范围与未决边界

已确认有验收计划的纯 Change 卡片受影响；尚未证明所有 REQ/BUG 卡片均有相同缺陷。现有 readiness 已有 stale AC，但更细的“文件缺失/内容变化”分类不应假定已完整输出；修复时需补齐可安全传播的诊断数据，并验证未知异常兜底。

## 后续修复验证方向

覆盖未执行验收、缺失输入、输入变化、未知错误及 ready 状态，从准入投影到真实卡片检查中文摘要、AC 标识、相对路径及处理提示。维持禁用判定，不允许以优化文案替代验收。已修复诊断传递，沿用现有字段和页面，真实部署效果见关联 Change verification.md。

## 文档与观测边界

当前已评审、纳入 sprint-011 并完成关联修复 Change 的实现；执行与验收证据以 Change verification.md、trace.md 和 acceptance.md 为准。复现场景的 sprint-011 与 optimize-governance-feedback-loop 不作为本 BUG 的交付归属。

- product_data_collection_observability: N/A，本次为缺陷文档生成，没有新增产品日志、埋点或持久数据。
- affected_layers: 部署态治理验收读取、归档准入及需求中心卡片投影。
- validation: 中文标题校验与 bug.complete Workflow Sync；产品修复验证已执行，见关联 Change verification.md。
- API、数据库、UI、部署、安全与客户端生成：本次无实现变更，无需同步生成产物；后续修复按实际影响另行评估。

---
bug_id: BUG-0053-deployed-acceptance-input-resolution
title: 部署态验收输入解析不完整导致纯 Change 归档误阻塞
status: done
created_at: '2026-10-20 18:53:04'
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
discovered_at: '2026-10-20 18:50:18'
root_cause_status: confirmed
---

# 部署态验收输入解析不完整导致纯 Change 归档误阻塞

## 现象与复现

1. 使用本地已通过自动验收的纯 Change `optimize-governance-feedback-loop`，来源迭代为 `sprint-011`。
2. 在 Docker 部署的需求中心刷新页面，定位“验收中”卡片。
3. 卡片研发任务为 6/6，却显示 `blocked`，“完成 / 归档”不可点击。

期望：同一验收清单、相同输入内容在本地与部署态得到一致 readiness；真实缺失或内容变化仍应阻断。
实际：本地 ready，部署态 blocked，合法归档入口被误禁用。

## 已有取证摘要

- 用户截图与刷新后的浏览器观察一致；截图未复制入仓库。
- 本地 `scripts/opsx_acceptance.py --change optimize-governance-feedback-loop --readiness` 返回 ready、stale=[]。
- 部署后端使用实际仓库绑定读取，source_root 已配置且可访问；同一 run_id 返回 blocked，stale 为 AC-001、AC-002、AC-004。
- 证据入口：`openspec/changes/optimize-governance-feedback-loop/evidence/acceptance/20261020183342423385-0a32c636/manifest.json`。
- 部署中的 `app.governance.acceptance_evidence.input_bytes` 只将 src、scripts 顶层路径路由至可信源码根，其余从治理投影根读取。
- 被误判缺失的输入：`tests/unit/test_governance_feedback.py`、`tests/unit/test_ai_usage.py`、`AGENTS.md`、`.gitignore`。
- 只读内存诊断改从已绑定源码根读取上述输入后，三个 AC 的指纹均与既有 manifest 一致；未改写证据或跳过校验。
- 取证时本地工作区已有并行修改，将 tests 纳入读取范围并增加目录处理；运行容器尚未包含该修改，且根级 AGENTS.md、.gitignore 仍需覆盖。修复时先核对当前版本，避免覆盖并行工作。

## 严重等级说明

严重等级 high：阻断已有验收通过成果的完成/归档流程。已确认该样本存在部署态输入解析范围不足；其他输入类型与全部 Change 的影响范围待补充。

## 建议验收要点

- 覆盖 src、scripts、tests、根级治理文件及合法目录输入的部署态解析，保持绑定边界与路径安全。
- 相同输入在本地、治理投影与可信源码绑定组合下指纹一致；真正缺失、变化和越界路径仍被拒绝。
- 重新部署后真实页面显示 ready 并开放完成/归档，不能只凭本地回归宣布恢复。

## 判重与关联

BUG-0018 处理独立 Change 验收来源识别；BUG-0035 处理卡片验收进度/门禁不一致与文档入口。二者与本次部署态输入路由缺口弱相关，非重复。阻塞详情丢失单独记录为关联 BUG-0054。


## 根因判断与证据链

根因状态：confirmed（针对本轮已取证样本及当时部署版本）。部署态输入读取按顶层目录限定源码来源，未覆盖验收计划引用的测试文件和根级文件；存在的输入被当作缺失参与指纹计算，导致有效证据被标为 stale，归档准入随之阻断。

| ID | 类型 | 来源 | 观察与支持的判断 |
|---|---|---|---|
| E1 | reproduction | 本会话刷新后的需求中心 `/requirements` 与用户截图，摘要见 capture.md | 同一卡片 6/6、blocked、完成/归档禁用，证明用户可见影响 |
| E2 | data_sample | 本地 readiness 命令及 manifest，路径见上文 | ready、stale=[]，run_id 与部署态相同，排除读取了不同验收轮次 |
| E3 | code_path | 当时运行容器的 acceptance_evidence.input_bytes；本地对应 `src/backend/app/governance/acceptance_evidence.py` | 部署仅将 src/scripts 路由至可信源码根，四个输入被误判缺失；源码绑定存在且可访问，排除全局未配置源码根 |
| E4 | data_sample | 本会话部署态只读输入诊断与内存指纹对照，摘要见 capture.md | 从既有绑定源码根读取四个文件后，三个 AC 指纹全部匹配 manifest，直接解释解析缺口与 stale 的因果关系 |

以上运行态证据复用本会话前序取证，不表示本次生成命令重新执行了部署验收。原始终端输出未复制入仓库；可按相同仓库绑定、验收轮次和四个相对输入复核。当前本地代码已包含 tests 与目录输入处理，但根级文件来源仍未覆盖；本地工作区与部署版本不可混同。

## 影响范围与未决边界

已确认影响该纯 Change 的 AC-001、AC-002、AC-004 和完成/归档入口。其他引用相同输入类型的 Change 有同类风险，但尚未逐项统计。问题不证明全部验收失效，也不授权忽略真实 stale。修复方案需明确治理文档与源码输入的权威来源，避免无条件回退到另一工作副本。

## 后续修复验证方向

分别验证读取来源、指纹一致性及真实部署页面恢复；增加缺失、改动、目录和越界输入的负向覆盖。源码根只读且可信这一安全边界保持不变。修复已实施，命令与真实部署验证见关联 Change verification.md。

## 文档与观测边界

当前已评审、纳入 sprint-011 并完成关联修复 Change 的实现；执行与验收证据以 Change verification.md、trace.md 和 acceptance.md 为准。复现场景的 sprint-011 与 optimize-governance-feedback-loop 不作为本 BUG 的交付归属。

- product_data_collection_observability: N/A，本次为缺陷文档生成，没有新增产品日志、埋点或持久数据。
- affected_layers: 部署态治理验收读取、归档准入及需求中心卡片投影。
- validation: 中文标题校验与 bug.complete Workflow Sync；产品修复验证已执行，见关联 Change verification.md。
- API、数据库、UI、部署、安全与客户端生成：本次无实现变更，无需同步生成产物；后续修复按实际影响另行评估。

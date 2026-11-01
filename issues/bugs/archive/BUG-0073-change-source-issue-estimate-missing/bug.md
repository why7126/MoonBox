---
bug_id: BUG-0073-change-source-issue-estimate-missing
status: done
severity: medium
created_at: '2026-10-31 23:08:26'
updated_at: 2026-11-01 00:02:00
owner: 产品团队
source: 用户 capture 授权与同会话 explore
captured_via: capture
classification_rationale: 已有来源 Issue 估算未在交付卡片展示，属于数据展示偏差。
lifecycle_stage: archive
iteration: null
openspec_changes: []
related_requirement: REQ-0056-requirement-center-change-delivery-cards
related_bug: BUG-0070-standalone-change-updated-time-missing
product_data_collection_observability:
  status: applicable
  affected_layers:
  - web
  - api
  reason: 涉及检查入口或估算投影；本次仅采集。DB、部署、对象存储不涉及；不改变安全授权。
  validation: 后续验证现有请求关联与检查门禁；API及客户端生成依契约差异决定。本次仅文档校验。
title: Change 卡片未展示来源 Issue 已有人力估算
discovered_at: '2026-10-31 23:08:26'
environment: 用户截图环境未核实；本地函数复现
root_cause_status: confirmed
---

# Change 卡片未展示来源 Issue 已有人力估算


## 现象
用户截图中 BUG-0070 对应 Change 卡片显示“人力待估算”，但 sprint-018 已记录 3 人天。

## 复现步骤
1. 在需求中心查看 fix-standalone-change-updated-time 交付卡片。
2. 对照 iterations/change/sprint-018/sprint.yaml 中 BUG-0070-standalone-change-updated-time-missing 的 scope_estimates 记录。
3. 观察卡片“人力待估算”与 estimated_person_days: 3 的差异。截图为历史验收中状态，当前 Issue 已归档，不宣称当前仍在验收中。

## 期望与实际
期望：来源估算明确且可归属时正确展示计划人天及来源；实际：显示待估算。计划估算不等于实际耗时。

## 证据与根因线索
Sprint 记录 id 为 BUG ID、change 为关联 Change ID、estimated_person_days 为 3。src/backend/app/governance/card_metadata.py 的 estimate_metadata 对 Change 排除带 Issue id 的记录；前端 estimate_status 非 available 时显示待估算。属于本地代码与数据证据，尚未进行运行态复验；最终根因及一对多分摊策略留待 bug-explore 确认。

## 建议验收
- 一对一来源关系展示已有 3 人天，并明确估算来源。
- 一对多、多个来源、冲突、缺失与零值分别验证，不重复累计或把未知当零。
- 刷新、阶段切换和归档后展示口径一致，不改写 Sprint 原始估算。

## 判重与授权
关联 REQ-0056-requirement-center-change-delivery-cards；BUG-0070 是复现样本，其修复目标为更新时间。用户确认新建关联缺陷并独立闭环，不重开旧交付。

## 严重度依据
medium：估算信息误导，尚无执行阻断或数据丢失证据。

## 根因判断及证据边界
已确认代码取值原因：同一真实scope数据，以Issue身份返回 {'estimated_person_days': 3, 'estimate_status': 'available'}，以Change身份返回 {'estimated_person_days': None, 'estimate_status': 'missing'}。本轮通过runpy直接调用estimate_metadata并断言复现，未修改生产数据。
change_index.py交付卡调用apply_card_metadata(card, card.id, card.sprint_id, [], None)；card_metadata.py仅接受Change自身id或无id的change行，主动排除带Issue id记录；前端非available显示待估算。证据支持取值原因，不声称浏览器当前状态已复验。

## 影响与修复边界
影响使用Issue id登记、带明确change关联的交付估算展示；当前确认样本为BUG-0070。原REQ-0056明确禁止复制Issue总估算给多个Change，因此优先自身估算，只在归属唯一且无冲突时考虑来源引用；一对多、共享及非法数据继续显式提示，不默认分摊、不改写Sprint容量。
严重度medium：计划信息误导，无数据损坏、权限越界或执行阻断证据。实际人力耗时不在本缺陷范围。

## 后续验证
覆盖独立估算优先、一对一来源、多个来源冲突、一对多、零值、非法值、缺失、归档及刷新。修复前完善根因文档与验收，运行态验证另行采集。

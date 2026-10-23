---
bug_id: BUG-0028-requirement-center-card-owner-raw-user-id
title: 需求中心 Capture 卡片直接显示内部用户标识
status: done
created_at: 2026-10-05 22:23:03
updated_at: 2026-10-19 11:23:32
owner: 产品团队
source: 用户截图反馈
lifecycle_stage: plan
captured_via: capture
classification_rationale: 已有的需求中心卡片展示将内部用户标识直接呈现给用户，属于现有界面的体验偏差。
environment: 待确认
related_requirement: REQ-0012-frontend-requirement-center
related_bug:
severity: medium
---

# 需求中心 Capture 卡片直接显示内部用户标识

## 现象

用户通过产品界面的“新建 Capture”创建卡片后，卡片的用户信息标签显示以 `user_` 开头的内部标识，且因长度过长被截断。截图中的 REQ-0038 卡片可见这一现象，无法让用户直观识别负责人。

## 复现步骤

1. 在产品界面的需求中心使用“新建 Capture”创建卡片。
2. 查看新卡片的用户信息标签。
3. 对照账号可读名称，检查卡片是否直接显示内部用户标识。

## 期望 vs 实际

- 期望：卡片显示可辨识的用户名称或清晰的身份标签；内部标识不直接作为面向用户的名称。具体展示优先级和缺失名称时的回退文案留待后续确认。
- 实际：截图中卡片直接显示并截断内部用户标识。

## 影响范围与初判

- 已观察到需求中心新建 Capture 的 REQ 卡片；BUG 卡片和其他来源卡片是否同样受影响待核实。
- 严重度暂定 `medium`：影响用户辨认负责人，不影响卡片创建与后续操作的证据尚不足。
- 截图证明展示现象，尚不能证明标识在前端映射、API 返回或治理文档写入中的哪一层产生；根因待排查。

## 附件

- 用户在本次对话提供的需求中心卡片截图；不将含完整内部标识的原图复制到仓库。

## 相似项检查

- BUG-0014 处理 Capture 持久化，BUG-0021 处理 BUG 卡片严重度字段，二者均不覆盖用户信息显示。
- REQ-0038 是截图中的业务卡片，需求内容是 Capture 编辑器，与本缺陷验收目标不同。

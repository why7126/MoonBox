---
bug_id: BUG-0031-requirement-card-chat-skill-token-missing
title: 需求卡片跳转 Chat 后治理技能未显示为标签
status: captured
created_at: 2026-10-05 23:15:20
updated_at: 2026-10-05 23:15:20
owner: 产品团队
source: 用户截图反馈与只读代码定位
lifecycle_stage: plan
environment: 待确认
related_requirement: REQ-0025-chat-workbench
related_bug: BUG-0025-requirement-center-command-chain-write-gap
severity: medium
---

# 需求卡片跳转 Chat 后治理技能未显示为标签

## 现象

点击需求中心卡片的治理动作后，页面跳转到 Chat 工作台，并在输入框预填 `/opsx-archive enable-agent-browser-product-evidence`。用户期望技能像手动选择时一样显示为「Opsx Archive」标签，实际显示为完整纯文本命令。

## 复现步骤

1. 在需求中心找到可执行「完成 / 归档」的卡片，点击该动作。
2. 等待跳转到关联 Chat 会话，查看输入框中的预填内容。
3. 对照在 Chat 中通过技能选择器手动选择 Opsx Archive 后的标签形态。

## 期望 vs 实际

- 期望：预填治理动作时，已匹配的技能显示为独立标签，命令参数仍可见且可编辑；发送时技能引用与目标参数保持一致。
- 实际：截图中输入框仅显示 `/opsx-archive enable-agent-browser-product-evidence` 纯文本，没有「Opsx Archive」技能标签。

## 影响范围与初判

- 已观察到需求卡片的 `/opsx-archive` 跳转；其他治理动作是否同样受影响待复现。
- 严重度暂定 `medium`：影响技能引用的可见性与操作预期；发送后的实际执行是否受影响尚无证据。
- 只读代码定位显示卡片跳转只缓存文本草稿，而 Chat 技能标签依赖独立的 skills 状态。运行态根因与修复验收仍需在后续探索中确认。

## 附件

- 用户本次对话提供的两张截图：实际 Chat 输入框与期望的技能标签形态。原图未复制到仓库。

## 相似项检查

- BUG-0025 涉及治理命令能否真实写入，BUG-0026 涉及归档执行权限与状态；本缺陷聚焦跳转后输入框的技能引用显示和提交数据，可独立复现与验收。

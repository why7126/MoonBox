---
bug_id: BUG-0029-chat-workbench-nonempty-page-scroll
title: Chat 工作台非空白对话出现页面级滚动条及底部布局异常
status: done
created_at: 2026-10-05 22:31:19
updated_at: 2026-10-12 23:01:34
owner: 产品团队
source: 用户截图反馈
lifecycle_stage: plan
captured_via: capture
classification_rationale: 已有 Chat 工作台在非空白对话场景出现页面级滚动和布局异常，属于现有界面行为偏差。
environment: 待确认
related_requirement: REQ-0025-chat-workbench
related_bug: BUG-0027-page-scroll-bottom-light-background-exposed
severity: medium
---

# Chat 工作台非空白对话出现页面级滚动条及底部布局异常

## 现象

Chat 工作台打开非空白对话时，出现页面级垂直滚动条；向下滚动后，页面底部布局表现异常。用户截图可见对话内容与底部输入框，页面整体可以继续向下滚动。

## 复现步骤

1. 打开 Chat 工作台，进入已有消息的非空白对话。
2. 检查页面外层是否出现垂直滚动条。
3. 向下滚动页面外层，观察输入框、主界面底部及悬浮元素的位置和背景。

## 期望 vs 实际

- 期望：对话内容在预期的对话滚动容器内滚动，工作台页面外层不因非空白对话产生异常滚动；底部输入区和页面背景保持正确布局。
- 实际：非空白对话出现页面级垂直滚动条，滚到底部后页面布局异常。具体超出视口的元素和滚动容器需进一步取证。

## 影响范围与初判

- 已观察到 Chat 工作台的非空白对话；空白对话、其他视口尺寸及浏览器环境待核实。
- 严重度暂定 `medium`：影响对话页布局与浏览体验；尚无证据表明消息数据或发送功能受损。
- 截图证明页面滚动及异常可见，不足以确认根因。后续需采集视口尺寸、`document.scrollingElement`、关键容器的 `scrollHeight/clientHeight`、computed style 与滚动前后截图。

## 附件

- 用户在本次对话提供的 Chat 工作台截图；截图中的会话内容不复制到仓库。

## 相似项检查

- BUG-0027 已归档，记录页面滚动后底部露出浅色背景。两者均涉及 Chat 工作台滚动边界，但本条明确以非空白对话触发页面级滚动条，并要求独立验证滚动容器和底部布局。用户已选择创建关联缺陷。

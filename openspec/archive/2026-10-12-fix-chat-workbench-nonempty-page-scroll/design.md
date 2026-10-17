---
title: Chat 消息卡片局部定位与滚动边界设计
created_at: 2026-10-06 21:29:10
updated_at: 2026-10-06 21:29:10
---

# Chat 消息卡片局部定位与滚动边界设计

## 根因与修复方案

依据 BUG-0029 root-cause.md E1–E5：`.chat-message > strong` 为视觉隐藏绝对定位元素，卡片未提供定位上下文，Firefox 的 offsetParent 为 BODY，长对话将页面高度由 832 撑至 2021。临时为卡片设置 position:relative 后高度回到 832，恢复后再次溢出。

在 `src/web/src/styles/chat-workbench.css` 为 `.chat-message` 建立局部定位上下文，保持角色标签隐藏方式和语义。检查 `ConversationMessages.tsx` 的直接子级结构及卡片其他定位元素。拒绝以删除语义标签或全局 overflow:hidden 代替根因修复。

## 验证策略

采用真实布局浏览器测试，不用 jsdom 尺寸模拟替代布局断言。Firefox 与 Chromium 覆盖空白、短消息、长对话；视口包含 1419×832 和 1440×900 CSS px，记录缩放及设备像素比。断言页面 scrollHeight-clientHeight 不超过 1px，页面 scrollTop 不随消息区滚动改变，消息首尾可达，输入区可聚焦编辑。

运行态采集 selector、offsetParent、position、overflow、尺寸及滚动前后截图，核对输入区、背景、悬浮元素。自动化测试数据可使用合成消息；真实产品观察另行记录，不复制聊天正文或凭证。关联 BUG acceptance.md AC-001–AC-006 全部回填实际结果。

## 风险与回滚

卡片建立定位上下文可能影响其其他绝对定位子元素，需对复制按钮、角色标识等逐项检查。回滚仅撤回局部样式；不涉及数据迁移。没有实际跨浏览器结果时不得宣称验收通过。

## 边界与文档同步

本次是局部布局缺陷修复，不是参考稿复刻，不引入新按钮、弹窗或页面结构。沿用既有 UI 基准，保留前后视觉证据；同步 BUG 验收和 Change trace。API、DB、部署、安全权限和客户端生成均不变。

product_data_collection_observability: not_applicable

affected_layers: []

reason: 仅修改消息卡片定位样式与回归测试，不改变请求封装、接口、数据库、usage_events、request_logs、Task Trace 或对象存储；不新增产品埋点。

validation: 实施时复核差异范围并执行浏览器布局与发送回归；当前只完成规划，测试未执行。

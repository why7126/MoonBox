---
title: "历史消息宽度与候选恢复复验"
created_at: 2026-10-14 10:03:00
updated_at: 2026-10-14 10:03:00
---

# 历史消息宽度与候选恢复复验

结论：通过。

证据：BUG-1001 助手外层消息和历史轨道 computed width 都是 1168px；前端聚焦测试验证历史仅轮询已有 operation、prepared 空候选不发 POST，3 个相关测试通过。

缺口：历史重开采用既有隔离 BUG-0037 与 REQ-0045 的真实产品轮次：历史入口可恢复对话且后端记录只有已有 application 的 GET、没有 candidate/application POST；此前产品证据已记入 Issue acceptance.md 的 AC-021 段。本轮 BUG-1001 新增 1440×900 助手外层宽度与 DOM 复核。浏览器会话随后过期，未重开 BUG-1001，但不影响上述历史轮次证据。

数据边界：专用隔离项目；未触碰正式 BUG 样本。当前五项保持未勾选。

---
bug_id: BUG-0029-chat-workbench-nonempty-page-scroll
title: Chat 工作台非空白对话出现页面级滚动条及底部布局异常根因分析
root_cause_status: confirmed
owner: 产品团队
created_at: 2026-10-05 23:22:51
updated_at: 2026-10-06 00:32:39
---

# Chat 工作台非空白对话出现页面级滚动条及底部布局异常根因分析

## 根因状态

status: confirmed

## 现象

在本机 MoonBox `/chat` 的 BUG-0029 非空白长对话中，页面外层产生可实际滚动的额外高度；消息区域自身也有内部滚动。浏览器为 Firefox，工作台版本标识 `v0.1.0`，测量视口为 1419×832 CSS px、设备像素比 2。取证未保存会话正文、账号和完整查询参数。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | reproduction | Firefox DevTools，`/chat` 的 BUG-0029 长对话，2026-10-06 00:30–00:33 | `body.clientHeight=832`、`body.scrollHeight=2021`；`window.scrollTo` 后 `body.scrollTop` 从 0 到 1189，恢复为 0 | 直接证明非空白对话产生页面级滚动，最大滚动量为 1189 px |
| E2 | computed_style | 同一页面的 DOM/计算样式测量 | `.chat-shell` 高 832、`overflow-y:hidden`；`.chat-conversation` 高 541、`scrollHeight=2279`、`overflow-y:auto`；10 个 `.chat-message > strong` 为 `position:absolute`，`offsetParent=BODY`，最远元素底部为 2021 | 消息区内部滚动设计仍存在；消息中的视觉隐藏标签脱离滚动容器，落到页面根层定位上下文并撑高页面 |
| E3 | reproduction | Firefox DevTools 临时样式对照，随后立即恢复 | 将 10 个 `.chat-message > strong` 临时设为 `position:static`：`body.scrollHeight` 2021→832；移除临时属性后恢复 2021 | 单变量对照证明这些绝对定位标签直接导致页面溢出 |
| E4 | reproduction | Firefox DevTools 第二次临时样式对照，随后立即恢复 | 将 10 个 `.chat-message` 临时设为 `position:relative`：`body.scrollHeight` 2021→832；子级 `strong.offsetParent` 变为消息卡片；恢复后回到 2021 | 建立消息卡片定位上下文可将视觉隐藏标签留在正确的滚动层，支持最小修复方向 |
| E5 | code_path | `src/web/src/components/chat/ConversationMessages.tsx:245-247`、`src/web/src/styles/chat-workbench.css:216-217` | 每条消息的 `article.chat-message` 直接包含用于标识角色的 `strong`；CSS 将 `strong` 绝对定位，却未给消息卡片建立定位上下文 | 将运行态异常定位到具体渲染结构与样式规则 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| 消息区没有内部滚动能力 | E2 显示消息区 `overflow-y:auto` 且 `scrollHeight > clientHeight` |
| 仅是工作台壳自身高度超过视口 | E2 显示壳高度与视口同为 832 px |
| 与 BUG-0027 的浅色背景来源是同一直接根因 | 本条 E2–E4 指向消息角色标签的绝对定位；BUG-0027 的已归档根因是根层背景颜色。两者可共同影响底部观感，但直接机制不同 |

## 已确认根因

消息组件为每条消息渲染一个视觉隐藏的 `strong` 角色标签，并通过 `.chat-message > strong { position:absolute; ... }` 隐藏它；`.chat-message` 未设置定位上下文。Firefox 中这些绝对定位元素的 `offsetParent` 因而是 `BODY`。长对话使后续标签按消息流位置落在视口以下，最远延伸到 2021 px；它们越过工作台内部滚动边界，将 `body.scrollHeight` 撑大，产生页面级垂直滚动条和滚到底部后的布局偏移。

## 修复方向

优先为 `.chat-message` 建立局部定位上下文，保留 `strong` 的语义和视觉隐藏行为。E4 已在浏览器中证明 `position:relative` 可消除页面外层溢出。实现阶段仍需检查消息卡片内部其他定位元素、不同浏览器及短/长消息场景；不以全局 `overflow:hidden` 掩盖溢出。

## 验证闭环

本轮只验证了根因和临时样式因果对照，未修改源码、未声明修复完成。正式修复后执行 [验收标准](acceptance.md) 的空白/短/长对话、页面与消息区滚动、输入区可见性及跨视口回归；真实浏览器观察与自动化测试分别记录。

---
title: AC-030 Chat 运行中助手输出全宽复验
created_at: 2026-10-14 15:49:00
updated_at: 2026-10-14 15:49:00
---

# AC-030 Chat 运行中助手输出全宽复验

结论：通过。宽度由 role=assistant 的通用 CSS 与组件结构决定，不按命令名或 action 白名单切换。

隔离产品 BUG-0039 `bug-generate` 执行中留存的 1440×900 与 390×900 截图和 computed style 见 `AC-030-assistant-running-*`：历史轨道与 assistant block/article 分别为 1168/294px，正文内容列及 bubble 分别为 1126/252px；用户消息仍右对齐且限宽。该旧产品样本所用样式和组件在本轮未改动。

本轮 Playwright 使用正式 Chat CSS 构造 11 个命令/阶段 DOM 样本，含 req-generate、req-complete、bug-generate、bug-complete、req/bug review、sprint、opsx、普通 Chat running、完成及历史恢复。11/11 样本、0 错误；每个 running 样本的 assistant block/article=1376px 历史轨道，内容列/TurnActivity/status/bubble=1334px。`AC-030-playwright-matrix.json` 保存每个样本的 computed width；`AC-030-req-complete-running-1440x920.png` 与同名样式 JSON 保留指定 req-complete 场景。真实 Web 组件加合成 API 的 390、1440、1920px running/saved/history 矩阵另有 9/9 结果，详见 `AC-027-playwright-matrix.json`；`chat-messages.test.tsx` 9/9 通过。

证据边界：本轮 req-complete 截图是正式 CSS 的合成 DOM，并非真实产品 req-complete 执行轮次；隔离产品真实执行中样本为 bug-generate。其他命令的宽度由通用 selector 与 Playwright 矩阵核对。`product_data_collection_observability: applicable`；`affected_layers: [web_runtime, chat_events]`；本轮未改 API、DB、埋点或 Task Trace。

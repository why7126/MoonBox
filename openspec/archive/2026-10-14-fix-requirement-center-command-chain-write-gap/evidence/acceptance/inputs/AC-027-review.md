---
title: AC-027 Chat 助手输出全宽布局复验
created_at: 2026-10-14 15:34:00
updated_at: 2026-10-14 15:34:00
---

# AC-027 Chat 助手输出全宽布局复验

结论：通过。按 role=assistant 的布局规则在产品历史轮次、隔离产品执行中轮次、Playwright 命令矩阵与真实组件合成 API 矩阵中一致；用户气泡保持右侧限宽。

## 真实产品与视觉证据

| 来源与状态 | 视口 | 历史轨道 / assistant block / article | 内容列 / Activity / bubble / markdown 或 alert | 用户气泡 |
|---|---:|---:|---:|---:|
| 39002 BUG-0036 `bug-generate` 历史恢复、展开正文 | 1440×900 | 1168 / 1168 / 1168px | 1126 / 1126 / 1126 / 1126px | 190.88px，右对齐；user article 760px |
| 同一产品会话 | 390×900 | 294 / 294 / 294px | 252 / 252 / 252 / 252px | 190.88px，右对齐 |
| 39002 REQ-0041 `req-generate` 历史恢复、完成正文及执行前 alert | 1440×900 | 三个 assistant block/article 均 1168px | 三个内容列/Activity 均 1126px；alert、完成 bubble/markdown 均 1126px | 三个 user article 均 760px；气泡分别为 183.8、183.8、417.7px |
| 隔离产品 BUG-0036 `bug-complete` 执行中，2026-10-13 已留存 | 1440×900、390×900 | 分别为 1168、294px | Activity/status 所在内容列分别为 1126、252px | 仍受限宽 |

本轮新截图为 `AC-027-当前产品场景-1440x900.jpg`、`AC-027-当前产品场景-390x900.jpg`、`AC-027-req-generate-history-1440x900.jpg`，计算样式分别见同名 `-style.json`。执行中真实产品旧截图及样式见 `AC-027-running-1440x900.png` 与同名 `-style.json`；其所用 CSS 和组件文件在截图时间后未改动。

## 自动回归覆盖

`chat-messages.test.tsx` 9/9 通过，断言真实组件 DOM、assistant 的 block/article/content column、Activity/status，以及用户 bubble 的限宽。`tests/chat-assistant-width.cjs` 的 Playwright 11/11 样本、0 错误，覆盖 req/bug generate、req/bug complete、req/bug review、sprint、opsx、普通 Chat 的 running，以及普通 completed 和 history restored。该矩阵使用真实 CSS 与合成 HTML。`tests/chat-live-output-width.cjs` 在 390、1440、1920px 的 running/saved/history 三阶段共 9/9 通过；此矩阵运行真实 Web 组件，但 API 为合成响应。脱敏尺寸结果汇总为 `AC-027-playwright-matrix.json`，原始截图和运行日志仍保留在 Git 忽略的本地日志目录，不入仓。

证据边界：本轮共享产品无活跃执行中的 Chat turn，普通 Chat 和各命令的 running 状态由上述 Playwright 矩阵验证；真实产品取证覆盖 BUG Generate 历史、REQ Generate 完成与 alert，并复核了此前隔离产品 bug-complete 执行中的截图及样式。所有命令使用同一 role=assistant CSS selector，未按命令名分支。

`product_data_collection_observability: applicable`；`affected_layers: [web_runtime, chat_events]`。本轮只读采样 DOM/computed style 与现有浏览器数据，不增改 API、DB、埋点或 Task Trace；`validation` 为 9 项组件测试、11 项 CSS Playwright 矩阵、9 项真实组件合成 API 矩阵及上述产品宽度采样。

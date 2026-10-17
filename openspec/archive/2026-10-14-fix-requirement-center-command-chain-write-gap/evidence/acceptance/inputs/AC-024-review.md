---
title: AC-024 Web 构建版本与历史入口清理复验
created_at: 2026-10-14 15:07:00
updated_at: 2026-10-14 15:07:00
---

# AC-024 Web 构建版本与历史入口清理复验

结论：通过。运行态当前 bundle 与 39002 服务 HTML 引用一致，旧 bundle 单次刷新及旧面板清理由当前实现和聚焦回归覆盖；历史入口的真实产品 DOM、截图与浏览器资源清单无治理大面板。

## 构建版本与旧 bundle 恢复

`App` 启动调用 `ensureCurrentRuntimeBundle`。生产环境以 `cache: no-store` 获取当前页面 HTML，比较页面已运行脚本与服务端最新脚本；不同时记录目标并刷新，同一目标在 sessionStorage 中只刷新一次。`runtimeBuild.test.ts` 验证旧脚本仅刷新一次、当前脚本不刷新及旧面板清理，3/3 通过。`governance.test.tsx` 的 17 项历史和自动应用轻量 UI 回归一并通过。命令使用 `NODE_OPTIONS=--no-experimental-webstorage` 以避免本机 Node 25 的全局 localStorage 与 jsdom 冲突；未修改产品代码。

39002 浏览器运行脚本和服务端 `/chat` HTML 均为 `/assets/index-evpnFHfi.js`；运行态根元素有非空构建 ID `mv7pwl7p-exvnom`。实际服务 bundle SHA256 为 `30ff6825590c713ad77f21c686868a8ee59294915901aea4d2ff381687302a65`，包含 `moonbox.web.build-id` 和 `moonbox.web.reload-target` 标识；“待应用成果”“查看成果”“审阅治理成果”“确认应用”字面串均为 0。本机 dist 又生成了 `index-CRdXItKX.js`；两份 bundle 仅随机 build ID 不同，替换该 ID 后正文逐字节一致，故没有代码版本落后。

## 历史入口产品观察

在已登录的 Chrome 39002 产品中，设置 1440×900 视口，打开“历史”列表并点选 `BUG-0036-bug · 生成 Bug`。当前页面有两条旧 Generate 轮次及轻量治理校验提示。DOM 中 `.chat-main > .pg-result` 和 `governance-result-preview` 共 0，dialog 共 0，“查看成果”“待应用成果”“审阅治理成果”“确认应用”按钮共 0。截图为 `AC-024-当前产品场景-1440x900.jpg`，样式及脱敏资源路径为同名 `-style.json`。

浏览器资源清单记录当前脚本、CSS、无缓存检查涉及的 `/chat`，以及历史会话消息、轮次、候选和事件读取路径；未观察到治理 application 创建路径。资源清单不含请求方法和响应体，因此只支持请求路径观察。旧 DOM 节点清理的命中行为由对应单元测试证明，真实历史入口证明清理后无旧面板；本轮未人为注入旧节点或替换正在使用的产品 bundle。

`product_data_collection_observability: applicable`；`affected_layers: [web_runtime, chat_events]`。本轮只读浏览器资源元数据与现有产品数据，不改 API、DB、日志、埋点或 Task Trace；`validation` 为 20 项前端回归通过、当前 HTML 与运行脚本一致、历史 DOM 和资源路径核对。

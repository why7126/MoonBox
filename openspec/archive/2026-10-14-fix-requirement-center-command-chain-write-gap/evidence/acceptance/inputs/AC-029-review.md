---
title: AC-029 Chat 网络异常分层提示复验
created_at: 2026-10-14 15:49:00
updated_at: 2026-10-14 15:49:00
---

# AC-029 Chat 网络异常分层提示复验

结论：通过受控故障注入和前端回归；故障注入运行的是 39002 实际 Web 构建，API 响应为合成数据，浏览器主动中断指定请求，不把它记为共享后端真实故障。

Playwright `chat-network-failure.cjs` 对工作台启动 `/spaces`、项目能力绑定 `/capabilities`、消息 `/messages`、治理候选 `/governance-candidates`、turn 轮询 `/turns` 和执行轨迹 `/events` 逐一注入网络失败，6/6 场景通过，浏览器页面均未显示 `NetworkError when attempting to fetch resource.` 或 `Failed to fetch`。启动和绑定显示中文连接提示；消息读取显示“消息暂不可读，请稍后重试”；governance、turn、events 失败后已生成助手消息仍可见。六场景的请求次数、可见文案与 computed style 记录在 `AC-029-network-failure-matrix.json`，Chat 页面截图见 `AC-029-events-1440x900.png`、`AC-029-messages-1440x900.png`，其余场景截图同目录。需求中心旧 `AC-029-context-refresh-failure-1440x900.jpg` 只作背景，不作为 Chat 通过依据。

前端测试 `chat-events.test.ts` 核对 fetch 错误归一化和 AbortError 保留；`chat-workbench.test.tsx` 核对已生成消息不被 turn 读取失败覆盖；`chat-messages.test.tsx` 核对局部消息错误；`chat-capabilities-recovery.test.tsx` 核对绑定能力中断后的草稿保留和恢复。合计 31/31 通过。

证据边界：本轮未破坏共享后端网络，也未重新发送真实治理命令；注入场景通过浏览器运行产品 bundle，覆盖发送后等价的已生成消息和轮询阶段。`product_data_collection_observability: applicable`；`affected_layers: [web_runtime, chat_events]`；验证只读 UI 与受控浏览器注入，不改 API、DB、埋点或 Task Trace。

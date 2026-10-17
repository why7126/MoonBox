---
title: Chat 助手正文修复验证与待验事项
created_at: 2026-10-08 19:56:38
updated_at: 2026-10-08 20:00:09
status: verified
---

# Chat 助手正文修复验证与待验事项

## 已验证

- 根因证据门禁通过，确认当前合成机制；历史 T1/T2 不可验证。
- 后端 Chat、执行、工具记录、长运行及新增正文测试：最终68 passed、2 skipped，其中正文聚焦套件14项；包含最终答案有无增量、并发恢复、字符上限与工具输出排除。
- 前端 TypeScript 检查通过；可移植 DOM 检查 unknown/stopped/failed/completed 四种状态通过，正文只显示一次，部分输出及未知警告保留。命令：`node src/web/tests/chat-assistant-output-dom.cjs`。这是合成 API + 真实 React 组件的 DOM 检查，不是浏览器视觉验收。
- 消息接口 OpenAPI 已聚焦导出，Orval Chat 客户端已生成。无数据库结构迁移、部署服务、对象存储或授权政策变化。

## 测试环境适配

仓库虚拟环境 Python 链接不可用，使用环境可用 Python，追加现有测试包目录并将 TestClient 配置为 uvloop 后运行。默认 asyncio portal 在本环境挂起，20秒诊断栈停在 TestClient 的跨线程调用；未修改业务实现以绕过断言。

复跑标准命令：`PYTHONPATH=src/backend:src/backend/tests src/backend/.venv/bin/python -m pytest -q src/backend/tests/test_chat_assistant_output.py src/backend/tests/test_chat.py src/backend/tests/test_chat_local_execution.py src/backend/tests/test_chat_tool_record.py src/backend/tests/test_chat_long_running.py`；本环境需采用上述解释器/uvloop适配。

## 浏览器验证补证

2026-10-08 的环境中 Firefox 与 Chromium 的 Playwright launch 返回 browser executable missing；前端 Vitest/Vite 缺少 Linux ARM64 Rollup 原生依赖，网络安装因 DNS 不可用失败。2026-10-09 已通过 REQ-0044 独立 runner 与真实 Linux ARM64 制品解决该验证环境缺口，补证见下文。

任务2.3、3.4所需的 1440px/窄屏浏览器布局、computed style、刷新重进与轨迹切换证据已于 2026-10-09 补齐；原故障实例 T1/T2 已删除，仍不可复验。BUG Change 的剩余任务、验收矩阵和完成态同步须在其自身 apply 中核对，不能由 REQ-0044 的证据回填自动宣告完成。

## 观测与安全边界

product_data_collection_observability：applicable。affected_layers：chat_messages、execution_events、request_logs、task_traces、task_trace_spans。validation：隔离消息/事件/状态/API关联、幂等、权限及有界读取回归通过；真实浏览器合成 API 场景已验证；原历史故障轮次不可验证。未新增 usage_events 动作；请求链路协议、保留周期、部署与对象存储均未修改。没有访问真实会话正文或重放业务命令。

## 治理校验与环境遗留

OpenSpec strict、当前 Change 中文/残留分离、6份文档标题、Agent 上下文预算与观测行为轨迹校验通过。Scope 和 opsx.progress 同步复核用于保持研发中，不代表完成。目录校验因已有根目录 .codex 未登记而失败；未删除归属未确认的工具目录。全仓 Design System 校验有178项既有样式/原生控件违规，本次未新增原生表单控件或修改 CSS，未扩大修复范围。

浏览器脚本为 `node src/web/tests/chat-assistant-output.cjs`，默认 Firefox，支持 `CHAT_TEST_BROWSER=chromium` 与 `CHAT_TEST_URL`。2026-10-09 已在隔离容器中使用当前 Web 构建及真实浏览器执行；DOM 回归、浏览器用例和后端测试均保留在 src 测试目录。

## 2026-10-09 REQ-0044 平台浏览器补证

当前源码独立构建的 Web 页面与合成 API 在真实 Firefox、Chromium 中均完成 unknown、stopped、failed、completed 四状态的 1440px/390px、打开/刷新回归，每浏览器 16 个场景和 16 张私有截图。正文、部分输出标识、unknown 不重复发送提示和视图切换断言通过；computed style 采样中助手列均无横向溢出。Firefox `1440-unknown-open.png` SHA256 为 `3b067252ce0e85f2bae1deb21885abec8d71c235de46113884b8190f016cd7a3`，Chromium 为 `49c6071faacd894dfb5c76f0fba7ce1eb49f8e2ed29527a816dee263bf07493c`。截图与摘要位于 Git 忽略的私有 `data/runtime/verification-bug-browser/`，不含真实会话内容。测试修复了将隐藏对话 DOM 错判为应被移除的断言，并将视口宽度与元素宽度分别记录；未降低正文或状态断言。

已登录的本地历史 BUG-0030 会话另行做只读浏览器观察：9 个正文气泡在刷新、轨迹切换和切回后保持数量及长度一致；1440px 助手列宽和 scrollWidth/clientWidth 均为 1126px，390px 均为 252px。未保存原始正文或截图。已删除的历史故障轮次 T1/T2 仍不可复验；合成 API 浏览器通过不代表对真实 unknown 轮次重新观察到同一行为。

AI Usage 自动定位未发现本地 session 来源，无法归因本次用量；不编造 token 数据。

## 本轮完成态复核

2026-10-09 使用仓库虚拟环境复跑后端相关套件：68 passed、2 skipped；前端 TypeScript 与合成 DOM 四状态检查通过。已复核 Firefox/Chromium 各 16 张私有截图存在且桌面 unknown 截图 SHA256 与原记录一致。原历史 T1/T2 不可复验，不将合成 API 浏览器通过写成原实例再现。

## 交付校验与已知告警

OpenSpec strict、当前 Change 中文、BUG/Change 中文标题、产品数据采集与链路观测、测试框架、目录结构及 `git diff --check` 通过。全仓 API 标准校验仅报告现存 `src/backend/app/api/v1/capture_drafts.py:53` 的 `image` 路由缺少 `response_model`；该路由不是 BUG-0030 修改范围，作为独立存量告警，不在本 Change 更改其契约。前端 TypeScript 与四状态 DOM 检查通过；后端 68 passed、2 skipped。

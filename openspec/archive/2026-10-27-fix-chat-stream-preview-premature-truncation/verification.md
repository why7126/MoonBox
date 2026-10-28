---
title: Chat 流式预览实施与验证记录
created_at: '2026-10-26 22:36:00'
updated_at: '2026-10-26 22:36:00'
---

# Chat 流式预览实施与验证记录

## 修复结果

去除固定 21 段判断，以字符、片段和字节预算读取，并通过额外元数据判断真实剩余。新增范围原因，前端区分展示限制、历史缺口和数据损坏。完整输出按页替换正文，支持前后页、失败重试、最终版本切换和跨轮次响应隔离。保护已有完整助手消息不被截断投影覆盖。

## 命令回归

- 红测：原实现的 20 段通过，21/22/294 段失败；与原现场截图半句一致。
- SQLite：preview、assistant_output、final_answer 合计 42 项通过；加入分片粒度用例后的最终验收批次 47 项通过。content_store 8 项通过。
- MySQL 8.2 临时空库：同组 35 项通过；新增边界/状态后的 preview 22 项通过。最终粒度/保护 6 项及旧格式反馈 2 项增量通过。测试数据库独立，不连接用户业务库。
- 前端：full-output、unified-run-status、chat-assistant-output 共 33 项通过；TypeScript 构建检查通过。测试从 src/web 执行，Node 25 使用 --no-experimental-webstorage；首次错误工作目录导致 setup 解析失败已纠正。
- 4096、4097、16384 段规模保持最多 20 次 SELECT；断言查询没有写操作。单页 262143/262144/262145 bytes 的边界可终止；200000 字符恰好预算不误报。
- 无新增数据库迁移、部署配置或权限扩张；API 增加可空字段，OpenAPI/客户端已生成，沿用既有请求审计。

## 浏览器视觉签认

使用 Chrome、当前源码的 ConversationMessages/TurnActivity/FullOutput、真实 FastAPI HTTP 读取及临时 SQLite。身份仅为隔离 fixture；503 错误由 fixture 模拟。上游 Agent 未在此 fixture 执行，不能把这组样本写成真实 Agent 轮次通过。

| 阶段 | 1440×900 | 390×844 | 目视结论 |
|---|---|---|---|
| 294 小片段运行中 | visual/short-1440.png | visual/short-390.png | 正文可读，无不完整警告 |
| 4097 段受限预览 | visual/limited-1440.png | visual/limited-390.png | 仅展示部分输出、完整内容入口可见 |
| 完整内容窗口 | visual/opened-1440.png | visual/opened-390.png | 共享对话框在视口内，正文独立滚动，前后页可操作 |
| 读取失败 | visual/error-1440.png | visual/error-390.png | 错误及重试清楚，未显示虚构成功 |
| 选定最终答复 | visual/final-1440.png | visual/final-390.png | 完成状态与正文一致，合法重复保留 |

路径均相对 evidence/acceptance/。computed-style.json 核对 pre-wrap、anywhere、overflow-y:auto；窄屏弹窗宽 358px、左右 16px，未越出 390px。已实际点击下一页到第 2 页及上一页回第 1 页。页面内合成测试控制条不属于交付产品界面。

## 真实轮次验收

用户授权后，执行标准配对部署脚本 `bash scripts/docker-down.sh self-storage-sqlite` 与 `bash scripts/docker-up.sh self-storage-sqlite`。原数据保留；backend、chat-worker、governance-controller 健康，Web 可访问。后端 assistant_output/output_window/result_reader 的运行态 SHA-256 与本地源码一致；实际 Web bundle 命中“仅展示部分输出”；controller 心跳就绪。

第一次测试在模型启动前的快照准备阶段出现 OperationalError，标记 result_persistence_failed；未产生执行器轮次或工具命令。数据库 quick_check 为 ok；具体异常根因未确认，不归因为本次预览修复。安全重试一次后成功，不重放原业务命令。

同一成功轮次 `f21b13b3-8df5-4005-97c9-0edbc8f2e6f3`：status completed、error_code 空，output 293 段、final 1 段，仅 printf BUG0067_READ_ONLY_ACCEPTANCE 一次命令，exit_code 0，files/cumulative_files 为空。运行中在事件序号 155 附近观察到正文 312 字且无缺失提示；后续最终正文保留合法重复。真实产品不是 fixture，完全只读权限未放宽。

已目视核对 `evidence/acceptance/visual/real-final-1440.png` 和 `real-final-390.png`，裁剪仅保留助手状态和合成验收答复，不含原始 Prompt。五类边界矩阵仍属于隔离 HTTP/页面证据，真实轮次只签认实际观察到的运行及完成表现。验收会话保留供追溯。

## 数据与资源边界

product_data_collection_observability: applicable；affected_layers: Web、API、DB 读取。无新增 request_logs/usage_events/Task Trace 字段或写入，复用原鉴权与请求审计；测试断言业务状态和消息数不因读取改变。截图仅含合成正文，未转存真实会话原文、凭证或数据库。临时 MySQL 与浏览器服务在阶段结束清理，AI 用量由命令 Hook 独立采集。

## 验收检查点

首次诊断保留：8 项通过、0 失败、1 项待采集。真实轮次证据已补齐，使用当前计划重新执行完整验收，避免把旧诊断冒充 ready。

临时隔离环境容器/专属网络均为 0，临时监听服务已关闭；正式本地服务保持运行。浏览器视口覆盖已恢复。

当前完整验收：`evidence/acceptance/20261026224933578470-95649d01/summary.md`，9/9 passed，0 failed，0 blocked；8 项复用。首次沙箱网络预检失败在获得本机网络权限后通过，未重复执行模型动作。

最终证据：evidence/acceptance/20261026225142511044-12b2315e/summary.md，9/9 passed，8 项复用；规格全文绑定已补齐，最终归档准入 ready，未执行正式归档。

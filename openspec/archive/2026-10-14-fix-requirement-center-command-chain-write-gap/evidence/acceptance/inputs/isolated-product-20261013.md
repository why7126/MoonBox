---
title: BUG-0025 隔离产品复验阶段证据
created_at: 2026-10-13 17:37:00
updated_at: 2026-10-13 20:45:00
---

# BUG-0025 隔离产品复验阶段证据

## 环境

- 当前代码副本：`/private/tmp/moonbox-bug0025-acceptance-isolated`。业务源代码由当前工作区同步；Issue、迭代及数据库保留独立测试数据。
- Web `127.0.0.1:39102`，后端 `127.0.0.1:39101`，隔离 Compose 网络 `moonbox-bug0025-network`；后端健康检查返回 200。
- 独立 SQLite 是本地库的离线快照，后续写入只发生在隔离副本。数据库与私有凭证不进入证据包。
- 需求中心初次读取约 1.3 MB 的历史对象，曾显示加载失败；将隔离副本中无关历史目录移入隔离运行目录备份后，产品看板显示专用 BUG-0037、BUG-0038、BUG-0039 和 REQ-0045。随后将两份隔离 registry 备份并收敛为这四个对象，避免 11 个缺文件历史对象继续进入投影。
- 为排除历史工作区基线与请求日志对隔离服务的影响，先将 SQLite 完整备份到隔离运行目录，再仅在隔离库保留本轮会话的基线与当日请求日志，并执行 VACUUM；库体积从约 185 MB 降至约 17 MB。此操作不触及共享库，重启后的产品复验结果另行记录。

## 视觉观察

| 样本 | 阶段 | 视口 | 截图 | 观察 |
|---|---|---|---|---|
| BUG-0038 | 规划中 draft | 1440×900 | [截图](AC-043-draft-1440x900.jpg) | 显示 `bug.md`、`trace.md`、`capture.md` 与“完善 Bug”；无独立 draft 标签。 |
| BUG-0038 | 规划中 draft | 390×900 | [截图](AC-043-draft-390x900.jpg) | 水平滚动对齐后卡片 x=89–389，文档、动作和负责人省略均可见。 |
| BUG-0037 | 规划中 enriching | 1440×900 | [截图](AC-043-enriching-1440x900.jpg) | 显示六份 Issue 文档、根因补证提示及“继续完善”。 |
| BUG-0037 | 规划中 enriching | 390×900 | [截图](AC-043-enriching-390x900.jpg) | 经水平滚动对齐后，300px 卡片完整显示于 x=89–389，无提示文字溢出；负责人 ellipsis。 |

DOM computed style 采样：两种视口中规划卡片 `display:flex`、`padding:15px 16px 18px`、宽 300px；负责人标签 `overflow:hidden`、`text-overflow:ellipsis`、`white-space:nowrap`，测得宽 223.938px。BUG-0037 移动卡片矩形为 x=89–389、y=567.07–778.86。该采样仅支持规划阶段卡片，未覆盖其他 AC 的阶段、视口和状态。

运行中 BUG-0039 Chat 助手输出：[1440×900 截图](AC-030-assistant-running-1440x900.jpg)、[390×900 截图](AC-030-assistant-running-390x900.jpg)；[桌面 computed style](AC-030-assistant-running-1440x900-style.json)、[移动 computed style](AC-030-assistant-running-390x900-style.json)。桌面消息历史与 assistant article 均宽 1168px，assistant bubble 为扣除 42px 头像列后的 1126px；移动端分别为 294px 和 252px，`max-width:none`。用户消息在桌面右对齐且宽 760px。该轮只覆盖 `bug-generate` 的运行中布局，不代替普通 Chat 和其他命令族的矩阵。

## 产品轮次

- 从 BUG-0039 看板动作进入 Chat，准备态输入框显示简洁 `/bug-generate BUG-0039`，主对象为完整 ID；[准备态/运行态截图](AC-052-stale-kind-chat-1440x900.jpg)。
- 2026-10-13 17:32:11 在隔离环境点击发送，数据库轮次 `fb856ea0-fb5a-4c34-a27a-421bbcafb684`。17:41:34 仍为 `running`，心跳同步更新，累计 254 条事件，已跨越 300 秒而未被默认墙钟上限中断；这覆盖 AC-038 的长运行观察片段。17:43:38 轮次 `completed`，无错误码。Chat 历史只展示可见命令 `/bug-generate BUG-0039`，点击“复制消息”后浏览器剪贴板读取同一字符串，无内部治理约束。
- 同轮 candidate `40c29637-50af-5825-92c1-e383937cbc11` 为 `applied`、无错误码；application `b627a50b-1102-4b22-9eac-9d93ee2f32f9` 为 `applied / verified`、无错误码。隔离事实源新增 `bug.md`，trace 与 registry 均为 `draft / plan`，CHANGELOG 下一步为 `/bug-complete BUG-0039-acceptance-stale-kind`；产品看板刷新后 BUG-0039 从采集池进入规划中并显示 `bug.md`、`完善 Bug`。这补充 AC-004、005、012 的同轮真实产品证据。
- 该轮**没有**产生 `workspace_fact_source_stale`，因此不能作为 AC-052 的新轮次通过证据。应用后历史 Chat 显示“完全只读：治理候选对象已失效”，重载后仍如此；同会话继续 complete 的写入能力需单独复验。
- 运行期间看板出现“更新失败，上次成功同步 17:35:02，写入已暂停”。这说明新一轮上下文读取不稳定，需以服务和文件事实进一步定位；先前已成功渲染的页面不能证明当前读写可用。
- 隔离库缩减并重启后，后端健康端点曾返回 HTTP 200（0.32–0.43 秒），看板在约一分钟后显示四个专用对象。但 Compose 首次就绪等待因后端健康检查超时失败，Chat worker 的执行器预检未生成 `worker-ready.json`，容器出现一次自动重启；因此不能按产品可写就绪处理。
- 18:12 后点击 BUG-0039 的“完善 Bug”，按钮短暂禁用后回到看板，并显示“更新失败…写入已暂停”；[画面](AC-041-isolated-continue-blocked-1440x900.jpg)。同会话 complete 未产生新轮次和应用记录，AC-041 的新轮次续接仍未通过。
- 打开 BUG-0037 的 `root-cause.md` 抽屉，先显示“Markdown 加载中”，随后显示“文档暂时无法加载 / 当前项目数据读取失败”；[失败画面](AC-043-document-load-failed-1440x900.jpg)。这轮不能证明 AC-043 的子文档可打开。

## 自动验收

- 19:33 后隔离 backend、worker 与 MinIO 恢复健康。旧未绑定候选选择偏差已按当前 Change AF-043 修复，后端聚焦 3 passed。BUG-0039 原会话 `bug-complete` 轮次 `c87b495f-9b33-4e41-bebe-5b761323fdad` completed；候选 `9ca95dc3-fadd-5825-87b4-2d29381df6fa` 与应用 `8509853c-83fa-44e8-9eb2-ea6f360316df` 均 applied，trace/registry 为 enriching、完成时间 null。证据见 `AC-041-review.md` 与当前产品截图。
- BUG-0037 `root-cause.md` 后续重试已在产品安全预览中打开，先前加载失败作为历史失败保留。draft/enriching 的四组截图已在服务健康时重新采集，样式 JSON 已补负责人完整 title 和 severity 宽度；AC-043、044 定向通过。
- 长运行 BUG-0039 生成轮次 11 分 27 秒完成，5 项长运行聚焦测试通过，AC-038 定向通过。17 项具备证据的检查在 `20261013195401693342-ea59ff96` 定向批量运行均 passed；完整清单因其余 35 项仍缺证据而输出 `blocked / diagnostic`，不构成 ready。

- 完整诊断 `20261013173243159682-d8e5c565`：52 项，14 passed、38 blocked，结论 blocked。
- 定向复验 AC-025 于 `20261013173324124400-02290103` 通过；完整诊断需在其余证据齐备后重跑，不提前宣称 ready。
- 本轮完整诊断 `20261013181018507195-487e4498`：52 项，12 passed、40 blocked，仍为 `blocked / diagnostic`。通过数较早前下降；不能把旧定向通过或历史人工勾选套用为本轮完整 ready。
- 收尾核验时隔离 backend 为 `unhealthy`、chat worker 处于自动重启，Web 与 MinIO 仍运行。OpenSpec 当前 Change 中文优先校验通过，6 份样式 JSON 可解析。未执行 `opsx.accept` Workflow Sync 或归档。

## 20:32 后隔离环境重建与新轮次

- 隔离源和运行目录在 20:32 左右被清空重建，原隔离 SQLite 的历史 Chat 轮次已不在当前数据库。重新复制当前代码到独立源，初始化独立备份存储并只重启隔离 Chat worker；当前 backend、worker、Web、MinIO 恢复可用。此前产品轮次的截图和证据文件作为**历史证据**保留，不能当作新数据库的当前轮次。
- 在产品 UI 中创建并批准专用隔离空间，绑定隔离源与新 SQLite。从需求中心 BUG-0036-bug 卡片进入 Chat，20:41:03 发送 `/bug-complete BUG-0036-bug`。轮次 `d2f97c04-1278-4196-9033-fb30dd83a0d9` 于 20:44:00 `completed`、无错误码；同轮候选 `e302bec5-3841-51e4-ae8c-931c303a069c` 为 `applied`，应用 `f6e8a59e-c504-4d50-a881-83339a3c1bab` 为 `applied/verified`。隔离源五份治理文档已保存；trace 为 `enriching`、完成时间为空，根因为 `unknown`。产品最终消息明确提示缺少异常与运行态证据，未执行完成态同步。此轮证明隔离对象的草稿写入和未确认根因门禁，不证明同会话 generate→complete 或 confirmed 根因升级。
- 运行中 Chat 的 [1440×900](AC-027-running-1440x900.png)、[390×900](AC-027-running-390x900.png) 与完成后的 [1440×900](AC-027-completed-1440x900.png)、[390×900](AC-027-completed-390x900.png) 截图均来自该产品轮次。运行中 [桌面样式](AC-027-running-1440x900-style.json)、[移动样式](AC-027-running-390x900-style.json) 显示 assistant article/block 宽度分别为 1168/294px，activity、bubble、markdown 扣除头像列后为 1126/252px，`max-width:none`。已目视检查截图；这些仅覆盖 `bug-complete` 的运行与完成状态，不能替代 AC-027/030 要求的全命令矩阵、历史恢复、普通 Chat 与 status/alert 采样。
- 完整 `/opsx-accept` 诊断 `20261013204500818933-ddb84103` 报告 52 项中 21 `passed`、31 `blocked`，结论 `blocked / diagnostic`。其中旧产品 turn ID 已不在当前隔离 SQLite，runner 对这些项沿用旧证据与历史结果；因此 21 项**不是本次数据库的 21 项新产品通过**，不能据此宣称当前环境 ready。尚未运行 `opsx.accept` 同步或归档。

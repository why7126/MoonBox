---
title: 需求中心验收投影与文档持续入口修复设计
created_at: 2026-10-09 23:00:00
updated_at: 2026-10-12 18:16:00
---

# 需求中心验收投影与文档持续入口修复设计

## 背景与现状

`BUG-0035-requirement-center-acceptance-readiness-projection` 根因已确认：后端人工验收待办固定为零，关联 Change 时用其文档清单覆盖 Issue 文档；前端再次按阶段白名单隐藏入口，归档按钮仅据任务计数判断。服务端归档仍独立阻断 BUG-0025。

## 修复方案

1. 以 Change `tasks.md` 保持研发、自动测试和人工任务门禁计数；研发与测试进度按钮复用当前关联 Change 的授权 `tasks.md` 文档入口并分别定位研发、测试章节，不能只查 Issue 自身文档，也不能在多 Change 来源不唯一时猜测。纯 Change 卡片仍打开自身 `tasks.md`。从 Issue `acceptance.md` 的 AC 勾选计算卡片“验收 已勾选数/总数”，另提取验收结论与证据缺口。验收按钮排在测试后并打开所属 Issue `acceptance.md`，不导航 Change tasks；悬浮说明明确当前计数只来自 Issue AC，自动验收结果尚未计入。三个进度仅在总数已知且完成数小于总数时把数字设为危险色，标签和已完成数字保留常规色；未知总数不显示虚假未完成。未勾选 AC 时合并重复阻断文案；全部勾选而结论仍 pending 时保留待签认提示。解析失败或来源不确定时给出待核验态，禁止将未知当通过。服务端归档时仍独立校验。
2. 在授权项目内分别枚举 Issue、当前关联 Change 和 Sprint 的真实文件，返回来源类型、对象 ID、文件名、可读能力与稳定读取身份。相同文件名保留各来源入口，不复用别的对象文件；缺失、目录冲突和权限不足返回脱敏不可用原因。关联 Sprint 的 `sprint.md`、`release-note.md`、`acceptance-report.md` 仅在真实存在且成员关系唯一时以只读入口展示。保留阶段写权限、归档只读和原项目隔离。
3. Web 卡片移除已生成文档的阶段过滤，按 Issue、Change、Sprint 三组和紧凑布局展示：Issue 组包含 BUG/REQ 各自主文档及 Issue trace，Change 组按钮直接用 `trace.md` 文件名，Sprint 三份文件独立成组；纯 Change 卡片不渲染 Issue 组。研发与测试进度仍指向 Change `tasks.md`，验收进度指向所属 Issue `acceptance.md`；较多文档可折叠，但入口始终可达。
4. Issue 验收逐项由验收人依据证据勾选并回填明确结论；当前验收阶段的页面文档读取仍为只读，本轮不增加文档写入权限。未勾选 AC 与缺少通过结论分别保守阻断归档，`opsx.apply` 或返修任务完成不自动代签验收。

验收中卡片的缺文档提示与可见入口使用同一来源口径：`trace.md` 核对 Issue 自身；`proposal.md`、`spec.md`、`design.md`、`tasks.md` 核对关联 Change 的授权文档清单。已在 Change 组显示的文档不得再被 Issue 自身清单误判为缺失。该修正不改变服务端验收结论或归档门禁。

## 接口与数据边界

若治理上下文响应需增加验收摘要、文档来源和阻断原因字段，同步 OpenAPI、生成客户端和 API 索引；只传状态、计数、受控标识与脱敏原因，不传完整文档正文、凭证或本机路径。文档读取沿用既有授权接口，新增字段不得放宽能力矩阵。无 DB schema 或数据迁移计划。

product_data_collection_observability: applicable；affected_layers: Web、治理上下文 API、授权文档读取 API、request_logs；validation: 对照归档请求状态与卡片摘要、文档读取授权和脱敏请求日志；纯 GET 与读取不伪造行为事件或 Task Trace，新交互如需埋点在实施时核定 usage_events；无 DB schema、对象存储或新保留周期，故这些层级暂为 N/A。

## 测试策略

按 BUG AC-001 至 AC-010 建立后端聚合、无权/缺失/冲突、前端跨阶段与归档提示回归；真实 BUG-0025 缺证据场景保持阻断。自动化与真实产品观察分开记录，桌面 1440px 和移动 390px 保存截图与 computed style 证据。前端先处理 Node 25/Vitest localStorage 初始化环境阻塞，再运行业务断言。

## UI Reference Replication Contract

保真模式为局部一致：用户截图用于确认现有卡片的研发/测试进度、文档入口和归档按钮位置；当前 MoonBox Ops 样式与既有页面为视觉事实源。保留九阶段看板、卡片密度、金色主动作和既有文档抽屉，不复刻截图分辨率或 Chat 页面。若截图与当前授权事实源冲突，以实际验收和归档门禁为准。

| 组件 | 参考锚点 | 目标 selector | 状态与视口 | 验收批次 |
|---|---|---|---|---|
| 文档区 | BUG-0025 卡片文档行 | `.rc-docs`、`.rc-doc-group`、`.rc-doc-source` | 已生成、同名、多文档；1440px/390px | 文档分组 |
| 进度与验收 | “研发 41/41、测试 37/37” | `.rc-progress`、`[data-testid="acceptance-readiness"]` | 满格但待验收；1440px/390px | 验收摘要 |
| 归档动作 | “完成 / 归档” | `.rc-card-actions button.primary` | 可执行、阻断、刷新；1440px/390px | 动作门禁 |
| 文档抽屉 | 现有右侧阅读抽屉 | `.rc-markdown-drawer` 或实际根节点 | 打开、关闭、只读、失败 | 文档读取 |

动作按钮矩阵：卡片 MD 入口 → 既有 Markdown drawer → `.rc-docs button` → 可读/无权/缺失 → 抽屉正文或脱敏提示；验收摘要入口 → `acceptance.md` drawer → `[data-testid="acceptance-readiness"]` → 待复验/已通过 → 验收摘要和正文；完成/归档 → 既有 action dialog/Chat → `.rc-card-actions button.primary` → 阻断/可执行/执行中 → 服务端门禁反馈。上述动作共用既有抽屉与按钮组件族，不新增弹窗。视觉采样检查 `.rc-doc-group` 的 `display`/`flex-wrap`/`gap`、`.rc-docs button` 的字号与颜色、`.rc-blocked` 的换行和 `.rc-card-actions button.primary` 的禁用状态。先核对现有卡片骨架与选择器，再验收文档分组和阻断状态，最后做双视口及关键交互截图；Mock/真实 API 边界分别记录。

## 风险与回滚方案

验收文档格式不齐可能导致误判：只认可可追溯的明确结果，未知时保守提示待核验。文档数量增加可能拥挤：按来源分组、折叠并验证双视口。回滚时恢复旧展示实现但继续依赖服务端最终归档门禁，不改写或删除治理文件。

## 存量 AC 迁移与无测试分母卡片

Issue 验收进度的唯一计数事实源为 `acceptance.md` 中的 AC 复选框。旧表格 AC 文档在未归档范围内逐份增补同编号的未勾选清单，保留表格原始操作、隔离测试与产品观察记录；表格“通过”不自动转为签认。`acceptance_status` 与服务端归档门禁不因格式迁移改变。进入验收阶段后，只要 Issue 有可计数 AC，即使 Change `tasks.md` 没有自动化测试任务分母，也展示独立“验收 X/Y”入口并打开 Issue 文档；研发和测试进度仍各自只在有对应分母时显示。

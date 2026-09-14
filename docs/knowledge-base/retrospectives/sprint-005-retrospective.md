---
title: Sprint-005 经验复盘
purpose: 复盘本地项目需求中心闭环、Capture 持久化、状态同步、Change 可见性和归档治理经验
content: 流程、模型 Token、需求设计、开发质量、可复用抽象和行动项
source: sprint-005 Fact Sheet 与归档验收证据
owner: MoonBox 产品团队
status: active
sprint_id: sprint-005
created_at: 2026-09-14 09:27:31
updated_at: 2026-09-14 09:27:31
ai_usage_mode: estimated_fallback
---

# Sprint-005 经验复盘

本迭代围绕需求中心本地项目闭环、Capture 持久化、研发启动状态同步、独立 Change 可见性、读取性能和归档索引刷新收口。交付已经归档，复盘重点是：把“卡片状态、文档入口、真实文件事实、归档路径”统一为可验证链路，并减少归档阶段的状态残留成本。

## Sprint 概况与证据范围

| 维度 | 事实 | 解释 |
|---|---|---|
| 状态 | completed / archive | 归档目录为 `iterations/archive/sprint-005` |
| 范围 | 2个 REQ、3个 BUG、8个 Change | 5个产品/缺陷闭环，3个治理 Change |
| 任务 | 121/121，8个 Change 全部归档 | 来自 Fact Sheet；本复盘不重新执行实现或归档 |
| 容量 | 30人天容量、32人天估算，106.67% | 超出2人天，属于 soft-pass；不能推断实际工时 |
| 归档检查 | readiness、stale scan、目录、env ignore、Workflow Sync 通过 | 关闭前曾有 active Change 与 stale 文案阻塞，已收口 |
| 观测适用性 | applicable | 覆盖 Web、API、request_logs、usage_events、Task Trace、Agent Workflow 与部署声明 |
| 复盘读取风险 | 四件套 167/243/164/196 行，8个 Change、121个任务 | 使用 Fact Sheet 作为主证据，不全文复制 trace、tasks 或测试日志 |
| AI Usage | estimated_fallback，snapshot stale | 自动发现不可用，不能作为真实 token 成本统计 |

主要事实源：[Sprint 事实源](../../../iterations/archive/sprint-005/sprint.yaml)、[验收报告](../../../iterations/archive/sprint-005/acceptance-report.md)、[发布说明](../../../iterations/archive/sprint-005/release-note.md)。Fact Sheet 通过 `python scripts/generate-sprint-fact-sheet.py --sprint sprint-005 --json` 生成；本报告只保存脱敏聚合结论。

## 流程复盘

**有效做法。** Sprint close 前先完成所有 Change 归档，再执行 readiness、env ignore、stale scan、Workflow Sync 与 Issue promote，最终迁移到 `iterations/archive/sprint-005`。这条顺序避免了“Issue 已 archive 但 Sprint 仍引用 active Change”的半闭环状态。

**主要卡点。** 首次归档时 `refresh-issue-index-after-archive-promotion` 仍为 active，任务 2/4；补齐归档后，剩余阻塞集中在 Sprint/Issue 文档里的旧 active path、`proposed`、`applied`、`in_sprint` 等历史表达。Workflow Sync 能更新派生字段和验收状态，但不会改写人工说明区；最终需要按 stale scan 命中的文件做聚焦收口。

**归档索引刷新值得保留为门禁。** `refresh-issue-index-after-archive-promotion` 解决 promote 后 registry 与 CHANGELOG 路径漂移，降低二次 Workflow Sync 成本。此类治理修复应放在 Sprint 内闭环，而不是在下一轮发布前临时补丁。

**容量管理需要更早触发取舍。** Sprint 估算 32/30 人天，虽然未触及 120% 硬门禁，但 fix buffer 为0。REQ-0026 增补阶段按钮后，仍然保留权限、视觉和真实观察验收是正确的；代价是归档阶段变得更密集。后续新增范围应先拆分低优先体验优化或明确延期。

## 模型 Token 使用分析

### Token Usage Fact Sheet

| 指标 | 值 | 证据/说明 |
|---|---|---|
| 精确 token 统计 | 无 | 自动发现未取得可归因 command run；不把旧快照当真实统计 |
| AI usage mode | estimated_fallback | Fact Sheet: `ai_usage_snapshot.ai_usage_mode` |
| Snapshot status | stale | generated_at 为 2026-09-11T09:10:19Z，早于最终归档与关闭更新 |
| 覆盖缺口 | requirements、bugs、changes 均 missing | REQ-0026、3个 BUG、7个 Change 缺失覆盖 |
| 自动发现复核 | warning / unavailable | `extract-ai-usage.py --post-command-hook --workflow-event sprint.archive --sprint sprint-005 --dry-run --json` 未得到可归因记录 |
| 主要输入消耗 | 估算风险高 | Sprint 四件套、8个 Change、121个任务、归档路径残留与 stale scan 明细 |
| 主要输出消耗 | 估算风险中高 | readiness、Workflow Sync、Fact Sheet、stale scan 和测试/验收摘要 |
| 已采用节省策略 | Fact Sheet 优先、聚焦读取、summary 输出 | 本复盘未全文读取所有 Issue/Change trace 与 tasks |

reason：snapshot 过期、覆盖不足，自动发现缺少可归因 token_count 事件。impact：不能计算本 Sprint 的真实总 tokens、缓存命中率、单位 Change 成本或重试成本；下方只分析上下文风险，不编造具体 token 数字。recommended_action：如需审计，使用显式 `--session-jsonl` 并必要时补 `--manual-map`，再重跑 `extract-ai-usage.py` 和 Fact Sheet。

### 高消耗来源

| 来源 | 影响 | 证据 | 优化方案 |
|---|---|---|---|
| Sprint close stale scan | high | 首轮 79 个 blocker，涉及 39 个检查文件 | 输出按文件/类型聚合，成功路径只报计数；失败时提供 JSON 供脚本化修复 |
| Sprint 四件套与验收报告 | high | `sprint.md` 243行，`acceptance-report.md` 196行 | 复盘默认读 Fact Sheet；仅在 warnings 或 focus 时分段回读 |
| OpenSpec archived lookup | high | 8个 Change、121个任务，归档路径依赖 `sprint.yaml` | 以 `sprint.yaml changes[]` 为队列，不对 `openspec/archive/**` 做宽泛搜索 |
| Workflow Sync 输出 | medium | sprint.archive 成功仍返回多组 subdocument apply details | 成功路径只保留 updated/skipped/errors/blocked 计数，详情按 `--output detail` 取 |
| AI Usage 快照 | medium | stale + coverage missing + auto discovery unavailable | 将真实快照刷新作为独立动作，不在复盘中复读旧矩阵 |
| UI/浏览器证据 | medium | 多组 1440/390、computed style 与截图证据 | 保留证据目录入口和摘要，不把图片清单或样式 JSON 全量塞入复盘 |

### 优化行动项

| ID | 优先级 | 描述 | 建议下一步 | 状态 |
|---|---|---|---|---|
| S5-A001 | P1 | 为 Sprint close stale scan 增加安全修复或聚合报告，区分当前态、历史事实与证据路径残留 | `/opsx-propose add-sprint-close-stale-scan-repair` | open |
| S5-A002 | P1 | 修复 AI Usage Sprint 快照归因和覆盖缺口，明确 unknown、0、missing 和 stale 的展示语义 | `/bug-capture sprint-005-ai-usage-snapshot-attribution-missing` | open |
| S5-A003 | P2 | 将 Fact Sheet 增加 `--fields` 或紧凑模式，默认只输出 scope、warnings、ai_usage、token_risks | `/opsx-propose optimize-sprint-fact-sheet-fields` | open |

## 需求与设计复盘

**需求中心卡片需要“事实源优先”。** REQ-0022、REQ-0026、BUG-0014、BUG-0015、BUG-0016 都指向同一类问题：卡片展示不能靠前端临时状态、历史 Change 状态或推断文本，要以 Issue trace、Sprint scope、Change archive path、真实文档存在性和后端能力字段为准。Capture 临时卡片未持久化、apply 启动后卡片仍准备开发、文档读取慢或失败，都是事实源与展示状态断裂的表现。

**动作按钮与执行能力要分离。** REQ-0026 的阶段按钮最终保守处理：有按钮，但真实开发/归档执行能力未接入时保持禁用并说明原因。这个决策避免了 Demo 弹窗伪造成功，也保留了未来执行服务接入的位置。

**原型和视觉证据应覆盖状态组合，而不只覆盖静态布局。** 本 Sprint 多次涉及 1440px/390px、深浅主题、禁用/恢复、长提示、抽屉、主文档和原型入口。有效模式是动作矩阵 + selector/computed style + 多视口截图；不足之处是文档证据容易散落到 Issue、Change 和 Sprint 多处，归档时要统一路径。

**数据观测声明应写清 N/A。** Sprint 明确适用 web、api、request_logs、usage_events、task_traces、task_trace_spans、agent_workflow 和 deployment；具体 Change 对 DB、对象存储、部署配置等无新增边界时要写出理由。这个做法比笼统写“不涉及”更利于归档门禁。

## 开发质量复盘

**测试分层比单一通过数更可靠。** Sprint 验收报告记录了后端、前端、TypeScript、浏览器、真实仓库聚合、合成 HTTP、临时 Compose 权限等多类证据。复盘不能把这些计数累加成唯一“总测试数”；应保留各自适用范围，尤其区分合成组件验证和真实部署观察。

**归档后文档状态同样是质量边界。** readiness 通过不只依赖 tasks 全勾，也依赖归档证据、Issue 子文档状态、active path 残留、stale scan 和 Workflow Sync。Sprint-005 的实际经验是：代码/Change 已完成后，文档中保留的历史中间态仍能阻断关闭。

**治理 Change 应和业务 Change 一起验收。** `unify-issue-classification-metadata`、`standardize-sprint-default-capacity`、`refresh-issue-index-after-archive-promotion` 都不是“顺手修文档”，而是降低后续流程错误率的交付项。它们需要 tasks、trace、归档证据和 Sprint scope 同等管理。

## 可复用抽象

| 模式 | 可复用价值 | 边界 |
|---|---|---|
| Requirement Center 事实源聚合 | 将 Issue、Sprint、Change、文档存在性和能力字段汇总给卡片 | 前端不得用临时卡片替代后端事实 |
| 动作族门禁矩阵 | 统一准备开发、研发中、验收中、已完成的按钮、弹窗和禁用原因 | 未接入真实能力时禁用，不用 Demo 冒充 |
| 文档常驻区与阶段区排序 | requirement/bug 主文档、sprint、trace、tasks、spec 等入口稳定展示 | 不扩大必需文档门禁，不回退其他 Issue/Change |
| 归档路径残留扫描 | 防止 active Change 路径和中间态文案污染已关闭材料 | 需要区分历史记录和当前事实，避免误伤根因证据 |
| Capture 持久化链路 | 锁内编号、文件写入、registry、CHANGELOG、刷新和失败保留输入 | 不自动迁移历史 Capture；真实写入边界仍需权限测试 |

## 行动项

| ID | 优先级 | 类型倾向 | 建议与验收目标 | 建议下一命令 | 状态 |
|---|---|---|---|---|---|
| S5-A001 | P1 | 治理 | stale scan 输出按当前态、历史事实、路径残留分组；提供 dry-run 修复计划；不得改写根因历史证据 | `/opsx-propose add-sprint-close-stale-scan-repair` | open |
| S5-A002 | P1 | BUG | AI Usage 快照覆盖 Sprint 全范围；unknown、0、missing、stale 语义清晰；自动发现失败给出可操作诊断 | `/bug-capture sprint-005-ai-usage-snapshot-attribution-missing` | open |
| S5-A003 | P2 | 治理 | Fact Sheet 支持字段筛选和紧凑摘要，减少复盘/归档阶段重复读取四件套与矩阵 | `/opsx-propose optimize-sprint-fact-sheet-fields` | open |
| S5-A004 | P1 | REQ | 将需求中心卡片“事实源优先”固化为产品能力：每张卡可解释来源、状态、文档、动作和拒绝原因 | `/req-capture requirement-center-card-source-explainability` | open |
| S5-A005 | P2 | 治理 | Sprint 容量 soft-pass 时强制输出取舍建议，并在追加范围时标记被延后项 | `/opsx-propose strengthen-sprint-capacity-soft-pass-gate` | open |
| S5-A006 | P2 | best-practice候选 | 沉淀需求中心动作族、文档入口、视觉证据和权限门禁的复用模式 | `/req-capture requirement-center-action-and-document-gate-best-practice` | open |

这些是待承接建议，不是已评审 Issue、已纳入 Sprint 的承诺或本轮开发任务；本命令未自动创建 Issue/Change。

## 执行链路复盘

链路状态：warning。Sprint 已完成归档，复盘基于 Fact Sheet 和关闭证据生成；AI Usage 仍为 estimated_fallback。问题证据：Fact Sheet 显示 snapshot stale、coverage missing，AI Usage dry-run 返回 unavailable；归档阶段曾出现 active Change 与 79 个 stale blocker，已在关闭前处理。规范优化建议：优先处理 S5-A001 与 S5-A002，再做 Fact Sheet 输出收敛。follow-up 状态：未自动创建 Issue/Change。

---
title: Sprint-007 经验复盘
purpose: 复盘图文 Capture、当前迭代归档入口、需求中心质量修复和治理门禁经验
content: 流程、模型 Token、需求设计、开发质量、可复用抽象和行动项
source: sprint-007 Fact Sheet 与归档验收证据
owner: MoonBox 产品团队
status: active
sprint_id: sprint-007
created_at: 2026-09-29 14:47:32
updated_at: 2026-09-29 14:47:32
ai_usage_mode: estimated_fallback
---

# Sprint-007 经验复盘

本迭代完成了图文 Capture 候选审阅与批量采集、当前迭代归档入口、需求中心文档抽屉简化、容器命名修复，以及多项工作流治理能力。复盘重点不是重复验收日志，而是沉淀三类经验：高复杂度 UI/存储/模型链路如何拆成可归档证据，需求中心状态展示如何保持事实源优先，以及归档/复盘命令如何控制上下文成本。

## Sprint 概况与证据范围

| 维度 | 事实 | 解释 |
|---|---|---|
| 状态 | completed / archive | 归档目录为 `iterations/archive/sprint-007` |
| 范围 | 3个 REQ、3个 BUG、13个 Change | 6个产品/缺陷闭环，7个治理 Change |
| 任务 | 276/276，13个 Change 全部归档 | 来自 Fact Sheet；本复盘不重新执行实现或归档 |
| 容量 | 30人天容量、30.5人天估算，101.67% | 低幅超出 soft-pass，fix buffer 为0 |
| 验收 | acceptance-report 为 passed | Issue 子文档关闭态一致性、readiness、env ignore、stale scan 与 promote gate 均通过 |
| 观测适用性 | applicable | 覆盖 usage_events、request_logs、task_traces、task_trace_spans |
| AI Usage | estimated_fallback，snapshot missing | 自动发现没有可归因 token_count；不能作为真实 token 成本统计 |

主要事实源：[Sprint 事实源](../../../iterations/archive/sprint-007/sprint.yaml)、[验收报告](../../../iterations/archive/sprint-007/acceptance-report.md)、[发布说明](../../../iterations/archive/sprint-007/release-note.md)。Fact Sheet 通过 `python scripts/generate-sprint-fact-sheet.py --sprint sprint-007 --json` 生成；本报告只保存脱敏聚合结论。

## 流程复盘

**有效做法。** 本 Sprint 把大需求和治理修复放在同一个可追踪范围里，最终依赖 Sprint archive readiness、Issue 子文档扫描、active path 残留扫描和 Workflow Sync 统一关闭。关闭前 `check-sprint-close-stale-scan` 从 26 个 blocker 收敛到 0，说明“归档不是移动目录，而是清理当前事实投影”这条门禁有效。

**主要卡点。** REQ-0029 的 Change 是本迭代最大项，单个 Change 112/112 个任务，横跨上传、对象存储、模型、候选编辑、幂等确认、真实浏览器与合成状态验收。其复杂度导致验收返修和文档回填周期偏长。类似功能后续应尽早拆出“输入/上传与草稿”“候选审阅 UI”“确认落盘与恢复”三个可独立验收的范围，而不是在一个 Change 内承载所有风险。

**归档入口本身也必须被归档门禁约束。** REQ-0037 新增当前迭代归档入口，但真实归档仍由 `/sprint-archive` 裁判，前端入口只负责安全摘要、权限、确认和禁用态。这种“入口可见，但执行不绕过治理命令”的设计值得保留。

**治理 Change 降低了下一轮成本。** `add-change-delivery-evidence-source-check`、`add-capture-dedup-gate`、`standardize-data-runtime-storage-layout` 等不是附带文档，而是减少后续归档、capture 和运行时目录漂移的防线。Sprint 中对治理 Change 同样做 tasks、trace 和 archive evidence，是正确的。

## 模型 Token 使用分析

### Token Usage Fact Sheet

| 指标 | 值 | 证据/说明 |
|---|---|---|
| 精确 token 统计 | 无 | 自动发现未取得可归因 command run；不生成真实 token 数字 |
| AI usage mode | estimated_fallback | Fact Sheet: `ai_usage_snapshot.ai_usage_mode` |
| Snapshot status | missing | `data/ai-usage/sprints/sprint-007.json` 不存在 |
| 自动发现复核 | warning / unavailable | `extract-ai-usage.py --post-command-hook --workflow-event sprint.archive --sprint sprint-007 --dry-run --json` 返回 `command_run_count: 0` |
| 主要输入消耗 | 估算风险高 | 13个 Change、276个任务、Sprint 四件套、Issue 子文档关闭扫描 |
| 主要输出消耗 | 估算风险中高 | readiness、stale scan、Workflow Sync、Fact Sheet、验收证据摘要 |
| 重复/浪费来源 | 估算风险中 | 归档阶段反复检查 Issue 子文档状态和 active path 残留；大型 Change 证据路径较多 |
| 已采用节省策略 | Fact Sheet 优先、聚焦读取、summary 输出 | 复盘未全文读取所有 Issue/Change trace 和 tasks |

reason：snapshot missing，自动发现缺少可归因 token_count 事件。impact：不能计算 sprint-007 的真实总 tokens、缓存命中率、单位 Change 成本、重试成本或工具输出字符数；下方只分析上下文风险，不编造具体 token 数字。recommended_action：如需审计，使用显式 `--session-jsonl` 并必要时补 `--manual-map`，再重跑 `extract-ai-usage.py` 和 Fact Sheet。

### 高消耗来源

| 来源 | 影响 | 证据 | 优化方案 |
|---|---|---|---|
| REQ-0029 大型 Change | high | 单 Change 112/112 tasks，覆盖上传、模型、UI、DB、对象存储和观测 | 下次拆分为 2-3 个可独立验收 Change；UI 返修用 acceptance-fixes 承载完整台账 |
| Sprint close stale scan | high | 首轮 26 个 blocker，涉及 Issue 子文档和 active path 残留 | 保持 stale scan 在 close 前运行；继续沉淀可安全修复的路径替换和状态投影脚本 |
| Fact Sheet 和 Sprint 四件套 | high | `sprint.md` 超过 200 行，13个 Change、276个任务 | 复盘与归档继续 Fact Sheet read-first，只按 warnings/evidence_hints 回读片段 |
| Workflow Sync 输出 | medium | sprint.archive 扫描 42 个子文档并回填 6 个验收结果 | 成功路径只输出 summary；warning 用 detail 聚焦查看，不默认复制所有 no-delta |
| AI Usage 快照 | medium | snapshot missing + auto discovery unavailable | 把真实用量回填做成独立审计动作；不要在复盘中复读旧矩阵或猜 token |
| UI/视觉证据 | medium | REQ-0029、REQ-0037、REQ-0036 均涉及 1440px/390px 与 computed style | 证据保留目录入口和摘要，复盘只引用路径和结论，不复制截图清单或 JSON |

### 优化行动项

| ID | 优先级 | 描述 | 建议下一步 | 状态 |
|---|---|---|---|---|
| S7-A001 | P1 | 将大型图文 Capture 类需求拆成输入/候选/确认三个验收单元，降低单 Change 任务量和返修成本 | `/req-capture capture-large-feature-change-splitting` | open |
| S7-A002 | P1 | 补齐 Sprint AI Usage session 显式回填流程，支持缺失快照时用 session-jsonl 做历史审计 | `/bug-capture sprint-ai-usage-snapshot-missing` | open |
| S7-A003 | P2 | 为 Sprint close stale scan 增加可安全应用的路径残留修复计划，减少手工 patch | `/opsx-propose add-sprint-close-path-residual-repair` | open |

## 需求与设计复盘

**REQ-0029 证明“候选态”和“正式态”必须隔离。** 图文输入、AI 整理、候选审阅和确认落盘的边界清楚，才能避免提前分配 REQ/BUG 编号、半成功写入、重复确认和来源丢失。有效设计包括：确认前不进入正式目录、候选可编辑/合并/拆分、确认时绑定完整版本、恢复期间不伪造成功。

**相似 Issue 提示必须服务于去重，而不是制造新空态。** `add-capture-dedup-gate` 和 REQ-0029 返修都指向同一个经验：相似项只在真实存在匹配时展示；无匹配时不要默认展示“可能相关”空模块，也不要诱导“继续创建新记录”。候选可合并到已有记录或作为补充材料，但这类候选不能进入确认创建批次。

**需求中心卡片仍应坚持事实源优先。** BUG-0019 修复标题来源，BUG-0023 修复验收中三类进度，REQ-0036 删除抽屉内 Change 属性噪音。三者共同说明：卡片显示要解释“标题来自哪里、进度按什么统计、文档入口打开什么对象”，不能让 UI 简化牺牲对象身份。

**归档入口是高风险动作入口，不是 shortcut。** REQ-0037 的正确范围是把 readiness、安全摘要、权限拒绝和确认流程放进 UI；真实关闭仍由 Sprint archive 命令、Workflow Sync 和目录迁移完成。后续所有高风险操作入口都应复用这种模式。

## 开发质量复盘

**测试证据要按层级分开读。** 本 Sprint 同时有 SQLite/MySQL、API、对象存储、真实模型、前端单测、TypeScript、真实浏览器和合成 UI 状态。复盘与验收都不能把这些简单合成“总测试数”；每类证据要说明适用层级和不能替代的边界。

**文档同步本身是质量成果。** sprint-007 关闭前的 blocker 主要来自 Issue 子文档里的中间态文案和旧 active path。代码和 Change 归档完成后，文档里的“待 archive”“openspec/changes/...”仍然会破坏需求中心和复盘事实源。以后 apply/modify/archive 阶段都要把“最终路径”和“当前态措辞”作为完成门禁。

**目录边界治理值得继续推进。** `standardize-data-runtime-storage-layout` 把 `data/sqlite`、`data/s3`、`data/runtime` 的职责讲清楚；最终目录校验仍保留 legacy runtime warning。这类 warning 不应在普通 Sprint 中删除真实数据，但应在未来单独迁移计划中关闭。

## 可复用抽象

| 模式 | 可复用价值 | 边界 |
|---|---|---|
| Capture 候选审阅流水线 | 支持自由输入、AI 整理、候选编辑、相似项处理和确认落盘 | 候选态不得提前分配正式编号或写入正式 Issue |
| 高风险操作入口 | UI 提供 readiness、禁用态、确认和权限说明 | 执行裁判必须留在后端/治理命令，不能前端绕过 |
| 需求中心文档入口模型 | 保持主文档、关联 Change trace、tasks、spec 等入口可解释 | 删除噪音属性时不能丢失对象身份和可达性 |
| tasks.md 分类进度 | 将研发、测试、人工验收进度统一回 `tasks.md` 分类 checkbox | 缺分类时应降级提示，不应误报满格 |
| 归档路径残留扫描 | 保证 archive 后不再引用 active change/sprint 路径 | 历史事件可保留事实，但当前事实段必须闭环 |

## 行动项

| ID | 优先级 | 类型倾向 | 建议与验收目标 | 建议下一命令 | 状态 |
|---|---|---|---|---|---|
| S7-A001 | P1 | 需求治理 | 大型 Capture/多媒体/模型链路需求在 sprint-propose 或 req-opsx 前拆分验收单元；单 Change tasks 超过 60 时必须给出拆分理由或豁免 | `/req-capture capture-large-feature-change-splitting` | open |
| S7-A002 | P1 | BUG | AI Usage Sprint 快照缺失时给出显式 session-jsonl 回填流程，区分 unknown、0、missing、unavailable，不影响主命令但可审计 | `/bug-capture sprint-ai-usage-snapshot-missing` | open |
| S7-A003 | P2 | 治理 | Sprint close stale scan 输出可安全修复计划，至少覆盖 active Change path、Sprint path 和当前态中间文案；先 dry-run 再 apply | `/opsx-propose add-sprint-close-path-residual-repair` | open |
| S7-A004 | P2 | best-practice候选 | 沉淀“高风险操作入口”模式：入口只做 readiness/确认/权限说明，真实执行复用治理命令或后端门禁 | `/req-capture high-risk-action-entry-pattern` | open |
| S7-A005 | P2 | 治理 | 将需求中心卡片标题、进度、文档入口的事实源说明沉淀为可复用验收 checklist | `/req-capture requirement-center-fact-source-checklist` | open |
| S7-A006 | P3 | 部署治理 | 为 `data/runtime/backend/sqlite` 和 `data/runtime/backend/media` legacy warning 制定迁移/清理计划，避免长期噪音 | `/opsx-propose migrate-legacy-runtime-data-paths` | open |

这些是待承接建议，不是已评审 Issue、已纳入 Sprint 的承诺或本轮开发任务；本命令未自动创建 Issue/Change。

## 执行链路复盘

链路状态：warning。Sprint 已完成归档，复盘基于 Fact Sheet、归档四件套和关闭证据生成；AI Usage 仍为 estimated_fallback。问题证据：Fact Sheet 显示 snapshot missing，AI Usage dry-run 返回 `usage_mode: unavailable`、`command_run_count: 0`；目录结构校验仍提示 legacy runtime path warning。规范优化建议：优先处理 S7-A001、S7-A002、S7-A003，再沉淀高风险入口和需求中心事实源 checklist。follow-up 状态：未自动创建 Issue/Change。

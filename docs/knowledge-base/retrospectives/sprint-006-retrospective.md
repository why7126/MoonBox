---
title: Sprint-006 经验复盘
purpose: 复盘需求中心迭代信息增强、Chat 工作台输入能力、Workflow Sync 治理和 Sprint 归档收口经验
content: 流程、模型 Token、需求设计、开发质量、可复用抽象和行动项
source: sprint-006 Fact Sheet 与归档验收证据
owner: MoonBox 产品团队
status: active
sprint_id: sprint-006
created_at: 2026-09-29 14:46:28
updated_at: 2026-09-29 14:46:28
ai_usage_mode: estimated_fallback
---

# Sprint-006 经验复盘

本迭代围绕需求中心迭代信息、筛选体验、Chat 工作台多材料与模型推理配置、以及 Workflow Sync / OpenSpec 治理能力收口。复盘重点是：在 17 个 Change、322 个任务的大范围 Sprint 中，如何让需求、BUG、治理 Change、验收返修、归档路径和知识库承接保持同一事实链路。

## Sprint 概况与证据范围

| 维度 | 事实 | 解释 |
|---|---|---|
| 状态 | completed / archive | 归档目录为 `iterations/archive/sprint-006` |
| 范围 | 7个 REQ、4个 BUG、17个 Change | 11个产品/缺陷闭环，6个治理 Change |
| 任务 | 322/322，17个 Change 全部归档 | 来自 Fact Sheet；本复盘不重新执行实现或归档 |
| 容量 | 30人天容量、30.25人天估算，100.83% | soft-pass；fix buffer 为0 |
| 归档检查 | readiness、stale scan、archived path residual、env ignore、Workflow Sync 通过 | 关闭前曾有 Issue 子文档旧状态和 active path 残留，已收口 |
| 观测适用性 | applicable | 覆盖 Web request wrapper、API、DB、usage_events、request_logs、task_traces、task_trace_spans |
| 复盘读取风险 | 四件套 189/245/23/28 行，17个 Change、322个任务 | 使用 Fact Sheet 作为主证据，不全文复制 trace、tasks 或测试日志 |
| AI Usage | estimated_fallback，snapshot missing | 自动发现不可用，不能作为真实 token 成本统计 |

主要事实源：[Sprint 事实源](../../../iterations/archive/sprint-006/sprint.yaml)、[验收报告](../../../iterations/archive/sprint-006/acceptance-report.md)、[发布说明](../../../iterations/archive/sprint-006/release-note.md)。Fact Sheet 通过 `python scripts/generate-sprint-fact-sheet.py --sprint sprint-006 --json` 生成；本报告只保存脱敏聚合结论。

## 流程复盘

**有效做法。** Sprint close 前 17 个 Change 已全部归档，readiness 显示 322/322 tasks 完成，且每个 archived Change 都有 `trace.md`。这让 Sprint close 的判断可以聚焦在 Sprint/Issue 文档的当前态一致性，而不是重新展开所有 Change 原文。

**主要卡点。** 首轮 `/sprint-archive` readiness 的 Change 层面已全部 PASS，但 Sprint close stale scan 阻断了 24 个 Issue 子文档命中，主要是 `openspec/changes/<change-id>/` active path、`proposed`、`applied`、`in_sprint`、`待实现` 等历史阶段文案。Workflow Sync 能回填验收结果和派生字段，但人工说明区仍需要聚焦修正。

**归档路径残留检查值得保留。** 本 Sprint 在关闭前还发现 41 个 archived path residual warning，覆盖 Issue 子文档和 archived Change trace/design 中的旧路径。修正后 `check-archived-path-residuals.py --sprint sprint-006` 为 0 residual。这个门禁能防止未来读者从归档材料跳回不存在或过期的 active 目录。

**大 Sprint 需要分批语义，但不必分批读取。** Fact Sheet 自动识别 large-sprint，分成 4 个 batch：5、5、5、2 个 Change。复盘阶段没有必要全文读四批 tasks；只要 Fact Sheet 显示 blockers=0、warnings=0、trace_present=17，就可以用批次聚合作为证据。

**容量门禁仍需更早触发范围取舍。** 30.25/30 人天看起来只超出 0.25 人天，但 fix buffer 为0。REQ-0028 和 REQ-0035 的 Chat 工作台返修非常密集，后续类似 Sprint 应在规划阶段保留返修缓冲，或把 UI polish 与治理增强拆到后续 Sprint。

## 模型 Token 使用分析

### Token Usage Fact Sheet

| 指标 | 值 | 证据/说明 |
|---|---|---|
| 精确 token 统计 | 无 | `data/ai-usage/sprints/sprint-006.json` 不存在 |
| AI usage mode | estimated_fallback | Fact Sheet: `ai_usage_snapshot.ai_usage_mode` |
| Snapshot status | missing | Fact Sheet: `ai_usage_snapshot.snapshot_status` |
| 自动发现复核 | warning / unavailable | `extract-ai-usage.py --post-command-hook --workflow-event sprint.archive --sprint sprint-006 --dry-run --json` 返回 `usage_mode: unavailable` |
| 覆盖缺口 | requirements、bugs、changes 均 unknown | 无真实 command run 矩阵，不能计算单位 Change token 成本 |
| 主要输入消耗 | 估算风险高 | 17个 Change、322个任务、29个 evidence hints、Sprint 四件套中 `sprint.md` 245行 |
| 主要输出消耗 | 估算风险中高 | readiness、stale scan、archived path residual、Workflow Sync、Fact Sheet 和长验收摘要 |
| 重复/浪费来源 | 估算风险中 | 首轮归档需要修复 active path / stale wording，若不依赖 Fact Sheet 容易展开大量 archived trace |
| 已采用节省策略 | Fact Sheet 优先、聚合计数、分段读取、summary 输出 | 本复盘未全文读取所有 Issue/Change trace 与 tasks |

reason：snapshot missing，自动发现没有可归因 `token_count` command run。impact：不能计算真实总 tokens、缓存命中率、工具输出字符数、重试成本或每个 Change 的 token 成本；下方只分析上下文风险，不编造具体 token 数字。recommended_action：如需审计，使用显式 `--session-jsonl <local-session.jsonl>` 并必要时补 `--manual-map`，再重跑 `extract-ai-usage.py` 和 Fact Sheet。

### 高消耗来源

| 来源 | 影响 | 证据 | 优化方案 |
|---|---|---|---|
| Sprint 范围规模 | high | 17个 Change、322/322 tasks、4个 batch | 复盘默认只读 Fact Sheet；warnings 或 focus 命中时再按 batch/evidence hint 展开 |
| Sprint close stale scan | high | 首轮 24 个 blocker，后续修复到 PASS | 为 stale scan 增加修复计划或归类输出，避免人工逐行判断历史记录 |
| Archived path residuals | high | 首轮 41 个 residual，修复后为0 | 提供 dry-run rewrite report，区分 Issue 子文档和 archived Change 内证据路径 |
| Sprint 四件套 | medium | `sprint.md` 245行，acceptance-report 包含长验收摘要 | 复盘引用关闭结论与路径，不复制验收报告全文 |
| Workflow Sync 输出 | medium | sprint.archive 更新9项、检查77个子文档、11个验收状态回填 | 成功路径只保留 updated/skipped/errors/subdocument 计数；详情按 `--output detail` |
| AI Usage 缺失 | medium | snapshot missing，hook unavailable | 将真实快照刷新作为独立审计动作，不阻断复盘，不输出虚构数值 |

### 优化行动项

| ID | 优先级 | 描述 | 建议下一步 | 状态 |
|---|---|---|---|---|
| S6-A001 | P1 | 为 Sprint close stale scan / archived path residual 增加安全修复计划，按文件、语义类型和建议替换聚合输出 | `/opsx-propose add-sprint-close-stale-repair-plan` | open |
| S6-A002 | P1 | 修复 Sprint AI Usage 快照归因缺失，让 `sprint-exps` 能区分 actual、missing、unknown 与真实 0 | `/bug-capture sprint-006-ai-usage-snapshot-missing` | open |
| S6-A003 | P2 | 将 large-sprint Fact Sheet 默认输出进一步压缩为 scope、batch、warnings、ai_usage、token_risks 五段 | `/opsx-propose compact-large-sprint-fact-sheet` | open |

## 需求与设计复盘

**需求中心迭代信息增强应使用同一状态词典。** REQ-0030、REQ-0031、REQ-0032、REQ-0033、REQ-0034 都围绕需求中心指标、容量、Sprint 状态、筛选顺序和默认当前迭代范围。有效模式是：后端提供稳定事实源，前端只展示轻量 badge / tooltip / 下拉摘要，不在 UI 内临时猜测状态。

**分级信息要避免跨域误映射。** BUG-0021 暴露了 BUG 严重度和 REQ 优先级混用的问题。后续需求中心、筛选和卡片组件必须保持 `priority` 与 `severity` 的字段语义、颜色和文案独立，避免把所有卡片统一成 P 值。

**Chat 工作台需求容易从输入区扩展到执行链路。** REQ-0028 和 REQ-0035 表面是多图片、文件、Skill、模型和推理配置选择，实际涉及对象存储、权限、请求封装、usage_events、request_logs、Task Trace、UI 视觉和会话关联。后续 Chat 输入区需求在 PRD 阶段就应列出材料、Skill、模型、权限、观测、执行配置和错误降级矩阵。

**UI 返修必须保留“动作族”视角。** REQ-0028 的返修覆盖 Composer、消息流、轨迹、历史、Skill menu、图片预览、复制、模型下拉等多个族。若逐按钮返修，会带来上下文膨胀；更稳的方式是先建立动作按钮/菜单/弹窗/状态矩阵，再批量验收。

**治理 Change 与业务需求互相支撑。** 本 Sprint 同时归档了 execution frontmatter schema、OpenSpec 中文标题、本地 Vite 缓存目录、Workflow Sync 状态块等治理 Change。它们不是旁支，而是让后续 REQ/BUG 链路可审计、可复盘、可归档的基础。

## 开发质量复盘

**完成度判断不能只看 Change tasks。** 本 Sprint 17 个 Change 全部 archived、tasks 全勾，但 Sprint close 仍被 Issue 子文档 stale wording 阻断。质量边界应包括：Change archive evidence、Issue acceptance projection、Sprint stale scan、archived path residual、Workflow Sync check 和 env ignore policy。

**验收证据要区分真实观察与合成验证。** Chat 工作台和需求中心 UI 都有真实浏览器截图、computed style、Vitest / TypeScript / 后端测试等多类证据。复盘报告只保存路径和结论，避免把截图清单、样式 JSON 或测试日志原文复制进知识库。

**对象存储和观测边界要随 UI 一起验收。** REQ-0028 / REQ-0035 证明输入区 UI 与材料上传、对象存储、请求日志、Task Trace 是同一条链路。UI 变更不能只看视觉，还要检查 metadata 脱敏、材料计数、权限降级和请求日志摘要。

**归档材料中的路径就是用户体验的一部分。** active path 残留会让后续 Agent、产品或研发读错事实源。Sprint close 前将证据路径统一到 `openspec/archive/YYYY-MM-DD-<change-id>/`，应成为关闭质量的一部分。

## 可复用抽象

| 模式 | 可复用价值 | 边界 |
|---|---|---|
| Requirement Center 状态事实源 | 统一 Sprint、REQ、BUG、Change 的状态、数量、容量、筛选和默认范围 | 前端只做展示和交互，不重新推断业务状态 |
| 分级字段双轨模型 | REQ 使用 priority，BUG 使用 severity，颜色和筛选分组独立 | 不把 severity 映射为 P 值，也不在文案中混称优先级 |
| Chat Composer 材料上下文 | 将图片、文件、Skill、模型、推理配置、权限与观测作为同一输入上下文 | 不在 usage_events/request_logs/task_traces 保存完整 Prompt、文件正文、对象 key 或本机路径 |
| UI 动作族验收矩阵 | 对按钮、菜单、modal、chip、复制、预览、轨迹入口做族级验收 | 不逐按钮临时问答返修；变化需回填 Change/REQ 证据 |
| Sprint close 事实漂移修复 | stale scan + archived path residual + Workflow Sync 共同保证关闭材料可读 | 不改写 root-cause 历史证据的事实，只改当前态误导和路径残留 |
| Large Sprint batch 复盘 | 使用 Fact Sheet batch 聚合评估范围，而不是展开所有 tasks | 只有 blockers/warnings/focus 命中才读原文 |

## 行动项

| ID | 优先级 | 类型倾向 | 建议与验收目标 | 建议下一命令 | 状态 |
|---|---|---|---|---|---|
| S6-A001 | P1 | 治理 | stale scan 与 archived path residual 输出修复计划，支持 dry-run，避免 Sprint close 手工逐行替换 | `/opsx-propose add-sprint-close-stale-repair-plan` | open |
| S6-A002 | P1 | BUG | Sprint AI Usage 快照能从显式 session 或自动发现中归因 command run；missing、unknown、0 和 unavailable 展示清晰 | `/bug-capture sprint-006-ai-usage-snapshot-missing` | open |
| S6-A003 | P1 | best-practice候选 | 沉淀 Chat Composer 材料、Skill、模型、推理配置、权限和观测的设计/验收模式 | `/req-capture chat-composer-material-skill-model-gate-best-practice` | open |
| S6-A004 | P2 | REQ | 需求中心筛选与指标组件共享状态词典、分级颜色、容量口径和 tooltip 模式 | `/req-capture requirement-center-filter-metric-state-system` | open |
| S6-A005 | P2 | 治理 | large-sprint Fact Sheet 支持默认紧凑输出和按 fields 读取，降低复盘/归档 token 成本 | `/opsx-propose compact-large-sprint-fact-sheet` | open |
| S6-A006 | P2 | 流程 | Sprint 容量 soft-pass 时要求明确返修缓冲和延期候选，避免 fix buffer 为0的 Sprint 继续追加范围 | `/opsx-propose strengthen-sprint-capacity-soft-pass-actions` | open |

这些是待承接建议，不是已评审 Issue、已纳入 Sprint 的承诺或本轮开发任务；本命令未自动创建 Issue/Change。

## 执行链路复盘

链路状态：warning。Sprint 已完成归档，复盘基于 Fact Sheet、readiness 和关闭证据生成；AI Usage 仍为 estimated_fallback。问题证据：Fact Sheet 显示 snapshot missing，AI Usage dry-run 返回 unavailable；归档阶段曾出现 24 个 stale scan blocker 和 41 个 archived path residual，已在关闭前处理。规范优化建议：优先处理 S6-A001 与 S6-A002，再沉淀 Chat Composer 输入上下文 best-practice。follow-up 状态：未自动创建 Issue/Change。

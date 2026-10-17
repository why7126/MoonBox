---
title: Sprint-008 经验复盘
purpose: 复盘需求中心命令链、Chat 归档权限、自动验收和迭代关闭经验
content: 流程、模型 Token、需求设计、开发质量、可复用抽象和行动项
source: sprint-008 Fact Sheet 与归档验收证据
owner: MoonBox 产品团队
status: active
sprint_id: sprint-008
created_at: 2026-10-17 17:10:00
updated_at: 2026-10-17 17:10:00
ai_usage_mode: estimated_fallback
---

# Sprint-008 经验复盘

## Sprint 概况与证据范围

| 维度 | 事实 | 说明 |
|---|---|---|
| 状态 | completed / archive | `iterations/archive/sprint-008/` |
| 范围 | 2 个 REQ、6 个 BUG、13 个 Change | 包含需求中心、Chat 归档权限、UI 质量和治理能力 |
| 任务 | 252/252 完成；13/13 Change 归档 | Fact Sheet 汇总；最大 Change 为 BUG-0025 的 84 项任务 |
| 容量 | 34.8/30 人天，116% | fix 缓冲为 0；范围增长压缩了返修余地 |
| 验收 | 8 个 Issue 已关闭；Sprint 关闭门禁通过 | 关闭记录确认 BUG-0025 完整验收 52/52 passed，并对 AC-003 附件变化做独立补证 |
| 观测适用性 | applicable | 覆盖 usage_events、request_logs、task_traces、task_trace_spans；脱敏边界见 Sprint 事实源 |
| AI 用量 | estimated_fallback | 快照缺失，不能推断实际 token 数 |

主要事实源：[Sprint 机器范围](../../../iterations/archive/sprint-008/sprint.yaml)、[验收结论](../../../iterations/archive/sprint-008/acceptance-report.md)、[发布说明](../../../iterations/archive/sprint-008/release-note.md)。本复盘基于 `generate-sprint-fact-sheet.py --sprint sprint-008 --json` 聚合结果；历史验收段落保留当时的 pending 状态，以报告末尾的关闭结论和当前结构化状态为准。

## 流程复盘

**有效做法。** 13 个 Change 的 tasks、trace 与归档证据全部闭环；Issue 当前态、Sprint readiness、目录、env ignore 和关闭陈旧扫描共同裁决关闭。BUG-0025 的完整 52 项验收清单在附件变化后没有被改写，而是对 AC-003 按原计划命令生成独立补证，保持原 manifest 的可审计性。

**主要卡点。** BUG-0025 的 Change 累积 84 项任务，需求中心命令链同时触及候选、应用、状态投影、文档读写和恢复。多轮 AF 记录中，产品镜像未部署、输入指纹过期和真实轮次不足曾让定向通过与整体验收 pending 并存。后续大 Change 应在设计时拆出事实源写入、产品入口与恢复验收，避免把单项诊断误读为整体验收。

**产品归档与宿主恢复要分层。** BUG-0026 曾出现对象 Chat 轮次 stopped/unknown，而宿主脚本完成唯一归档和同步。宿主恢复保证仓库事实一致，但不能替代产品同轮命令成功。最终关闭应同时核对产品轮次、规范合并、归档目录、Workflow Sync 和 Issue 投影。

**容量控制需提前介入。** 估算达到 116% 且无 fix 缓冲时，继续纳入高风险权限和治理链路会放大返修压力。下一次规划应将已评审范围、真实验收样本、预留返修与容量阈值一起审查。

## 模型 Token 使用分析

### Token Usage Fact Sheet

| 指标 | 值 | 证据与影响 |
|---|---|---|
| 精确 token 统计 | 无 | 无可归因 command run；不编造 input、cached、output、reasoning 或 total tokens |
| AI usage mode | estimated_fallback | Fact Sheet `ai_usage_snapshot.ai_usage_mode` |
| Snapshot status | missing | `data/ai-usage/sprints/sprint-008.json` 未生成 |
| 自动发现 | unavailable，command_run_count 0 | `extract-ai-usage.py --post-command-hook --workflow-event sprint.archive --sprint sprint-008 --dry-run --json` |
| 主要输入风险 | high | 13 个 Change、252 项任务，四件套中 `sprint.md` 为 231 行 |
| 主要输出风险 | high | 验收诊断、Workflow Sync、归档路径扫描和长回归日志 |
| 已采用节省策略 | Fact Sheet 优先 | 按 warning 与 evidence hint 定位，未全量读取 13 份 Change 和 8 份 Issue 原文 |

reason：snapshot missing，自动发现未取得可归因 `token_count`。impact：不能计算真实总用量、缓存比例、单 Change 成本、失败重跑成本或工具输出字符数。recommended_action：如需历史审计，提供显式本地 `--session-jsonl`，必要时按 `turn_hash` 提供 `--manual-map`，再刷新快照与 Fact Sheet。

### 高消耗来源与优化

| 来源 | 影响 | 证据 | 优化方案 |
|---|---|---|---|
| 大型命令链 Change | high | BUG-0025 单 Change 84 项任务 | 按事实源写入、产品入口和恢复验收分批，保留统一 trace |
| 归档历史证据 | high | Fact Sheet 记录 5,492 条旧活动路径引用，其中 5,488 条位于 `openspec/archive/` | 当前态扫描与历史证据盘点分离；汇总按目标和文件聚类，不复制逐行警告或改写原 manifest |
| Sprint 四件套与多 Issue | high | 13 个 Change、8 个 Issue，`sprint.md` 231 行 | 先读 Fact Sheet 的 counts 和 warning 聚合，仅在结论冲突时分段回读 |
| 长测试及同步输出 | medium | 多轮定向验收、Workflow Sync 与真实产品观察 | 成功路径保留命令、退出码和计数；失败时截取聚焦错误与证据入口，先看 diff/stat |
| 规则与技能重复读取 | medium | 命令链覆盖 apply、accept、archive、Sprint close | 同会话复用已读摘要；搜索排除 archive、generated、模板与构建目录，必要时按 Change 分段 |

### Token 优化行动项

| ID | 优先级 | 描述 | 建议下一步 | 状态 |
|---|---|---|---|---|
| S8-A001 | P1 | 建立历史 Sprint AI Usage 显式 session 回填与覆盖报告，缺失时保持估算模式 | `/opsx-propose add-historical-sprint-ai-usage-audit` | open |
| S8-A002 | P2 | Fact Sheet 将归档证据旧路径按目标、文件和当前态影响聚合，限制逐行提示量 | `/opsx-propose aggregate-archived-path-residuals` | open |

以上是可执行建议，未自动创建 Issue 或 Change。

## 需求与设计复盘

**事实源必须贯穿命令链。** REQ-0027、REQ-0039 与 BUG-0025 表明，Chat 会话复用、治理候选、应用记录和需求中心卡片不能分别依赖模型回复或 UI 临时状态。设计时应明确“谁写入、谁确认、谁投影、恢复后从何重建”，并用同一对象身份和版本摘要串联。

**验收计划需要区分单项、完整和真实产品轮次。** BUG-0025 的定向 AC 通过不能替代 52 项完整清单；BUG-0026 的隔离探针不能替代对象 Chat 首次产品归档。需求验收文档应从一开始标注命令、视觉、产品轮次三类证据，说明哪些可合成、哪些必须真实观察。

**安全权限由可信治理事实决定。** BUG-0033 涉及治理 source 只读与 apply 写入范围；单凭卡片标签或模型执行结束不得授予写入权限。此经验承接 sprint-007 的 S7-A004/S7-A005，并落实到权限组合与负向回归。

## 开发质量复盘

- 把“命令返回成功、产品轮次完成、文件持久化、Workflow Sync 投影一致”作为不同检查点；未知与停止状态必须保留，不补造成功。
- UI 返修需按桌面和移动视口分别保留截图、computed style 与文档入口证据；BUG-0027/0029 的滚动和底色问题适合在共享页面根布局上做回归。
- 归档后证据附件变化应走独立补证，保留原 manifest；命令型 AC 可重跑原命令，产品轮次和视觉证据不能借此补签。
- Fact Sheet 的 5,492 条旧路径引用是历史材料可读性警告，不能等同于 5,492 个当前关闭 blocker；现行关闭扫描已是 0 blocker。后续应聚类治理，避免大输出掩盖真实问题。

## 可复用抽象

| 模式 | 可复用价值 | 使用边界 |
|---|---|---|
| 治理动作事实链 | 候选、应用、trace、registry、卡片从同一身份与版本推导 | 模型文本和 UI 标签不作为持久化成功证据 |
| 产品归档五点核对 | 轮次、命令退出、规格合并、唯一目录、状态同步 | 宿主恢复与产品同轮成功分别记录 |
| 自动验收证据层级 | 命令、视觉、产品轮次分别给结论和入口 | 定向诊断不覆盖完整清单 |
| 归档后独立补证 | 原 manifest 不变，补证记录旧/新哈希和原命令 | 仅适用合规的命令型 AC |

## 行动项

| ID | 优先级 | 类型倾向 | 建议与验收目标 | 建议下一命令 | 状态 |
|---|---|---|---|---|---|
| S8-A001 | P1 | 治理 | AI Usage 历史回填显示覆盖率、缺口和真实/估算模式，不把未观测写成 0 | `/opsx-propose add-historical-sprint-ai-usage-audit` | open |
| S8-A002 | P2 | 治理 | 归档路径残留按目标和文件聚合，当前态 blocker 与历史 evidence warning 分开，报告保持可读 | `/opsx-propose aggregate-archived-path-residuals` | open |
| S8-A003 | P1 | 需求治理 | 大型命令链需求在设计阶段拆成事实源、产品入口、恢复验收三个可交付单元；保留跨单元 trace | `/req-capture split-governance-command-chain-acceptance` | open |
| S8-A004 | P1 | 测试治理 | 产品同轮归档与宿主恢复使用不同证据标签，验收矩阵覆盖 stopped/unknown/权限失效/恢复 | `/opsx-propose standardize-product-archive-evidence-levels` | open |
| S8-A005 | P2 | UI 质量 | 需求中心和 Chat 工作台共享页面根布局的滚动、底色、双视口视觉回归清单 | `/req-capture shared-workbench-root-visual-regression` | open |

这些行动项是复盘建议，尚未评审或纳入后续 Sprint。本命令未自动创建 Issue/Change。

## 执行链路复盘

链路状态：复盘已生成，Sprint 已完成归档。问题证据：AI Usage snapshot missing、自动发现无可归因 command run；Fact Sheet 有大量归档证据旧路径 warning，当前关闭扫描为 0 blocker。规范优化建议：优先推进 S8-A001 和 S8-A002，让历史用量与路径报告可审计且可读；S8-A003 至 A005 按下一轮容量选择。未自动创建 Issue/Change。

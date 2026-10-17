---
title: Sprint-009 经验复盘
purpose: 复盘本地数据边界、共享验证环境、Chat 输出、验收投影与迭代关闭经验
content: 流程、模型 Token、需求设计、开发质量、可复用抽象和行动项
source: sprint-009 Fact Sheet 与归档验收证据
owner: MoonBox 产品团队
status: active
sprint_id: sprint-009
created_at: 2026-10-17 17:20:00
updated_at: 2026-10-17 17:20:00
ai_usage_mode: estimated_fallback
---

# Sprint-009 经验复盘

## Sprint 概况与证据范围

| 维度 | 事实 | 说明 |
|---|---|---|
| 状态 | completed / archive | `iterations/archive/sprint-009/`，用户已确认总体验收 |
| 范围 | 2 个 REQ、6 个 BUG、20 个 Change | 本地数据、共享验证环境、Chat 输出、需求中心验收投影及治理闭环 |
| 任务 | 152/152 完成；20/20 Change 归档 | 最大 Change 为 BUG-0035 的 33 项任务 |
| 容量 | 35.99/30 人天，约 120% | fix 缓冲为 0；治理兼容修复纳入后接近容量硬阈值 |
| 验收 | 8 个范围 Issue 已关闭 | Sprint readiness、子文档、env ignore、目录和陈旧扫描通过；最终 `sprint.archive` 同步 0 error |
| 数据与观测 | applicable | DB、Chat 消息与事件、request_logs、Task Trace/span、Web 与治理文档读取层适用 |
| 发布 | release-note 为 draft | 迭代关闭不代表产品对外发布 |
| AI 用量 | estimated_fallback | 快照缺失，不能推断真实 Token 成本 |

主要事实源：[Sprint 范围](../../../iterations/archive/sprint-009/sprint.yaml)、[验收报告](../../../iterations/archive/sprint-009/acceptance-report.md)、[发布说明](../../../iterations/archive/sprint-009/release-note.md)。本复盘先用 `generate-sprint-fact-sheet.py --sprint sprint-009 --json` 汇总，再仅按 warning 与证据提示回读关闭片段。历史验收批次中的 pending、failed 或 stopped 是当时事实，以当前结构化状态和最终关闭签认为准。

## 流程复盘

**关闭门禁有效，但历史事实需要正确投影。** 首轮关闭扫描发现 Sprint 验收报告和已归档 Issue 子文档中 8 处旧当前态或活动 Change 路径；修正后 readiness 才通过。两个未归档 Change 顺序完成归档。最终 `sprint.archive` 曾被历史 AC-005 样本状态 `completed-source-archive` 阻断；通过受控 Change `accept-legacy-archive-sample-status` 兼容已归档计划、保留原 manifest，再重跑同步成功。经验是当前态文档、历史证据和读取器 schema 都是关闭输入，不能只看 tasks 全勾选。

**技术证据与用户签认要分开。** 19/19 个原范围 Change 先达到归档证据门禁，但 Sprint 报告仍有未勾选的聚合验收项；用户确认总体验收后才记录关闭签认。新增治理 Change 归档后范围成为 20/20。以后关闭报告应在顶部明确“技术就绪、用户签认、发布状态”三个独立结论，避免旧批次 pending 文案遮住最终结论。

**验收样本的生命周期需预先安排。** BUG-0040/0041/0042 为归档 Issue promote 的独立复验样本，部分产品轮次 stopped，需要全新样本；五个 `verify-chat-*` Change 覆盖归档转换、跨挂载复制、收尾与历史引用窗口。这些小 Change 有助于隔离具体失败窗口，但连续新样本也消耗容量和验证时间。规划阶段应为“产品首次归档”和“宿主恢复”分别准备样本与判定表。

**容量已近极限。** 35.99 人天接近 30 人天容量的 120% 上限，原定结束时间晚于实际关闭时间不等于返修缓冲充足。后续新增治理修复应优先置换范围或显式重估容量，而不依赖极小估算绕过压力。

## 模型 Token 使用分析

### Token Usage Fact Sheet

| 指标 | 值 | 证据与说明 |
|---|---|---|
| 精确 token 统计 | 无 | 未取得可归因 command run；不编造 input、cached、output、reasoning 或 total tokens |
| AI usage mode | estimated_fallback | Fact Sheet `ai_usage_snapshot.ai_usage_mode` |
| Snapshot status | missing | `data/ai-usage/sprints/sprint-009.json` 未生成 |
| 自动发现 | unavailable，command_run_count 0 | `extract-ai-usage.py --post-command-hook --workflow-event sprint.archive --sprint sprint-009 --dry-run --json` |
| 主要输入风险 | high | 20 个 Change、152 项任务、四件套中 `sprint.md` 为 279 行 |
| 主要输出风险 | medium/high | 多批次验收摘要、Sprint readiness、Workflow Sync 与目录扫描 |
| 已采用节省策略 | Fact Sheet 优先 | 只读聚合计数与聚焦片段，不展开全部 Issue/Change trace |

reason：snapshot missing，自动发现无可归因 `token_count`。impact：无法计算实际总用量、缓存率、单 Change 成本、失败重跑消耗和工具输出字符数；本节仅做上下文风险估算。recommended_action：历史审计时显式提供本地 `--session-jsonl`，必要时按 `turn_hash` 提供 `--manual-map`，重跑提取与 Fact Sheet；未观测的 `-` 不解释为真实 0。

### 高消耗来源与优化

| 来源 | 影响 | 证据 | 优化方案 |
|---|---|---|---|
| 多 Change 归档与验收 | high | 20 个 Change、152 项任务，4 个批次 | 按 Sprint 队列分批处理，成功路径只保留计数和下一项；同会话复用已读规则摘要 |
| BUG-0035 UI 验收返修 | high | 33 项任务，双视口、阶段矩阵、computed style 与多轮增量验收 | 按 AC 和视口索引证据，先看输入指纹、最新完整 manifest 与差异摘要 |
| 历史路径提示 | medium | Fact Sheet 35 条旧路径，全部位于归档 Change 材料，集中于 3 个目标 | 以目标、文件和当前态影响聚类；不打印全部 warning，也不改写不可变原证据 |
| 长输出和生成物 | medium | 测试、Docker/build、OpenAPI/Orval、Workflow Sync 可产生大量文本 | `rg -l` 定位；排除 archive、generated、模板与构建目录；先用 diff/stat，失败只取聚焦摘要 |
| Sprint 四件套与规则 | medium | `sprint.md` 279 行；治理命令跨多个规则和技能 | Fact Sheet read-first，片段读取；已读且未变更的规则用摘要承接，避免反复全量读取 |

### Token 优化行动项

| ID | 优先级 | 描述 | 建议下一步 | 状态 |
|---|---|---|---|---|
| S9-A001 | P1 | 为历史 Sprint AI Usage 提供显式 session 回填与覆盖缺口报告 | `/opsx-propose add-historical-sprint-ai-usage-audit` | open |
| S9-A002 | P2 | Fact Sheet 对归档证据旧路径按目标和文件聚合，同时保留当前态 blocker | `/opsx-propose aggregate-archived-path-residuals` | open |

S9-A001、S9-A002 与 sprint-008 复盘的 S8-A001、S8-A002 方向相同；后续规划应合并承接，避免重复创建 Change。本命令未自动创建 Issue/Change。

## 需求与设计复盘

**本地数据边界要以恢复能力定义完成。** REQ-0043 不只改挂载路径：旧 SQLite 库迁移、自动快照上限、0 的语义、受保护副本、删除账本、离线恢复和 Task Trace 都属于同一数据生命期。真实本机没有 legacy 业务库，双库迁移和故障注入由隔离合成回归覆盖；真实 Worker 轮转与重启则单独观察。这种分层证据应在需求验收矩阵中显式区分。

**共享验证环境是交付依赖。** REQ-0044 把 Node 锁文件制品、Firefox/Chromium、跨空间隔离、双项目真实浏览器验收和身份复用作为可验证能力。后续涉及产品观察的需求应在规划时先确定工具链、制品、权限和回退入口，避免实现完成后才发现无法取证。

**Chat 输出需要消息、事件、终态和页面的一致性。** BUG-0030 不能只修一处渲染。合成 API 真浏览器场景、只读历史会话观察、分页、无输出、停止/未知/恢复和脱敏共同形成可读性判定。已删除原故障轮次无法复验，复盘不把替代样本写成历史根因确认。

**验收投影必须可解释。** BUG-0035 的卡片进度由 Issue AC 与 Change tasks 分别提供；缺文档提示必须按真实可访问文档判断。双视口阶段矩阵和 11/11 完整增量验收解决了“功能已修但证据过期”的问题。需求文档应提前定义来源、点击目标、权限与各阶段缺失态。

## 开发质量复盘

- 部署端口迁移的规格差异必须区分新增 Requirement 与修改已有 Requirement；归档前校验标题匹配可阻止错误合并。部署改动另需检查示例、Compose 配置、私有 env 范围和运行时切换边界。
- 自动验收需先预检环境、样本、视觉阶段×视口和附件；命令通过不能代替产品轮次或视觉签认。归档后原 manifest 保持不变，命令型 AC 的合法附件变化走独立补证。
- 历史归档计划的兼容应限于 canonical archive，活动 Change 继续使用严格 schema；BUG-0034 AC-005 的旧值只在既有 manifest 与附件通过核验后参与投影。聚焦回归与最终 Workflow Sync 通过说明该边界有效。
- 35 条归档旧路径提示均属历史材料，当前关闭扫描为 0 blocker；后续宜改进聚合显示，不批量改写已归档证据。

## 可复用抽象

| 模式 | 可复用价值 | 边界 |
|---|---|---|
| 本地数据恢复矩阵 | 挂载、迁移、快照、保护引用、删除账本、离线恢复一起验收 | 合成故障注入与真实运行观察分别标注 |
| 共享项目验证环境 | 锁文件制品、浏览器工具链、隔离身份、双项目验收可复用 | 不把隔离验收外推为生产压力或回滚通过 |
| Chat 输出四层核对 | 消息持久化、执行事件、终态、API/页面展示一致 | 已删除历史轮次不伪造直接复验 |
| 验收卡片事实源映射 | Issue AC、Change tasks、文档入口和权限分开核对 | UI 数字与服务端归档门禁保持一致 |
| 归档计划窄兼容 | 原归档证据保留，旧值仅在 archive 读取 | 活动计划不可继承旧状态 |

## 行动项

| ID | 优先级 | 类型倾向 | 建议与验收目标 | 建议下一命令 | 状态 |
|---|---|---|---|---|---|
| S9-A001 | P1 | 治理 | AI Usage 历史回填展示会话覆盖与缺口，区分 missing、unknown、观测到的 0；与 S8-A001 合并承接 | `/opsx-propose add-historical-sprint-ai-usage-audit` | open |
| S9-A002 | P2 | 治理 | 将归档路径 warning 聚类，区分不可变历史证据和当前可修复引用；与 S8-A002 合并承接 | `/opsx-propose aggregate-archived-path-residuals` | open |
| S9-A003 | P1 | 验收治理 | Sprint close 报告分别展示技术就绪、用户签认和发布状态，并保证最终结论优先于历史批次文字 | `/opsx-propose clarify-sprint-close-verdict-projection` | open |
| S9-A004 | P2 | 测试治理 | 产品首次归档样本预设 stopped/unknown/跨挂载/收尾窗口的判定与替代规则，避免反复新建样本 | `/opsx-propose standardize-chat-archive-sample-matrix` | open |
| S9-A005 | P2 | 需求治理 | 本地快照类需求在验收计划里标注真实 Worker、隔离迁移、故障注入与生产 N/A 的证据层级 | `/req-capture snapshot-recovery-evidence-matrix` | open |

行动项是待评审建议，未自动创建 Issue/Change，也未自动纳入后续 Sprint。

## 执行链路复盘

链路状态：Sprint 已归档，复盘已生成。问题证据：首次关闭需修正 8 处当前引用；历史 AC-005 样本状态触发同步错误，受控兼容 Change 归档后关闭成功；AI Usage snapshot missing；归档证据仍有 35 条旧路径提示、当前关闭扫描 0 blocker。规范优化建议：优先合并推进 S9-A001/S8-A001 和 S9-A002/S8-A002，并在关闭输出中区分技术、签认与发布结论。未自动创建 Issue/Change。

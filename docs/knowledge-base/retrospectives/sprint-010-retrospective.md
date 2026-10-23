---
title: 自动验收与治理恢复迭代经验复盘
created_at: 2026-10-20 08:22:33
updated_at: 2026-10-20 08:22:33
sprint_id: sprint-010
status: active
---

# 自动验收与治理恢复迭代经验复盘

## 迭代概况与证据边界

| 指标 | 事实 | 解释 |
|---|---|---|
| 生命周期 | completed / archive | 已关闭；本轮复盘不重复归档或发布 |
| 范围 | 1 REQ、8 BUG、10 Change | 其中 BUG-0050、BUG-0051 是授权验收样本，非新增产品缺陷 |
| 实施任务 | 91/91 | 任务完成不单独替代验收或真实产品观察 |
| 估算 / 容量 | 36 / 30 人天，120% | 估算不是实际投入；没有 fix 缓冲 |
| 归档队列 | 10 项已归档，0 项待归档 | 关闭时无需重新合并规格 |
| 关闭修正 | 2 处过期 Sprint 描述、5 处 Issue 证据路径 | 修正后 readiness、stale scan、Workflow Sync check 通过 |
| AI 用量 | estimated_fallback | 快照缺失、覆盖 unknown；不提供虚构 token 数 |
| Fact Sheet 提示 | 166 条 archived-path-residual、186 个 evidence hints | 2026-10-20 采样；不是 166 个未解决产品缺陷 |

事实源：[Sprint 范围](../../../iterations/archive/sprint-010/sprint.yaml)、[关闭验收](../../../iterations/archive/sprint-010/acceptance-report.md)、[Sprint](../../../iterations/archive/sprint-010/sprint.md)。计划结束日期仍为 2026-10-30，关闭记录在 2026-10-20；不据此推算真实工时、提前量或生产效率。复盘沿用归档证据，不声称本轮重新执行产品测试。父需求关联不等于纳入 Sprint，REQ-0046 不计入本次正式 REQ 范围。

## 流程复盘

完成事实需要贯穿工具、业务成果与状态投影。BUG-0044 聚焦阶段门禁与会话连续性，BUG-0047 暴露恢复记录的生产/消费契约，BUG-0049 则说明包装命令成功不能仅靠顶层命令名识别。可复用做法是核对操作身份、产物、工作流结果，再投影状态；失败、停止和未知的历史事实不改写。

首次成功与历史恢复是两种验收。BUG-0050 遭遇父任务并发治理写入，正确触发拒绝；BUG-0051 用于独立串行样本。恢复成功不追认原轮次首次成功，实际归档、Issue 迁移、状态同步和用量写入保持串行。证据：[归档完成证明事故](../incidents/20261019-archive-wrapper-completion-proof.md)。

容量从持续追加范围收敛到 120%，fix 缓冲为零。后续规划宜显式记录“新增范围替换什么、保留多少返修容量”，不能因未超过硬门禁就视为无风险。本轮没有实际工时统计，不能断言发生了工期超支。

关闭门禁有效拦截了 7 处旧当前态与失效链接。修正只落在可变聚合文档和证据入口，原始 manifest 保留。Fact Sheet 的历史路径提示与当前关闭阻塞属于不同层级；逐条输出历史提示会掩盖真正待处理项。Workflow Sync 的 5 项子文档提示分别涉及 review 的 done 与 root-cause 的 confirmed，核对语义后保留；不批量改为统一状态。

## 模型 Token 使用分析

### Token Usage Fact Sheet

| 指标 | 值 | 说明 |
|---|---|---|
| ai_usage_mode | estimated_fallback | 定性风险估算，不估算 token 数 |
| snapshot_status / generated_at | missing / 无 | data/ai-usage/sprints/sprint-010.json 未生成 |
| reason | snapshot-missing；无可归因 command run | 本轮已调用 sprint.exps dry-run 自动发现 |
| coverage | unknown | REQ、BUG、Change 均不能确认覆盖 |
| command run | 本次发现 0 条 | 不能解释为整个 Sprint 没有模型调用 |
| 模型/工具调用、失败重跑 | 未知 | 未获得完整可归因统计 |
| input / cached input / output / reasoning / total tokens | 未知 | 不填 0；工具输出字符总量同样未知 |
| impact | 无法比较模型成本、缓存收益和每项交付成本 | 只能基于结构与已观察输出风险分析 |
| recommended_action | 显式会话回填并核对覆盖，必要时配置 manual-map | 历史审计不依赖自动发现；不持久化原始会话 |

矩阵中的 `-` 表示未观测，只有已观测的真实零值才写 `0`。自动发现无结果属于 warning，不阻断知识库沉淀。

### 高消耗来源与优化

| 来源 | 影响与证据 | 优化方案 |
|---|---|---|
| 全量 Sprint/Issue/Change 读取 | 高：四件套分别 107、203、35、36 行，10 Change、91 tasks | Fact Sheet 先取计数与状态，再按 Change 和 evidence hint 分段 |
| 归档 warning 与 evidence hints | 高：166 条路径提示、186 个入口；前轮 summary 输出仍出现长 JSON | 按类别、Change、文件聚合，默认仅展示计数与当前 blocker；完整明细按需读取 |
| 重复规则/技能读取 | 高风险：前轮入口规则与技能合并读取触发输出截断 | 复用会话内已读摘要，仅读取变更或缺失段落 |
| 宽泛搜索与历史归档 | 中：Fact Sheet 可直接给出 10 个唯一归档路径 | 搜索默认排除 Harness、模板 assets、archive、generated、node_modules、dist、coverage；只有命中的目标归档例外 |
| diff 与生成物 | 高风险：前轮全仓 diff stat 仍混入大量无关未提交变更 | 先限定本次路径，再 name-only/stat；OpenAPI/Orval 只看契约差异，不倾倒生成物 |
| 测试、构建与同步日志 | 中高风险：本轮没有全 Sprint 字符统计，不能量化浪费 | 只报退出码、失败数、首个根因和证据入口；Docker/build 与 Workflow Sync 默认摘要，失败才展开 |
| Harness/模板注入 | 潜在风险，未测得本轮实际占比 | 仅加载当前命令所需资产，不把潜在风险写成已发生消耗 |

本轮遵守 Fact Sheet read-first、复用已读规则摘要、证据聚合和聚焦回读。前轮长 summary、全仓 stat 和合并规则输出应改进；终端 max_output_tokens 截断会丢失关键内容，优先在输出前聚合，而不是反复读取被截断全文。

Token 优化承接 S9-A001（历史用量覆盖）与 S9-A002（路径提示聚合），不重复建立同义行动。S10-A003 补充输出预算的回归门禁，与这两项合并排期。

## 需求与设计

需求中心布局与负责人显示两类问题可按共享卡片契约预防：布局覆盖九阶段、长标识和双视口，身份显示保留稳定 owner 键并提供可读名称及安全回退。证据见 [布局修复](../../../openspec/archive/2026-10-19-fix-requirement-center-card-width-sprint-tag-wrap/trace.md)和[负责人修复](../../../openspec/archive/2026-10-19-fix-requirement-center-owner-display/trace.md)。

REQ-0047 复用 BUG-0044/0047 的阶段门禁与记录契约，限定评审恢复试点；23 项验收覆盖功能、知识承接及原型。不能因本 Sprint 有 8 个 fix-* 就推断需求没有原型：其中 2 个为验收样本，且已有视觉与原型证据。当前材料不足以建立“原型缺失导致缺陷数量”的因果关系。

沿用[原型驱动 UI 门禁](../best-practices/prototype-driven-ui-gate.md)，补充跨状态卡片与长文本清理边界；现有证据不支持为了统一而新建通用 AdminListPage。组件抽象应优先从重复出现的动作、状态和边界出发。

## 开发质量与证据分层

| 主题 | 已有证据 | 质量结论与限制 |
|---|---|---|
| 布局与身份 | 布局 5 AC；负责人 8 AC | 截图、computed style、权限与回退并行核对；不冒称未知原视口精确复刻 |
| 阶段与恢复 | BUG-0044 12 AC；BUG-0047 9 AC；REQ-0047 23 AC | 合成故障、真实正常/中断、部署版本分别记录 |
| 清理边界 | BUG-0048 5 AC；Web 40、后端 96 项回归 | 旧面板清理按 DOM 所有权界定，不能从正文关键词猜测可删除容器 |
| 归档证明 | BUG-0049 7 AC | 身份、失败、幂等、重启与真实样本分开；恢复不重放归档 |
| 验收编排 | 治理 Change 7 AC、50 项聚焦回归 | 指纹复用与命令去重减少重复执行；不代表全仓测试覆盖 |

以上数字为各归档 trace 的历史计数，不跨 Change 相加为唯一测试总数。代码验收、真实产品观察、部署版本一致性与 Sprint 关闭门禁互不替代。[恢复记录契约事故](../incidents/20261019-review-operation-record-contract.md)中的阶段性 REQ-0046 观察保留原日期事实，后续结果以 BUG-0048 归档证据为准。

product_data_collection_observability: applicable（复盘对象）；affected_layers: API、DB、request_logs、usage_events、task_traces、task_trace_spans、Web 与治理恢复。validation: 复用 REQ-0047 与 BUG-0049 归档验证摘要，保持不透明身份关联、原终态与直接 API 不伪造行为事件。本轮仅知识库文档，新增运行采集、schema、部署、安全策略及客户端生成为 N/A。

## 可复用抽象

形成[治理恢复与归档验收证据分层实践](../best-practices/governance-recovery-archive-evidence.md)：以生产/消费契约、业务效果核验、不可变历史与可变投影、串行样本四部分组织验证。复用既有事故，不复制完整 trace 或另建同义事故文章。

可考虑提取共享的状态判定与证据摘要，但保留对象身份、阶段权限和不同命令的成功条件；本轮只沉淀建议，不自动修改实现或规则。

## 行动项

| ID | 优先级 | 建议与验收目标 | 建议下一命令 | 状态 |
|---|---|---|---|---|
| S10-A001 | P1 | 关闭时同步可变证据入口，聚合报告区分技术就绪、关闭授权与发布；保留 manifest 哈希与历史语义。与 S9-A002/A003 合并 | `/req-capture 归档当前态引用与关闭结论一致性` | open |
| S10-A002 | P1 | 治理样本明确首次成功、失败拒绝、原执行恢复与并发隔离；不得靠重放消除历史失败。承接 S9-A004，已有 BUG-0049 实现作为基线 | `/req-capture 治理归档样本隔离与证据矩阵` | open |
| S10-A003 | P2 | Fact Sheet 摘要输出按字段/类别聚合；以 10 Change 和大量历史提示验证输出预算，不丢当前 blocker；失败日志只输出摘要 | `/req-capture Sprint事实摘要输出预算与覆盖检查` | open |
| S10-A004 | P2 | 共享卡片契约覆盖长 ID、同名/缺失 owner、九阶段和窄视口；清理函数仅触及所属旧面板，普通正文关键词不得触发删除 | `/req-capture 需求卡片与会话清理边界回归契约` | open |

S9-A001 至 S9-A005 保持 open；本次未证明其全部验收目标已落地，不因方向相关而标记 done。上述命令为后续建议，执行前查重并走评审/Sprint 链路，未自动创建 Issue/Change。下一 Sprint 规划优先合并已有行动并保留返修缓冲，不自动扩大容量。

## 执行链路复盘

链路状态：warning。交付为复盘、实践、索引和回链；归档状态不变。问题证据：AI 快照 missing、166 条历史路径提示、前轮 7 项关闭残留修正记录。规范优化建议集中在行动表，先复用既有 S9 行动，不自动改 rules 或业务代码。验证结果由本次命令最终报告提供。

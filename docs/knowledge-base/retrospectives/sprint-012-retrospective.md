---
title: 跨入口续接与迭代归档经验复盘
created_at: 2026-10-23 22:51:31
updated_at: 2026-10-23 22:51:31
sprint_id: sprint-012
status: active
---

# 跨入口续接与迭代归档经验复盘

## 迭代概况与证据边界

本迭代完成从直接命令证明、跨入口续接到Sprint归档入口的交付；反复返修集中在后继变更如何影响旧成果的判定。关闭成功不意味着原有证明机制的所有扩展场景都已解决。

| 指标 | 事实 | 边界 |
|---|---|---|
| 生命周期 | completed / archive | 2026-10-23关闭；本次仅复盘 |
| 范围 | 1 REQ、4 BUG、5 Change | 任务83/83完成，全部已归档 |
| 估算/容量 | 34/30人天，113.33% | 超出4人天；不是实际投入，不能推算效率 |
| 规划增长 | 8 → 16 → 26 → 34人天 | 已交付项仍计入累计范围；容量不通过改大数值消除风险 |
| 最终逐AC结论 | BUG-0060 16/16、0061 14/14、0062 11/11、REQ-0049 30/30、BUG-0063 18/18 | 属于各自最终有效报告，不累加重复运行测试数 |
| 关闭门禁 | 严格预检通过、陈旧扫描39文件0阻塞、同步0错误 | legacy SQLite路径及根因confirmed语义提示保留 |
| Fact Sheet | 513条历史路径提示 | 不等于513个产品缺陷；原始manifest不改写 |

证据：[范围](../../../iterations/archive/sprint-012/sprint.yaml)、[最终验收](../../../iterations/archive/sprint-012/acceptance-report.md)、[关闭记录](../../../iterations/archive/sprint-012/sprint.md)。Fact Sheet采样于2026-10-23；计划结束日期仍为2026-11-04，不以提前关闭推算节省人天。复盘没有重跑产品验收。

## 流程复盘

1. **准备、发送、执行完成与成果核验分别证明。** BUG-0060暴露“命令产物存在”与“原轮次可安全续接”之间的缺口；BUG-0061进一步覆盖产品受阻→CLI续接→产品核验→实际发送→归档终态。按钮准备成功不能替代真实发送，恢复成功不能把失败历史改成成功。
2. **后继变更判断需要完整场景设计。** BUG-0062将模块级冲突缩小到条文；BUG-0063又遇到同条文兼容追加及显式替代边界。最终策略取消独立兼容证明硬限制，但保留正常验收、唯一身份、连续归档链、交付增量、最终效果和并发检查。早期设计是历史决策，不能继续作为当前强制约束。
3. **先稳定策略，再收集完整验收。** BUG-0063经历多轮重新部署、旧真实轮次不可核验、隔离数据库unknown投影修正，最终18/18通过。教训是把策略选择、环境样本和输入指纹提前固定；变化后只复验受影响项，不能借历史通过掩盖当前缺证。
4. **容量门禁不是缓冲承诺。** 34人天低于36人天硬上限，却已无返修缓冲。S11-A001在本迭代得到范围与风险记录方面的落实，但未证明通用容量治理已闭环，继续保留open。
5. **收尾入口也需要环境前检。** 本轮关闭的默认Python缺SQLAlchemy，已有后端虚拟环境重跑成功。关闭摘要仍有待人工sign-off投影，与completed并存；不虚构人工签署，纳入S10-A001核对当前态与摘要契约。

## 模型 Token 使用分析

### Token Usage Fact Sheet

快照：`data/ai-usage/sprints/sprint-012.json`；生成于 `2026-10-23T14:44:11.432955Z`，`snapshot_status: present`，`ai_usage_mode: actual`，REQ/BUG/Change覆盖均pass、快照warning为0。以下是采集器报告的实测聚合值，**不是已经完成归属审计的Sprint精确成本**。

| 指标 | 采集值 |
|---|---:|
| input_tokens | 115,098,998 |
| cached_input_tokens | 113,379,200 |
| output_tokens | 267,316 |
| reasoning_output_tokens | 34,022 |
| total_tokens | 115,681,033 |
| command_run_count | 51 |
| model_call_count | 770 |
| tool_call_count | 130 |
| tool_output_chars | 0 |
| retry_count | 0 |

覆盖列表包含REQ-0002、REQ-0046、REQ-0050等范围外对象；这可能来自关联会话或识别规则，尚不能确定各对象成本归属。total_tokens与input_tokens加output_tokens相差314,719，当前材料不能解释该口径差异，保留原值不自行修正。缓存输入已包含于输入，推理输出也不能重复加总。retry_count和tool_output_chars为0只是采集结果，不证明没有返修或工具输出；实际trace明确存在失败与重跑。关闭hook的token-count-missing说明本轮计量有缺口，历史实测快照有效不等于本轮计量完整。本次复盘也尝试了本地session自动发现dry-run，返回token-count-missing；不编造本命令Token数。不据此换算金额、单位任务成本或节省比例。

阶段聚合中Opsx-Accept为32,658,992、Opsx-Apply为25,358,479、Opsx-Modify为23,043,285 token，是观测值最高的三个阶段。真实验收、部署和策略返修是需要关注的成本来源，但不能从阶段总数判定浪费比例。未观测阶段显示“-”，不写成真实0；已观测零值保留0并说明缺计量可能性。

### 高消耗来源与优化方案

| 来源 | 证据与影响 | 优化方案 |
|---|---|---|
| 四件套与历史证据 | 69/258/70/94行，5 Change、83任务；513条提示放大输出 | 先Fact Sheet字段聚合，只按evidence hints读取对应片段；警告按类型计数，明细按需 |
| 归档摘要倾倒 | 本次关闭曾返回约5.5万token工具输出，随后被截断；不是全量模型消费测量 | 生成JSON到本地后仅输出选定字段，不能依赖末端截断代替源头聚合 |
| 重复规则与技能 | 同会话重复全文读取会放大输入；未测占比 | 复用已读摘要，版本或边界变化才补读 |
| 宽泛搜索 | archive/checkpoint/模板及生成物会重复命中 | 默认排除archive、generated、Harness、assets、node_modules、dist、coverage；目标归档仅定向放开 |
| diff与生成客户端 | 全量OpenAPI/Orval diff不能代表本次变更 | 先限定路径的name-only/stat，再读契约差异 |
| 测试、Docker与同步日志 | 多次部署/返修真实存在；失败次数不能由retry_count=0推断 | 成功只输出退出码与计数，失败摘要含首个根因和证据入口，按Change分段处理 |
| 验收重跑 | BUG-0063最终增量复用17项、执行1组 | 稳定后集中验证，输入指纹驱动受影响AC复验；必要时沉淀输出预算及前检gate |

读取边界和稳定增量复验符合上下文预算方向；全量摘要输出需修正。优化均为建议，尚无对照实测收益。S10-A003承接输出预算，S9-A001承接范围外归属、缺计量和指标口径审计，避免另建同义行动项。

## 需求与设计

REQ-0049把归档入口放在Sprint对象上下文，预填草稿与执行归档分离；草稿保护、会话复用、忙碌状态、未签署拒绝和终态回读必须一起验收。最终30/30覆盖了功能、知识库与原型条件。4个fix Change集中于治理证明边界，没有证据证明是缺少UI原型导致，不能据缺陷数量倒推原因。

前置设计应列出“同模块不同条文、同条文追加、显式替代、断链/篡改、并发变化、外部结果未知”的行为矩阵，写清每种情况对当前动作与历史事实分别有什么影响。BUG-0045与REQ-0048不在本迭代Scope内；独立验收环境诉求只能作为关联背景，不能计入本次交付。

## 开发质量与可复用抽象

复用[治理恢复与归档验收证据分层实践](../best-practices/governance-recovery-archive-evidence.md)。合成回归验证负例、权限与并发；独立MySQL验证兼容性；真实产品轮次验证首次完成和原操作恢复；部署指纹、1440/390视口与computed style提供不同层面的证据。它们不能互相代替，也不能把多轮通过数累加为新的覆盖率。

可复用抽象是共享准入判定、结构化诊断、业务成果与轮次状态分离、当前态与历史证明分离。现有事故文档已覆盖实现经验，本次不新增近义best-practice，也不建议无证据支撑的通用页面组件。

证据入口：
- [直接命令最终记录](../../../openspec/archive/2026-10-21-fix-direct-command-completion-proof/trace.md)。
- [跨入口续接最终记录](../../../openspec/archive/2026-10-21-fix-cross-entry-continuation-guard/trace.md)。
- [条文冲突修复](../../../openspec/archive/2026-10-21-fix-archive-requirement-scope-conflict/trace.md)。
- [Sprint归档入口](../../../openspec/archive/2026-10-21-add-sprint-archive-chat-entry/trace.md)。
- [后继策略最终验收](../../../openspec/archive/2026-10-23-fix-compatible-requirement-successor/trace.md)及[策略修订经验](../incidents/20261022-compatible-requirement-successor.md)。

product_data_collection_observability: applicable；affected_layers: API、Web、治理证明、执行保护、请求审计与Task Trace；validation: 引用已归档最终验收及关闭门禁。N/A：本次仅更新知识库和Sprint回链，无API、数据库、UI、部署、安全权限或客户端生成变化。

## 行动项与前序承接

| ID | 优先级 | 行动与验收边界 | 下一命令 | 状态 |
|---|---|---|---|---|
| S10-A001 | P1 | 当前态路径及completed/sign-off摘要一致；历史附件原样保留，当前入口可解析 | `/req-capture 归档当前态引用与关闭结论一致性` | open |
| S10-A002 | P1 | 通用样本矩阵覆盖首次成功、失败、原操作恢复和跨入口对照；本迭代复用不等于整体关闭 | `/req-capture 治理归档样本隔离与证据矩阵` | open |
| S10-A003 | P2 | 用513条提示验证摘要上限、按需明细及不遗漏阻塞；比较输出字符数与实际输入计量 | `/req-capture Sprint事实摘要输出预算与覆盖检查` | open |
| S9-A001 | P1 | 审计范围外对象、token总数差额与缺计量；未知不表示0，禁止双计缓存 | `/req-capture Sprint用量归属与统计口径审计` | open |
| S11-A001 | P1 | 下一轮规划明确追加/替换范围、返修缓冲与外部关闭依赖；不以硬上限代替风险评估 | `/sprint-explore` | open |
| S12-A001 | P2 | 治理入口前检解析依赖和项目解释器；缺依赖在迁移前给出诊断，已迁移失败可幂等续接 | `/req-capture 治理命令运行环境前检与恢复` | open |

五项沿用原ID，不修改历史行动状态；新增一项环境前检建议。每个capture先检查重复Issue，尤其验收环境能力需先比对BUG-0045、REQ-0048及REQ-0044边界。当前未自动创建Issue/Change、未加入后续Sprint；下一轮规划再确认承接。

## 执行链路复盘

链路：Fact Sheet → 针对性证据复核 → 五维分析 → 知识库与Sprint回链 → 文档验证。问题证据包括阶段策略变动、范围增长、计量归属疑点及关闭解释器失败。建议沿既有行动项收敛，不在本命令修改rules、脚本或产品代码。

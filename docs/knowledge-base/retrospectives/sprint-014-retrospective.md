---
title: Sprint-014 经验复盘
created_at: 2026-10-30 08:37:47
updated_at: 2026-10-30 08:37:47
sprint_id: sprint-014
status: active
---

# Sprint-014 经验复盘

## 交付概况

本迭代完成Chat恢复、回答一致性、自动核验、正文预览、数据库竞争、后继完成证明及需求中心性能修复，并交付临时资源、探索反馈、归档Python入口、Issue阶段和原型引用治理。12个Change已归档，118/118任务完成，7个BUG关闭，未纳入REQ。Sprint已completed/archive；这是交付归档事实，不代表统一生产部署或版本发布。

规划39故事点、34人天，对30人天容量为113.3%，无剩余返修缓冲。人天为规划估算，不是实际投入；计划结束日期仍是2026-11-09，不能把该日期当作实际关闭时间。实际关闭依据[验收报告](../../../iterations/archive/sprint-014/acceptance-report.md)。

事实源：[Sprint机器范围](../../../iterations/archive/sprint-014/sprint.yaml)、[迭代规划与关闭记录](../../../iterations/archive/sprint-014/sprint.md)。本次先生成Fact Sheet，再根据警告和本会话已核对证据定位原文，没有重跑产品测试。

## 流程复盘

1. **任务完成、验收通过与迭代关闭是不同事实。** 首次归档检查12个Change全部通过，但1项当前状态和9项旧引用阻断关闭。修复后严格扫描53文件，0阻断、0警告；同步7项BUG验收passed并纠正旧阶段字段。归档签认来源于用户明确授权，不表示用户亲自运行了全部测试。
2. **当前入口可修复，历史证据保留。** Fact Sheet仍报告396条archived-path-residual、416个证据提示，代表文本中旧路径出现；已抽查的来源包括历史summary/checkpoint。不能把396条全部断言为失效链接，也不能为了清零改写manifest。当前关闭扫描通过与历史文本提示并不矛盾。
3. **增量追加消耗了返修容量。** 从治理改进扩展到七项缺陷，最终34/30人天。BUG-0056多轮性能返修说明局部回归通过不等于现场表现稳定；现有材料不足以量化超容量对耗时的因果影响，但没有余量是明确规划风险。
4. **资源清理和现场可达性按时间分开。** 临时Docker治理曾验证2容器、1网络正常/取消清理，模拟到期不等于后台调度。归档入口docker info不可达不能推翻历史clean，也不能证明当前全机零残留。本次复盘未创建环境。
5. **状态源需要注明语义。** 根因文档confirmed表示根因确认，不能为消除同步提示改成done。目录已归档而trace保留applied执行历史也需结合目录和共享派生语义解读，不据单字段重跑归档。

## 模型 Token 使用分析

### Token Usage Fact Sheet

| 指标 | 判定 | 依据与影响 |
|---|---|---|
| ai_usage_mode | estimated_fallback | Sprint快照不满足完整actual统计条件 |
| snapshot_status | stale | 采样generated_at为2026-10-30T00:34:10.220667Z |
| reason | coverage-missing | 缺fix-chat-final-answer-duplicate-concatenation覆盖；覆盖集合还有范围外标签 |
| impact | 不展示精确Token、成本或节省比例 | 聚合值不能作为本Sprint可靠实测 |
| recommended_action | 用明确可归因会话补齐历史覆盖，必要时manual-map，再刷新快照 | 不复制原始会话或凭据 |
| 本次自动发现探针 | actual，1个command run，0警告 | 仅dry-run结果，不能补齐整个Sprint历史覆盖 |
| 结构性规模 | 12 Change、118任务、635行四件套、396路径提示、416证据入口 | 仅用于定位阅读成本，不换算Token |

input、cached input、output、reasoning output、total tokens，以及模型调用、工具调用、失败重跑、工具输出字符数均不作为可靠Sprint总量展示。矩阵“-”表示未观测，不等于0；缓存输入和推理输出属于子项，不重复累加。本次治理运行无覆盖完整边界的实测Token，不宣称净收益。

### 高消耗来源与优化方案

| 来源 | 本次证据或风险 | 可执行优化 |
|---|---|---|
| 规则和技能重复读取 | 归档初期组合读取发生截断 | 复用已读版本摘要，只补变更及必要片段 |
| Fact Sheet大输出 | summary仍含大量路径提示；本次把warnings误当映射，实际为列表 | JSON先落本地临时文件，先检查字段形态，再输出计数、分类、少量样本 |
| 四件套及Change全文 | sprint.md为294行，12项共享证据 | 按Change与evidence hints分批，只读相关任务计数及验证片段 |
| 宽泛搜索和diff | 大量并行修改与归档文件，完整git status输出截断 | rg先定位；默认排除Harness、模板assets、archive、generated、node_modules、dist、coverage，精确目标才放开；diff先stat/name-only |
| 测试、Docker及同步日志 | 多轮长测、共享回归和阶段同步容易重复输出 | 成功报结果；失败仅命令、退出码、首因和证据入口；按输入变化决定增量复验 |
| 末端截断 | max_output_tokens不能控制源头返回体 | 工具输出前结构化裁剪，阻断项单独保留，明细按需展开 |

符合预算的做法包括复用本会话证据、定向读取、共享状态串行写入、对精确计量缺口保持回退。需要修正的是大组合输出与字段形态假设。优先承接S10-A003和S9-A001，不新建重复行动；脚本改进需后续Change和实际输出量对照验证。

## 需求与设计复盘

七项BUG按业务边界拆分：unknown恢复退避、最终答案身份与去重、核验刷新失效保护、正文预算与截断原因、核验事务边界、后继完成证明、需求中心读取成本。共同原则是把执行终态、已提交成果、核验资格与展示分开，不能为了恢复入口改写原失败或停止历史。

BUG-0056与BUG-0068共享读取和数据库路径，需要明确输入版本与集成边界；BUG-0069虽然承接BUG-0061复发背景，仍使用独立证明与验收，不能继承历史passed。12项中9个fix-*（含两项治理修复），不能据此推断UI原型不足；没有足够证据证明返修由缺原型导致。本次不建议无依据新增通用页面或弹窗框架。

## 开发质量与证据边界

- BUG-0056最终正式120请求全部成功、218授权对象、默认30卡。自然打开HTTP/首卡P95为0.307/0.573秒，刷新0.389秒；额外2CPU打开0.384/0.715秒，刷新1.199秒。请求ID对账与120后台审计关联通过。历史20秒、59秒及压力失败窗口保留，结论只适用于实测窗口，不保证任意过载。资源/配对结果按明确版本边界复用，不宣称所有长测在最终版本重跑。
- BUG-0068的[验证记录](../../../openspec/archive/2026-10-27-fix-chat-database-lock-execution-interruption/verification.md)区分SQLite155项、MySQL82项、真实执行器90次并发核验和隔离浏览器。零行UPDATE仍可能参与锁竞争；文件扫描移出写事务、短事务及权限/版本复核共同构成修复。既有两项治理看板文案断言失败被保留为基线warning，不计为通过。
- BUG-0064真实Docker恢复样本采用合成认证和固定镜像，不调用模型；暂停330秒没有新增容器，6创建/6销毁。恢复调度的通过不能替代所有部署或模型运行证明。
- 前端的核验GET次数、最终回答唯一性、微片段/多字节边界和会话切换保护分别验证；合成身份、真实HTTP、真实模型与视觉证据不混算。回归数量跨Change可能重复引用，不加总为唯一测试总数。

证据入口：[BUG-0056最终验证](../../../openspec/archive/2026-10-30-fix-requirement-center-context-load-latency/verification.md)、[BUG-0064验收](../../../issues/bugs/archive/BUG-0064-chat-unknown-recovery-container-churn/acceptance.md)、[临时资源治理](../../../openspec/archive/2026-10-26-add-temporary-docker-lifecycle/trace.md)。

## 可复用抽象与知识沉淀

复用有界恢复状态、稳定回答身份与幂等合并、读取预算和明确截断原因、短事务外扫描、不可变快照内索引、请求到后台审计关联及独立后继证明。权限和资格每次重新判断，缓存不能替代授权新鲜度。

已有[需求中心读取成本经验](../incidents/requirement-context-read-cost.md)承载性能机制，本次只更新最终证据定位与适用边界；已有[治理恢复与归档证据分层](../best-practices/governance-recovery-archive-evidence.md)承载历史保护，本次不另建重复最佳实践。临时资源实践直接引用既有标准与Change，不复制规范。

## 行动项与前序承接

| ID | 优先级 | 行动与验证边界 | 建议下一命令 | 状态 |
|---|---|---|---|---|
| S10-A001 | P1 | 区分当前链接和历史字面量；本次10项修复不等于通用扫描完成 | `/req-capture 归档当前态引用与关闭结论一致性` | open |
| S10-A002 | P1 | 真实首次、拒绝、恢复、视觉与资源清理独立取证；临时资源治理为局部落实 | `/req-capture 治理归档样本隔离与证据矩阵` | open |
| S10-A003 | P2 | Fact Sheet输出有界摘要、稳定字段形态；用396条提示检查阻断不遗漏 | `/req-capture Sprint事实摘要输出预算与覆盖检查` | open |
| S9-A001 | P1 | 补齐缺失Change覆盖并排除范围外归属；单命令actual不冒充全迭代actual | `/req-capture Sprint用量归属与统计口径审计` | open |
| S11-A001 | P1 | 后续追加明确替换或延期与返修缓冲，不把34/30理解为有余量 | `/sprint-explore sprint-016` | open |
| S12-A001 | P1 | Python归档入口已局部交付；继续验证wrapper、依赖和中断恢复的完整边界 | `/req-capture 治理命令运行环境前检与恢复` | open |
| S15-A002 | P1 | 关联S13-A001；本Sprint机器文件仍有重复空列表键，后续写入应拒绝重复键并复核范围 | `/bug-capture Sprint范围追加产生重复空列表键` | open |
| S14-A001 | P2 | 性能验收固定自然/受控负载、并发服务、版本、请求ID与样本停止规则；保留所有失败窗口 | `/req-capture 需求中心性能验收窗口与版本边界回归` | open |

沿用前序ID以避免重复；S13-A002等未在本表重复的行动仍保留原状态。Sprint的S13-resource-lifecycle承接标签不是前序正式行动ID，不据此关闭S10-A002。新增S14-A001仅为知识库建议；capture时先检查现有注册表与相似Issue，再经评审纳入Sprint。本次未创建Issue/Change，不自动实施治理优化。

## 验证与执行链路复盘

Fact Sheet → 聚焦证据与前序去重 → 五维分析 → 更新既有事故经验 → 索引及Sprint回链 → 文档检查。仅改知识文档与回链，不执行apply/archive，不改业务代码、规则、采集字段或生命周期状态；不为写复盘重放sprint.archive。

product_data_collection_observability: not_applicable（本次文档写入）；affected_layers: []；reason: 仅引用已交付验证，不改变API、DB、UI请求、遥测、权限、部署或客户端生成；validation: 元数据、五维章节、行动项、链接及索引检查。历史产品测试引用原证据，不冒称本次重跑。

链路状态warning：历史路径提示、整体用量覆盖缺失和Docker现场连接限制保留。规范优化建议由行动表承接，未自动创建Issue/Change，未宣称Token或时间收益。

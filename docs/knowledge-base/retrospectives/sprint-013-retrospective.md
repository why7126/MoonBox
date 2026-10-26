---
title: 规则演进、Chat规模扩展与归档补证经验复盘
created_at: 2026-10-26 11:28:36
updated_at: 2026-10-26 11:28:36
status: active
sprint_id: sprint-013
---

# 规则演进、Chat规模扩展与归档补证经验复盘

## 迭代概况与证据边界

本迭代完成规则差异审阅、需求卡片持续信息展示、Chat 大规模工作区与结果保存三项需求，并完成五项治理 Change。主要经验是先确定业务规则及证据边界，再稳定实施；归档历史必须可验证，不能用重写原记录消除差异。

| 指标 | 本轮事实 | 解释边界 |
|---|---|---|
| 生命周期 | completed / archive，2026-10-26 11:12:06 关闭 | 计划结束为11月5日，不能据提前关闭推算节省工时 |
| 范围 | 3 REQ、0 BUG、8 Change | 0 BUG 指纳入范围的BUG数，不代表零缺陷或零返修 |
| 任务 | 105/105 | 各Change完成数46、17、3、3、4、24、4、4 |
| 容量 | 估算33/30人天，110% | 低于120%硬上限，仍无返修缓冲；不是实际投入 |
| 范围演进 | 13 → 16 → 17 → 30 → 32 → 33人天 | 来自scope_estimates与纳入理由，非逐日实际燃尽 |
| 关闭质量 | 8项深层归档检查通过，25文件陈旧扫描零阻断 | 本次复盘引用关闭证据，未重新运行产品验收 |
| 补证修复 | 3项基线阻断、4处失效引用已解决 | 独立修复Change归档；189项联合回归不是全Sprint独立测试总数 |
| 保留限制 | legacy SQLite目录警告；运行容器未因关闭自动升级 | 迭代关闭不等于产品部署或版本发布 |

事实源：[范围与估算](../../../iterations/archive/sprint-013/sprint.yaml)、[最终验收](../../../iterations/archive/sprint-013/acceptance-report.md)、[交付说明](../../../iterations/archive/sprint-013/release-note.md)。本次Fact Sheet采样于2026-10-26；105个任务不是105个AC，反复运行的测试数不累加为覆盖率。

## 流程复盘

1. **策略改变需要同步证据口径。** REQ-0050从独立授权、首次可信启用等方案转为当前差异审阅及正常验收门禁，旧界面与旧确认不再代表当前交付。多轮v5—v11材料保留过程事实；最终12项AC的证据才支持本版结论。应在完整样本采集前明确哪些动作保留、退出，以及取消额外签字不等于取消权限、验收、完整历史或并发检查。
2. **完成验收与允许归档分别检查。** REQ-0053的27项联合验收通过后，仍需解决同名业务规格演进的正式准入；support-reviewed-spec-evolution以完整结构化验收覆盖相关delta全文。验收通过不能直接覆盖恢复链阻断。
3. **不能改写历史来消除哈希差异。** REQ-0050归档结果少一个末尾换行，导致后续基线断链。隔离重放精确复现原哈希，独立清单只证明末尾LF差异；原journal和manifest保留。见[末尾空行补证事故](../incidents/20261026-archive-newline-proof.md)。
4. **容量追加仍需明确取舍。** 两项XXL需求合计26人天；追加治理收尾后总量33人天。S11-A001仅落实了估算与风险记录，尚未建立实际缓冲；后续规划应先处理替换、延期或显式接受风险，而非仅检查是否低于36人天。
5. **统一解释器尚未覆盖全部壳脚本。** 虽已交付unify-governance-python-entry，归档wrapper仍曾因裸python选中缺SQLAlchemy的解释器失败；显式项目虚拟环境重跑成功。S12-A001保留open，不能仅凭统一入口Change完成就宣称全部路径已覆盖。
6. **当前入口、历史文本与关闭授权分开记录。** 四处Issue验收引用已修正；历史checkpoint/manifest路径保持原样。最终关闭依据用户“验证通过后继续归档”的条件式授权，不虚构用户亲自测试或独立复验。

## 模型 Token 使用分析

### Token Usage Fact Sheet

采样快照为 `data/ai-usage/sprints/sprint-013.json`，生成于 `2026-10-26T03:14:29.748759Z`。Fact Sheet报告 `snapshot_status: present`、`ai_usage_mode: actual`、warning_count=0。以下仅列采集器的实测聚合值，尚不能当成已完成归属审计的Sprint精确成本。

| 指标 | 采集值 |
|---|---:|
| input_tokens | 88,184,111 |
| cached_input_tokens | 86,568,448 |
| output_tokens | 228,655 |
| reasoning_output_tokens | 30,730 |
| total_tokens | 88,616,726 |
| command_run_count | 35 |
| model_call_count | 654 |
| tool_call_count | 112 |
| tool_output_chars | 0 |
| retry_count | 0 |

本轮session自动发现dry-run返回actual、warning_count=0；这不追溯证明上一关闭命令的缺计量已修复。关闭Hook曾为estimated_fallback，原因token-count-missing，与聚合快照标记actual并存，需保留两个口径。

覆盖集合包含REQ-0002、REQ-0008、REQ-0025、BUG-0063等范围外关联对象及archive-change、build-images等疑似命令词；仅凭覆盖pass不能认定精确归属。total_tokens比input_tokens加output_tokens多203,960，原因尚未核实，保留采集值不自行修正。cached_input是输入子项，reasoning_output也不重复相加。tool_output_chars=0、retry_count=0只是字段采集结果，不证明无输出或无重跑；本会话已有多次测试、预检和环境失败证据。矩阵“-”表示未观测，不能填0；实测零值保留0并标注口径。不据这些值换算金额、单位任务成本或优化收益。

阶段采集值最高的三项为opsx.modify 32,696,106、opsx.apply 21,463,803、opsx.accept 12,120,685 token。多轮规则策略返修值得关注，但没有完整归因不能把阶段总量直接标为浪费。

### 高消耗来源与优化方案

| 来源 | 事实与影响 | 后续方法 |
|---|---|---|
| 摘要仍携带大量历史路径 | Fact Sheet 1,066条提示；529条验收历史、535条checkpoint、1条Issue历史、1条原型上下文 | 先落本地JSON，再只取类型计数、代表样本及必要字段；明细按需，不靠末端截断 |
| 四件套与归档遍历 | 115/245/63/126行，8 Change、105任务 | 先scope/counts/tasks/token_risks；只按提示定位原文，不展开全部trace |
| 重复规则、技能读取 | 首轮归档出现组合全量读取与截断；同会话多数规则已读 | 复用规则摘要与版本，变化时只补读相关章节 |
| 宽泛搜索与生成物 | 历史acceptance和checkpoint反复命中同一引用 | 默认排除archive、generated、node_modules、dist、coverage、Harness及模板assets；仅为目标归档定向放开 |
| diff与工具日志 | 关闭曾因输出过大被截断；wrapper解释器失败有明确首因 | 先name-only/stat，再局部diff；成功仅计数，失败给首因、退出码和脱敏证据入口 |
| 验收输入未稳定 | 空行补证修复在测试后又完善结构校验与delta位置，产生再次完整验证 | 先完成边界审查和规格位置，输入稳定后集中跑验收；变化后按AC输入复验，不能省略必要检查 |
| 工作流收尾 | 迁移、同步、用量快照共享事实源 | 严格串行，以wrapper成功结果为准；按Change分段处理，不重复已完成副作用 |

本次复盘采用字段裁剪、定向片段和既有规则摘要；初次归档的超长输出不符合预算目标。读取、检索、输出及增量复验方案分别承接S10-A003、S10-A002、S12-A001；没有对照测量，不宣称节省比例。

## 需求与设计复盘

- **REQ-0050：业务简化应贯穿长期知识。** 当前仅从相关阻断上下文审阅规则差异，正常验收、权限、历史和写前复核继续生效；旧独立密钥、签名收据与确认流程只作历史。已有最佳实践仍保留旧流程，本次补充当前适用边界，避免知识库反向恢复已退出要求。
- **REQ-0051：信息持续展示要按数据语义验收。** 根因状态、根因文档入口、人天数值及五档展示是一组契约；样式、键盘focus、非法值隐藏、跨阶段持续展示需要一起验证。多次标签细节返修不证明缺少原型，而说明组件级尺寸和交互契约需要更早收敛。
- **REQ-0053：取消业务总量门槛不等于无限资源。** 采用数据库分块、增量快照、有界读取与部署级资源保护；恢复区分准备失败、已开始执行和未知终态。旧记录缺全文用legacy_unavailable表达，不能伪造内容。选择数据库分块降低新服务依赖，同时增加数据库体量与备份责任，双库和回退边界不能只靠SQLite通过代替。

## 开发质量与可复用抽象

最终证据按来源分层：合成回归覆盖权限、并发及失败边界；真实模型轮次验证执行与结果保存；隔离API验证数据与恢复；截图及computed style验证局部组件。REQ-0053 trace记录1440/1024/390深浅主题与30组视觉材料，不能由此推断全部产品页面重新验收或现有生产部署已升级。

REQ-0053在1GiB worker样本中，12,000文件/600MiB快照67.912秒，48,000文件/2.4GiB快照330.925秒；32MiB及128MiB结果保存分别9.856秒、41.218秒。样本证明指定条件下的容量行为，不是所有环境SLA或无限规模承诺。复盘不重新执行容量测试。

可复用抽象包括：有界正文分块与引用读取、已提交区间和未知尾段分离、共享归档准入、不可变历史与可修复当前入口分离，以及同类标签的样式token。优先复用现有组件和服务，尚无证据支持新增通用页面框架。

证据入口：

- [规则审阅最终追溯](../../../openspec/archive/2026-10-24-add-controlled-rule-replacement-proof/trace.md)。
- [卡片持续标签与视觉返修](../../../openspec/archive/2026-10-22-add-card-persistent-info-tags/trace.md)。
- [Chat容量、双库、恢复与视觉结论](../../../openspec/archive/2026-10-26-update-chat-scalable-execution-storage/trace.md)。
- [已验收规格演进](../../../openspec/archive/2026-10-26-support-reviewed-spec-evolution/trace.md)。
- [空行证明根因与189项回归](../../../openspec/archive/2026-10-26-repair-archive-newline-proof/trace.md)。

product_data_collection_observability: applicable（被复盘交付）；affected_layers: web、api、db、usage_events、request_logs、task_traces、task_trace_spans；validation: 引用各Change有效证据及最终关闭报告。N/A：本次只修改知识库、索引和Sprint回链，不变更API、DB、UI、部署、安全权限、客户端生成或采集字段。

## 行动项与前序承接

| ID | 优先级 | 行动与验收边界 | 建议下一命令 | 状态 |
|---|---|---|---|---|
| S10-A001 | P1 | 当前引用与关闭结论一致；本轮4处已修，但通用引用检查及明确历史定位仍需覆盖 | `/req-capture 归档当前态引用与关闭结论一致性` | open |
| S10-A002 | P1 | 方案稳定后固定首次成功、拒绝、原操作恢复及跨入口样本；不以局部真实证据代替全链 | `/req-capture 治理归档样本隔离与证据矩阵` | open |
| S10-A003 | P2 | 用1,066条提示验证摘要输出上限、明细按需和阻断不遗漏；对比源头输出字符数 | `/req-capture Sprint事实摘要输出预算与覆盖检查` | open |
| S9-A001 | P1 | 核实范围外归属、203,960总量差额及actual聚合与单命令缺计量并存；未知不填0 | `/req-capture Sprint用量归属与统计口径审计` | open |
| S11-A001 | P1 | 下一轮明确追加、替换或延期与返修缓冲，33/30不能当作有余量 | `/sprint-explore` | open |
| S12-A001 | P1 | 统一入口已局部交付，继续核对shell wrapper的解释器与SQLAlchemy依赖；迁移前失败、恢复幂等 | `/req-capture 治理命令运行环境前检与恢复` | open |
| S13-A001 | P2 | 范围追加兼容无缩进YAML列表，写前解析与原子写入，重复执行无重复项；失败不损坏原文件 | `/bug-capture Sprint范围追加生成无效YAML` | open |
| S13-A002 | P2 | 业务策略退出时同步知识库适用版本和替代来源；旧文档不再被当成当前强制步骤 | `/req-capture 知识库经验适用版本与失效提示` | open |

六项沿用原ID，不关闭通用目标，不改历史行动表。S12-A001因本轮再次阻断提高当前承接优先级；统一Python入口交付只算部分落实。新增两项仅为复盘行动，未创建Issue/Change或纳入新Sprint。执行capture前先检查重复项；需求评审通过后再规划，不把复盘建议直接纳入开发。

本次局部闭环：空行补证、四处引用修复、归档完成已验证；知识库旧方案提示已更新。以上局部结果不替代行动表的通用治理验收。

## 执行链路复盘

Fact Sheet → 对照最终交付与前序行动 → 五维分析 → 知识库适用边界修订 → 文档验证与Sprint回链。交付与生命周期不变；历史路径提示和计量口径疑点保留为warning。建议先探索承接优先级，再按原行动命令去重capture。本命令未修改rules、src、治理脚本，未重复apply/archive，未自动创建Issue/Change。

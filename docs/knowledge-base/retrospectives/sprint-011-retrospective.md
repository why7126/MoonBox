---
title: 完成证明与执行保护收敛迭代经验复盘
created_at: 2026-10-21 19:39:00
updated_at: 2026-10-21 19:38:59
sprint_id: sprint-011
status: active
---

# 完成证明与执行保护收敛迭代经验复盘

## 迭代概况与证据边界

| 指标 | 事实 | 边界 |
|---|---|---|
| 生命周期 | completed / archive | 本次仅复盘，不重复归档或发布 |
| 正式范围 | 1 REQ、4 BUG、8 Change | BUG-0062属于sprint-012，是解除本迭代关闭阻塞的外部修复 |
| 任务 | 84/84 | 不把任务勾选替代产品验收 |
| 估算与容量 | 29.5/30人天，34故事点 | 占用98.33%，缓冲0.5人天；不是实际工时 |
| 归档 | 8项全部归档 | 关闭时全部SKIP，无重复合并 |
| 关闭验证 | 严格预检通过；陈旧扫描39文件、0阻塞；同步0错误 | 目录旧SQLite路径为既有warning |
| Fact Sheet | 2053条warning、2067个evidence hints | 主要是历史归档路径提示，不等于2053个产品缺陷 |
| 用量 | estimated_fallback | 覆盖不足，不能展示为全迭代精确成本 |

事实源：[范围](../../../iterations/archive/sprint-011/sprint.yaml)、[最终验收](../../../iterations/archive/sprint-011/acceptance-report.md)、[规划与关闭记录](../../../iterations/archive/sprint-011/sprint.md)。Fact Sheet采样于2026-10-21。计划结束日期为2026-11-03，关闭发生于2026-10-21；没有实际投入数据，不推算提前交付效率。本轮沿用已有验收，不声称重新执行产品测试。

## 流程复盘

完成证明、执行保护和业务状态投影需要分别保存事实，再通过可核验关系衔接。BUG-0052与REQ-0046联合返修经历准备检查、真实HTTP发送、并发拒绝、模型到归档终态、跨日恢复等多层验证；早期准备成功不能覆盖后来发现的发送竞争问题。最终签认以当前有效证据为准，历史失败保持原样。

关闭曾被同模块后继规格误判冲突阻断。sprint-012的BUG-0062将冲突键细化为模块与Requirement标题，同时保留完整哈希链、原条文保护和保守拒绝。归档该修复后，REQ-0046仍为36/36且ready，随后sprint-011完成关闭。不能为了关闭迭代而改写旧manifest、journal或将真实进度清零。证据：[条文冲突事故](../incidents/20261021-archive-requirement-scope-conflict.md)。

容量缓冲仅1.67%，虽低于硬上限，联合返修与外部修复依赖仍容易挤占收尾空间。后续追加范围应显式记录替换项和返修缓冲，不能从容量门禁通过推断无交付风险。

关闭时按当前事实更新聚合文档，历史验收轮次保留。Workflow Sync的根因confirmed提示经语义复核后保留，不把根因状态改为Issue状态。生成的“待人工sign-off”摘要与最终签认可能并存，当前事实以最终关闭记录为准；该投影一致性问题承接S10-A001，不在复盘中修改同步实现。

## 模型 Token 使用分析

### Token Usage Fact Sheet

| 指标 | 值 | 说明 |
|---|---|---|
| ai_usage_mode | estimated_fallback | 只分析风险，不编造Token数量 |
| snapshot_status | stale | 当前快照覆盖不足且需刷新 |
| reason | coverage-missing | optimize-acceptance-stable-validation未覆盖 |
| 自动发现 | 本次dry-run成功，发现1次command run | 单次actual不等于整个Sprint actual |
| 全Sprint调用数、重跑数、工具输出字符数 | 无可靠完整统计 | 不用局部数据外推总量 |
| input、cached input、output、reasoning、total tokens | 不报告精确总数 | 缺失不填0，矩阵“-”表示未观测 |
| impact | 不能可靠比较成本、缓存收益或单位交付效率 | 快照还包含Sprint外关联对象，需核验归属 |
| recommended_action | 补齐缺失Change会话归属并刷新快照 | 历史审计使用显式会话及必要manual-map，不持久化原始会话 |

### 高消耗来源与优化

| 来源 | 观察或风险 | 优化方案 |
|---|---|---|
| 摘要输出 | 前轮summary仍返回大量历史路径明细，发生截断；本轮2053条warning | 持久到本地临时文件，仅投影计数、当前阻塞及指定字段；承接S10-A003 |
| 四件套与归档 | 当前四件套93/176/68/88行，8 Change、84任务 | Fact Sheet先读，再按Change与证据入口分段；不默认展开全量 |
| 重复规则与技能 | 同会话重复读取会增加输入；无精确占比 | 复用已读摘要，仅补变更段落 |
| 宽泛搜索 | 历史证据与checkpoint会放大命中 | 默认排除archive、generated、Harness、模板assets、node_modules、dist、coverage；仅定向打开命中的归档 |
| diff与生成物 | 工作区混有其他任务，宽范围diff不代表本次成本 | 限定路径，先name-only/stat，再看契约差异；不倾倒OpenAPI/Orval生成物 |
| 测试与构建日志 | 长Docker日志、全量Workflow Sync输出存在放大风险 | 输出退出码、失败数、首个根因和证据路径；失败再展开 |
| 稳定性与重跑 | 指纹、部署输入和派生输出混淆会造成无效复验 | 稳定修改后集中验证，仅复验受影响AC，wrapper成功不重复收尾 |

本轮先读取Fact Sheet，再提取指定字段与目标事故文件，符合上下文预算方向。曾把warnings列表误作映射，后改用列表计数；数据形状应先核对。以上均为定性风险，未计算节省比例。S9-A001承接用量覆盖，S10-A003承接输出预算，不建立同义新行动项。

## 需求与设计

REQ-0046的状态展示依赖BUG-0052的执行证明与保护契约，跨入口联合验收应前置到设计阶段。状态详情、动作准备、实际发送与最终核验分别建立验收条件，避免只证明按钮可用就宣称链路完成。缺陷数量不能直接证明缺少原型，本次材料不足以建立这种因果关系。

BUG-0053暴露部署输入解析边界，BUG-0054暴露诊断传播缺口：输入来源、失败原因、中文提示和脱敏应作为同一消费契约检验。BUG-0055则区分消息因果排序与显示时间，不能依赖修正时间戳掩盖顺序问题。证据：[消息排序实践](../incidents/20261021-chat-message-causal-order.md)。

## 开发质量与可复用抽象

复用[治理恢复证据分层实践](../best-practices/governance-recovery-archive-evidence.md)：合成负例证明拒绝与零写入，真实部署证明版本一致、产品行为和视觉结果；两类证据不能互相冒充。BUG-0062的256项回归属于外部修复验证，不能并入本迭代测试数作为新增成果。

可复用边界是共享准入判定、结构化诊断、有效AC进度和恢复状态分离，以及排序与显示时间分离；没有证据支持新增通用页面或弹窗组件库。具体实现经验已在事故文档中存在，本轮只建立索引，不重复生成近义best-practice。

product_data_collection_observability: applicable；affected_layers: API、Web、governance_proof、execution_guard、request_logs、task_traces、消息持久化与恢复；validation: 引用归档验收与关闭深层门禁结果。N/A：本轮只写复盘与链接，无新增采集、API、DB、UI、部署、安全策略或客户端生成变化。

## 行动项与前序承接

| ID | 优先级 | 行动与验收边界 | 下一命令 | 状态 |
|---|---|---|---|---|
| S10-A001 | P1 | 继续承接当前态引用与关闭结论一致性；覆盖completed后sign-off摘要，不改历史证据 | `/req-capture 归档当前态引用与关闭结论一致性` | open |
| S10-A002 | P1 | 本迭代复用分层、串行与失败保留实践；通用样本矩阵尚未整体交付 | `/req-capture 治理归档样本隔离与证据矩阵` | open |
| S10-A003 | P2 | 用本次2053条提示样本验证摘要预算；保留当前blocker，明细按需，兼容JSON字段形状 | `/req-capture Sprint事实摘要输出预算与覆盖检查` | open |
| S9-A001 | P1 | 补齐历史用量覆盖与归属，区分单次hook actual和Sprint整体覆盖 | `/opsx-propose add-historical-sprint-ai-usage-audit` | open |
| S11-A001 | P1 | 下一轮追加范围时明确替换项、返修缓冲及外部关闭依赖；规划记录可核对 | `/sprint-explore sprint-012` | open |

前四项沿用已有行动ID，不宣称本轮关闭或新建。S10-A004保持原复盘状态，不因本次未分析该组件领域而关闭。BUG-0062已完成并归档，仅作为已落地经验，不再提出重复缺陷。任何capture先做重复检查，本轮未创建Issue/Change，未自动加入下一Sprint。

## 执行链路复盘

链路：归档事实读取→证据聚焦→用量自动发现与降级→五维复盘→知识库索引与Sprint回链→文档校验。问题证据集中于归档冲突粒度、真实验收与恢复状态混淆、摘要超量和用量覆盖缺口。规范优化建议沿用上述行动，不自动修改rules、技能、脚本或业务代码。

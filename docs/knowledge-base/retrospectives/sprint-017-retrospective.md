---
title: Sprint-017 经验复盘
created_at: 2026-10-31 16:03:16
updated_at: 2026-10-31 16:03:16
status: active
---

# Sprint-017 经验复盘

## 交付概况

7个Change全部归档、68/68任务完成，4个BUG关闭，无REQ范围；新增的标题误报治理修复包含在上述计数中。估算35.5人天、容量30人天，占118.3%，无返修缓冲，距离120%上限仅0.5人天。估算不是实际投入。计划结束时间2026-11-14不是实际关闭时间，不能据此宣称提前交付收益。本次没有生产发布。

证据：[Sprint关闭记录](../../../iterations/archive/sprint-017/sprint.md)、[验收报告](../../../iterations/archive/sprint-017/acceptance-report.md)。复盘复用已归档验证结论，没有重新执行产品验收。

## 流程复盘

独立Change初始化与Sprint纳入分开约束：有提案不代表可以开发；正式状态通过共享事件初始化，实施前检查Sprint范围。归档时先检查事实，再修复：本次扫描把BUG名称中的“待开发”误判为当前状态，最初误诊为文档过期并产生两次确认。后续保留原标题，按用户授权建立治理Change、纳入Sprint、回归、归档，消除了误报。经验是先读命中行与匹配逻辑，再提出修复方案；不能通过改标题或忽略整行绕过检查。

标题修复5项回归及实际Sprint扫描通过；真正的标题外待实现仍阻断。归档最终readiness、stale scan、Workflow Sync check通过。历史路径提示不等于当前链接全部可用，历史manifest和取证原文不批量改写。子文档confirmed属于根因确认，不与Issue生命周期混同。Docker到期扫描连接失败，不能宣称零残留，本次未创建容器。

## 模型 Token 使用分析

### Token Usage Fact Sheet

| 指标 | 结论 | 证据与边界 |
|---|---|---|
| 精确统计 | 无可用于本Sprint完整成本的统计 | 不展示不完整累计值为精确成本 |
| ai_usage_mode | estimated_fallback | Fact Sheet及自动会话发现dry-run均降级 |
| snapshot_status | stale | 快照时间2026-10-31T08:00:16.776461Z |
| reason | changes-coverage-missing；当前发现缺少token_count | 缺少fix-sprint-close-title-classification覆盖 |
| impact | 无法量化各阶段成本、重跑占比或优化收益 | 缺测不记零，不据累计值推断节省 |
| recommended_action | 用明确会话文件及必要映射审计归属后刷新 | 不以跨Sprint记录冒充独占成本 |
| 工作量代理 | 7 Change、68任务、4 BUG | 只用于读取风险分析，不换算Token |
| 四件套规模 | 79/178/41/45行 | 依次为yaml、规划、发布说明、验收报告 |

command run、模型调用、工具调用、失败重跑、输入、缓存输入、输出、推理输出、总Token及工具输出字符数均不作为完整实测报告。矩阵中的“-”表示未观测，不是0；缓存和推理子项不重复加总。

### 高消耗来源与改进

| 来源 | 判断 | 改进 |
|---|---|---|
| 本会话前段批量读取规则和技能 | 输出被截断，增加复读风险 | 复用已读摘要，只展开当前门禁段落 |
| Fact Sheet历史路径及用量矩阵 | 全量输出大于实际决策需要 | JSON落临时文件，仅输出计数、覆盖缺口与前几个命中 |
| 7个Change证据 | 全读成本随范围扩大 | 按Change身份和evidence hints定点取证 |
| 测试、Docker及同步日志 | 长成功日志信息密度低 | 成功报摘要，失败仅保留错误与相关上下文 |
| 搜索和diff | generated与历史目录容易放大输入 | rg先定位，排除generated/node_modules/dist/coverage/archive，确需历史时显式指定；先stat/name-only |

本次复盘遵守Fact Sheet先读、结构化字段投影和既有经验复用；归档前段宽泛读取与截断需要修正。没有精确实测成本，不宣称优化已节省Token。

## 需求与设计

范围集中在Chat历史读取、执行中问答、验收能力和治理边界。6个fix命名Change不证明需求设计不良，更不能推断缺原型是根因。问答设计需要分别定义问题创建、答案接收、协议投递、任务完成；验收能力需要分别定义依赖声明、镜像构建、worker在线、目标环境探针和业务闭环。权限、幂等、终止竞争及重连均应在验收前明确。

## 开发质量

历史读取采用共享请求和隐藏详情生命周期控制，权限检查与迟到响应隔离仍保留；优化读取不能降低授权检查。问答协议回归使用真实产品ByteQueue接口，普通替身不足以证明兼容；合成故障与真实同轮答案消费分开签认。验收环境在目标镜像执行依赖导入、线程池和前端项目配置探针，静态配置不替代运行证据。

已有证据分别记录单元、合成UI、真实浏览器和真实产品轮次；复盘不把不同套件数量简单相加为无重复测试总数。截图配额与浏览器进程文件限制分开，资源限制验证要覆盖实际页面加载。生产未部署的边界保持明确。

## 可复用抽象

优先复用[Chat身份与验收经验](../incidents/chat-answer-identity-and-verification.md)，不再复制同主题事故文档。可复用模式是共享读取生命周期、同轮问题身份、能力探针与结果分层、归档工具摘要绑定，以及标题与当前状态分离的治理扫描。当前没有多个相似管理页的证据，不建议新增AdminListPage或共享弹窗抽象。

证据入口：
- [历史读取验证](../../../openspec/archive/2026-10-31-fix-chat-history-read-lifecycle/verification.md)
- [问答验证](../../../openspec/archive/2026-10-31-fix-chat-midrun-question-response/verification.md)
- [验收能力验证](../../../openspec/archive/2026-10-31-fix-chat-acceptance-runtime-capability/verification.md)
- [工具版本路由追溯](../../../openspec/archive/2026-10-31-add-archive-tool-version-routing/trace.md)
- [标题识别修复](../../../openspec/archive/2026-10-31-fix-sprint-close-title-classification/trace.md)

## 行动项

沿用前序ID避免重复创建候选；本表的建议不代表已创建Issue或Change。

| ID | 优先级 | 行动与验收要点 | 下一命令 | 状态 |
|---|---|---|---|---|
| S16-A001 | P1 | 保留完整/部分交付的投影幂等回归；本轮不能证明前序问题全量解决 | /spec-opt 多Change完整验收投影与同步幂等门禁 | open |
| S16-A002 | P1 | 用量覆盖与归属审计，补齐明确会话映射，缺测不记零 | /spec-opt AI用量覆盖与归属审计 | open |
| S16-A003 | P1 | 摘要投影、搜索排除、diff/stat优先、失败日志摘要、已读规则复用，补长Fact Sheet评测 | /spec-opt 复盘读取预算与摘要输出评测 | open |
| S16-A004 | P2 | 本轮已纳入容量承接并重新计算35.5/30；下一轮仍需保留返修余量 | 核对下一Sprint容量与缓冲 | done |
| S17-A001 | P1 | 知识库当前导航和历史字面路径分开检查，不修改历史manifest | /spec-opt 知识库当前证据链接检查 | open |
| S17-A002 | P2 | 下一轮规划显式处理118.3%和零缓冲经验，追加前重算，不改历史估算 | /sprint-propose | open |
| S17-A003 | P2 | 标题误报已修复；后续观察陌生标题与真实状态反例，不宣称效率收益 | 复用tests/unit/test_sprint_close_stale_history.py回归 | done |

## 执行链路复盘

链路状态warning：交付与关闭检查通过；用量缺测、历史路径提示和Docker扫描不可用分别保留。规范优化建议归入上述既有及新增行动项，本次只沉淀文档，不修改规则、不执行开发或归档，不自动创建Issue/Change。

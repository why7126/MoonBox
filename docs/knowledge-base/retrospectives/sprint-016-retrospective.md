---
title: Sprint-016 经验复盘
sprint_id: sprint-016
status: active
created_at: '2026-10-31 07:45:00'
updated_at: '2026-10-31 07:45:00'
owner: MoonBox 产品团队
---

# Sprint-016 经验复盘

## 交付结果与证据边界

Sprint已completed并迁入archive：1项REQ、1项BUG、7个Change、83/83任务完成。REQ-0048完整隔离验收编排和BUG-0057快速打开修复均验收passed。容量30人天、估算32人天，占106.7%，无修复缓冲；这是计划估算，不是实际投入或提前交付收益。计划结束日期不等于实际关闭日期。产品版本尚未发布。

事实源：[Sprint](../../../iterations/archive/sprint-016/sprint.md)、[验收报告](../../../iterations/archive/sprint-016/acceptance-report.md)。Fact Sheet确认7项任务齐备；最终readiness、关闭陈旧扫描、Workflow Sync与check均通过。107条路径残留提示包含历史证据引用，不能等同107项当前缺陷；正式陈旧扫描为零阻塞，不批量改写历史清单。

## 流程复盘

归档曾在初检通过后被最终同步阻断。直接原因是derive_issue在关联全部已归档时默认选择列表首项；REQ-0048首项为旧partial子交付，同步将完整验收passed覆盖为partial。原完整20项验收、附件哈希及归档恢复链均有效，问题不在产品证据。当前处理为保留两个关联并优先完整交付，再定向同步，关闭后复验保持passed。此为本对象的恢复措施，不能宣称通用选择算法已修复。

证据代码：[关联选择](../../../scripts/workflow_sync/derive.py)、[子文档投影](../../../scripts/workflow_sync/issue_subdocuments.py)。经验：迁移目录不等于关闭完成；最终同步后再复核准入。先定位具体失效层，不把通用“证据过期”提示直接当根因，不要求用户反复确认可自行核查的事实。

本轮读取曾合并多份长规则导致截断，Fact Sheet全量输出也触发过超预算；后续改为临时结构化输出后只提取目标字段。前次停止在未核实摘要，应改为先自主对照最终证据。

## 模型 Token 使用分析

### Token Usage Fact Sheet

当前读取快照为present、actual，生成于2026-10-30T23:39:32.037454Z；REQ、BUG、Change覆盖检查均pass，warning_count为0。来源：data/ai-usage/sprints/sprint-016.json经Fact Sheet聚合；本轮也尝试自动发现dry-run。此前关闭hook曾返回estimated_fallback，不抹去当时缺少可归属事件的事实。

| 指标 | 快照观测值 |
|---|---:|
| command run | 37 |
| 模型调用 | 1380 |
| 工具调用 | 206 |
| 失败重跑计数 | 0 |
| input tokens | 202450180 |
| cached input tokens | 199839744 |
| output tokens | 562786 |
| reasoning output tokens | 112355 |
| total tokens | 203775768 |
| 工具输出字符 | 0 |

覆盖集合还含跨迭代关联对象，以上不代表sprint-016独占成本。工具输出字符0及失败重跑0是该统计字段观测值，不能解释为没有日志或没有失败；本会话明确发生过命令失败。各类Token直接保留来源口径，不自行相加或重复扣除缓存。未取得可比干预前后边界，不计算节省比例、费用或收益。矩阵缺测用“-”，不伪装为0。若需独占成本审计，应显式会话映射并重算覆盖。

### 高消耗来源与优化方案

| 来源 | 影响 | 证据与优化 |
|---|---|---|
| 规则和技能重复全读 | high | 本会话长输出截断；复用已读摘要，只读变化段 |
| Sprint/Issue/Change全量展开 | medium | 四件套94/199/29/37行、7 Change、83任务；先Fact Sheet字段，按Change分段 |
| 历史路径与证据扫描 | high | 107条提示；区分历史原件与当前导航，按指定Change定位，默认排除archive、Harness、assets、generated、node_modules |
| diff、测试及构建日志 | medium | 先stat和失败摘要，成功只记计数；大日志保存在本地忽略目录，不整段注入 |
| 状态反复同步与重试 | medium | partial投影导致重复门禁；稳定修改后集中校验，同步前后状态断言 |
| 用量归属混合 | high | 覆盖含额外关联对象；显式session映射与覆盖审计，未经实测不宣称收益 |

## 需求与设计

快速打开将进入Chat编辑草稿与发送前完整检查分开；减少首屏等待，同时保留权限、阶段、Sprint、幂等和未知执行保护。真实浏览器10次观察上界中位数868.5ms、最大1311ms；不是浏览器性能事件精确计时。发送检查约5.45–8.81秒来自3次受控副本样本，不代表成功模型轮次。旧方案AC-02失败留存，最终8/8通过不能反写旧窗口。

完整需求与子交付分别签认，需求关联顺序不应承担隐式业务语义。本Sprint有4个fix Change，但无证据证明由缺原型导致；不从命名数量推断需求质量。容量超额已明确接受，后续范围追加继续保留缓冲耗尽风险。

## 开发质量与观测

对象归档诊断8/8通过；快速打开最终8/8通过。真实操作、视觉、computed style、合成负例和命令回归分别标注；未发送成功模型轮次和历史21.27秒精确归因未知继续保留。
product_data_collection_observability: applicable；affected_layers: API、Web请求封装、request_logs/Task Trace、归档治理；validation: 最终验收分别核对脱敏、请求关联、权限与恢复边界。复盘自身不改API、DB、UI、部署或安全边界，无客户端重新生成需要。

[诊断最终报告](../../../openspec/archive/2026-10-30-add-object-archive-diagnostics/evidence/acceptance/20261031071641012333-297fc6e2/summary.md)；
[快速打开最终报告](../../../openspec/archive/2026-10-30-fix-object-session-preparation-latency/evidence/acceptance/20261030233606383318-49df5430/summary.md)。

## 可复用抽象

优先复用现有共享归档收尾检查器、只读诊断与恢复权限检查，不新增另一套完成定义。交互可复用“立即进入、异步准入、草稿保留、发送时最终检查”的模式，但适用前提是最终检查不能被绕过。
复用[会话准备延迟经验](../incidents/20261030-object-session-preparation-latency.md)与[子交付承接实践](../best-practices/partial-delivery-sprint-handoff.md)，本次不另建重复best-practice。

## 行动项

| ID | 优先级 | 行动与验收要点 | 下一命令 | 状态 |
|---|---|---|---|---|
| S16-A001 | P1 | 治理关联选择显式区分完整与部分交付；两种列表顺序、全归档、重复同步均不降级，保留真实partial负例；当前仅对象恢复 | /spec-opt 多Change完整验收投影与同步幂等门禁 | open |
| S16-A002 | P1 | Token归属审计：补充显式会话映射，区分跨Sprint观测与独占成本，缺测不记零 | /spec-opt AI用量覆盖与归属审计 | open |
| S16-A003 | P1 | 长输出先结构化摘要、搜索排除、diff/stat优先、失败日志摘要、已读规则复用；加入长Fact Sheet评测，不把静态检查等同收益 | /spec-opt 复盘读取预算与摘要输出评测 | open |
| S16-A004 | P2 | 下一Sprint规划承接32/30超额与零缓冲经验，范围追加重新算容量，不改历史估算 | /sprint-propose | open |

上述为候选建议，未创建Issue/Change，未修改rules或业务代码。Docker到期扫描曾因daemon不可达未完成，不宣称全局零残留；SQLite旧路径警告保留。相应环境检查与迁移需按原登记及部署边界处理。

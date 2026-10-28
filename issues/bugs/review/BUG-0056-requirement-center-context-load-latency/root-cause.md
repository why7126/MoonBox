---
bug_id: BUG-0056-requirement-center-context-load-latency
title: 需求中心首屏加载延迟根因分析
created_at: "2026-10-21 09:08:41"
updated_at: 2026-10-28 11:59:29
status: confirmed
---

# 需求中心首屏加载延迟根因分析

## 根因状态

status: confirmed

初次确认范围是三个已测得的性能瓶颈机制，不是原始 26.86 秒请求的精确分摊，也不是修复完成。2026-10-27 晚间现场复测补充 E9—E11：重复状态核对及后台备份、孤儿内容维护争用，见本文后续补充与关联 Change 的返修台账。初次样本口径、运行镜像摘要及代码定位见 [缺陷文档](bug.md)。

## 现象与因果链

进入需求中心先等待 projects，再等待 context 完整响应才显示卡片。context 每次构建全量治理快照、构建授权范围内全部卡片，随后逐卡补充状态；前端筛选发生在响应之后。历史归档越多、对象越多，重复扫描与解析成本越大。可见页面每轮请求完成约 3 秒后继续刷新，因此持续重复成本，而非固定每 3 秒重叠请求。

## 证据链

编号沿用 bug.md，源材料为本会话工具结果的脱敏摘要；未保存原始 HAR、截图或 profiler 附件，不提供虚构文件入口。

| ID | 类型 | 可复核入口与结果 | 支持结论及边界 |
|---|---|---|---|
| E1 | network_request | bug.md E1：GET context 200，总耗时 26.86 s，Waiting 26.77 s，下载 74.72 ms | 首字节前等待主导；单次样本不是 P95 |
| E2 | network_request | bug.md E2：snapshot_and_fences 7.48 s、parse 8.02 s、total 24.98 s | 约 9.47 s 尚未由子阶段解释 |
| E3 | data_sample | snapshot.py stable/read_once；4,342 文件、14,928,435 字节，其中归档 4,043 文件；stable 4.987 s，双遍读取 4.165 s | 全量双遍快照是可测成本；后续物化缓存不跳过此步骤 |
| E4 | data_sample | requirement_center.py _change_dir；immutable=True 直接治理目录诊断 189 卡、169 次底层查找累计 6.963 s | 归档查找重复扫描；此路径不等同 HTTP cached_materialize 路径 |
| E5 | data_sample | reader.py _call、execution_context.py canonical_id；只读后处理 9.403 s，其中 106 次注册表 safe_load 4.846 s | 逐卡反复解析注册表；不含 reconcile、外部核对和提交 |
| E6 | reproduction | 同一内存快照 106 个 REQ/BUG 原函数与两次注册表解析建索引：1.4411 s 对 0.0182 s，完整 ID 列表相同 | 重复解析可避免；短 ID 全唯一，异常身份尚未验证 |
| E7 | reproduction | 同一目录 171 个唯一 Change 原逐项扫描与一次索引：0.8241 s 对 0.0456 s，路径列表相同 | 重复目录扫描可避免；异常路径和并发尚未验证 |
| E8 | config_diff | reader.py、snapshot.py、requirement_center.py、execution_context.py 容器与工作区 SHA-256 一致 | 定位文件对应运行版本；不证明前端及全仓一致 |
| E9 | network_request | 本文真实后台并发补证：22.687/23.460秒及29.39秒刷新 | 首轮隔离结果不能代表实际并发；不将单样本称为P95 |
| E10 | data_sample | 本文剖析：214卡、1848条SQL、217次epoch；关联Change返修台账 | 重复状态核对和快照可减少；采样开销单列 |
| E11 | reproduction | 本文维护锁证据；关联Change evidence/acceptance/repair-measurements/background.json 与后台回归 | 整库复制和无索引引用扫描造成读写争用；分步复制和引用索引机制已验证，最终SLA另验 |
| E12 | reproduction | 本文第二批暖缓存复发；关联 Change acceptance-fixes.md 与 tail-measurements/formal-before-metadata-navigation.json | 正式页面暖缓存仍有长尾；候选 P95 3.419 秒未达标，最终版本待跨负载复测 |
| E13 | code | 本文健康检查与同步审计取证；关联 Change tail-measurements/deployed-source-final.json、regression-parser.txt、regression-mysql.txt | 健康检查重导入、重复状态查询与同步审计成本已定位，隔离回归通过，正式页面效果另验 |
| E14 | reproduction | 关联Change evidence/acceptance/tail-measurements/formal-diagnostic-20261028/summary.json | 解锁后两种负载各30次打开和刷新均仍超标，保留开发者工具打开的诊断条件，正式无工具验收另采 |
| E15 | reproduction | 关联Change evidence/acceptance/tail-measurements/read-scheduling-comparison.json 与设计中的CPU预算补充 | 第二遍安全分片读取在固定副本改善时延；低CPU配额的MD回退促使按实际资源选择调度，不放宽一致性 |

| E16 | reproduction | 关联Change tail-measurements/final-read/formal/status.json 与120个正式样本 | 无开发者工具、后台健康，两种负载仍有打开长尾；自然刷新达标不代表整体完成 |
| E17 | reproduction | 关联Change tail-measurements/candidate-enumeration-comparison.json | 首遍重复候选枚举可消除；完整当前路径/字节比对及变化回退须由回归证明，不等同正式SLA通过 |

| E18 | data_sample | 关联Change tail-measurements/validated-candidate/live-parser-profile.txt | 真实214卡解析剖析包含验收核验输入路径与Sprint纯事实重复工作；profiler会放大函数调用成本，不作为端到端SLA |

| E19 | data_sample | 关联Change tail-measurements/parser-facts/audit-plan.json；328129条审计记录，EXPLAIN确认按request_id更新全表扫描、按主键更新命中索引 | 每次请求的无效审计更新随历史增长放大，现场request_audit长尾522–767ms；不把该段全部归因SQL扫描 |
| E20 | data_sample | 关联Change tail-measurements/two-reader/two-reconcile-profile.txt、two-archive-profile.txt | 旧归档核验约0.418秒，同次核验重复读取历史baseline，最终以archive_baseline_missing拒绝；不缓存结果、不解除旧保护，仅合并同次输入读取并前置必要证据缺失检查 |
| E21 | network_request | 关联Change tail-measurements/released-host-20261028/live-browser.json、summary.json | 用户释放其他应用后，400次正式观察同版本且全部成功，四组P95仍超标；自然打开最慢20.704秒、压力刷新39.700秒，不能以释放负载或短窗口改善认定已解决 |

## 已确认根因

1. **快照构建未避开全量历史双遍扫描。** `ProjectReader.snapshot → stable → read_once × 2` 覆盖 issues、iterations、openspec、docs、rules 及归档。读取发生在物化缓存之前；归档规模直接放大每轮成本。一致性栅栏有必要，优化应复用可验证版本或减少安全等价的读取，而非直接取消双遍检查。
2. **全量卡片关联查询重复遍历归档。** `ChangeIndex.cards` 构建全部授权对象，`_change_dir` 只对同 ID memo，不同 ID 继续遍历相同归档目录。E7 以相同结果确认一次索引可去除该重复工作。全量标题与 YAML 解析进一步增加成本，但其独立优化收益尚未隔离测量。
3. **逐卡身份投影反复解析同一注册表。** parse 计时之后，`canonical_id` 每个 REQ/BUG 都重新解析整份注册表；E6 在同一快照上确认按版本建索引可保持样本结果一致并显著减少局部成本。其后的核对、状态查询和提交仍需单独计时。

## 初次探索的已排除假设与剩余边界（历史）

- 本次下载约 75 ms，不能解释约 27 s 等待；响应约 1.8 MB 的裁剪收益须另测。
- E5 的 772 次 SQL 执行累计 0.558 s，不支持把整个 9 秒归为数据库执行慢；ORM 与查询次数仍有优化空间。
- 四个定位文件无版本差异；未证明旧 BUG-0016 的回归提交，保留关联而不重写其历史结论。
- E3—E7 来自不同采样，cProfile 有开销且累计时间嵌套，禁止相加还原原始请求或声称端到端提速比例。早期非 immutable 的 11.421 s 不是正式基线。
- 初始页面约 20 个对象、后续页面 25 个、诊断全量 189 卡不是同一筛选口径。直接治理目录与 HTTP 物化目录存在路径差异。
- reconcile/reconcile_external、条件写入、提交、并发等待和序列化的完整分段占比未确认；诊断为避免写状态只覆盖纯读取子集。
- 尚无固定版本多轮冷暖分布、完整前端版本校验、修复回归与异常输入对照。以上是后续验收待补项，不扩张 confirmed 范围。

## 修复方向与验证闭环

优先在同一快照内复用注册表索引与归档目录索引，保留歧义、活动优先、路径安全和权限语义；再评估安全的版本复用、重复文档解析消除及按需聚合。缓存不可代替实时授权、写入栅栏、执行占用和完成核验。

后续修复通过评审、Sprint、OpenSpec 实施；按 [验收标准](acceptance.md) 完成相同环境对照、正常 HTTP 路径分段及安全回归。根因可评审，修复效果仍未验证。

product_data_collection_observability:
- status: applicable
- affected_layers: Web、API、request_logs、Task Trace
- reason: 需要完整请求和治理阶段计时；当前仅完善文档，无采集契约变更。DB 结构、对象存储、部署和客户端生成目前不适用，若后续方案改变对应边界则同步。
- validation: 复用 E1—E8，新增 instrumentation 与实际回归留待 Change；未新增原始敏感日志。

## 2026-10-27 真实后台并发复发补证

E9 network_request：Firefox需求中心两次重载context22.687/23.460秒；Server-Timing分别记录snapshot10.51/6.93秒、parse4.11/6.12秒、reconcile6.45/7.82秒，接收8/43毫秒。后续自动刷新等待29.39秒。

E10 runtime_profile：同部署、同项目ProjectReader剖析214卡、1848条SQL；214次reconcile_external累计11.73秒，217次epoch累计11.48秒；两次完整快照累计4.14秒。运行的8个读取相关模块摘要与首次验收一致，排除修复未部署。当前6407文件、约18.66MB。

确认请求内重复版本查询、二次快照和重复纯解析仍有成本；E11继续确认后台持锁来源，仍不能把全部差额归为SQLite或主机。旧隔离验收保留，仅不代表当前真实并发现场通过。返修台账为关联Change/acceptance-fixes.md。

### E11：后台维护持锁与重复工作（2026-10-27返修）

已确认：worker历史journal扫描在终态判断前反复解码baseline；自动快照对775151616字节源库整库单步复制；空闲内容清理的相关引用查询缺少object_id索引。线程采样捕获worker的backup.create与collect_orphans，API同时停在审计commit、登录态commit及项目SELECT；锁表显示worker共享读锁。完整备份只读计数21,331对象、66,265条目、1,109结果段，EXPLAIN显示两个相关子查询全表扫描。

处置为终态扫描跳过、在线备份小批次与自动超时重试、补引用索引；不会清空历史、关闭后台作为验收条件或绕过权限/写入保护。真实效果及未完成验证以Change acceptance-fixes.md为准。

### 返修闭环

后续完成普通外部同步有界批量提交、不可变解析复用、归档匹配循环外提与重复元数据查询削减；所有权限、绑定、源快照与历史执行围栏保留。真实后台暖导航/刷新各30次P95为HTTP1.359/1.111秒，首卡1.776秒，首次重启及源变化初始化8.620秒单列；完整失败批次、版本摘要和10项验收见关联Change返修台账。

### E12：暖缓存跨负载复发（第二批返修）

正式页面在相同交付源码下再次出现打开20.148秒、刷新23.75秒，详见Change第二批台账；上轮短窗口达标不代表持续现场达标。非阻塞调用栈采样确认worker重复尝试已释放并发槽位的终态UPDATE，controller每轮发布持久心跳并扫描所有历史保留状态。控制器308个采样中，store.write、readiness.publish和retention分类/扫描是主要应用栈；采样有54次读取错误，仅作热点证据，不换算精确耗时占比。后台重复维护与请求重复读取已确认；不同主机负载造成的独立增量仍需分窗口对照。

只消除已释放并发槽位UPDATE后，正式页面仍12.318秒（request_id 130cd641-24f0-49f3-988a-dda05c83c501），snapshot4.885秒、parse2.790秒、卡片状态3.218秒。这证明单项修复不足，不能宣布解决。四线程快照候选在同副本12组交错对照中耗时中位1.351→1.071秒、CPU1.350→2.269秒；因CPU增加约68%撤回，不部署，不削减原完整读取安全检查。

### E13：频繁健康检查和同步审计成本

控制器分频后主进程10分50秒累计CPU约25秒，但健康检查子进程单次耗时1.220秒、CPU1.219秒；检查每5秒启动一次，仅读取就绪心跳却通过ChatError导入SQLAlchemy及全量表模型。后台正式路由采样810个样本（156次读取错误）再次捕获snapshot目录/文件打开，以及chat.api同步审计UPDATE；后者在异步路由包装器中执行。固定副本一次暖HTTP有1196条SQL，其中对象权限322条，DB执行合计约0.325秒；不能将全部7.389秒归为SQL执行本身。批量化只针对重复状态投影，不缓存对象权限。

维护分频版本的正式路由30次打开P95 10.455秒、最大11.223秒，后段约2秒；完整失败样本保留，证明只调度后台仍不足以满足跨负载目标。后续交付收益须以新源码正式窗口验证。

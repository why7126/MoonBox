---
bug_id: BUG-0056-requirement-center-context-load-latency
title: 需求中心首屏加载延迟根因分析
created_at: "2026-10-21 09:08:41"
updated_at: "2026-10-21 09:08:41"
status: confirmed
---

# 需求中心首屏加载延迟根因分析

## 根因状态

status: confirmed

确认范围是三个已测得的性能瓶颈机制，不是原始 26.86 秒请求的精确分摊，也不是修复完成。证据复用本会话既有探索结果，本命令没有重新运行性能测试。完整样本口径、运行镜像摘要及代码定位见 [缺陷文档](bug.md)。

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

## 已确认根因

1. **快照构建未避开全量历史双遍扫描。** `ProjectReader.snapshot → stable → read_once × 2` 覆盖 issues、iterations、openspec、docs、rules 及归档。读取发生在物化缓存之前；归档规模直接放大每轮成本。一致性栅栏有必要，优化应复用可验证版本或减少安全等价的读取，而非直接取消双遍检查。
2. **全量卡片关联查询重复遍历归档。** `ChangeIndex.cards` 构建全部授权对象，`_change_dir` 只对同 ID memo，不同 ID 继续遍历相同归档目录。E7 以相同结果确认一次索引可去除该重复工作。全量标题与 YAML 解析进一步增加成本，但其独立优化收益尚未隔离测量。
3. **逐卡身份投影反复解析同一注册表。** parse 计时之后，`canonical_id` 每个 REQ/BUG 都重新解析整份注册表；E6 在同一快照上确认按版本建索引可保持样本结果一致并显著减少局部成本。其后的核对、状态查询和提交仍需单独计时。

## 已排除假设与剩余边界

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

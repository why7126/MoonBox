---
bug_id: BUG-0056-requirement-center-context-load-latency
title: 需求中心首屏聚合请求耗时约二十七秒
severity: high
status: in_sprint
owner: 产品团队
created_at: '2026-10-21 09:02:26'
updated_at: 2026-10-27 10:09:18
discovered_at: '2026-10-21'
environment: local docker chrome
related_requirement: null
related_bug: BUG-0016-capture
related_change: fix-requirement-center-context-load-latency
root_cause_status: confirmed
lifecycle_stage: review
---

# 需求中心首屏聚合请求耗时约二十七秒

## 现象与影响范围

需求中心从页面加载到卡片数据出现等待过长。2026-10-21 同会话 Chrome 已登录页面中，GET `/api/v1/requirement-center/context` 单次耗时约 26.86 秒，阻碍看板浏览和后续卡片操作。首次样本页面显示约 20 个对象，后续补证显示 25 个；后端诊断聚合了 189 张卡片。这些是不同采样时点，不能混成同一数据集。

本条仅覆盖需求中心首屏和刷新聚合。卡片跳转、Chat 历史读取、治理命令提交分别由 BUG-0057、BUG-0058、BUG-0059 跟踪，不把本条计时套用到其他接口。

严重等级保留 high：核心研发入口有可复现的长等待；没有数据丢失、安全事件或全站不可用证据。关联已归档 BUG-0016-capture，按用户明确选择独立记录当前复发，不重写旧修复结论。

## 复现步骤

1. 使用有项目读取权限的现有会话进入 `/requirements`，记录部署版本、项目数据规模和筛选状态。
2. 在 Chrome DevTools Network 保留记录后刷新，观察项目目录请求、context 请求以及首张卡片可见时刻。
3. 读取 context 的 Timing 与 Server-Timing；另在同一后端容器对治理快照、解析和后处理纯读取路径做内存计时。
4. 使用同一份内存快照对照逐对象注册表解析与一次索引，使用同一归档目录对照逐 Change 扫描与一次索引；校验输出相同。

期望：首屏及时显示所需数据，相同版本的公共解析结果可安全复用，重复刷新不会反复执行与可见范围不成比例的工作。
实际：目录与看板串行等待；后端先扫描、聚合全部治理历史并逐卡补充状态，前端再筛选；完整响应后才显示卡片。

## 根因状态与确认范围

`confirmed` 限于以下三个性能机制及可测成本，依据 E1—E8。它不表示已经精确还原原始 26.86 秒的每一毫秒，也不表示修复或验收已完成。

### 一、每次聚合先对全量治理历史做双遍快照扫描

`ProjectReader.snapshot()` 调用 `stable()`；`stable()` 连续执行两次 `read_once()` 比较文件内容。扫描覆盖 issues、iterations、openspec、docs、rules，包含归档目录。即使后续物化缓存命中，扫描仍先执行。

容器内样本读取 4,342 个文件、14,928,435 字节，4,043 个文件位于 archive 路径；双遍读取约 4.165 秒，stable 总计约 4.987 秒。前端筛选不减少后端扫描范围。这是随治理历史规模增长的首屏成本；双遍检查本身承担一致性职责，修复不能直接删除安全校验。

### 二、全量卡片构建中重复查找归档目录与解析文档

`ChangeIndex.cards()` 对授权对象全量构建卡片及关联 Change 摘要；`RequirementCenterPage.filteredCandidates` 在响应后按 Sprint 等条件筛选。本轮授权项目所有者诊断构建 189 张卡片，而浏览器筛选后显示 25 个。

`_change_dir()` 对每个不在活动目录中的 Change 遍历归档目录匹配完整 ID。请求内 memo 可避免同 ID 重复查询，但不同 ID 仍分别扫描同一目录。标题、任务、文档列表等路径还产生大量读取与 YAML 解析；已有缓存不是全局索引。

171 个唯一归档 Change 的只读对照，逐个查找耗时 0.8241 秒，一次目录索引耗时 0.0456 秒，路径列表完全一致。确认目录重复扫描是可避免成本；标题解析与卡片数据裁剪的具体收益尚未做逐项对照。

### 三、逐卡后处理反复解析同一注册表

`ProjectReader._call()` 在 parse/cleanup 计时结束后，对每张卡片调用 `canonical_id(snapshot, card.id)`。该函数对每个 REQ/BUG 都重新 `safe_load` 对应整份注册表，随后寻找完整 ID；没有复用当前快照的身份索引。

106 个对象的只读对照，原实现累计 1.4411 秒，两个注册表各解析一次并建立索引累计 0.0182 秒；所有短 ID 在样本中均唯一，返回完整 ID 列表完全一致。未来实现仍需保留重复短 ID/不唯一身份的失败语义，该样本没有覆盖异常注册表。

## 证据链

| 编号 | 类型 | 来源与采样口径 | 结果及边界 |
|---|---|---|---|
| E1 | network_request | 同会话首次 Chrome 原生 Network / Timing，context GET | HTTP 200；26.86 s 总耗时；Waiting 26.77 s；下载 74.72 ms；响应约 1,793 kB。projects GET 约 813 ms。确认首字节前等待为主，单次值不是 P95。 |
| E2 | network_request | E1 同次 Server-Timing | snapshot_and_fences 7.48 s、materialize 0.58 ms、object_authorization 0 μs、parse 8.02 s、cleanup 9.84 ms、total 24.98 s；约 9.47 s 内部耗时未由现有子阶段覆盖。 |
| E3 | runtime_profile | 容器内 Python -B、内存 cProfile，stable 实际治理数据源 | 4,342 文件、14,928,435 字节；stable 4.987 s，其中两次 read_once 共 4.165 s；14,950 次 open、8,684 次文件 read、22,218 次 stat。归档文件 4,043 个。 |
| E4 | runtime_profile | 同容器解析诊断，immutable=True、项目所有者权限、直接治理目录、只读 SQL 防护 | 189 卡；总计 30.988 s，cards 26.902 s；169 次底层 _change_dir 累计 6.963 s，636 次 YAML load 累计 5.043 s，402 次 read_title 累计 5.107 s。281 次 SQL 执行累计 0.765 s。嵌套累计时间不能相加，直接目录不等同 HTTP 的 cached_materialize 路径。 |
| E5 | runtime_profile | 同容器后处理只读子集：canonical_id、guard_read、visible_state、completion status；未调用 reconcile/reconcile_external | 总计 9.403 s；189 次 canonical_id 累计 4.930 s，其中106次注册表 safe_load 4.846 s；772次 SQL 执行累计0.558 s。仅证明该子集成本，不等于 E2 未计时部分已精确还原。 |
| E6 | comparison | 同一内存快照，106 个 REQ/BUG 的原 canonical_id 与一次索引对照 | 1.4411 s → 0.0182 s，全部结果相同；单次诊断，无并发修改与异常身份测试，不是生产提速承诺。 |
| E7 | comparison | 同一归档目录，171 个唯一 Change 原查找与一次目录索引对照 | 0.8241 s → 0.0456 s，全部路径相同；保留样本中的活动目录优先与重复归档回退逻辑，异常输入待回归。 |
| E8 | config_diff / code_path | 容器与工作区四文件 SHA-256 比较 | reader.py、snapshot.py、requirement_center.py、execution_context.py 均一致；排除这四个定位文件的运行版本错配，不代表全仓或前端镜像完全一致。 |
| E9 | reproduction | 后续独立 Chrome 标签页访问 /requirements | 页面从加载态到“已同步”，显示25个对象；完成后关闭诊断页以停止额外轮询。本次未重测精确端到端计时。 |

证据来源为本会话工具返回的脱敏观察与计时摘要，本次文档复用既有证据，没有声称重新执行。未保存原始 HAR、截图或 profiler 文件；不虚构附件链接。后端运行镜像摘要为 `sha256:d92473dea47fcd70f969d7dfaaaaee1f37a0b5ac7172bd5baa624126de118aa2`，容器启动时间为 2026-10-21 08:27:56（Asia/Shanghai）。未保存真实账号标识、连接串、凭证、消息正文或本机绝对路径。

## 代码定位与放大因素

- `src/backend/app/governance/snapshot.py`：stable、read_once，双遍全量读取。
- `src/backend/app/governance/change_index.py`：ChangeIndex.cards，全量对象构建及关联摘要。
- `src/backend/app/services/requirement_center.py`：_change_dir、_memoized_read、build_requirement_center_context。
- `src/backend/app/governance/execution_context.py`：canonical_id，逐对象重复解析注册表。
- `src/backend/app/governance/reader.py`：ProjectReader._call，parse 计时后继续执行状态核对、逐卡补充和提交。
- `src/web/src/pages/catalog/RequirementCenterPage.tsx`：loadContext 先 projects 后 context；filteredCandidates 在完整响应后筛选；可见页面每轮完成约3秒后继续刷新。轮询不是固定每3秒重叠 context，但会持续重复上述成本。

## 已排除与尚未确认

- E1 的下载只占约75ms，不能把本次慢主要归为传输体积；约1.8MB响应仍值得单独裁剪，但不是已证实的主等待来源。
- E5 的 SQL 执行约0.558s，不能把9秒后处理笼统归为数据库慢；772次查询仍存在批量化空间，ORM、Python解析和等待开销需分别看待。
- 非 immutable 的初次诊断曾测得解析11.421s，不作为真实请求基线；不同缓存、挂载、权限、数据变化和负载会改变结果。
- cProfile 的累计时间有嵌套且有分析器开销；E3、E4、E5、E6、E7是不同采样，不相加拼成原始27秒，也不据此计算端到端提速比例。
- 未执行会写入保护状态的 reconcile/reconcile_external 独立诊断。它们的验证、快照重取、条件写入、提交及并发等待占比仍未知。
- 尚无同版本同负载多轮冷暖样本、P95、修复后回归；未证实旧 BUG-0016 修复被哪次提交引入回归。

## 后续补证与验收方向

1. 在正常页面 GET 路径细分 snapshot、解析、reconcile、逐卡投影、序列化与提交计时，以同一个 request_id 关联。先使用现有可用观测；若需新增 instrumentation，通过后续 Change 实施，不为补证篡改运行服务。
2. 固定镜像、治理快照版本、对象/文件数量、权限、前端筛选与同期负载，多轮测冷暖首屏和刷新；报告样本数、中位数、P95及首卡可见时间。
3. 注册表索引按快照版本构建，覆盖短 ID 重复、对象删除、权限变化与并发写入；目录索引保留完整日期后缀、归档歧义和路径安全语义。
4. 评估按实际可见范围聚合或分页、版本级纯解析缓存、权限与状态批量查询；不可缓存越权结果，不省略写入栅栏、执行占用或完成核验。
5. 在相同数据规模下对照修复前后请求次数、读文件次数、解析次数、返回体积和端到端时延。量化验收目标见 [验收标准](acceptance.md)，为已评审修复目标，尚无达标结果。

补证返回格式：环境/镜像摘要、快照版本、样本规模、操作、脱敏请求路径、状态码、request_id、总耗时、Waiting、各阶段耗时及是否冷缓存。由 Agent 优先自主采集；当前无需用户提供凭证或原始日志。不要返回 Authorization、Cookie、完整业务正文、真实身份或本机路径。

## 修复建议与边界同步

优先处理请求内注册表索引和归档目录索引，再压缩重复文档解析与全量历史聚合成本。上述只是已验证方向，未修改业务代码。API裁剪/分页若改变契约，需要同步 OpenAPI、客户端生成、API文档及测试；内部缓存与索引保持权限和快照一致性。当前没有证据要求数据库迁移、部署拓扑或安全策略改变。

product_data_collection_observability:
- status: applicable
- affected_layers: Web、API、request_logs、Task Trace
- reason: 定位与验收需要请求分段和治理步骤计时；本命令仅生成缺陷文档，不改变采集契约。DB物理结构、对象存储和部署拓扑暂不提出变更。
- validation: 复用同会话浏览器实测、只读函数分析、两项一致性对照与源码摘要校验；尚未修复，完整端到端复验待后续完成。

## 当前交付状态

已补齐 [根因分析](root-cause.md)、[临时规避](workaround.md) 和 [验收标准](acceptance.md)，根因证据与中文标题门禁已通过，已评审通过并纳入 sprint-014，当前状态为 in_sprint。三个瓶颈机制已确认，剩余证据边界保留；已创建 [修复Change](../../../../openspec/changes/fix-requirement-center-context-load-latency/proposal.md)，尚未实施修复或完成验收。

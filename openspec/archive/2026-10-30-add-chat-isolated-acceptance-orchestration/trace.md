---
title: Chat 隔离验收与原操作续接变更追溯
created_at: 2026-10-29 17:11:36
updated_at: 2026-10-30 11:32:20
change_id: add-chat-isolated-acceptance-orchestration
requirement_id: REQ-0048-chat-isolated-acceptance-orchestration
type: add
status: applied
iteration: sprint-016
depends_on:
  - add-isolated-candidate-validation
prototype_refs:
  - path: issues/requirements/review/REQ-0048-chat-isolated-acceptance-orchestration/prototype/web/prototype.html
    role: html-structure
  - path: issues/requirements/review/REQ-0048-chat-isolated-acceptance-orchestration/prototype/web/context.md
    role: decomposition
prototype_gate:
  decomposition: done
  ui_skeleton: done
  visual_acceptance_1440: passed
  req_final_consistency: passed
product_data_collection_observability:
  status: applicable
  affected_layers: [web, api, database, chat, environment_orchestration, usage_events, request_logs, task_traces, task_trace_spans, evidence]
  reason: 原操作与环境、AC、恢复和回收存在跨请求异步状态，需要可信关联与脱敏计时。
  validation: 已执行授权API行为、后台Task Trace、持久SQL及合成Docker回归；本机真实模型工具、失败源续接、撤权/停止/回读/清理样本与长期摘要访问已验证，生产数据未接入。
execution:
  schema_version: 1
  started_at: 2026-10-29 17:16:46
  completed_at: 2026-10-30 11:32:20
  last_event: opsx.apply
---

# Chat 隔离验收与原操作续接变更追溯

## 来源与准备度

REQ已于2026-10-21评审通过，现由sprint-016承接剩余13人天范围。Readiness为Ready：六件套、review、原型拆解和20项AC完整，需求status为in_sprint。已归档 `openspec/archive/2026-10-29-add-isolated-candidate-validation/` 属于sprint-015必要子交付，不重写其验收，不代表完整需求完成。

本Change为新增Chat编排能力；只生成文档，未实施业务代码，未启动正式apply、模型、容器或产品验收。原REQ的partial子交付历史在REQ acceptance.md独立保留；当前完整验收投影与本Change均为not_started。

## 原型承接与冲突处理

用户选择沿用现有设计系统，复用Chat组件与样式并保留原型状态/动作语义。design.md记录Conflict Resolution、UI Contract、UI Skeleton、selector、动作/弹窗矩阵和样式清单；acceptance.md记录七阶段×双视口证据计划。骨架确认、1440px与390px截图、computed style、真实API交互与REQ最终一致性均pending。原型为合成无API；正式产品必须接真实服务，不以原型充产品证据。

## 验证记录

### Apply 中间检查点（2026-10-29）

- 用户已通过原生交互卡片确认验收详情骨架：保持当前区域层级，继续接入真实状态和动作。证据为 `evidence/skeleton/desktop-1440x900.jpg` 与 `desktop-style.json`；这是合成预览，不能替代真实 Chat 视觉验收。
- 持久状态首批 12 项合成回归通过；授权查询/停止接口 2 项回归通过。授权未提交快照 9 项回归通过，覆盖内容变化、删除、越界、敏感文件、软硬链接及未授权文件排除。
- 已接入 metadata 迁移入口；MySQL 事务竞争及真实环境矩阵仍待执行，任务不提前勾选。
- Apply 中 Docker 已通过获准的受限环境外探针确认 linux/aarch64；重新 reap 返回已有 26 个登记均 clean、零所属容器/网络。本次尚未创建 Docker 测试资源。
- 当前代码为实施中间态：创建与调度、环境资源配额、身份、模型结果消费/续接、完整动作族和产品证据尚未完成，不声明 applied 或 ready。

Change身份创建门禁已通过；OpenSpec CLI创建并按proposal→design/specs→tasks取模板。标题校验14份文件通过；当前Change中文校验及全仓残留报告通过；OpenSpec严格校验、身份、上下文预算、目录结构及Sprint scope校验通过。Workflow Sync最终check为Updated 0、Errors 0，REQ/Change/sprint-016双向关联一致。目录校验另提示既有legacy SQLite路径，未修改运行数据。运行证据未采集，acceptance.md仅为计划。

## 风险与非阻断诊断

入口temporary_docker reap对既有登记返回docker_command_failed:info，当前未能确认daemon资源状态；本次未创建资源，不声称历史零残留。运行阶段需重新检查Docker与批准模板，不阻断本次文档产物。已有无关工作区改动保留，不批量修改正式规格或其他Change。

## 用量与治理边界

本次治理run在入口阅读和门禁检查后开始计时，不能代表完整会话耗时；精确Token未知，不按零记录。完成hook已自动采集1条actual命令记录并刷新sprint-016快照，warning 0；进行中会话用量不冒充治理run完整边界Token。未创建额外follow-up Issue/Change。

## 执行链路复盘

链路状态warning：主链路生成与验证通过，Docker入口扫描未连接daemon，既有legacy SQLite路径仅警告。同步器首次保留Sprint空changes键并遗漏REQ空清单，已定向去重、补齐两条历史/当前关联并通过无差异check；未修改同步脚本。建议后续spec-opt覆盖空列表规范化与多Change部分交付历史保留回归；未自动创建额外Issue/Change，本轮精确优化预算未知，不进入自动优化。

### Apply 机制验证进度（2026-10-29）

- 承接用户确认：复用现有设计系统、保持验收详情区域层级；先用登记合成项目验证，真实产品模板和模型轮次验收待接入。原始完整20项AC不删减，不自动归档。
- 已新增持久编排、授权检查点导出、受控模板/身份/运行器、worker恢复、查询/停止/继续/清理接口及Chat组件。模型结果消费的预留与接收确认分开；缺实际模型适配不宣称一次消费或自动续接已经实现。
- `evidence/implementation/backend-regression.json` 为有输入哈希的合成回归；`mysql-state.json` 为真实MySQL8.4.13的并发创建/领取、BIGINT预算、取消和证据保留样本。合成状态与真实产品轮次分开记录。
- 既有固定候选路径已在登记Docker运行中通过SQLite3.46.1、MySQL8.4.13、Chromium156.0.8078.73与两个视口，源码运行期间稳定，所属资源清理完成；证据 `candidate-compatibility.json` 与 `candidate-browser-*.png`。这不覆盖新编排的双浏览器/角色/模型全矩阵。
- UI七阶段×两个视口×深浅主题共28张截图与computed style，保存于 `evidence/implementation/ui/`。这是合成状态、真实API和生产组件组合；完整Chat与真实角色样本仍待接入。已验证停止确认、内部点击、遮罩关闭、Esc与焦点恢复，修复窄屏长摘要溢出。
- 前端5项动作测试及TypeScript通过；运行器/既有候选25项非运行态回归通过，两个显式运行态样本默认跳过。跳过项不计通过。新编排真实Docker矩阵等待固定双浏览器测试镜像准备，未把镜像构建成功视为运行验收成功。
- API索引、DB设计、部署边界、模块README及env示例已同步；OpenAPI/Orval已更新。未修改真实环境、密钥或生产数据；数据库变更由Chat迁移入口承接。`product_data_collection_observability` 涉及web/api/database/usage_events/request_logs/task_traces，已有授权行为与后台事实分离测试，不产生后台伪造点击。
- 当前仍为in_progress，不运行opsx.apply完成同步，不标ready。完整资源预算整合、长期证据转存、真实产品模板/轮次和模型自动续接仍保留未完成门禁。

### 分项拒绝与计划补全

- 20项机器计划已通过结构与视觉矩阵检查。AC-001/006/007及相关横切产品样本明确为 `product_turn` 且 `turn_id: null`，保留pending，不由命令回归冒充。
- 新编排在真实Docker合成项目中已完成一次预期拒绝：固定测试镜像故意缺Firefox，两个数据库AC均记录 `browser_acceptance_failed`，最终 `blocked` 且 `cleanup_state=released`；回归断言通过。证据 `evidence/implementation/runtime-missing-browser.json`。该样本不证明双浏览器成功，也不证明模型轮次。
- 局部数据库预检失败后先丢弃未知初始化环境，再运行独立数据库；未确认清理则拒绝复用。三个故障注入测试已通过；新运行器禁止无界daemon日志。最新集中合成回归41项通过，真实运行矩阵补充后仍需按最终输入复验。

### 共享预算与模板变化回归

- 候选供应与验收编排共用持久资源池；主机容量收缩、每空间唯一约束及旧环境未释放均拒绝新增占用。44项相关合成回归通过，1项显式Docker用例在该批跳过；随后单独执行原候选真实SQLite/MySQL/Chromium用例通过且清理完成，更新 `candidate-compatibility.json`。
- 部署模板摘要随尝试保留；模板变化会将复用结果标为失效、保留历史证据并推进围栏，拒绝迟到回调。27项状态、运行器故障和worker前置检查回归通过。
- MySQL8.4.13真实状态探针再次通过并清理完成；它证明事务与竞争机制，不证明完整产品验收。

### 当前机制回归（2026-10-29）

- 集中后端回归71项通过、1项显式Docker用例跳过；后者另行运行并通过。证据为 `evidence/implementation/backend-regression.json`。
- 主动停止真实Docker合成环境已通过，取消到释放耗时13.97秒，小于60秒；取消意图保留，续接计数为0，证据 `evidence/implementation/runtime-cancel.json`。这不包含真实模型执行的停止观察。
- 模板变化后只读查询不再把历史结果展示为当前ready，保留历史证据且不修改操作版本。

### 登记合成项目正向矩阵

- 固定镜像 `sha256:ea1b40f67db99bc30fff8ad98bf661143019b56bd320c859f6b601f1d3e7fed7` 的 Linux arm64 探针通过：Python3.12.15、Node24.22.0、MySQL8.4.13、Chromium156.0.8078.73、Firefox153.0。
- SQLite/member 与 MySQL/reader 两项合成AC通过，各执行Chromium/Firefox及双视口，保存8张截图；46组容器资源样本满足本次断言，源码运行期间稳定。最终status=passed、cleanup=released，证据 `evidence/implementation/runtime-positive.json` 与 `runtime-image.json`。
- 这是用户选择的登记合成项目验证，使用来源导出替身；不包含真实产品模板、完整Chat轮次、模型投递/续接或长期证据回填，不替代完整20项AC。完整磁盘限额的破坏性边界试验仍未完成。
- 当前仍保留in_progress和原始未完成任务。真实产品验收按用户选择待接入；模型执行器回调/关联续接与长期证据转存仍未交付，不能归因成已通过或仅待签字。未执行opsx.apply完成同步、opsx-accept完成签认或归档。
- 本次标准MCR镜像下载未完成；合成测试镜像可用后已停止备用构建，不宣称生产镜像构建成功。临时UI服务结束，登记容器/网络最终按run精确清理和check复核。

## 本轮续接与长期转存实施（2026-10-29）

REQ-0048 / add-chat-isolated-acceptance-orchestration / sprint-016。用户选择登记合成验证，真实产品验收待接入。模型一次消费、一次关联续接、原期限/token余额、长期摘要不可变转存及归档后引用已实现。详见verification.md和evidence/implementation/continuation-evidence.json；停止前门禁仍等待6.3真实产品轮次、6.4完整Chat视觉样本及其依赖7.3。保持in_progress，不执行applied或archive同步。

### 本轮停止前决策

全部可执行实现和收尾已推进，任务23/26；剩余6.3/6.4直接依赖用户保留待接入的真实产品模板、角色与模型轮次，7.3依赖其签认。最终稳定入口103通过、1显式Docker跳过；独立MySQL和磁盘探针通过。前端6通过及类型检查通过。20项诊断3通过、17受阻、0失败、0待自主采集；证据evidence/acceptance/20261029212332409662-f9462e56/summary.md。临时登记524a086936a24eafbef4ede35a967c55精确cleanup/check为零容器、零网络；测试API与预览已关闭。未执行applied、accept完成同步或archive。交付与证据分开记录，完整结论仍blocked。


## 本机真实产品接入与验证（2026-10-30）

本轮按用户授权创建当前MoonBox独立产品模板、全新SQLite/MySQL与短期角色，未连接生产数据。已完成实际模型原生工具消费、失败源一次关联续接、停止、执行器回读、撤权和清理失败重试样本，以及真实Chat七阶段双视口深浅主题视觉。原“真实产品待接入”为历史检查点，已解除。根因和修复包括MySQL重复索引/UTC、恢复提前释放文件锁、摘要关闭焦点和后台冻结账号权限复核；验证分类和限制见 verification.md。未授权正式归档。


## 完成门禁记录（2026-10-30）

正式完整验收 `20261030112909168308-f917f18d` 为20/20通过，当前readiness通过；归档临时副本预演通过。集中后端152 passed/1 skipped（显式独立Docker入口已有真实运行），前端交互6 passed、TypeScript通过；新增证据适配35项通过，权限夹具及共享回归已修复并复验。中文校验、37份标题校验、OpenSpec严格校验及diff空白检查通过。临时服务停止，登记容器/网络零残留，模型授权副本已删除；镜像缓存保留。正式归档未获授权、未执行。

---
change_id: fix-requirement-center-apply-lifecycle-sync
bug_id: BUG-0015-requirement-center-apply-start-stage-not-synced
created_at: 2026-09-12 21:00:30
updated_at: 2026-09-13 23:43:10
---

## 背景

根因见来源BUG的root-cause.md与logs/state-matrix.json。当前Sync按任务数推断状态，看板优先读取Change trace。零完成数不能区分未开始与正在首项任务；部分完成后两条读取路径也可能分歧。

## 目标与非目标

目标：启动0/N可见、状态投影一致、幂等恢复、完成门禁不被绕过。范围含两份apply技能与Sprint编排，沿用Issue主状态in_sprint和BUG severity字段。

非目标：不改版页面、不新增聊天调度器、不开发新的实时通信协议、不改变归档权限，不将BUG-0014的后续修复成果计入本条验收。

## 设计决策

### 1. 启动、进度、完成事件分离

新增opsx.start与opsx.progress同步事件，现有opsx.apply保留完成语义。两份apply入口在根因、Sprint、授权等前置门禁通过后、正式实现前串行执行启动同步；dry-run不写入。启动同步失败时不开始依赖它的实施，报告具体文件/权限/冲突原因。sprint-apply委托同一入口，避免重复逻辑。

拒绝以第一项任务勾选作为启动事件，因为首项长任务仍有0/N窗口；拒绝提前调用完成同步，因为会混淆验收语义。

### 2. Change可选执行元数据作为事实源

在Change trace中增加版本化执行块（建议execution.schema_version=1、started_at、completed_at、last_event）；具体序列化遵循现有YAML写入工具，不重复Issue分级字段。status保留proposed/in_progress/applied，Issue主状态仍in_sprint。执行块表示生命周期事实而非Agent进程在线状态；中断不清除started_at，也不伪报仍有活跃进程。

新契约判定顺序：归档/闭环优先；完成事件通过门禁并写入completed_at才applied；存在started_at为in_progress；否则proposed。任务计数独立报告。opsx.progress不设置completed_at；新契约下全勾选但未完成同步仍为in_progress。

旧条目缺少execution时沿用明确的applied/archived终态；历史部分/全部任务计数兼容原有展示，但标明legacy来源，不生成虚假started_at或批量迁移历史文件。仅显式启动目标Change时升级执行块。历史状态冲突在目标操作中报告，禁止以新契约重开已完成Issue。

### 3. 统一解析与投影

将状态归一化和阶段判定提取为无写入副作用的可复用规则；CLI与后端均调用或遵守同一实现契约。部署中scripts目录是否可导入需实施前核验；业务共用逻辑放src约定边界，避免后端运行时依赖未挂载脚本目录。复用现有项目根解析、权限与归档保护。

同步先持久化目标Change事实，再更新Issue关联Change状态、registry、索引和Sprint投影。单文件原子写、目标锁和冲突检查复用现有机制；中途失败保留事实与失败报告，重跑幂等修复派生投影。不能把跨文件更新声称为数据库事务。不得覆盖其他条目或并行Agent新写入。

看板读取相同事实，保留现有stage和tasks响应字段；快照版本变化应包含执行元数据变更。前端通过现有轮询/焦点/手动刷新读取服务端结果，不以点击启动后的本地假移动作为成功证据。活动项目切换后的旧响应不能串卡。

### 4. 完成门禁与自举

对本Change首次实施也要执行启动语义：若opsx.start尚不可用，先以现有允许的兼容状态机制记录开始，并明确旧工具能力边界；实现新事件后立即迁入新执行块并验证0/N合成样本。不要因本Change实现新启动命令而陷入先要求不存在命令的循环；不得提前执行opsx.apply完成同步。

完成验证和文档回填后才运行opsx.apply；闭环同步与命令末尾收尾任务按既有连续执行契约处理。全部任务勾选不单独构成完成授权，完成事件拒绝明显不完整任务并报告原因。

## 风险与取舍

- 新旧状态兼容 → 版本化执行块、旧终态保护及双路径回归；不批量回填虚假执行时间。
- 多Agent并发与跨文件部分成功 → 原子文件、目标锁、冲突拒绝和可重放投影，测试中断点。
- 真实部署刷新问题尚未排除 → 单列API/浏览器验收，保留请求与快照证据。
- Sprint剩余机动仅3人天 → 复用现有入口、聚焦本缺陷；新增架构范围重新评估。

## 迁移计划

先验证旧条目兼容，再接入共享解析、事件写入和两个apply入口，最后真实项目验证。回退按proposal整体回退；保留新增可选元数据，不删除历史证据。无计划数据库迁移或生产部署操作。

## 测试与观测

AC-001至011映射到tasks：状态函数、CLI事件、跨文件恢复、REQ/BUG接口、前端刷新、真实浏览器分别取证。真实环境使用合成条目与授权隔离项目，保持现有鉴权，不写真实客户数据。

product_data_collection_observability: applicable

reason: 研发启动与进度同步涉及Agent Workflow、后端治理状态和Web快照；无新增数据库表或对象存储，沿用现有请求关联与脱敏。

affected_layers: agent_workflow、web、api治理读取。启动日志只记事件类型、条目/Change/Sprint、时间和结果，沿用现有请求关联；CLI不伪造usage_events。N/A：无新增DB表、对象存储、端侧追踪协议或保留周期；接口字段不变则OpenAPI/Orval生成N/A，若变化则同步索引、生成物及契约测试。validation：根因复现已通过；实现回归、实际部署context响应与截图尚未执行。

## 待确认事项

无需要用户先决策的阻塞项。实施前核验部署导入路径、现有锁机制、快照revision组成与兼容字段解析，按证据调整实现细节并保持上述契约。

## 实施差异与验证

## 实施与验证记录

- CLI 的 opsx.start、opsx.progress、opsx.apply 分别记录启动、进度和完成；Change trace.execution.schema_version=1。started_at 与任务计数分离；0/N 已启动为研发中，全勾选但未完成仍为研发中。旧条目保留兼容推导，不补造历史时间。
- 共享纯函数位于 src/backend/app/governance/lifecycle.py，CLI 通过 scripts/workflow_sync/shared.py 导入；后端镜像已有 app 目录，不依赖部署 scripts。CLI 简单 YAML 解析器不能解析嵌套映射，因此为 execution 使用受限、版本化块解析器，后端沿用现有 YAML 读取。
- 全流程项目锁、逐文件原子替换及内容冲突检查；Change 事实先写，投影失败保留事实、重跑恢复。协作锁不替代其他编辑器的锁，也不是跨文件数据库事务。
- tests/unit/test_workflow_execution.py：启动0/N、dry-run、缺Sprint拒绝、未启动拒绝进度、未全勾选拒绝完成、全勾选进度不完成、重复启动、旧六状态、聚合、符号链接拒绝、冲突/替换中断恢复与投影失败重跑。
- src/backend/tests/test_governance_lifecycle.py：REQ/BUG 真实 context 接口阶段和快照变化；test_governance_board.py 覆盖既有项目绑定、范围读取及缺文件兼容。工作流与后端目标回归85项通过。
- src/web/src/governance.test.tsx：9项通过，含REQ/BUG服务端阶段刷新及现有项目范围、并发刷新回归；npm run build通过，未改业务UI布局。
- 真实Chromium：1440×1000，/requirements；隔离账号和合成项目内REQ-9091/BUG-9091，真实登录、CLI和HTTP，无网络mock。10次CLI事件成功，11个不同snapshot_revision。验证轮询、手动刷新、页面重载、focus事件处理器、0/2启动以及2/2完成前后状态。focus由浏览器脚本派发，不等同人工切换操作系统窗口；没有修改BUG-0014作为通过证据。
- 浏览器证据：evidence/browser-lifecycle.json 与 before-start-1440.png、requirement-started-1440.png、bug-started-1440.png、completed-1440.png。已检查截图：卡片阶段与动作一致；computed style为display:flex、font-size:13px、width:300px。截图中的合成BUG分级标签沿用现有展示，本次不调整分级映射。
- 自检修复：隔离API夹具缺工作区表改为测试边界隔离；CLI夹具YAML列表缩进修正；故障恢复测试重新从文件读取完整frontmatter，避免旧record错误报告额外变更。失败均在当前apply内修复并重验。
- 证据边界：浏览器是真实本地服务与合成数据，未执行生产发布；中断/冲突为故障注入测试，未制造线上进程故障。API响应结构、DB、OpenAPI/Orval、对象存储、部署配置、安全权限及埋点协议均无变化，无需迁移或客户端重生成；API索引补充状态语义。CLI不伪造usage_events。

AC映射：001/002/007→共享状态+接口+浏览器；003→dry-run/缺Sprint/未启动拒绝；004→状态计数+接口；005/006→重复/旧终态/原子中断/投影重跑；008→两份apply与sprint-apply契约；009→CLI投影+context；010→真实浏览器；011→既有项目范围回归+脱敏证据。技能文本契约校验不宣称启动了其他Agent会话。


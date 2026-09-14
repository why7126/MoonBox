---
purpose: 架构说明
content: MoonBox MVP 架构边界、模块分层和数据流
created_at: 2026-07-29 22:55:00
updated_at: 2026-09-14 00:03:14
owner: MoonBox 产品团队
---

# 架构说明

MoonBox MVP 采用 Web + API + SQLite + MinIO 的本地优先架构，围绕项目空间、Agent Workflow、产品知识图谱和 Harness Runtime 建立研发组织基础设施。

## 分层

| 层 | 目录 | 责任 |
|---|---|---|
| Web | `src/web` | 品牌入口、工作台、管理后台、Agent Workflow 可视化 |
| API | `src/backend` | REST API、认证、组织空间、Workflow 状态、知识索引 |
| Shared | `src/shared` | 跨端类型、契约、设计 token 和共享常量 |
| Infrastructure | `src/infrastructure` | Docker、存储、数据库、部署脚本 |
| Data | `data` | 本地运行数据和开发样例，不提交真实数据 |

## 核心模块

- Project Workspace：组织空间、项目空间、成员角色和权限边界。
- Harness Runtime：项目结构、规则、技能、上下文和治理流程。
- Agent Workflow：节点、状态、审批、执行记录和复盘。
- Product Knowledge Graph：需求、设计、代码、测试、决策与经验的追溯关系。

## 数据流

用户在 Web 工作台创建产品目标或研发事项，API 将其写入 SQLite，并通过 Workflow 状态机推进到需求、OpenSpec、Sprint、实现、验证和知识沉淀。文档与图片资产通过对象存储保存，元数据和引用关系保存在数据库中。


## Chat后端首批接入

app/chat提供个人会话API、受控业务存储和独立恢复进程。API复用前台认证并验证有效空间所有者/成员；候选仓库只通过MOONBOX_CHAT_REPOSITORIES映射不透明id和space_id。恢复worker仅将过期心跳标记unknown并保留会话锁，当前不领取模型任务。

模型执行、凭证代理/隔离与额度预留仍未完成；本机App Server协议验证不等于平台执行能力。新发送默认拒绝，前端骨架尚未绑定本批API。

Chat Web通过现有Bearer认证接入会话管理，事件使用有限SSE游标页；新增admission模块以事务实现用户/空间双重预留、同请求幂等与终态结算。API发送门禁尚未连接admission与真实模型worker，恢复worker仍不领取模型任务。


Chat执行器分为app_server协议适配、workspace工作区/快照和execution单轮持久化执行三个模块。App Server固定0.153.4 stdio版本，恢复先验证线程ID/工作目录；中止发送后持续消费终态通知，RPC超时与断连保留unknown。run_claim通过worker generation校验，按真实通知保存回复、事件、用量和Diff。已在一次性仓库+测试数据库验证本机登录的两轮修改及进程重建恢复；这不是平台凭证、网络或跨租户容器隔离的证明。

Chat执行边界增量：业务API与内部run_claim分离；执行前及运行中校验会话/空间/对象与治理写权限，缺少合规Change时强制只读。Relations、admission、policy、execution、observability、cleanup分别维护引用、事务、授权、执行、脱敏追踪和清理状态。正式平台认证/持续worker尚未接通，API能力门禁仍关闭；个人本机执行探针与无凭证容器隔离探针不能组合推断正式端到端完成。

### 工作台共享侧边栏

需求中心与 Chat 复用 `src/web/src/components/workbench/WorkbenchSidebar.tsx`，账号资料、密码和空间动作从需求中心提取到共享模块。`useWorkbenchTheme` 使用既有 UI 偏好存储及事件同步，两页只改变当前导航项，业务上下文通过类型化属性提供。Chat 的账号目录复用现有需求中心鉴权上下文接口；空间选择与 Chat 授权空间目录取交集，服务端继续独立校验执行权限。样式位于 `src/web/src/styles/workbench.css`，Chat 按钮通用样式仅作用于会话、执行栏和 Chat 弹窗。


Chat本机隔离验收拓扑（2026-09-08）：回环同源构建Web/API → 私有测试门禁 → 持久化队列 → 独立local_worker → 固定App Server及原生权限 → 每会话受控代码目录。worker可正常重启并恢复原线程，运行中SIGTERM请求原轮次停止而不重放；可信用量receipt支持幂等补结算。该拓扑只用于用户授权的临时测试账号/仓库，不是正式多租户凭证方案。清理和限制见部署文档。


### Chat恢复与清理补验（2026-09-09）

REQ-0025受控验证新增独占进程组守护、可信副本清理回调和失败重试，清理状态仍受当前空间权限控制。无DB结构或API字段变更。MySQL 8.2独立容器32 passed/1 skipped，SQLite后端回归46 passed/1 skipped，新增清理权限聚焦2 passed。非root只读镜像重启后保留unknown活动锁，不自动重领。真实Codex线程历史删除通过，但实际备份适配、正式平台配置与模型容器执行未完成；证据见openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/recovery-cleanup/，不代表正式发布。


### REQ-0025推荐组合增量（2026-09-09）

新增app/chat/backup.py本地SQLite适配：业务库之外的deletions.sqlite保存identity（数据库归属）、deletions（会话删除意图）和backups（副本摘要清单）。不增加业务库表字段，不改变MySQL业务schema；SQLite恢复不代表MySQL/S3恢复通过。在线一致性备份、独立删除日志、离线恢复重放、旧任务unknown隔离、清理库存验证和明确副本物理删除已测试。恢复账本仍需可信对账；日志不允许随旧业务库回滚。

新增ContainerAppServer及隔离worker的container执行方式。模型工具无法读取认证、业务DB或Docker socket；实际双轮/同线程恢复/停止及后端claim、Diff持久化和用量结算通过。专用seccomp允许嵌套用户命名空间所需调用，保留非root和能力清空，不宣称达到虚拟机隔离强度。正常平台仍关闭发送；部署入口和限制见docs/02-deployment.md，证据见Change evidence/recommended-deployment/。


日常部署脚本增量（2026-09-09）：`--chat-test` 经 `app/chat/deployment.py` 私有 Unix 控制通道管理一次性 harness；宿主控制器持有 Docker 调用能力，执行容器仍不挂 Docker socket。测试 API/worker/SQLite/备份独立于常规 Compose 服务，静态资源由本次 Web 镜像导出。控制目录按项目与所选 env 文件定位，幂等启停且不按历史 PID 终止进程；清理测试数据后才释放控制端。无 API schema、业务表或 UI 组件变更，不需客户端生成。正式平台门禁与此前未完成项不因脚本接入而解除。


### 终态并发释放补充（2026-09-09）

Chat并发占用与Token/容量结算拆分：可信终态事务幂等释放并发槽，未知用量继续预留。accounting提供旧终态补偿，settle不再重复释放并发；并发释放失败时事务回滚，不能伪造可执行状态。


### 执行进程计量范围补充（2026-09-09）

App Server按每次run_claim新建独占进程，线程恢复只恢复上下文，不保证Token计数器跨进程累计。真实探针确认total重置；计量改为匹配线程/轮次的本进程total单调最大值，不能减去上次执行的token_total。


### 单机常驻方案确认（2026-09-09）

用户已明确采用单机 Docker Compose、SQLite、本地独立备份、本机 Codex 认证单文件，取消用户/空间额度、并发和存储运营上限。显式 unlimited 与缺失配置区分，仍计量结算；同会话互斥、权限、未知态和单轮结果处理技术边界保留。历史及备份不自动过期；主动删除仍记录和跟踪主存储/执行线程/备份，副本无固定删除截止时间，旧备份物理移除前保持待清理。单机控制器顺序处理持久队列，容量不足不绕过隔离。正式仓库路径及空间映射尚待提供，当前不宣称正式服务已开放。方案细节以 docs/02-deployment.md 的单机常驻章节为准，替代此前“认证、限额和期限尚未决定”的当前态描述；历史证据保留。

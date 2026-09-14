---
purpose: 数据库设计
content: MoonBox SQLite 初始数据域与迁移治理
created_at: 2026-07-29 22:55:00
updated_at: 2026-09-14 00:03:14
owner: MoonBox 产品团队
---

# 数据库设计

MoonBox MVP 采用双数据库策略：开发和自动化快速测试使用 SQLite，生产环境使用 MySQL。迁移策略为 Alembic 或等价 schema 初始化机制；在当前基线中，`schema_metadata` 由后端数据库初始化流程维护。

本地 Docker 环境默认通过 `DATABASE_TYPE=sqlite` 与 `DATABASE_URL=sqlite:////app/data/sqlite/moonbox.db` 注入后端服务。运行时数据库文件属于本地数据，不得提交 Git。

生产环境必须显式设置 `DATABASE_TYPE=mysql`，并通过 `DATABASE_URL` 或 `MYSQL_DATABASE_URL` 注入 MySQL 连接串。MySQL 凭据不得写入仓库；生产环境配置缺失、连接串非 MySQL 或误用 SQLite 时，服务必须启动失败。

## 初始数据域

| 数据域 | 说明 |
|---|---|
| workspaces | 组织空间、项目空间、成员关系 |
| agents | Agent 角色、能力、工具权限和运行配置 |
| workflows | Workflow 定义、节点、状态流转和审批记录 |
| knowledge_nodes | 需求、设计、代码、测试、决策、经验等知识节点 |
| knowledge_edges | 知识节点之间的追溯关系 |
| assets | 文档与图片对象存储元数据 |
| admin_users | 管理后台用户账号、角色、状态、冻结前状态、空间数、超级管理员保护和会话失效时间 |
| admin_sessions | 管理后台 access token 对应的服务端会话记录，支持过期、撤销和最后使用时间追溯 |
| admin_audit_events | 用户管理写操作审计，记录操作者、对象、动作、前后值、原因、结果和请求 ID |
| admin_spaces | 管理后台空间主表，记录空间编码、负责人、状态、来源、配额、有效期、回收期和保护标记 |
| admin_space_products | 空间与产品绑定表，当前约束为一空间一产品绑定 |
| admin_space_members | 空间成员关系表，保留空间成员角色和去重约束 |
| admin_space_applications | 管理后台空间申请与审批兼容表，记录申请人、拟负责人、目标空间、资源诉求、决策原因和决策人 |
| admin_space_audit_events | 空间管理写操作审计，不记录 token、会话 ID 明文或敏感凭证 |
| schema_metadata | 初始化 schema 版本追踪 |

## 管理后台用户表

`admin_users` 由 `add-admin-user-management` 引入，当前使用应用层 Repository + SQL 初始化维护。

| 字段 | 说明 |
|---|---|
| `id` | 服务端生成用户 ID |
| `username` | 全局唯一，4-32 位，字母开头，仅字母数字 |
| `nickname` | 昵称 |
| `avatar_url` | 头像访问 URL 或对象引用 |
| `role` | 仅允许“后台管理员”或“前台用户” |
| `status` | 待激活、正常、已冻结、已删除 |
| `status_before_freeze` | 冻结前状态，仅允许待激活、正常或空；解冻时据此恢复目标状态 |
| `workspace_count` | 关联空间数聚合结果 |
| `password_hash` | 管理后台账号密码哈希；不得保存明文密码 |
| `is_system_superadmin` | 系统内置唯一超级管理员保护标记 |
| `session_invalidated_at` | 冻结后 10 秒内会话失效目标时间 |
| `deleted_at` | 逻辑删除时间 |

冻结待激活或正常用户时，应用层必须写入 `status_before_freeze`；重复冻结已冻结用户不得覆盖既有冻结前状态。解冻成功后必须清空该字段；历史数据缺少冻结前状态时不得静默恢复为正常，应返回受控错误或执行明确兼容策略。`admin_audit_events` 记录用户管理写操作审计，不存储临时密码明文，仅记录重置动作结果和状态变化摘要。

## 管理后台会话表

`admin_sessions` 由 `add-admin-auth-system` 引入，用于让 access token 具备服务端可撤销能力。

| 字段 | 说明 |
|---|---|
| `id` | 服务端会话 ID |
| `user_id` | 关联后台用户 ID |
| `token_hash` | access token 哈希；不得存储明文 token |
| `expires_at` | 会话过期时间 |
| `revoked_at` | 会话撤销时间 |
| `last_used_at` | 最近使用时间 |
| `created_at` / `updated_at` | 创建与更新时间 |

## 管理后台空间表

`admin_spaces`、`admin_space_products`、`admin_space_members`、`admin_space_applications` 与 `admin_space_audit_events` 由 `add-admin-space-management` 引入，当前使用应用层 Repository + SQL 初始化维护。

| 表 | 关键字段与约束 |
|---|---|
| `admin_spaces` | `code` 全局唯一；`status` 仅允许 `ACTIVE`、`FROZEN`、`RECYCLE`；`source` 仅允许“后台创建”或“申请审批”；`expiry_type` 仅允许 `fixed_date` 或 `long_term`；`protected` 控制冻结、回收和彻底删除限制；`deleted_at`、`deleted_by`、`delete_reason`、`purge_at` 支撑回收站和 30 天保留 |
| `admin_space_products` | `space_id` 唯一，保证一空间一产品绑定；`immutable_binding` 标记绑定不可随意替换 |
| `admin_space_members` | `(space_id, user_id)` 唯一，记录空间普通成员与角色；负责人由 `admin_spaces.owner_id` 表达，不在成员列表中重复维护 |
| `admin_space_applications` | 管理后台审批兼容表；`application_type` 仅允许 `create` 或 `join`；`target_space_id` 记录历史加入空间申请的目标空间；`status` 仅允许“待审批”“已通过”“已拒绝”“已撤回”；保存申请人、拟负责人、产品、用途、资源诉求和审批决策字段 |
| `admin_space_audit_events` | 记录空间 ID、操作者、动作、前后状态摘要、原因、结果、请求 ID 和创建时间；不得写入 token、会话 ID 明文、密码或临时凭证 |

空间删除为软删除：正常空间移入回收站后写入 `deleted_at`、`deleted_by`、`delete_reason` 和 `purge_at`，默认列表不展示回收站数据；恢复会清理删除字段；彻底删除仅允许系统超级管理员对回收站空间执行，并级联清理绑定和成员关系。配额字段当前直接保存在 `admin_spaces`：`member_count/member_quota`、`storage_used_gb/storage_quota_gb`、`ai_used_tokens/ai_quota_tokens`，其中 `member_count` 口径为负责人加普通成员，普通成员关系保存在 `admin_space_members`；后续接入真实用量聚合时必须保持字段含义兼容。前台创建空间入口写入 `admin_space_applications` 待审批申请；平台管理员审批通过后再写入 `admin_spaces` 与 `admin_space_products`，申请人成为 `owner_id`。

## 双数据库兼容策略

| 项 | SQLite | MySQL |
|---|---|---|
| 使用场景 | 本地开发、快速测试 | 生产环境、发布前兼容验证 |
| 默认连接 | `sqlite:////app/data/sqlite/moonbox.db` | `mysql+pymysql://<user>:<password>@<host>:3306/<db>` |
| 字符集/排序规则 | 不适用；应用层约束 | `utf8mb4` / `utf8mb4_0900_ai_ci`，生产前人工确认 |
| 时间策略 | `CURRENT_TIMESTAMP` 文本或 ORM 映射 | `TIMESTAMP`，默认 `+00:00` 策略 |
| JSON 策略 | 优先应用层校验或 SQLite JSON1 能力 | 使用 MySQL JSON 能力时需补兼容测试 |
| 迁移策略 | 支持本地空库初始化 | 发布前验证迁移、约束和事务行为 |

当前基线 SQL 位于 `src/backend/app/db/schema.sql`，运行时初始化由 `src/backend/app/db/session.py` 按数据库方言执行。数据库变更必须同步模型、Repository、迁移脚本或 schema SQL、数据库文档、兼容性记录和测试。


## Chat增量数据结构（首批）

app.chat.schema通过SQLAlchemy create_all仅创建12张Chat表，应用启动时在既有schema之后调用，可重复执行，不修改既有表：chat_conversations、chat_turns、chat_events、chat_messages、chat_context_snapshots、chat_diff_snapshots、chat_request_logs、chat_usage_accounts、chat_usage_reservations、chat_workspace_baselines、chat_relations、chat_object_access。用户和空间外键引用既有admin_users/admin_spaces；外部表定义仅用于解析外键，不由本迁移创建。

会话owner+space+activity索引、会话+client_request_id唯一键、轮次+source_id及sequence唯一键用于查询、幂等和重放。active_turn_id与generation承载会话互斥和fencing；心跳失效保留锁并进入unknown，禁止自动重新执行。事件写入通过轮次行条件UPDATE串行化后分配序号，终态拒绝后续事件。业务正文使用SQLite Text/MySQL LONGTEXT，时间采用UTC ISO字符串。

本批只允许删除无轮次会话并保留墓碑；有执行历史时拒绝清理，尚不具备代码/副本/备份清理事实，不能宣称彻底删除。额度预留与终态结算已实现内部事务服务；主对象关联持久化、真实执行端接线和完整清理策略未实现，执行入口关闭。请求摘要单独存储，只包含服务端request_id、actor、路由模板、方法、状态及耗时，不存Prompt、回复、Diff或认证头。

SQLite和独立MySQL 8.2.0相同13例通过；生产目标MySQL 8.4仍待单独矩阵。本地升级已先执行SQLite在线备份，仅增表。回退先停止chat-recovery再回退应用镜像，保留Chat表和数据，不自动恢复或删表。

额度账户分别保存全局并发/容量和UTC月份Token使用量，用户与空间固定顺序更新，条件UPDATE原子预留；预留与turn唯一关联。未知或运行中状态不释放预留，确认终态后幂等结算；跨月结算回到原预留月份。超出预留的实际计量仍记账，不能据此宣称执行端已具备硬停止边界。


Chat执行基准增量：workspace_baselines以conversation_id为主键，workspace_id唯一，保存初始内容清单/hash与已确认累计Token计数。每轮Diff同时保存本轮files、cumulative_files与initial_hash；messages/turns/snapshots增加查询索引。迁移在create_all之后逐个checkfirst创建索引，覆盖既有表新增索引的情况。SQLite与独立MySQL 8.2.0均验证16个Chat用例（真实模型测试另行执行），SQLite另验证主动移除索引后迁移补建。

关联增量：chat_relations 保存会话当前主对象/引用；chat_object_access 保存空间、仓库、对象、用户的收窄权限。无显式对象 ACL 时继承预配置仓库对应空间权限，有 ACL 时仅允许明确 can_read 的用户。每轮入队原子写入不可变引用快照、完整源版本摘要和截断标记；正文总量限制48KB、单对象12000字符。历史读取与列表分页/计数前重新授权，不可访问历史引用时整个会话不可读，防止派生回复泄漏。

运行观测与清理增量：当前迁移共管理16张表（13张chat前缀业务/审计表以及 usage_events、task_traces、task_trace_spans）。chat_cleanup_jobs 独立记录主存储清理、执行副本与备份状态及到期时间，不随正文删除；task_traces/ spans 无业务外键级联，按90天观测周期保留。usage_events 只保存稳定字典、可信服务端request_id及结果，180天清理；不保存Prompt、引用原文或Diff。普通查询仅写请求日志，无长任务Trace。恢复worker执行本能力观测清理，不清理其他能力的事件。

历史删除检查会话锁、结算状态、当前git工作区与确认hash，允许历史有Diff但当前已处理的会话删除；代码目录不删。正文物理删除后副本/备份状态保留pending，不能仅因时钟到期自动标记清理完成。恢复备份必须从独立删除记录重放墓碑；执行副本清理及独立墓碑备份机制仍待平台部署验证，未配置时禁止正式历史删除。

观测关联补充：成功且已授权的停止/发送/重试记录仅附加受限turn_id，失败越权请求不附加对象标识；调用端自报标记不能成为权限依据。


Chat结算恢复语义更新（2026-09-08）：在chat_events以source_id=runner:accounting保存可信执行端本轮用量、线程累计用量和保留结果字节数；字段允许用量为null表示待核实。终态后有界接收迟到用量，匹配thread/turn并保持计量单调；receipt持久化后可重复运行补结算，chat_usage_reservations状态CAS防重复扣费。没有用量仍reserved，不按零值释放；未知运行保持活动锁。沿用已有表与索引，无schema或迁移变化。SQLite真实四轮含一个停止待对账，MySQL结算更新沿用已有参数化事务路径，本批新增语义的MySQL实跑未覆盖，不宣称完整生产矩阵通过。


### Chat恢复与清理补验（2026-09-09）

REQ-0025受控验证新增独占进程组守护、可信副本清理回调和失败重试，清理状态仍受当前空间权限控制。无DB结构或API字段变更。MySQL 8.2独立容器32 passed/1 skipped，SQLite后端回归46 passed/1 skipped，新增清理权限聚焦2 passed。非root只读镜像重启后保留unknown活动锁，不自动重领。真实Codex线程历史删除通过，但实际备份适配、正式平台配置与模型容器执行未完成；证据见openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/recovery-cleanup/，不代表正式发布。


### REQ-0025推荐组合增量（2026-09-09）

新增app/chat/backup.py本地SQLite适配：业务库之外的deletions.sqlite保存identity（数据库归属）、deletions（会话删除意图）和backups（副本摘要清单）。不增加业务库表字段，不改变MySQL业务schema；SQLite恢复不代表MySQL/S3恢复通过。在线一致性备份、独立删除日志、离线恢复重放、旧任务unknown隔离、清理库存验证和明确副本物理删除已测试。恢复账本仍需可信对账；日志不允许随旧业务库回滚。

新增ContainerAppServer及隔离worker的container执行方式。模型工具无法读取认证、业务DB或Docker socket；实际双轮/同线程恢复/停止及后端claim、Diff持久化和用量结算通过。专用seccomp允许嵌套用户命名空间所需调用，保留非root和能力清空，不宣称达到虚拟机隔离强度。正常平台仍关闭发送；部署入口和限制见docs/02-deployment.md，证据见Change evidence/recommended-deployment/。

本批最终兼容回归：后端51 passed/3 skipped，独立MySQL 8.2矩阵33 passed/1 skipped；SQLite本地备份4项通过。所有跳过的显式真实测试均与单独运行证据区分，详见Change evidence/recommended-deployment/verification.json。


### 终态并发释放补充（2026-09-09）

Chat预留表增加concurrency_released INTEGER NOT NULL DEFAULT 0，作为并发释放幂等标志。migrate检测旧结构后增列，将已有settled记录标为1；迁移不重算或清空任何额度。终态事务更新标志并递减空间/用户active_runs，缺失用量仍reserved且actual_tokens=NULL；可信用量到达后仅结算Token与容量。旧终态reserved由worker对账循环补偿，重复/竞争调用至多释放一次。SQLite和MySQL 8.2迁移、竞争验证通过。


### 执行进程计量范围补充（2026-09-09）

本轮无DB结构变化。workspace_baselines.token_total保留兼容记录，含义为最近执行进程观察值，不再充当下一轮扣减基线。runner:accounting事件增加usage_scope=app_server_process_v1；同进程total去重取最大，迟到补结算不覆盖新轮次的兼容记录。缺少scope的旧receipt保持reserved并提示待核实。历史已settled的测试数值不自动重写。


### 单机常驻方案确认（2026-09-09）

用户已明确采用单机 Docker Compose、SQLite、本地独立备份、本机 Codex 认证单文件，取消用户/空间额度、并发和存储运营上限。显式 unlimited 与缺失配置区分，仍计量结算；同会话互斥、权限、未知态和单轮结果处理技术边界保留。历史及备份不自动过期；主动删除仍记录和跟踪主存储/执行线程/备份，副本无固定删除截止时间，旧备份物理移除前保持待清理。单机控制器顺序处理持久队列，容量不足不绕过隔离。正式仓库路径及空间映射尚待提供，当前不宣称正式服务已开放。方案细节以 docs/02-deployment.md 的单机常驻章节为准，替代此前“认证、限额和期限尚未决定”的当前态描述；历史证据保留。


### Chat工具详情兼容补充（2026-09-11）
既有chat_events.payload按detail_version=1保存经脱敏限长的白名单工具详情，无DDL迁移；历史null/缺失字段显示未采集，不回填推算。个人访问权限、主动删除与备份删除重放沿用现有规则，参数/输出不复制到通用审计metadata。

## 治理成果持久化（REQ-0022）

新增governance_candidates、governance_applications、governance_project_locks，通过app.chat.schema.migrate增量create_all创建，迁移可重复执行，不修改既有Chat记录。三表复用SQLite/MySQL通用String/Integer/BigInteger与显式唯一约束；正文和前后镜像仅存私有文件，DB保存opaque ID和SHA-256。

- candidates：操作者、空间/仓库、个人会话、成功turn、对象、动作、绑定/基准/manifest摘要、revision、state。一个turn最多一个候选；conversation+created_at索引支持个人成果查询。prepared状态同时承载动作准备，执行后成为pending或rejected。
- applications：candidate唯一有效操作、actor/scope/idempotency唯一约束，idempotency键先SHA-256编码避免MySQL默认大小写不敏感排序导致键碰撞；request_hash防止同键不同内容。state+created_at索引支撑控制器队列，phase/fencing_token/worker_id支持恢复。
- project_locks：scope_key主键、单调fencing_token、当前operation_id/worker_id/updated_at。DB记录配合本机私有文件锁；过期时间不构成接管依据。

迁移回退保留新增表与私有目录，不drop。备份需覆盖数据库和私有记录，同一维护窗口下形成一致副本。未终态恢复记录不按时间删除；治理会话在保留清理能力验收前拒绝删除。请求日志90天、行为180天、已终态治理Task Trace90天；未终态trace不按finished_at清理。对象存储没有新增表或依赖。

当前验证包含SQLite真实读写/唯一键/重启恢复、MySQL DDL编译及独立MySQL 8.2.0矩阵13项通过；生产数据迁移尚未执行，不能据此宣称生产升级已经验收。


## Chat 延迟创建与幂等

会话创建可选请求标识以固定命名空间、用户及请求值派生UUID，复用chat_conversations主键唯一约束处理并发；不增加列或索引，无迁移。重放通过原会话权限查询，软删除墓碑阻止原请求复活；SQLite并发测试覆盖，SQLAlchemy原主键机制兼容MySQL，本批未重复执行MySQL实机矩阵。

## Capture 操作记账（BUG-0014）

复用governance_applications、governance_project_locks及既有观测表，不新增表或迁移。幂等范围为actor、项目与键摘要；Capture前后镜像和最终完整ID位于既有私有operation记录，业务事实仍是项目issues目录内文件。编号在项目锁内读取注册表与所有阶段目录后分配；202不能视为提交完成，applied才代表整批核验通过。重启使用同一私有记录恢复，遇外部修改保留recovery_blocked读屏障。

SQLite与一次性MySQL 8.2.0均验证创建、幂等、恢复和操作查询；数据库备份必须继续与私有状态目录成套，不把文件镜像移入行为事件或请求日志。

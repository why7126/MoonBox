---
title: 治理命令持久化恢复闭环设计
---
# 治理命令持久化恢复闭环设计

## 背景与现状
现有 direct_command_journal 保存准备与观察记录；writer/application 保留逐文件写入和同步事实；controller 可继续未终态应用，execution_context 的核验不重跑模型。当前缺少统一操作阶段、持久重试预算和可授权恢复入口。本设计复用这些事实源，避免另建写通道。

## 目标与非目标
首期覆盖 req-review / bug-review 的正常评审和中断恢复。其他10种 direct action 只展示适用性，不开放新的自动恢复。共用反馈展示仍归REQ-0046；不实现通用调度器、不自动重跑模型、不开展真实生产升级。

## 设计方案
### D1：现有设计系统与局部结构迁移
采用现有Web设计token、按钮和对话框，迁移原型布局及状态语义。纯CSS整页复制会重复现有Chat框架，故不采用；无外部图片资产需求。

### 首期动作适用矩阵
| 动作 | 本能力状态 | 恢复边界 |
|---|---|---|
| req-review、bug-review | 支持 | 完整阶段、预检、预算、受控续接 |
| req-generate、bug-generate、req-complete、bug-complete | 只观察 | 复用既有状态，无新增恢复领取 |
| sprint-propose、req-opsx、bug-opsx | 只观察 | 保留既有journal，不自动重新执行 |
| opsx-apply、opsx-modify、opsx-archive | 不支持本恢复入口 | 沿既有专用执行契约，不能套用评审续接 |

### D2：业务操作、尝试与阶段
新增治理操作记录 governance_operations，以不可变operation_id关联conversation_id、origin_turn_id、candidate_id和application_id；执行尝试保留独立turn及原始terminal。数据库是领取权、预算和版本事实源，私有journal是原文件集合/逐文件前后镜像证据，application仍是写入结果事实源。禁止以DB状态单独证明文件提交。
操作stage为prepare/generation/validation/apply/readback/complete；state为active/waiting/blocked/completed；页面loading单独维护。phase失败不逆改turn。每次检查点保存schema_version、source/manifest/input指纹及证据引用，单调version用于CAS。文件写入前持久化意图，后记录证据；崩溃后比对前后镜像，不推断跨存储原子性或exactly-once。
新增governance_recovery_attempts保存operation_id、request_key、request_hash、kind、领取时间、fencing_token、结果；同操作同键唯一。同键同输入返回原尝试，异输入409；新生成必须新操作并记录parent_operation_id。操作创建的幂等键按actor/space/repository/action作用域唯一，保存请求指纹。
SQLite以短事务条件更新，MySQL以等价条件更新/行锁领取，统一校验version、lease和fence；不长持DB事务等待模型。对象互斥复用execution_guard，不同时持有相反顺序的锁。过期lease不足以证明执行器结束：未知占用阻塞；接管前验证原执行已终结或fence生效。持有旧fence的执行器不得提交。

### D3：启动预检与恢复决策
在模型调用前检查baseline/operation完整性、记录schema、action、绑定版本，以及backend/worker/controller发布的schema区间和动作集合交集；检查心跳新鲜度。不同发行版本允许兼容；缺记录、损坏或能力未知均失败终结，不消费模型。旧记录只读或经可证明幂等迁移，保留原件，不补造历史阶段。
恢复读取当前权限、绑定、固定成果、源hash、application、lease、操作version和期限。生成不完整时只允许明确重新生成；完整成果未校验先校验；已校验未应用进入原writer；部分应用先核对所有文件前后镜像，仅续接原授权集合；外部冲突阻塞；提交响应丢失先读回原application；只有页面失败只刷新。complete要求validation、文件集合、Workflow Sync、registry/index与读回一致，不能只看助手文本或进程exit。

### D4：预算与停止
仅临时连接/存储异常或已证明未提交超时可自动重试；未知提交先读回。每operation总共3次自动重试（不含首尝试），退避2/10/30秒；领取重试前原子保存次数与next_retry_at，重启不重置、阶段不重置；争锁不消耗预算。权限撤回、绑定/源变化、损坏、成果拒绝、占用未知及不兼容不可自动重试。
耗尽进入blocked；只读复查不消耗写预算。原因消除且后端允许后，用户明确确认可领取一次剩余事务尝试，独立manual_count，同请求去重，不重置自动预算或自动新建操作。
主动停止终止生成并撤销尚未领取的自动续接。apply前必须由用户确认继续；正在提交的原事务仅允许完成其最小一致性恢复与读回，不扩到下一命令。权限/绑定撤销仍阻塞，不以停止恢复绕过；管理员恢复合法权限后复用受控通道。原turn的stopped/failed不可改写成completed。

### D5：期限与清理
恢复截止为可靠turn终态时间加7天、部署既有artifact保留期限和原记录更早期限的最小值。读、重试、重启不延期；配置缺失返回retention_unconfigured，成果不存在返回artifact_unavailable。活动执行与提交事务保护清理；到期不再领取新写尝试，允许只读确认已提交结果。完成后释放引用；半迁移保留最小证据并标记cleanup_blocked，不静默无限备份。显式处置必须再次验证管理员合法权限、操作version和保留集合，经同一审计受控路径决定保留或清理，不新增默认删除任务。
诊断摘要90天，usage_events180天，聚合1年；不扩大既有敏感原文保留期限。实际策略配置本轮不变。

## 数据与 API
新增表字段除上文身份外含stage/state/version/schema_version、execution_terminal、reason_code、artifact_refs/application_ref、auto_retry_count/manual_count/next_retry_at/recovery_expires_at、lease_owner/lease_until/fencing_token、created_at/updated_at。索引覆盖对象活动操作、到期领取、清理阻塞及幂等唯一键；时间统一UTC。迁移同时维护SQLite与MySQL，回填仅可证事实，未知保持只读。
在现有 `/api/v1/chat` 路由族新增 GET `/governance-operations/{operation_id}`（只读详情/权限过滤allowed_actions）、POST `/governance-operations/{operation_id}/recoveries`（expected_version、idempotency_key、明确确认）。返回既有ApiResponse与请求关联字段，202返回同一operation及attempt；版本/指纹冲突409，权限沿现有不可枚举规则，语义拒绝附reason_code。GET不领取任务、不触发写入或模型；POST服务端重校验，不信任前端allowed_actions。重新生成只填当前会话草稿，用户发送后才新建linked操作。
OpenAPI、Orval、docs/03-api-index.md及契约测试同步；数据库设计、SQLite/MySQL迁移与唯一性/并发测试同步。无需新计费事件；只记录恢复关联，不重复计算原模型usage。

## UI Contract
事实源顺序：HTML > PNG（本需求无）> context.md > acceptance.md > ui-design.md >既有spec；业务执行真实性由后端能力与正式验收约束。截图为事故背景，未要求一对一复刻。
采用原型bg #0a0d14、panel #131826、border #242a3a、gold #d8ac55、text #eceae4、muted #98a0b3；映射现有token，有差异先记录不静默改色。字体Inter/Noto Sans SC/system-ui，14px/1.45，圆角不超过8px，main最大960px，对话框min(560px,100vw-32px)、最高80vh纵滚。640px以下阶段纵排，390px无横向溢出。保留现有图标族及“继续剩余步骤”语义。
前后台一致性checklist：原执行终态不变；业务阶段从GET读取；allowed_actions由后端决定；无权限不泄漏证据；提交期间防重复；409重新读回且不覆盖；完成后刷新卡片。管理端不新增页面。
原型是Mock交互设计输入，产品删除demo-state选择器；不得模拟计时成功。恢复成功仅来自读回。以真实API实现详情、证据、动作与请求关联；原型没有真实网络调用。

## UI Skeleton
先搭Chat内RecoveryOperationPanel，包含执行终态、业务状态、stage-list、reason/limits、actions、feedback；ResumeDialog与EvidenceDialog组成共享动作族，DraftRegion承载草稿。数据依赖为操作GET、恢复POST及现有会话草稿入口。
1440px首轮确认区域宽度、阶段行、按钮排列、对话框边界，确认后才实现细节；Skeleton状态pending，不宣称已确认。

| 动作 | modal类型 | 原型→目标测试selector | 状态 | 证据 |
|---|---|---|---|---|
| 刷新 | 无 | #refresh→[data-testid=recovery-refresh] | 除权限失效外可读，独立loading | 网络仅GET/截图 |
| 继续剩余步骤 | 确认dialog | #resume/#resume-dialog/#confirm-resume→recovery-resume/recovery-resume-dialog/recovery-confirm | recoverable可用，submitting禁用，取消/Esc不写 | 1440与390确认/提交 |
| 查看证据 | 详情dialog | #evidence/#evidence-dialog→recovery-evidence/recovery-evidence-dialog | denied隐藏，其他按能力 | 权限与键盘录证 |
| 重新生成 | 无，填草稿 | #regenerate/#draft-region→recovery-regenerate/recovery-draft | expired且允许时提供，不自动发送 | 草稿与无POST证明 |

其余selector business-state/stage-list/reason/limits/feedback映射recovery同名data-testid。feedback使用role=status和aria-live=polite；对话框焦点进入/约束/返回触发器，Esc关闭，键盘可达。recoverable/submitting/completed/conflict/denied/incompatible/expired/unknown全部有状态容器。
Computed style采样：1440x900深色recoverable及confirmation采面板max-width、背景/边框、字体/line-height、gap、按钮颜色、dialog宽/高/overflow；390x844采dialog、长原因、阶段换行与页面scrollWidth。颜色/字体按token精确，布局允许1px取整；证据写evidence/acceptance，当前值待实现采集。

## Conflict Resolution（冲突处理）
没有实质语义冲突。HTML的demo-state和手工切成功仅供演示，不进入产品；正式完成必须后端读回。原型native dialog迁移为共享DS语义等价组件，记录computed style差异；没有新增截图复刻门禁。验收以本设计、REQ AC、真实截图、样式证据、Mock/API边界及文档回填共同成立。

## 观测声明
product_data_collection_observability:
  status: applicable
  affected_layers: [api, db, request_logs, usage_events, task_traces, task_trace_spans, web]
  reason: 操作、尝试、应用和恢复请求需要同一身份关联且避免重复计费
  validation: AC-013/014/015验证请求关联、直接API调用不伪造行为事件、脱敏白名单与保留期限；复用现有trace/spans，日志不写prompt、token、绝对路径或文件原文
对象存储无新协议；私有成果引用沿既有访问控制。文档与测试覆盖API/DB/UI/安全/部署兼容；不新增管理端生成客户端。

## 迁移与回滚
先部署向后兼容增量schema，再部署支持能力声明的backend/worker/controller，交集通过后开放评审恢复按钮。部署预检记录实际代码版本，不用仓库版本代替服务版本。旧版本不识别schema时阻止恢复写入。回滚先停止新领取并确认在途事务，再关闭能力入口，保留表、journal和原成果，旧只读展示；不自动drop表或恢复生产DB。
风险为DB/文件检查点窗口、并发旧fence、保留清理竞态和滚动不兼容；用故障注入、重启、SQLite/MySQL并发与真实样本验证。没有待用户决定的策略；未知环境仅在实施预检中确认。

## 实施细化

新增 `governance_operations` 与 `governance_recovery_attempts`，源 turn 和 application 身份保持。候选 baseline 同时保存 binding_revision；worker 启动前核对私有 journal、持久操作、候选身份及运行角色能力。运行心跳不进入备份，避免恢复后把旧服务声明当作在线事实。

管理员处置接口 `POST /api/v1/chat/governance-operations/{id}/retention-dispositions` 接收 expected_version 与 recheck / retain_7_days。管理员需具备该空间、仓库和对象写权限；不要求维护者冒用原会话所有者。该接口只维护本功能保护引用，七天续保不延长恢复期限；未知执行或未完成提交不释放保护，不删除共享日志、源文件或真实数据。诊断元数据按90天清理；运行角色/服务端请求链路沿既有观测结构。

重新生成入口只写草稿。明确发送新评审命令时，仅在原轮次终结、无活动 lease、没有任何原 application 且旧成果过期/被拒绝时释放原 needs_review 入场阻断；保留原候选、终态和父操作关联。已有应用或提交未知仍经原 writer 处理，不借重新生成绕过。

详情轮询以请求序号拒绝迟到响应；所有续接写入仍由用户确认触发。UI 仅投影后端能力，测试状态切换不进入正式页面。

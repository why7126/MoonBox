---
title: 需求中心卡片全命令产品链路真实化验收返修台账
change_id: add-requirement-center-command-chain-realization
source_requirement: REQ-0027-requirement-center-command-chain-realization
created_at: 2026-09-30 18:37:27
updated_at: 2026-10-13 18:12:00
owner: MoonBox 产品团队
---

# 需求中心卡片全命令产品链路真实化验收返修台账

## AF-051 多 Change 归档状态聚合

| 项 | 内容 |
|---|---|
| 验收反馈 | AC-008 独立双 Change 产品轮次中，首个 Change 已归档、第二个仍 applied，Workflow Sync 一度把 REQ 投影为 `done`。 |
| 根因状态 | confirmed；`derive_issue` 只读取第一个 `openspec_changes` 条目，忽略其余关联 Change。 |
| 调整内容 | 聚合全部可信关联 Change；仅全部归档时为 `done`，任一未归档时保持 `in_sprint`，并优先将待处理 Change 作为当前关联。 |
| 影响范围 | REQ/BUG、Sprint 派生状态与归档迁移门禁；无 API、DB、UI、部署或客户端生成变化。 |
| 验证证据 | 双 Change 单测覆盖 1/2 与 2/2；隔离项目首个 Change 归档后重跑 Workflow Sync，REQ 保持 `in_sprint`、仍在 review，Sprint 保持 planning。 |
| 观测边界 | `product_data_collection_observability` N/A：本地治理文档同步，无请求或埋点结构变化。 |

## AF-050 归档权限识别生成的来源字段

| 项 | 内容 |
|---|---|
| 验收反馈 | AC-008 正向产品轮次已具备签认及归档材料，但 Chat `archive_write` 因 Change trace 的 `requirement_id` 未识别而拒绝。 |
| 根因状态 | confirmed；Chat 归档权限预检只读取旧字段 `requirement`/`source_requirement`，与 `req-opsx` 生成字段不一致。 |
| 调整内容 | `archive_ready` 同时识别 `requirement_id`/`bug_id`，继续执行 Issue 验收与归档就绪门禁。 |
| 影响范围 | 隔离与正式产品的归档权限判定；不扩大来源对象权限，也不改变 API/DB schema。 |
| 验证证据 | 旧、新字段参数化测试 2 passed；隔离产品首个 Change 的规格合并与目录迁移成功。 |
| 观测边界 | `product_data_collection_observability` 仅既有请求日志及 Task Trace；无新增字段或保留周期。 |

## AF-049 验收清单整项签认投影

| 项 | 内容 |
|---|---|
| 验收反馈 | AC-005/006/007/009 已逐项签认后运行 `opsx.modify` Workflow Sync，旧投影把命令探针 passed 的 AC-011/012/014/015/017 等 partial 样本自动勾选，同时把样本已签认但探针暂过期的 AC-020 清空，导致卡片计数偏离事实。 |
| 根因状态 | confirmed；`issue_subdocuments` 仅按 manifest 单项探针与指纹改写 checkbox，未读取验收计划的整项样本状态，也未保留既有人工签认。 |
| 调整内容 | 清单投影要求 `required_sample.status: passed` 与当前探针通过才新增勾选；partial/pending/blocked/failed 样本保持未勾选；已签认的 passed 样本在探针暂过期时保留原勾选，等待复验。 |
| 影响范围 | Workflow Sync 的 Issue acceptance checkbox 投影；无 API、DB、Web、部署、对象存储或客户端生成变化。 |
| 验证证据 | 新增投影规则单测 2 passed；按真实样本恢复功能 AC-001～007、009、018、020 和原型 AC-PROTOTYPE-002/003 后重跑 `opsx.modify`，报告 updated=0、updated_fields=0，功能清单稳定为 10/20。 |
| REQ 子文档一致性 | 只更正 `acceptance.md` 的整项勾选投影；正文、业务流程、用户故事、trace 与 prototype 不变。 |
| 观测边界 | `product_data_collection_observability` N/A：纯本地文档状态同步，无请求、DB、事件、Task Trace 或对象存储变化。 |

## AF-048 归档验收门禁识别生成的 Issue 追踪字段

| 项 | 内容 |
|---|---|
| 验收反馈 | AC-008 正向准备发现 `req-opsx` 生成的 Change trace 使用 `requirement_id`，而归档前 `validate-issue-acceptance-ready.py` 只读取 `requirement` / `source_requirement` 等字段；此类 Change 会被误判为 standalone，可能跳过人工验收签认门禁。 |
| 根因状态 | confirmed；对 `add-isolated-connection-state-ac006` 的未修复解析相当于无来源，而其 trace 与 Issue 实际有完整 `requirement_id` 关联。 |
| 调整内容 | 归档验收门禁同时识别 `requirement_id` 与 `bug_id`；仍要求对应 Issue 唯一 acceptance 文件、`acceptance_status: passed` 与全部 AC 勾选。 |
| 影响范围 | 归档前验收门禁脚本；无 API、DB、Web、部署、对象存储或客户端生成变化。 |
| 验证证据 | `test_issue_acceptance_archive_recovery.py` 6 passed，新增 REQ/BUG 两类生成字段的缺证据、pending、passed 路径；独立 Change 当前返回 `ACCEPTANCE_GATE_BLOCKED issue_acceptance_pending checked=0 total=10`。完整 AC-008 正向归档仍待产品轮次。 |
| REQ 子文档一致性 | `acceptance.md` 归档需验收证据的要求已覆盖；其他子文档意图不变。 |
| 观测边界 | `product_data_collection_observability` N/A：纯本地归档前只读文件门禁，无请求、DB、事件、Task Trace 或对象存储变化。 |

## AF-047 OpenSpec 会话动作关联 Change 阶段门禁

| 项 | 内容 |
|---|---|
| 验收反馈 | AC-009 当前独立 API 中，无关联 Change 的 `REQ-9108` 调用 `opsx-apply`、Change 仍 `in_progress` 的 `REQ-9104` 调用 `opsx-archive` 均曾返回 200/0，会话受理与治理执行阶段不一致；未发送这两种写入轮次。 |
| 根因状态 | confirmed；对象会话预检只核对 Issue 为 in_sprint，并未核对同一完整 Issue 对应的活动 Change trace 状态。 |
| 调整内容 | 从可信 Issue trace 的 `openspec_changes` 读取活动 Change，核对 Change trace 来源与阶段；apply 仅 proposed/in_progress，modify/archive 仅 applied。直接用 Change ID 请求时核对活动 trace 阶段及 Change 的写关联；仅有只读来源关联者 403/2601，纯治理 Change 仍可在授权项目中写；阶段不符 409/2604 且不创建会话。 |
| 影响范围 | 对象会话 API 阶段拒绝；不改归档执行门禁、响应结构、DB schema、Web、部署、对象存储或客户端生成。 |
| 验证证据 | 后端新增无关联、未 applied、直接 Change ID 只读关联拒绝和阶段放行测试；候选与 scope 联合回归 62 passed。独立服务重启后的直接 API 阶段结果见 AC-009 样本；只读关联分支由聚焦测试证明。 |
| REQ 子文档一致性 | `acceptance.md` 的八动作后端阶段门禁已覆盖；其他 REQ 子文档产品意图不变。 |
| 观测边界 | `product_data_collection_observability` 仅 API 拒绝日志适用；无新增任务、Task Trace 或持久结构变化。 |

## AF-046 生成动作备用会话入口阶段门禁

| 项 | 内容 |
|---|---|
| 验收反馈 | AC-009 后端阶段矩阵发现 `/api/v1/chat/object-sessions` 对 `draft` REQ 的 `req-generate` 返回 200/0，虽然正式卡片使用 `/governance-preparations` 且未发送 Chat，该备用入口仍绕过会话准备阶段校验。 |
| 根因状态 | confirmed；对象会话白名单接受生成动作，但 `_require_issue_fact_source` 未为它们定义阶段规则，回退为普通对象解析。 |
| 调整内容 | 对象会话入口的 `req-generate` 限 `captured/exploring`，`bug-generate` 限 `captured`，均要求非空 capture 与 trace；不改变专用 candidate 生成入口。 |
| 影响范围 | 对象会话 API 阶段拒绝；无响应结构、DB schema、Web、部署、对象存储或客户端生成变更。 |
| 验证证据 | 后端新增 REQ/BUG draft 拒绝及 captured 放行测试，完整候选回归 52 passed；独立产品 API 复验中，draft `REQ-9098` 为 409/2604、captured `REQ-9199` 为 200/0，见 AC-009 样本。 |
| REQ 子文档一致性 | `acceptance.md` 的八动作后端阶段门禁已覆盖；需求正文、流程、用户故事、trace 和原型意图不变。 |
| 观测边界 | `product_data_collection_observability` 仅 API 拒绝日志适用；无写任务、Task Trace、DB 结构或客户端生成变化。 |

## AF-045 OpenSpec 对象会话正式 Sprint 范围门禁

| 项 | 内容 |
|---|---|
| 验收反馈 | AC-006 独立项目中，`REQ-9111-scope-missing` 虽标记 `in_sprint` 并指向 `sprint-010`，却未列入 `sprint.yaml` 正式 `requirements`；直接调用 `req-opsx` 对象会话 API 曾返回 200/0。未发送 Chat 轮次、未创建 Change。 |
| 根因状态 | confirmed；会话预检仅比对 registry、trace 状态及主文档，未核对 trace 的迭代归属与 Sprint 正式范围。 |
| 调整内容 | `req-opsx` 和对称的 `bug-opsx` 预检读取当前事实源的迭代 `sprint.yaml`，校验完整 ID 位于对应正式范围；缺失、非法或不一致均以 409/2604 拒绝，且不创建会话。 |
| 影响范围 | 治理对象会话 API 的既有阶段门禁；无 DB schema、Web UI、部署、对象存储或客户端生成变更。同步 API 索引说明。 |
| 验证证据 | 后端 `test_governance_candidates.py` 50 passed，新增 REQ/BUG 越界拒绝与正式范围放行测试；独立 39028 API 重启后，`REQ-9105` rejected、`REQ-9110` approved 和 `REQ-9111` 越界三路均 409/2604。正向 Change 产品轮次与文档校验记录见 `evidence/acceptance/samples/AC-006.md`。 |
| REQ 子文档一致性 | `acceptance.md` 已要求正式范围，`requirement.md`、流程、用户故事、trace 和 prototype 意图均一致，无需改写。 |
| 观测边界 | `product_data_collection_observability` 适用于 API 请求日志；拒绝发生在会话创建前，无 Task Trace、Web 事件、DB 结构、客户端生成或对象存储变化。 |

## AF-044 对象会话动作白名单

| 项 | 内容 |
|---|---|
| 验收反馈 | AC-009 隔离 `39028` 项目中，完整合成对象对未接入的 `ac009-unknown-action` 返回 200/0 和会话。 |
| 根因状态 | confirmed；`prepare_object_session` 只区分只读与写动作，未知动作落入普通对象解析并复用会话的分支，未执行动作白名单校验。 |
| 调整内容 | 在项目授权和会话创建前限定已接入只读、需求、缺陷与 OpenSpec 动作；未知动作返回 422/2604，不创建会话。 |
| 影响范围 | 已有对象会话 API 的输入校验与权限边界；不改响应字段、DB schema、Web UI、部署、客户端生成或对象存储。 |
| 验证证据 | 隔离产品失败请求与新构建复验见 `evidence/acceptance/samples/AC-009.md`；后端 `test_governance_candidates.py` 46 passed，其中新增未知动作无会话测试。重启隔离 API 后，未知动作 422/2604 且无会话，合法只读动作 200/0；会话、候选、轮次聚合数量不变。其他矩阵未齐，AC-009 不签认。 |
| REQ 子文档一致性 | `acceptance.md` 的动作白名单要求已覆盖本行为；`requirement.md`、业务流程、用户故事、trace 与 prototype 的产品意图不变，无需改写。 |
| 观测边界 | `product_data_collection_observability`：仅 API 请求日志适用；直接 API 不生成界面行为。DB、Web、Task Trace、客户端生成及对象存储 N/A，原因是入口拒绝发生在会话与任务创建前。 |

## AF-043 Capture 弹窗 Tab 焦点约束

| 项 | 内容 |
|---|---|
| 验收反馈 | AC-PROTOTYPE-005 的真实隔离页面中，Capture 浮层打开后焦点留在外部触发器，首次 Tab 跳到背景统计按钮。 |
| 根因状态 | confirmed；`CaptureDialog` 声明 `aria-modal`，但未设置初始焦点，也未处理 Tab 边界。 |
| 调整内容 | 外层浮层挂载时聚焦关闭按钮；仅在其为最上层时约束 Tab。嵌套确认弹窗同样聚焦关闭按钮并约束 Tab，取消后回到外层触发器；外层关闭后仍由父页面恢复页面触发器焦点。 |
| 影响范围 | Web Capture 键盘导航；无 API、DB、部署、安全策略或客户端生成变化。 |
| 验证证据 | 新增聚焦前端测试 2 passed；真实隔离页面在 1440px 复验外层首次与循环 Tab 均留在弹窗，Escape 回到页面触发器；嵌套删除确认在 1440/390 取消后回到外层触发器，隔离草稿 revision/state 未变、确认任务 0。截图与样式见 `evidence/acceptance/visual/AC-PROTOTYPE-005/`；AC-PROTOTYPE-005 整项仍 partial。 |

## AF-042 worker 拒绝未声明的副本模式

| 项 | 内容 |
|---|---|
| 验收反馈 | AC-020 要求本地默认 source、copy 只作为显式模式；worker 原先对缺失 `workspace_mode` 的绑定静默回退 `copy`。 |
| 根因状态 | confirmed；`platform_deployment.mapping()` 已输出 source，但 `platform_worker.main()` 的 `binding.get('workspace_mode') or 'copy'` 会为手工或旧绑定创建隐式副本。 |
| 调整内容 | worker 启动预检仅接受显式 `source` 或 `copy`；缺失或非法模式拒绝启动。部署文档说明旧绑定迁移需按场景显式补模式。 |
| 影响范围 | Chat worker 绑定预检与部署配置；不改 API、DB schema、权限授予、对象存储或客户端生成。缺失模式的旧配置需人工补全后才能启动。 |
| 验证证据 | `test_worker_requires_explicit_workspace_mode` 覆盖 source/copy/缺失三路；本地默认绑定测试与 source 产品轮次继续作为 AC-020 的正向证据。 |

## AF-041 文档抽屉关闭后焦点回归

| 项 | 内容 |
|---|---|
| 验收反馈 | AC-PROTOTYPE-005 独立已登录产品页中，关闭文档抽屉后焦点未返回 `requirement.md` 触发器；关闭新建 Capture 浮层后也未回到其触发按钮。 |
| 根因状态 | confirmed；`closeDrawer` 和 `closeCapture` 只更新浮层状态，没有保存或恢复打开时的焦点。产品观察：抽屉蒙层关闭后 `BODY` 获焦，Escape 后用户菜单获焦；Capture 蒙层关闭后 `BODY` 获焦。 |
| 调整内容 | 打开 Markdown 抽屉或新建 Capture 时记录外部触发元素；关闭并卸载浮层后，如果触发器仍在文档中，恢复焦点。HTML 新标签预览不记录抽屉触发器。 |
| 影响范围 | Web 需求中心文档抽屉键盘与蒙层关闭体验；无 API、数据库、部署、安全边界、对象存储或客户端生成变化。 |
| 验证证据 | 聚焦前端测试 2 passed、121 skipped，Web 生产构建通过；当前隔离产品 HMR 后 Escape 与蒙层关闭均把焦点返回文档或 Capture 触发按钮。脱敏记录见 `evidence/acceptance/visual/AC-PROTOTYPE-005-current/`。完整浮层矩阵仍待复验，不签认整项。 |

## AF-040 对象会话排序的 MySQL 兼容返修

| 项 | 内容 |
|---|---|
| 验收反馈 | AC-018 当前代码的独立 MySQL 8.2.0 空库矩阵首次 55 passed、31 failed。 |
| 根因状态 | confirmed；31 项失败共同触发 `_latest_object_conversation` 生成的 `NULLS LAST` 排序，MySQL 8.2 报 SQL 语法错误。 |
| 调整内容 | 以 `IS NULL` 布尔键将空时间置后，再按时间降序；保持原会话复用优先级。 |
| 影响范围 | 对象会话准备查询；无 API/OpenAPI 字段、DB schema/迁移、Web UI、对象存储、生产部署或认证体系变化。同步 API 与数据库设计说明。 |
| 验证证据 | SQLite 聚焦 3 passed；隔离 MySQL 8.2.0 空库完整矩阵复验 86 passed、1 条第三方弃用提示；测试容器已删除。AC-018 其余文档一致性审计仍单独判断。 |


## AF-039 Change 创建期间治理权限升级

| 项 | 内容 |
|---|---|
| 验收反馈 | 隔离 `req-opsx` 轮次已生成 Change 与 Sprint 关联，却在收尾时变为 `stopped / write_permission_revoked`。 |
| 根因状态 | confirmed；Change 建立后同一对象从 `governance_write` 变为 `implementation_write`，执行监控要求当前权限档位与启动时完全相等，把权限升级误判为撤销。 |
| 调整内容 | 仅当当前策略确认为同一对象的 `implementation_change_in_sprint` 时，保留本轮启动时已获准的较窄治理沙箱直到轮次结束；权限降级、只读或归档档位变化仍拒绝。 |
| 影响范围 | Chat 运行中权限监控；无 API/DB schema、UI、部署或客户端生成变化。安全边界仍以启动时治理写沙箱为限。 |
| 验证证据 | 权限档位聚焦测试通过；隔离创建轮次 `a1c2475e-d4f4-4fb1-9804-0bfaadf241c5` 中断后，修复代码加载的新 worker 处理幂等恢复轮次 `7dbf9836-33bc-4c54-8458-f54a1ad592db`，终态 completed，未重复创建 Change，事实源和卡片进入待开发。尚缺新的单轮无中断创建产品样本。 |


## AF-038 评审目录迁移窗口与拒绝回退

| 项 | 内容 |
|---|---|
| 验收反馈 | 两个独立隔离产品轮次在 plan→review 迁移后变为 `unknown`，候选仍 `running`；后续轮次虽能完成，评审范围拒绝后却未恢复 plan 文件。 |
| 根因状态 | confirmed；授权历史读取在注册表尚指向 plan 时无法解析已迁移的同一对象。拒绝回退使用 `create_parents=False`，无法重建被删除的 plan 目录；恢复失败错误码又被评审拒绝原因覆盖。 |
| 调整内容 | 对已授权同一对象增加精确 plan→review 路径回退；恢复基准文件时安全重建其父目录；保留 `source_recovery_blocked` 错误优先级。日志只记录异常类型。 |
| 影响范围 | 对象 Chat 历史读取、source 模式评审收尾和脱敏诊断；无 API/DB schema、UI、部署、安全策略或客户端生成变化。 |
| 验证证据 | 第四隔离轮次 `6142a574-933f-4659-9daf-04ddd7a623be` 迁移期间历史读取成功。第五独立轮次 `73d4c7b6-f8e2-4e4d-bd7b-1404ba6be28f` 触发越界改动拒绝，候选无应用，前置 1926 个文件逐字节恢复，刷新后卡片仍在待评审。新增目录迁移拒绝回退测试及相关后端回归 62 passed。补齐隔离夹具 requirement.md 的 P2 分级后，轮次 `7375c67f-7a15-4fe0-a5bf-1b4cbf14f9fc` 候选与应用均为 applied / verified，事实源和卡片进入已评审；拒绝、延后和取消分支仍待验收。 |


## AF-037 完善需求拒绝规则诊断

| 项 | 内容 |
|---|---|
| 验收反馈 | `req-complete` 候选仅返回通用 `governance_validation_failed`，无法定位独立产品轮次的拒绝分支。 |
| 根因状态 | confirmed；完成校验器内部抛出固定规则标识，候选收尾未映射到脱敏错误码。 |
| 调整内容 | 完成校验器仅向控制器传递固定规则名；解析器异常统一折叠为 `document_format`，候选错误码写为 `completion_<reason>`，不外传文档内容。 |
| 影响范围 | REQ/BUG 完善候选的诊断错误码；无数据库结构、权限、部署或客户端生成变化。 |
| 验证证据 | 后端聚焦回归 2 passed；真实隔离轮次 `9e417e13-a227-434f-865d-fda8bdb20d48` 明确返回 `completion_knowledge_refs`，即 trace 的 `knowledge_base_refs` 非列表。新隔离对象的轮次 `9cb22262-60ba-412f-a9c5-52eeafa617cd` 候选 `applied`、应用 `verified`，事实源与页面均进入待评审。 |


## AF-036 source 模式拒绝候选回退

| 项 | 内容 |
|---|---|
| 验收反馈 | 独立副本 `req-complete` 候选因越界 trace 字段被拒绝，无应用记录，但 source 事实源及需求卡片已推进到待评审。 |
| 根因状态 | confirmed；执行器在 source 工作树直接写入，`collect()` 校验失败后只拒绝候选，没有恢复被拒绝轮次的治理文件。 |
| 调整内容 | 拒绝候选时在项目锁内核对工作区快照，只对同轮变更的治理文件按前置字节进行安全回退；若存在并发修改、非治理文件差异或回退不完整，标记 `source_recovery_blocked`。Chat 被拒绝轮次的助手原文默认折叠，并显示未通过校验的事实源结论。 |
| 影响范围 | 后端 source 模式治理候选失败收尾与 Web Chat 历史消息展示；不修改 API、DB schema、客户端生成或部署策略。 |
| 验证证据 | 后端相关测试 99 passed；前端消息、Chat 工作台与治理测试 42 passed，TypeScript 与生产构建通过。独立产品轮次 `4c3bb66b-3671-4669-9b55-7f902cb824ee` 的候选 rejected，trace/注册表回到 draft，新增文档消失，卡片仍在规划中；刷新后的 Firefox Chat 默认折叠错误成功话术并显示拒绝摘要。第二次完善轮次亦被校验拒绝且安全回退，成功路径仍未通过。 |

## AF-035 HTML 预览对象 URL 延时清理兼容

| 项 | 内容 |
|---|---|
| 验收反馈 | REQ-0027 前端聚焦回归首次运行出现 121/122 通过及一个未捕获异常：测试环境缺少 `URL.revokeObjectURL`，HTML 预览延时清理直接调用该方法。 |
| 偏差证据 | 首轮 Vitest 退出 1；异常定位到 `RequirementCenterPage.tsx` 的预览关闭延时回调。相邻 HTML 预览分支已有可选调用，受影响分支未保持一致。 |
| 影响范围 | Web 需求中心 HTML 文档预览的对象 URL 清理；不改变用户可见交互、API、DB、权限、部署、对象存储或客户端生成。 |
| 根因状态 | confirmed；失败堆栈与代码分支一致。 |
| 调整内容 | 弹窗被拦截时和延时清理时均在 API 存在的情况下调用 `URL.revokeObjectURL`，避免测试或不完整浏览器实现抛异常。 |
| 验证证据 | `NODE_OPTIONS=--no-experimental-webstorage npm --prefix src/web test -- --run src/requirement-center.test.tsx`：122 passed，退出 0；后端候选、writer、review 测试分别为 42、14、56 passed。 |
| 其他文档 | 纯实现兼容修复，不改变验收标准、原型意图、业务流程或用户故事；REQ 子文档、Change 规格、API/DB/部署/安全文档无需更新。产品视觉矩阵仍待独立验收。 |


## AF-033 事实源唯一完成门禁

| 项 | 内容 |
|---|---|
| 验收反馈 | Chat 工作台和需求中心动作必须以治理事实源为唯一完成依据；工作区、assistant 输出和 candidate 只能作为候选或执行证据。 |
| 方案选择 | 方案 B：事实源唯一，工作区是候选沙箱。 |
| 偏差证据 | 代码路径确认 `governance.writer.process()` 已校验 manifest、binding revision 和最终文件集合，但应用成功前缺少统一的 Workflow Sync 后置门禁和同步后事实源重读记录。 |
| 影响范围 | 后端治理候选应用流程；REQ/BUG generate、complete、review 类候选写入完成语义；不新增 API、DB、权限、部署或对象存储边界。 |
| 根因状态 | confirmed。证据来自 `src/backend/app/governance/writer.py` 应用流程和新增聚焦回归。 |
| 调整内容 | 在 writer 层对可映射到 REQ/BUG 生命周期事件的治理写入执行 Workflow Sync；同步成功后重读事实源并记录派生 hash；同步失败时不进入 `applied`，保留待恢复状态和原 candidate。 |
| 失败语义 | 若 Workflow Sync 失败、事实源版本变化或外部修改冲突，应用不得展示成功，不得更新卡片阶段；已落盘文件保留为恢复证据。 |
| 验证证据 | `uv run pytest src/backend/tests/test_governance_writer.py src/backend/tests/test_requirement_completion_recovery.py`，25 passed。新增测试覆盖 sync 成功才 applied、sync 失败不 applied。 |

## AF-034 本地部署默认 source 工作区

| 项 | 内容 |
|---|---|
| 验收反馈 | MoonBox 空间当前产品策略实际为 `copy`，会带来会话副本空间占用和事实源漂移；用户要求本地部署默认推荐并使用 `source`。 |
| 偏差证据 | `platform_deployment.mapping()` 未输出 `workspace_mode`，而 `platform_worker` 使用 `binding.get('workspace_mode') or 'copy'`，导致本地常驻部署默认进入 copy；当前运行数据已有 `data/runtime/chat-platform/workspaces` 副本约 473M。 |
| 影响范围 | 本地常驻部署仓库绑定、Chat 执行工作区选择、部署/API 文档、REQ 验收标准和 Change 规格；不新增 API schema、DB schema、权限、对象存储或生产共享部署拓扑。 |
| 根因状态 | confirmed。证据来自代码默认分支、部署映射和本地运行副本目录统计。 |
| 调整内容 | `platform_deployment.mapping()` 默认写入 `workspace_mode: "source"`；本地受信任部署直接以 `source_root` 当前工作树为执行工作区。`copy` 保留为共享、多人或强隔离场景的显式模式。 |
| 失败语义 | source 模式仍保留单 worker 串行、成员写权限、对象状态门禁、产物 allowlist、manifest/revision 校验、请求日志和 Task Trace；不得在共享生产或多人同时编辑场景默认启用。 |
| 验证证据 | `uv run pytest src/backend/tests/test_chat_platform.py::test_platform_deployment_defaults_local_binding_to_source_mode src/backend/tests/test_governance_candidates.py::test_source_workspace_mode_generate_writes_directly_without_second_apply -q` 通过，覆盖本地绑定默认 source 与 source 模式直接落盘、不走副本二次应用。 |

## AF-045 AC-001 分析轮次权限与完整 ID

| 项 | 内容 |
|---|---|
| 验收反馈 | captured/exploring 分析 Chat 显示“治理可写”，且卡片预填短编号；不能签认只读分析。 |
| 根因证据 | 隔离产品 captured 轮次的执行器权限事件为 `governance_write / governance_object_writable`；需求中心辅助动作以卡片短 `id` 构造命令。该轮治理文件未变化不能替代权限证明。 |
| 调整内容 | 服务端对 captured/exploring 的 REQ/BUG 普通对象会话返回 `read_only / analysis_object_read_only`；受控候选运行态仍经对象、操作者和绑定版本校验后临时写入。需求中心分析命令从卡片主动作提取完整对象 ID；Chat 标识“只读分析”。 |
| 影响边界 | 会话权限原因值和 UI 文案更新；未新增 API 字段、数据库表、部署或对象存储行为。安全规则与 API 索引同步说明。 |
| 验证 | 后端聚焦回归及候选运行态回归通过、前端聚焦回归 2 项和 Web 构建通过。隔离产品 captured、exploring、缺主动作材料、生成与归档反例共五类轮次均确认只读，治理树前后 SHA-256 零差异；当前构建整项证据见 `evidence/acceptance/samples/AC-001.md`。 |

## AF-046 AC-002 探索态生成门禁

| 项 | 内容 |
|---|---|
| 验收反馈 | exploring 对象卡片允许“生成需求”，但 `governance-preparations` 返回 409/2604；候选校验也仅认可 captured 起点。 |
| 根因证据 | 独立隔离对象 `REQ-9099-isolated-readonly-analysis` 的 trace 与 registry 为 exploring，capture/trace 非空；同一对象准备接口仍报“需处于采集池”。 |
| 调整内容 | 准备接口与候选结果校验接受 captured/exploring 起点；完成态仍须 draft，候选写入仍限制目标主文档、trace、registry 和 CHANGELOG。 |
| 影响边界 | REST API 阶段门禁扩展，与 REQ-0027 已批准验收口径一致；不改变权限身份、数据库结构、UI、部署或对象存储。 |
| 验证 | 后端候选回归 47 项通过，前端命令草稿聚焦回归 2 项通过、Web 构建通过；captured 与 exploring 独立产品轮次均 applied，目标业务文件集、状态和文档重读通过，整项证据见 `evidence/acceptance/samples/AC-002.md`。 |

## AF-047 AC-011 持久写入器同步阶段恢复

| 项 | 内容 |
|---|---|
| 验收反馈 | 七写动作在写前、部分落盘和同步前后故障时须区分状态、重启后按事实恢复，不盲目重放已完成步骤。 |
| 偏差证据 | 隔离写入器故障注入初跑：`req-generate`、`req-complete`、`req-review` 的同步已完成但终态未提交时，同步各被调用两次；同步中途异常后也可能重入。 |
| 根因状态 | confirmed；`writer.process()` 之前只在同步返回后记录结果，没有恢复时验证该结果并跳过重放，也未在同步前持久化输入 hash。 |
| 调整内容 | 写入器在同步前持久化 `syncing` 与输入 hash；同步完成后记录事件、对象与结果 hash。重启时若完成标记和当前文件 hash 一致，原子提交候选、锁与应用终态；同步状态不明且文件已变则阻断并保留现场。 |
| 验证 | 隔离 `copy` 模式三动作 × 写前、首文件后、同步前、同步完成后及部分同步场景；相关 91 项后端回归通过。矩阵见 `evidence/acceptance/samples/AC-011-fault-matrix.json`。 |
| 剩余范围 | 本地默认 `source` 模式绕过该 writer；`sprint-propose`、`req-opsx`、`opsx-apply`、`opsx-archive` 由 Chat 命令直接写文件，尚无相同矩阵。AC-011 保持未签认。 |
| 边界与文档 | 未改变 API、DB schema、UI、部署、权限或对象存储；既有 REQ 业务流程和 Change 规格已要求同步门禁与恢复，故本轮只补测试、返修台账、验收样本和任务缺口。 |

## AF-048 AC-011 已终态候选的重启收尾

| 项 | 内容 |
|---|---|
| 偏差证据 | 默认 source 模式的 Chat 轮次在外部终态确认后，若 worker 在 `collect` 前退出，候选仍为 running；原重启扫描只恢复 Chat 终态，不补候选收尾。 |
| 根因状态 | confirmed；`reconcile_unknown` 和正常 `run_claim` 的收尾之间没有针对已终态候选的持久恢复入口。 |
| 调整内容 | 两类 worker 每轮扫描已绑定终态的 running 候选，仅在会话无活动轮次时读取既有工作区并执行一次 `collect`；候选转终态后重复扫描无效，不重新启动外部轮次。扫描故障保留 running，记录脱敏原因类别。 |
| 验证 | 定向重启窗口测试和相关后端回归 201 passed、1 skipped；定向测试确认重复扫描只有一个应用记录。 |
| 剩余范围 | source 模式逐动作的写前、部分落盘、同步前后注入，以及四个直接 Chat 命令的阶段记录和重启恢复仍缺证据；AC-011 保持未签认。 |
| 边界与文档 | 仅修改 worker 内部恢复和测试，不改变 API、DB、UI、部署、权限及对外规格。REQ 子文档一致性扫尾：现有 requirement、业务流程、用户故事、acceptance、trace 与 prototype 不需要改变行为描述；本项只补实现内部恢复证据。 |

## AF-049 AC-011 默认源工作区非完成轮次恢复

| 项 | 内容 |
|---|---|
| 偏差证据 | 独立隔离项目的真实 `req-generate` 轮次 `2aa5fecb-7d9a-445f-9091-8fe88456e451` 在首份 `requirement.md` 落盘后强制终止 worker；重启确认为 stopped，候选 rejected / executor_unavailable，但 requirement 与 trace 仍有差异。安全手动恢复后，完整治理快照与该轮不可变基线逐字节一致。 |
| 根因状态 | confirmed；`collect` 在读取 baseline 前遇到非完成终态即抛错，异常分支因 baseline 为空跳过 `_restore_rejected_source`。 |
| 调整内容 | 先读取不可变 baseline，再判断终态；停止或失败的 source 候选对实际文件逐字节核对并安全恢复；未知外部编辑保留现场且标记 `source_recovery_blocked`。 |
| 验证 | 首次定向测试复现残留，修复后通过；三候选动作 × 写前、首文件、同步前、部分同步、同步后、未知外部编辑共 18 项 source 隔离注入通过；相关后端回归 206 passed、1 skipped。第二条修复版真实轮次 `86246c55-cc81-443b-a0a9-fde622da682e` 在首文件前执行器失败，不能充当修复版产品故障复验。 |
| 剩余范围 | 四个直接 Chat 命令尚无逐阶段持久步骤记录与恢复矩阵；修复版真实 source 首文件故障轮次未取得。AC-011 不签认。 |
| 文档与一致性 | Change design 增补 source 安全恢复门禁。REQ 既有 requirement、业务流程、用户故事、acceptance、trace 与 prototype 中，只有 acceptance 增补本轮事实；其余仍与设计一致。无 API、DB schema、UI、部署、权限或对象存储边界变化。 |

## AF-050 AC-011 四直接命令步骤分类

| 项 | 内容 |
|---|---|
| 偏差证据 | 四条历史成功产品轮次只有命令基线，没有各步落盘记录；故障后不能区分同步完成与部分写入。 |
| 调整内容 | 四个直接命令新增私有 hash 步骤记录、同步退出码判定及重启终态分类；未知来源差异阻断，已完成同步仍标为业务待核验，不自动重放。 |
| 验证 | 4×6 故障窗口与同步失败额外场景通过；扩展回归 172 passed、1 skipped。真实产品轮次及动作语义恢复门禁尚未完成。 |
| 一致性 | 仅增私有步骤摘要，不改变 API、DB schema、UI、部署、权限或对象存储边界。REQ 文档仅 acceptance 追加状态说明，requirement、业务流程、用户故事和 prototype 无行为改动。 |

## AF-051 AC-011 候选轮次日志缺席与真实首文件恢复

| 项 | 内容 |
|---|---|
| 偏差证据 | 两条全新隔离候选轮次在首个只读工具后停止，未到写入窗口；日志观察钩子对没有直接命令私有记录的候选动作抛出 `WorkspaceError`。 |
| 调整内容 | 缺少四直接命令操作目录时不记录步骤，保留危险目录仍由私有存储校验拒绝。 |
| 验证 | 回归 78 passed、1 skipped；修复版隔离 `REQ-9204` 真正写入首份 4,682 字节业务文档后中断 worker，重启确认 stopped / rejected、零应用、文件清除，全治理树与不可变基线 2,212 文件逐字节一致。 |
| 剩余范围 | 该轮只覆盖 `req-generate` 首文件窗口；七动作其他窗口及四直接命令的真实产品恢复仍缺，AC-011 不签认。 |
| 一致性 | 无 API、DB schema、UI、部署、权限、对象存储边界变化。REQ 子文档仅 acceptance 增补取证事实；原需求行为未变。 |

## AF-052 AC-011 其余真实故障窗口与 Change 控制文件快照

| 项 | 内容 |
|---|---|
| 偏差证据 | 真实 `req-opsx` 首文件中断后，治理快照遗漏同一 Change 的 `.openspec.yaml` 控制文件；同时七动作的产品中断窗口仍未覆盖完整矩阵。 |
| 调整内容 | 快照读取纳入活动 Change 目录直属 `.openspec.yaml`，保留其他点文件排除；在独立隔离项目新增七动作写前、部分落盘、同步中/后轮次与重启观察。 |
| 验证 | 控制文件回归先红后绿；相关后端回归 156 passed、1 skipped。真实轮次详见 `evidence/acceptance/samples/AC-011.md` 与两份 `20261014.json` 摘要。 |
| 剩余范围 | 七动作各窗口未齐；归档在规格合并与目录迁移后中断，私有日志安全阻断并保留部分现场，尚无安全续做证明。AC-011 不签认，12/20 不变。 |
| 一致性 | 仅治理快照与验收证据变化；无 API、DB schema、UI、部署、安全权限、对象存储或客户端生成变化。REQ 子文档仅 `acceptance.md` 增补事实，其余需求与原型意图不变。`product_data_collection_observability` N/A：不新增请求日志、事件、Task Trace 字段或保留周期。 |

## AF-053 AC-011 归档部分现场安全续办与 Sprint 范围解析

| 项 | 内容 |
|---|---|
| 偏差证据 | 隔离归档现场已合并规格、迁移 Change，但首轮 worker 中断使后置校验未完成；`archive-change.sh --finalize` 的自动 Sprint 定位漏读合法的无缩进 YAML 列表。后续 `sprint-propose` 轮次还生成无效 Sprint YAML，虽 Sync 返回成功。 |
| 调整内容 | 核对唯一归档目录与规格 hash 后执行既有恢复分支，未再次合并；Workflow Sync 对 Sprint 使用完整 YAML 解析，接受合法无缩进列表，语法无效时返回错误。无效 Sprint YAML 仅在保留失败事实后修正隔离样本，不将该产品轮次记为通过。 |
| 验证 | 归档脚本后置检查通过，正式规格 hash 前后一致、归档目录唯一；显式同步零错误，修复后原列表样式自动定位成功；Workflow Sync 聚焦回归 20 passed。新增真实写前轮次及 `req-opsx` unknown 状态见 AC-011 样本。 |
| 剩余范围 | `req-opsx` 外部轮次仍 unknown，中止 API 409/2506；同源后续写操作暂停。七动作各阶段矩阵与无效 Sprint YAML 的新产品轮次复验仍缺，AC-011 不签认，12/20 不变。 |
| 一致性 | 仅 Workflow Sync 解析、测试与验收材料变化；无 API、DB schema、UI、部署、安全权限、对象存储或客户端生成变化。REQ 子文档仅 `acceptance.md` 增补，不改原需求行为。`product_data_collection_observability` N/A：未新增请求、Task Trace 或留存字段。 |

## 附件截图逐项视觉对照表

## AF-055 AC-012 规格合并中断后的防重复续做

| 项 | 内容 |
|---|---|
| 偏差证据 | `AC-012-merge-window-injection.json` 证明旧归档脚本在规格已合并、Change 尚未迁移时会再次调用 OpenSpec，脚本级夹具产生重复规格条目。 |
| 调整内容 | `archive-recovery-guard.py` 在临时副本运行 OpenSpec 预览，以 SHA-256 私有日志记录活动 Change、原规格和预期规格；重试按文件事实选择正常合并、仅迁移或阻断未知编辑。归档后进入同步前再次核对预期规格；产品容器不允许写普通诊断目录，故指纹改放归档权限内的忽略目录，并要求技能在归档命令后不直接编辑正式规格。 |
| 验证 | 真实 CLI 的隔离分段现场中，已合并规格重试选择 `--skip-specs`，目标条目一份；Sync 在 trace 写入后中断可续跑至零差异；Issue 目录移动后中断可识别唯一归档目录；外部编辑返回 `ARCHIVE_RECOVERY_BLOCKED` 并保留文件与日志。归档/Issue 回归 27 passed。真实隔离产品轮次的归档命令退出 0，但模型随后直接修改正式规格；重试护栏阻断并保留现场。详见 `evidence/acceptance/samples/AC-012.md`。 |
| 剩余范围 | 四阶段尚未全部取得完整产品对象 Chat 中断及重进轮次；AC-012 保持 partial，不签认。 |
| 一致性 | 变更仅涉及归档治理脚本、回归和验收资料；无 API、DB schema、UI、部署、安全权限、对象存储或客户端生成变化。`product_data_collection_observability` N/A：未新增采集字段、日志正文或 Task Trace。 |

## 附件截图逐项视觉对照表

## AF-054 AC-011 第二隔离项目的正式同步窗口

| 项 | 内容 |
|---|---|
| 偏差证据 | 四直接命令的私有日志把 `--dry-run` 同步记作成功；原隔离项目的 `req-opsx` 轮次长期 unknown，不能安全重放。 |
| 调整内容 | 正式同步识别排除 dry-run/check；在第二独立隔离项目采集七动作的新写前、同步中和同步后轮次，对部分现场先核对身份、文件和版本，再只续做目标 Sync，不重放模型。 |
| 验证 | `req-opsx` 部分同步与归档迁移后的两个现场均安全续做；后者规格哈希不变、归档目录唯一。第二隔离项目另有一次归档成功路径，但未注入中断。逐轮证据见 `evidence/acceptance/samples/AC-011.md`。相关 Chat/日志回归 83 passed、1 skipped。 |
| 剩余范围 | 七动作写前、部分文件、同步前后完整矩阵仍缺归档正式同步中断等格子；无效 Sprint YAML 修复后尚缺新产品轮次。AC-011 不签认，12/20 不变，不重跑完整验收。 |
| 一致性 | 本轮只改内部日志分类、Workflow Sync 解析、测试和验收材料；无 API、DB schema、UI、部署、安全权限或客户端生成变化。`product_data_collection_observability` N/A：未新增请求采集、Task Trace 或留存字段。 |

## 附件截图逐项视觉对照表

本次反馈不包含 UI 截图、标注图、原型截图或实际页面视觉偏差；返修范围为后端完成语义、事实源门禁和本地部署工作区策略，不触发视觉对照表。

## REQ 子文档一致性扫尾检查

| 子文档 | 结论 | 原因 |
|---|---|---|
| `requirement.md` | 已更新 | 补充工作区/candidate/assistant 只能作为候选或证据，完成态以 Workflow Sync 和事实源重读为准。 |
| `business-flow.md` | 已更新 | 补充写操作顺序中的 Workflow Sync 后置门禁、事实源重读和失败恢复语义。 |
| `acceptance.md` | 已更新 | 新增事实源唯一完成门禁验收项。 |
| `trace.md` | 由 Workflow Sync 投影 | 生命周期与事件行通过 `opsx.modify` 同步维护。 |
| `prototype/web/**` | 无需更新 | 本次不改变页面布局、浮层、selector、视觉样式或 Mock/API 边界。 |
| `user-stories.md` | 无需更新 | 用户目标不变，变化为完成判定与恢复门禁强化。 |
| `requirement.md` | 已更新 | AF-034 补充本地部署默认 source、copy 作为显式隔离模式。 |
| `acceptance.md` | 已更新 | 新增 AC-020 验收本地部署默认 source 策略。 |
| `business-flow.md` | 已更新 | AF-034 补充本地常驻部署默认 source 的写操作路径，以及 copy 的适用边界。 |

## 文档未更新项与原因

| 文档 | 结论 | 原因 |
|---|---|---|
| `docs/03-api-index.md` | 已更新 | 补充本地默认 source、copy 显式隔离模式下 `workspace_fact_source_stale` 语义。 |
| `docs/04-database-design.md` | 无需更新 | 未新增或修改数据库表、字段、索引、迁移或保留周期。 |
| `docs/02-deployment.md` | 已更新 | 补充本地常驻部署默认 source，copy 作为共享/强隔离显式模式。 |
| 部署环境变量示例 | 无需更新 | 未新增环境变量；变更为后端绑定生成默认字段。 |
| 对象存储文档 | 无需更新 | 未涉及对象存储或媒体路径。 |
| 安全文档 | 无需更新 | 未放宽鉴权或权限边界，仍使用既有项目授权与 writer 门禁。 |

## AF-056 AC-012 四个产品归档中断窗口与规格完成门禁

| 项目 | 记录 |
|---|---|
| 偏差证据 | 前次隔离产品归档命令成功后仍直接改写正式规格；Change 迁入 OpenSpec 过渡目录时，原产品对象无法重进；Issue 已迁移后，关联 REQ 的后置归档轮次被活动 Change 门禁拒绝。 |
| 返修 | `src/backend/app/chat/execution.py` 在提交 Chat 终态及 unknown 恢复时核对预期规格指纹；`direct_command_journal.py` 将漂移分类为 `blocked_archive_spec_drift`。`relations.py`、`policy.py`、`preparation.py` 只对有匹配私有日志、来源身份和规格指纹的过渡/已归档现场开放原对象安全重进。归档脚本的实际文件续做仍由既有 `archive-recovery-guard.py` 决定。 |
| 隔离产品证据 | 四个独立产品对象在规格合并、Change 迁移、Workflow Sync、Issue 迁移后被测试停点中断；原轮次均 stopped，再次进入同对象的恢复轮次均 completed，正式归档目录唯一、规格指纹与各自准备结果一致。另一个后置规格漂移样本命令退出 0、产品轮次 failed / `archive_recovery_blocked`，文件和日志保留。脱敏摘要见 `evidence/acceptance/samples/AC-012-product-four-windows-and-completion-gate-20261016.json`。 |
| 边界 | 测试停点只在独立隔离项目的归档脚本内，未加入正式仓库脚本；完整产品轮次与脚本级夹具分层记录。多 Change 部分归档未提前 done 的既有产品证据见 `evidence/acceptance/samples/AC-008.md`。 |
| 文档与采集 | `docs/03-api-index.md` 已补既有 Chat 终态字段语义，`rules/security.md` 已补受控重进权限门禁；DB、UI、部署、安全角色与客户端生成无需变更。`product_data_collection_observability`: status=not_applicable，affected_layers=[]，原因是仅复用现有 Chat 轮次状态/error_code 与私有 hash 日志，不新增请求日志、usage_events、Task Trace、行为埋点或采集字段；validation 为产品轮次、文件指纹、权限门禁与回归测试。 |
| 验收 | AC-012 四窗与未知修改阻断整项通过，单项签认；其余 AC 保持原状态，完整验收仍须据各项事实报告 readiness。 |

## AF-057 AC-011 Sprint 完成门禁返修

| 项 | 内容 |
|---|---|
| 偏差证据 | 隔离产品轮次 `8aa39956-c4ea-4428-a807-a315298eb193` 的正式同步退出 0，但 Sprint YAML 列表缩进无效，Chat 仍可能报告完成；旧 `req-opsx` 轮次精确外部事实不可读取，继续保持 unknown。 |
| 调整内容 | `sprint-propose` 在 Chat 完成提交和可信 unknown 终态恢复时重读 Sprint 源文件，检查 YAML、Sprint 身份及目标 Issue 正式范围；失败返回固定 `sprint_source_invalid` 并保留文件。私有日志分类为 `blocked_invalid_sprint_source`。不根据时间或外部轮次缺失强制结束旧 unknown。 |
| 验证 | 聚焦后端 `test_ac011_direct_command_journal.py` 与 `test_chat.py`：88 passed、1 skipped；相关恢复测试 23 passed。新增无效 YAML、缺正式范围与有效 Sprint 对照。验收器新增 `required_sample.status` 门禁，21 项回归通过；聚焦诊断 `20261017081303746139-e4eb3609` 的 AC-011 为 `blocked / sample-incomplete`。完整验收 `20261017081405723872-4df67216` 为 21 passed、7 blocked，AC-011 明确阻断。隔离服务健康探测当前不可连接，尚无修复版真实产品轮次。 |
| 剩余范围 | 需在独立隔离产品重启修复版 Worker，取得无效 Sprint YAML 的失败轮次及 `req-opsx` 新写前中断的安全状态；其余七动作故障格子逐项核对后才签认 AC-011。 |
| 一致性 | 复用既有 Chat `status/error_code` 字段，无 DB schema、UI、权限、对象存储、部署或客户端生成变化；`docs/03-api-index.md`、`docs/standards/opsx-acceptance.md` 已同步。`product_data_collection_observability` 适用 Chat Task Trace，但本次无新增采集字段或正文，验证固定错误码与脱敏私有分类。 |

### AF-057 产品复验结论

隔离环境 API/Worker 重启并确认 Chat ready 后，`req-opsx` 新写前轮次 `9b249258-944e-4708-a264-543b64c4cb57` 在零步骤与事实源基线一致时中断，重启为 stopped / no_governance_write；部分写入轮次 `f623dfdc-1742-49b8-915a-70eea82f5d6f` 为 stopped / partial_write，文件保留且 0 个正式同步步骤。`sprint-propose` 新轮次 `a2593400-4dce-4f8c-8f36-053fa3f880f2` 自身生成无效 Sprint YAML，正式同步记录成功，但产品终态 failed / sprint_source_invalid、私有日志 blocked_invalid_sprint_source。保存原无效文件 SHA-256 后，仅修正独立样本的两个列表缩进；未把事后修正写成产品自动回滚。旧外部轮次仍 unknown，不推断终态或重放。脱敏轮次及 28 格映射见 `evidence/acceptance/samples/AC-011-product-recovery-20261017.json`、`AC-011-matrix-audit-20261017.json`；AC-011 整项签认，Change 总体就绪另由完整验收决定。

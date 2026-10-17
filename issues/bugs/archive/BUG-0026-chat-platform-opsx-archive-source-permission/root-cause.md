---
bug_id: BUG-0026-chat-platform-opsx-archive-source-permission
title: Chat 平台无法归档 source 工作区 Change 且状态未知根因分析
created_at: 2026-10-04 11:11:31
updated_at: 2026-10-10 11:48:55
status: confirmed
---

# Chat 平台无法归档 source 工作区 Change 且状态未知根因分析

## 根因状态

status: confirmed

## 现象

新增范围：宿主工作区的 `openspec/archive/`、`openspec/changes/`、`openspec/specs/`、`docs/spec-logs/` 下各有一对空 `.agents`、`.codex`。现有 worker 清理和目录校验仅覆盖 `issues/`、`iterations/`；这直接确认全仓治理缺口。同款执行器镜像的离线隔离探针已直接观察归档 profile 在六个写入根下形成 12 个空工具路径；退出后宿主清理使其全部不存在。新八路径的历史创建轮次仍无法追溯，不把隔离复现等同于该轮次的原始日志。

AF-010：17:33 产品重试原始 execution.tool 再次显示标准脚本在目录校验处 exit 1。`shell_environment_policy.inherit="none"` 使前版判定依赖的 `CODEX_HOME` 不进入命令环境；沙箱执行还会在宿主生成四个空目录，不能仅用独立设备挂载来识别。改为私有 Chat 命令标记，并在 worker 归档前后清理四个空残留，继续拒绝非空目录和符号链接。

AF-009：REQ-0043 产品归档轮次的用户截图显示规格已合并、Change 已移动，而执行沙箱的四个空工具目录使目录校验失败，`rmdir` 返回 `Device or resource busy`；宿主同名路径不存在且宿主校验通过。同款归档沙箱的隔离探针复现四个独立设备的空挂载点，退出后宿主不存在这些目录，并确认沙箱拒绝读取 mountinfo。隔离反例证实真实空目录会被同类挂载遮蔽，必须在沙箱启动前检查真实工作区。可确认执行时挂载被误判为仓库残留，归档脚本在移动后、Workflow Sync 前被阻断；不推断执行器内部的具体挂载实现。

AF-008 补证：BUG-0027 已进入执行器后，Path.rename 跨挂载失败（Errno 18）；补救后 archive 已存在，但 Issue 仍 in_sprint，轮次被 reconcile 为 stopped。代码另确认 archive 写策略只读取 active trace，移动后会撤销归档权限；回归证明该路径。历史 stopped 是否仅由此触发仍需执行端日志，不将其唯一来源写为 confirmed。

修复方向：标准脚本优先、跨设备安全移动、唯一 archive 身份权限重检、半归档串行验证/sync/promote，以及已完成命令和可信 accounting 收据恢复。完整证据与验证见 Change `acceptance-fixes.md` AF-008。

产品补证：轮次 `2f62925a-2eb6-4731-9914-92328ef1e0d1` 已推进 BUG-0027 Issue promote，但进入 execution_access_or_workspace_error。代码与回归确认 promote 先移目录、后更新 registry 期间，对象解析仍访问旧 review 路径。修复为既有 ACL 授权后读取唯一同身份 archive 目录；旧轮次无权威最终收据，不伪造成功或结算用量。

进一步产品补证：标准脚本第一次因 AI Usage 自动发现调用 Path.home 在无 HOME 容器报错；修复后下一轮标准脚本 exit_code=0，但 Chat 报 executor_buffer_limit。接收队列仅允许 128 条、满一秒后退出，慢消费者回归证实终态和用量可因此无法消费；修复为维持有界内存的可关闭背压等待。它是新复验轮次的已证实错误来源，不反推历史 stopped 的唯一原因。

Chat 工作台执行 `/opsx-archive REQ-0039-requirement-center-card-chat-session-reuse` 后没有归档事实源。第一次执行端已明确报告归档权限与工具链阻塞；第二次重试在 setup 阶段进入 unknown，前端只能提示“暂无法确认执行状态”。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | runtime_db | `chat_turns` | 2026-10-04 10:55:31 对应 turn `2ba76ae6-c0ad-4f30-a2d1-b8b10486e15c` 为 `unknown`，`error_code=platform_execution_setup_failed`，`executor_turn_id` 为空 | 重试未进入 Codex runtime，失败发生在执行 setup 层 |
| E2 | runtime_db | `chat_events` | 该 turn 事件数为 0 | setup 失败没有记录执行轨迹，用户只能看到 unknown |
| E3 | runtime_history | Codex thread history | 上一轮 archive final answer 明确写出：禁止写入 `openspec/specs/` 和 `openspec/archive/`、Change 身份校验被 `.agents/.codex/.git` 阻断、OpenSpec CLI 不可用 | 归档未完成的业务阻塞已由执行端确认 |
| E4 | compose_config | Docker Compose 渲染 | `MOONBOX_CHAT_REPOSITORY_BINDINGS` 包含 `workspace_mode: "source"`，但 chat-worker 将源仓库挂载为 `read_only: true` | source 模式的“直接写真实仓库”与容器挂载权限冲突 |
| E5 | code_path | `src/backend/app/chat/container_server.py` | `moonbox-governance` 权限 profile 只允许 `/work/issues`、`/work/openspec/changes`、`/work/iterations`、`/work/docs/spec-logs` 写入 | archive 所需 `openspec/specs` 与 `openspec/archive` 不在允许写入范围 |
| E6 | code_path | `src/backend/app/chat/platform_worker.py` | 执行线程外层 `except Exception` 将 setup 异常统一标记为 `platform_execution_setup_failed` | 具体 setup 异常未落库，导致可诊断性不足 |
| E7 | fact_source | `openspec/changes/add-requirement-center-card-chat-session-reuse/trace.md` | Change 仍为 `status: applied`，`execution.last_event: opsx.apply` | 治理事实源未归档 |
| E8 | data_sample | `chat_turns` / `chat_events` 脱敏查询 | REQ-0039 后续产品归档轮次为 `failed`，`executor_turn_id` 为空，原始事件只有 `workspace_prepare` 阶段 `execution_internal_error` | 产品归档进入了预期的 Chat/Agent 路径，但失败发生在模型执行前 |
| E9 | product_intent | 用户验收反馈 | 用户明确说明需求中心归档按钮应跳转到 Chat 并塞入 prompt，通过 Agent 归档 | 不应通过新增产品后端直归档 API 绕过 Agent 执行语义 |
| E10 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx` | 归档卡片动作应走 `/api/v1/chat/object-sessions` 并写入 `sessionStorage` prompt | 前端正确契约是准备对象会话、填入 `/opsx-archive <object-id>` 并跳转 Chat |
| E11 | fact_source | `issues/requirements/review/REQ-0039-requirement-center-card-chat-session-reuse/acceptance.md` | Chat 中“接受现有验证证据”消息没有更新 `acceptance_status` 或验收文档 | 聊天消息可作为 Agent 上下文，但不应被产品后端静默解释成直归档授权 |
| E12 | container_probe | source root 连接与 DB rollback 探针 | 执行容器连接 source root 和 DB 事务写入均通过 | 后续失败不是 source root 不可达或基础 DB 写入不可用 |
| E13 | runtime_log | `moonbox-chat-worker` 脱敏日志 | BUG-0027 归档轮次 `workspace_prepare_failed` 的内层 `cause_type=IntegrityError` | source 对象归档仍在模型启动前失败，且直接指向 baseline 持久化约束冲突 |
| E14 | code_path | `src/backend/app/chat/schema.py` / `src/backend/app/chat/execution.py` | `chat_workspace_baselines.workspace_id` 保持唯一约束，旧执行器对所有 source 对象会话写入 `workspace_id=source` | 多个对象会话共享 source root 时会竞争同一个 baseline workspace key |
| E15 | screenshot + fact_source | REQ-0043 产品归档截图、当前归档与 Issue trace | Change 已移动，目录校验因四个空工具目录阻断，Issue 仍在 review/in_sprint；宿主四路径不存在 | 证实移动后校验失败造成半归档 |
| E16 | container_probe | 同款归档镜像与一次性工作区 | 四个目录在沙箱内为独立设备空挂载，退出后宿主无残留；预存真实空目录会被挂载遮蔽 | 证实需要沙箱外真实目录预检与沙箱内精确挂载识别两层校验 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| `/opsx-archive` 已经完成但前端没刷新 | E7 和 archive 目录检查显示 Change 仍在 active changes，Sprint 仍显示待 archive |
| REQ-0039 本身未 ready 导致无法归档 | 关联 Change tasks 全勾、trace 验证记录齐全，上一轮阻塞点集中在归档写权限、身份校验和 CLI 可用性 |
| Docker worker 整体不可用 | Docker 状态显示 `moonbox-chat-worker` healthy，10:55 问题是单 turn setup 失败和权限模型不匹配 |

## 已确认根因

本地 Chat 平台 source 工作区策略已经让仓库绑定输出 `workspace_mode: source`，但 worker 的 Compose 挂载和容器权限 profile 仍按只读/治理写子集设计：源仓库以只读方式挂入 chat-worker，执行容器的 governance profile 也没有 `openspec/specs` 与 `openspec/archive` 写权限。因此 `/opsx-archive` 这种需要合并正式规格并移动 Change 目录的命令无法在 Chat 平台中完成。

同时，platform worker 对 setup 阶段异常缺少细分持久化：执行线程异常被统一折叠为 `platform_execution_setup_failed`，未保存安全错误摘要或失败阶段，导致前端只能显示状态未知，用户无法判断是权限、工具链、工作区还是容器沙箱问题。

补充根因：需求中心卡片归档的正确产品语义是复用对象 Chat 会话并注入 `/opsx-archive ...` 命令草稿，由 Agent 执行归档。后续失败说明 Agent 执行准备链路仍在模型启动前失败，且 `SetupFailure` wrapper 没有暴露内层异常类型；修复应继续收敛 Chat/Agent 执行权限和诊断，而不是把需求中心按钮改成产品后端直归档。

补充根因：source 模式允许多个对象会话共享同一个真实仓库 root，但 `chat_workspace_baselines.workspace_id` 仍保留历史唯一约束。旧 `run_claim` 把每个 source 对象会话的 baseline 都写为 `workspace_id=source`，第一个 source 会话写入后，后续对象会话在插入 baseline 时触发 `IntegrityError`，并被标记为 `workspace_prepare` 阶段失败。

## 修复方向

1. 为 Chat 平台区分 archive-capable 治理写入：source 模式下 worker 需要对授权源仓库具备受控写权限，执行容器需要允许 archive 命令写入 `openspec/specs` 与 `openspec/archive`。
2. 修正 Change 身份校验输入边界，避免运行环境注入目录或挂载目录出现在 `openspec/changes/` 下被当作 Change ID。
3. 在 worker setup 失败时落库安全错误摘要和阶段码，区分 workspace、container preflight、auth、toolchain、permission profile 等原因。
4. 保持需求中心卡片归档为对象会话入口：前端准备对象 Chat、填入 `/opsx-archive <object-id>` prompt，由 Agent 完成归档；不得用产品后端直归档替代该语义。
5. 保持默认安全：只对已授权的 archive 命令、已纳入 Sprint 且 applied 的 Change 开启归档写权限，不扩大普通 Chat 写入范围。
6. source 模式 baseline 存储键按 conversation 独立保存，保留 `chat_conversations.workspace_id=source` 的运行语义，避免多对象会话争抢同一个 baseline 唯一键。

## 验证闭环

AF-013 补充确认两处准备与归档执行的独立触发条件：受限容器中的 npm/pnpm/OpenSpec 冷启动可能超过原 10 秒版本探测限时，镜像工具实际存在且固定版本正确，却被报告为 `container_toolchain_unavailable`；产品轮次 `12006fe2-c44b-451a-8642-e3b77a3b495f` 与 `1ba87aed-1cbd-4639-baa7-c870a6935e6d` 分别指向 pnpm 和 OpenSpec。第三轮 `188f3bf2-eea4-4f33-b211-0349ee619f93` 通过预检后，在 OpenSpec CLI 将 Change 暂置 `openspec/changes/archive/` 的窗口中，权限循环因主对象解析仅支持 active 与标准 archive 而撤销 `archive_write`，轮次成为 `unknown/write_permission_revoked`。唯一目录与规格合并事实由宿主恢复脚本核对；新产品同轮闭环仍待复验。证据和修复边界见 Change `acceptance-fixes.md` AF-013。

AF-014 补充跨挂载复制的直接证据：产品轮次 `5cf62853-c01e-4620-9317-c00e6ed55ab6` 在标准归档目录已创建、trace 与 Sprint 尚未同步时成为 `unknown/execution_access_or_workspace_error`。`archive-change.sh` 使用 `shutil.move`，其目标目录可能先于 `trace.md` 出现；聚焦测试构造“完整旧源 + 未完成同名标准目标”，修复前权限返回 `read_only/governance_facts_invalid`，修复后保持 `archive_write/archive_change_transition`；不同日期的第二目标仍拒绝。该中间态是本次权限撤销的已复现触发条件，轮次没有归档命令完成事件，不能由目录结果反推完整命令回执。详见 Change `acceptance-fixes.md` AF-014。

AF-012 验收投影子问题：Issue `acceptance.md` 原 AC-001～007 只出现在 Markdown 表格中，而需求中心 `_acceptance_readiness` 仅识别 `- [ ] AC-001` 形式的复选框行，因此分母为零；`acceptance_status: pending` 使卡片显示“验收结论待核实”。此原因与 Chat 归档权限原根因独立，已通过保留表格并增加九条未勾选 AC 清单修正文档格式，不改通用解析器。真实归档复验和验收签认仍待完成。

当前已有 DB、runtime history、Compose 渲染、worker 日志和代码路径证据，根因状态为 confirmed。后续修复需要覆盖 source 模式 archive 权限、copy 模式兼容、source baseline 多对象会话兼容、setup 失败可诊断性和归档事实源闭环。

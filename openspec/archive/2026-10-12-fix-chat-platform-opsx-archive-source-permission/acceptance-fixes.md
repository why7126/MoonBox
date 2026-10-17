---
title: Chat 平台 source 工作区归档权限与状态诊断修复返修台账
created_at: 2026-10-04 14:43:02
updated_at: 2026-10-11 07:30:00
---

# Chat 平台 source 工作区归档权限与状态诊断修复返修台账

## 2026-10-11 产品首次归档取证

用户授权以 `add-git-sync-skill` 作为纯治理归档样本。对象 Chat 会话 `da03406e-6450-573c-8945-f7d653effbab` 在 07:23:21 发起首次归档，显示 `archive_write`；Agent 完成任务和规格门禁后，真实目录已移动、三条规格已合并。产品轮次最终为“已停止”，最后命令事件缺完成结果，可信用量仍待核实；原轮次重试返回请求失败。宿主 `archive-change.sh add-git-sync-skill --finalize` 在唯一归档上恢复验证与同步，exit 0，Sprint 为 archived，未重复合并。产品执行终态与宿主事实分开记录，BUG-0026 验收仍 pending。完整 AC 结论见 Issue `acceptance.md` 的本日复验段。

## AF-011：全仓自有目录空工具残留

验收反馈：`issues/`、`iterations/` 的四路径处理不足以保证仓库目录整洁。期望仅根目录 `.agents/` 作为技能入口，其他仓库自有目录均不得出现 `.agents`、`.codex`。实际盘点在 `openspec/archive/`、`openspec/changes/`、`openspec/specs/`、`docs/spec-logs/` 发现八个空目录；目录校验此前仍返回通过。用户明确选择沿用 BUG-0026。

| 证据 | 来源 | 结论 |
|---|---|---|
| AF-011-E1 | 宿主文件系统只读盘点与目录元数据 | 八个目标均为真实空目录；`issues/`、`iterations/` 当前无同类残留；未观察到创建瞬间 |
| AF-011-E2 | `container_server.py` 写入 profile 与 `execution.py` 现有清理函数 | 新路径与 Chat 治理/归档写入根目录吻合，旧清理只覆盖两个治理根；本次八路径的创建轮次仍为 probable |
| AF-011-E3 | `validate-directory-structure.py` 与聚焦测试 | 原目录校验漏报八路径；扩展后在清理前逐项报错，确认八路径为空后用 `rmdir` 移除，复检通过 |
| AF-011-E4 | 同款执行器镜像、合成凭据与隔离工作区 | 归档 profile 内六个写入根下的 12 个工具路径均为空且存在；容器退出后宿主安全清理，12 路径均不存在；无模型调用或业务仓库写入 |

调整：目录校验递归检查仓库自有目录，仅根 `.agents` 例外；沙箱运行态只放行私有标记、`/work`、已配置写入根下的精确空路径。worker 在写入型轮次前后检查并安全清理真实工作区空残留；非空目录、文件和符号链接阻断并保留内容。Git 元数据、虚拟环境、依赖、构建缓存和本地运行数据不自动清理。原 BUG 的归档根因与首次 apply 时间保持不变。

验证：工具路径单元测试 3 项通过；后端目录聚焦 2 项通过；Chat 后端全套 48 passed、1 skipped；同款执行器镜像离线隔离探针 1 项通过。目录结构、Agent 上下文预算、当前 Change 中文优先、OpenSpec strict、BUG/Change/治理日志标题、Sprint Scope、产品数据采集与链路观测聚焦校验均通过。Workflow Sync `opsx.modify` 解析 `sprint-008`，0 errors、0 blockers，BUG 验收仍为 pending；两个旧子文档状态语义提示需人工复核，不影响本次同步。AI Usage hook 为 warning/unavailable，0 command runs。真实产品新轮次尚未观察，隔离探针不冒充产品端验收。

文档一致性：BUG capture、bug、root-cause、acceptance、trace 已补充全仓范围；Change proposal、design、delta spec 与目录规则同步；Sprint acceptance-report 记录待复验。REQ-0039 只作为原归档对象来源，本次只变更本地工具目录治理，不改变其业务流程或原型，故不修改其子文档。API、DB、Web、管理端、客户端生成、Orval、Docker Compose 均无契约变化；产品数据采集与链路观测 N/A，原因是未新增行为事件、请求日志、Task Trace 字段或保留周期。

## AF-010：真实 Chat 命令环境遗漏变量并残留空目录

用户 17:33 的产品复验仍在目录校验处退出。原始 `execution.tool` 显示标准脚本 exit 1，四路径被判为禁用目录；后续 `rmdir` 在命令沙箱中返回 `Device or resource busy`。代码交叉核对确认 app-server 用 `shell_environment_policy.inherit="none"`，前版识别器依赖的 `CODEX_HOME` 不会进入命令环境。宿主仓库中还出现四个该轮次生成的空目录，说明沙箱会留下可安全移除的空残留，先前仅检查独立设备挂载的假设也不成立。

| 附件/截图编号 | 页面/状态 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|
| 用户 17:33 截图 | Chat 归档轮次完成后 | REQ-0043 归档闭环 | 目录阻断、收尾未执行 | 状态和文案；无需样式改动 | 截图、execution.tool、宿主路径检查 | 本次修复 | AF-010 原始轮次与聚焦测试 |

调整：私有 Chat 配置显式设置命令环境标记；沙箱判定限定精确空路径并排除符号链接，不再依赖 `CODEX_HOME` 或设备号；worker 归档前后安全清理四个空残留，非空目录、文件和符号链接保持阻断。宿主残留已用 `rmdir` 清理。

验证：60 passed、1 skipped；OpenSpec strict、diff 检查通过；同款执行镜像在不继承 `CODEX_HOME` 的命令下目录校验 exit 0。标准部署完成，五项服务健康。REQ-0043 半归档由宿主标准脚本安全续跑：exit 0，Workflow Sync 0 errors、acceptance passed，Issue 已进入 archive，四个宿主空目录均不存在。此为真实仓库标准脚本闭环；新的产品 Chat 轮次尚未复验。

## AF-009：执行沙箱空工具目录挂载阻断归档收尾

验收偏差：期望 Chat 中的 `/opsx-archive` 在规格合并与目录移动后完成目录校验、Workflow Sync 和 Issue 迁移；实际 REQ-0043 轮次因四个空 `.agents`、`.codex` 路径校验失败，`rmdir` 返回 `Device or resource busy`，只完成了前半段归档。

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| AF-009-E1 | screenshot | 用户 2026-10-08 Chat 截图 | Change 与规格已移动，目录校验失败，收尾三步未执行 | 证实半归档失败阶段 |
| AF-009-E2 | code_path | `scripts/archive-change.sh` | 旧脚本在移动后才执行目录校验，失败即停止后续同步 | 解释为何 Issue 保持未完成 |
| AF-009-E3 | data_sample | 当前宿主工作区 | 四个禁用路径不存在，宿主目录校验通过；唯一 archive 存在，REQ 仍在 review/in_sprint | 执行环境与宿主目录状态不同，且半归档可续跑 |
| AF-009-E4 | container_probe | 一次性仓库与同款归档执行镜像 | 沙箱内四路径均存在、为空、为独立设备挂载点；退出后宿主四路径均不存在；沙箱拒绝读取 mountinfo | 直接确认临时挂载的运行态事实，排除持久仓库残留 |
| AF-009-E5 | container_probe | 一次性仓库内预存同名目录 | 预存非空目录可见，预存空目录在沙箱内与执行时空挂载不可区分 | 证实必须在沙箱挂载前额外检查真实工作区 |

### 附件截图逐项视觉对照

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户 2026-10-08 归档截图 | Chat 工作台，深色主题，归档轮次完成后 | 归档命令结果及对象状态 | 完成归档并同步 Issue | 显示目录校验阻断，Change 已移动 | 执行链状态偏差，非视觉样式偏差 | 截图、脚本顺序及宿主事实源核对 | 本次修复脚本和校验；无需 UI 样式修改 | AF-009-E1～E3 |

调整：worker 在归档执行器启动前检查未被沙箱遮蔽的四个真实路径，空目录、非空目录和符号链接均拒绝。`scripts/runtime_tool_mounts.py` 仅在私有 Chat 命令标记、`/work`、四个精确路径为空且非符号链接时识别临时工具目录；校验器报告警告。标准归档脚本在移动前增加目录预校验；已归档的唯一身份续跑仍沿用既有串行收尾分支。没有扩大执行器写权限，也没有绕过对象鉴权。

验证：聚焦目录识别与归档脚本单元测试 14 项、worker 真实目录预检 1 项通过，宿主目录校验通过。同款归档沙箱隔离探针确认四个独立设备空挂载点，判定器在沙箱内全部返回 true；同款沙箱对当前工作区执行真实目录校验返回 0，并仅报告四个临时挂载警告。真实产品归档闭环仍需复验。当前 REQ-0043 半归档未在本次 BUG 返修中自动续跑。

部署与补充回归：标准 `scripts/docker-up.sh self-storage-sqlite` 完成，backend、web、minio、chat-worker、governance-controller 均健康；运行中的 chat-worker 已加载沙箱外目录预检。Chat 模块全套回归 46 passed、1 skipped。Workflow Sync `opsx.modify` 成功，BUG 验收保持 pending；AI Usage 自动发现无可归因用量，报告 warning/unavailable，不影响返修事实。

文档同步：更新 Change design/delta spec、BUG root-cause/acceptance、目录规则、Sprint 验收、治理日志与本台账。BUG bug.md、capture.md、review.md、workaround.md、trace.md 不需手工改变原问题、评审结论或状态；trace 由 Workflow Sync 维护。API、DB、UI、客户端生成、Docker Compose、权限边界均未变化；产品数据采集与观测为 N/A，理由是只调整本地目录判定与脚本调用顺序，既有执行事件和 Task Trace 契约未变化。

## AF-008：跨挂载归档、权限连续性与半归档恢复

期望：需求中心归档按钮进入对象 Chat，由 Agent 完成归档验证、目录移动、Workflow Sync 和 Issue promote。实际：BUG-0027 读取 21 次工具调用后 stopped；active 目录消失而 Issue 仍位于 review。

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| AF-008-E1 | runtime_log | BUG-0027 轮次 `999ac3ef-1622-4c81-b56f-13b636f817ff` 的 execution.tool | Path.rename 返回 Errno 18；后续校验返回 archive path not found；shutil.move 补救命令仅有 started | 直接确认跨挂载失败，收尾未确认完成 |
| AF-008-E2 | data_sample | 同轮次 execution.state 与事实源目录 | reconcile:terminal 为 stopped/usage_pending；archive 已存在，Issue trace 仍 in_sprint | 目录与逻辑状态不一致，需要恢复入口 |
| AF-008-E3 | code_path | `src/backend/app/chat/policy.py` | 旧权限仅读取 active trace，移动后重检失败，执行器进入 unknown 并关闭 | 确认存在权限连续性缺陷；历史 stopped 的唯一触发来源仍无日志确认 |
| AF-008-E4 | regression_test | Chat accounting、archive policy 与 Change identity 测试 | 移动后 scope 有效；模拟 EXDEV；半归档串行收尾；失败不执行 sync | 覆盖实际目录移动与状态漂移路径 |
| AF-008-E5 | runtime_event | 产品复验轮次 `2f62925a-2eb6-4731-9914-92328ef1e0d1` 与 Issue promote 事实 | Issue 已迁入 archive，但轮次在迁移附近进入 execution_access_or_workspace_error；旧 registry 路径读取存在间隙 | 补充目录迁移期间的对象解析连续性缺陷，不能仅以目录已归档宣称产品执行成功 |
| AF-008-E6 | regression_test | `test_write_policy_grants_archive_scope_only_for_opsx_archive_turn` | Issue 移入 archive、registry 仍指 review 时 history 授权与 archive scope 均通过；非归档命令仍只读 | 同身份恢复不绕过对象 ACL 或扩大普通写权限 |
| AF-008-E7 | runtime_event | 产品复验轮次 `cf31e8c1-792a-47b4-acf9-5b1e06d8df1c` 的标准脚本完成事件 | AI Usage hook 因执行容器无 HOME 抛异常，脚本 exit_code=1 | 无本机会话目录应明确 unavailable，不应阻断归档收尾 |
| AF-008-E8 | runtime_event | 产品复验轮次 `30389f0c-d946-4ef6-9016-4ea61ca01f3b` | 标准脚本完成 exit_code=0，随后 Chat unknown/executor_buffer_limit | 接收队列满一秒退出导致终态与用量未完整消费，不能将脚本成功等同于产品轮次成功 |

### 附件截图逐项对照

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户最后一次 BUG-0027 截图 | Chat，对象归档轮次，已停止 | 归档闭环事实 | Agent 输出结果且对象 archive/done | 21 次工具调用后已停止，无完成结果 | 执行链不闭环 | execution.tool/state、目录与 trace 对照 | 本次修复执行链；不修改布局，视口/style 不影响该根因 | AF-008-E1/E2/E3 |

### 调整与恢复

- 产品执行 prompt 追加标准脚本与安全移动约束；需求中心按钮和 Chat 可见 prompt 保持原有语义。
- archive 权限兼容唯一同身份 archive trace，同时保留命令、成员与对象 ACL 检查。
- 标准脚本使用 shutil.move 迁移 CLI legacy 输出；active 缺失且唯一 archive 存在时续跑验证。`--finalize` 串行执行验证、Workflow Sync、Issue promote、AI Usage，失败退出。
- 恢复前 Agent 检查已有 delta 合并与验收证据。BUG-0027 在产品复验中已由 Agent 推进 Issue promote，不由本次返修绕过产品直接搬移。旧中断轮次无权威终态与最终收据时保留 unknown/pending；新对象会话验证恢复闭环。
- Issue promote 先迁目录再刷新 registry；对象解析在既有授权后允许读取同 ID 的 archive 目录，避免迁移间隙导致运行中权限重检失败。
- terminal grace 保留晚到的 command completed；unknown reconciliation 仅补录权威已完成 items，已有可信 accounting 收据立即幂等结算。缺少最终收据保持 usage_pending，不填零或以中间用量冒充最终账单。
- App Server 接收队列维持 128 条上限，满队列时背压等待消费者，不因正常流量突发一秒超时而断开；关闭时可退出等待。回归验证慢消费者超过一秒仍完整接收 terminal 与 usage，以及满队列关闭不挂死。
- AI Usage 本机会话发现兼容无 HOME 执行环境，输出 unavailable 与补证建议；不替代 Chat 最终账单。

### 文档与观测

更新 tasks、design、delta spec、trace、BUG root-cause/acceptance、Sprint 验收与发布说明、archive 技能及治理日志。API/数据库结构、UI 样式、权限可写目录、Docker 拓扑和客户端生成不变；需重建 worker/backend 加载 Python 修改。

product_data_collection_observability：applicable；affected_layers：execution events、chat_turns、usage reservations、task_traces。验证覆盖已完成工具事件、终态对账、幂等结算和无收据仍 pending。行为字典、请求日志、公开 API、OpenAPI/Orval、保留周期不变，故生成与迁移不适用。沿用脱敏 tool_payload，metadata 不写入 prompt、凭证或本机路径。

BUG 子文档一致性扫尾：更新 root-cause 与 acceptance，trace 由 Workflow Sync 维护；bug/review/workaround 不改变原问题和评审范围，无需更新。

### 验证

相关套件：88 passed，1 skipped；覆盖 Chat 执行、权限、用量、长运行、有界背压、无 HOME 用量发现及归档脚本。OpenSpec strict、中文与根因证据校验通过。

真实产品复验：标准部署脚本重建后，Firefox 对象 Chat 会话 `7d37b021-72d2-58f4-a44d-d19881f76723` 发送原归档命令。轮次 `12822d4c-c26d-4c3a-8ab3-8050d3103dd1` 正常 completed、error_code 为空；标准脚本 completed/exit_code=0，最终回复可见。runner:accounting 最终收据 total_tokens=242062、usage_pending=false，reservation settled、并发释放。Workflow Sync 与 Issue promote 已串行执行，BUG-0027 目录在 archive、验收 passed。此为真实半归档恢复与幂等复验，不冒充全新 Change 首次归档；跨设备首次迁移另由 EXDEV 合成测试覆盖。旧中断轮次缺少最终收据时继续保留 pending，不伪造账单。

## AF-001 source 工作区 run_claim 身份校验返修

### 验收反馈

source 工作区 `run_claim` 仍保留旧的 `workspace.name == conversation_id` 前置校验，导致真实仓库 `source_root` 在进入 `_workspace_identity` 前被 `workspace_binding_mismatch` 拒绝。

### 偏差证据

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| AF-001-E1 | code_path | `src/backend/app/chat/execution.py` | `run_claim` 在调用 `_workspace_identity` 前先比较 `workspace.name` 与 `token['conversation_id']` | source 模式真实仓库目录名通常不是会话 ID，会被旧 copy 模式校验提前拒绝 |
| AF-001-E2 | test_failure | `uv run pytest src/backend/tests/test_chat.py::test_run_claim_accepts_source_workspace_identity ... -q` | 新增回归测试在补齐绑定后稳定进入 `workspace_binding_mismatch`，移除前置校验后通过 | 证明 source 模式应由 `_workspace_identity` 统一识别 |

### 调整内容

- 移除 `run_claim` 中旧的 `workspace.name == conversation_id` 前置校验。
- 保留 `_workspace_identity` 内的统一身份判定：source 模式匹配绑定的 `source_root` 并记录 `workspace_id: source`；非 source 模式仍要求工作区目录名等于 conversation id。
- 新增 `test_run_claim_accepts_source_workspace_identity`，覆盖 source 模式下真实仓库目录名不等于会话 ID 的完整 `run_claim` 完成路径、baseline 记录和用量预留结算。

### 验证证据

| 命令 | 结果 | 说明 |
|---|---|---|
| `uv run pytest src/backend/tests/test_chat.py::test_run_claim_accepts_source_workspace_identity src/backend/tests/test_chat.py::test_execution_setup_failure_is_failed_and_releases_reservation src/backend/tests/test_chat.py::test_execution_disconnect_after_external_turn_keeps_unknown_lock_and_reservation -q` | 3 passed | 覆盖 source 模式身份、启动前失败 failed、启动后断连 unknown 三条关键回归 |

### 文档同步判断

- BUG `acceptance.md`：已更新 AC-001 的合成回归说明，加入 source 模式 `run_claim` 身份回归。
- Change `tasks.md`：已追加 AF-001 返修任务和台账链接。
- Change `trace.md`：已追加返修摘要、证据入口和验证摘要。
- Sprint `acceptance-report.md`：已追加 AF-035 验收返修摘要。
- 长期 API、DB、UI、部署、安全文档：无需更新。本次只移除执行器内部旧前置校验，不新增 API/DB/UI/部署配置或权限边界。

### BUG 子文档一致性扫尾检查

BUG 来源 Change 已检查 `bug.md`、`root-cause.md`、`acceptance.md`、`trace.md`、`workaround.md`。本次返修不改变原根因和 workaround；只需更新 `acceptance.md` 与 Change/Sprint 返修证据。`trace.md` 由 Workflow Sync 维护，不手工改写 Issue trace。

## AF-002 旧 copy 会话迁移到 source 工作区返修

### 验收反馈

重启 backend 与 chat-worker 后，BUG-0024 对象会话继续执行 `/opsx-archive BUG-0024-login-expired-refresh-not-redirect-login` 仍失败。轨迹原始事件显示 `workspace_prepare` 阶段返回 `workspace_binding_mismatch`。

### 偏差证据

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| AF-002-E1 | runtime_event | Chat 平台轨迹截图 | 原始事件为 `execution.state`，`status: failed`、`error_code: workspace_binding_mismatch`、`stage: workspace_prepare` | 新代码已进入准备阶段并明确失败，不再是不可诊断 unknown |
| AF-002-E2 | container_inspection | `docker exec moonbox-chat-worker ... inspect app.chat.execution.run_claim` | backend 与 chat-worker 容器中均已移除旧 `workspace.name == conversation_id` 前置校验 | 重启后的失败不是镜像未更新到 AF-001 |
| AF-002-E3 | code_path | `src/backend/app/chat/execution.py` | source 工作区识别为 `workspace_id: source` 后，旧会话持久化的 `parent.workspace_id == conversation_id` 仍会被二级绑定校验拒绝 | 需要允许已验证 source root 的旧 copy 会话安全迁移为 `source` |

### 调整内容

- 新增 `_workspace_id_allowed`，在 `_workspace_identity` 已确认当前目录为绑定的 source root 后，允许历史 copy 会话从 `workspace_id == conversation_id` 迁移为 `workspace_id: source`。
- `run_claim` 更新 conversation workspace id 时同步更新既有 `workspace_baselines.workspace_id`，避免后续同会话继续命中旧 baseline 身份。
- 新增 `test_run_claim_migrates_legacy_copy_workspace_to_source`，覆盖旧 copy workspace id、既有 baseline、source 绑定和完整执行结算路径。

### 验证证据

| 命令 | 结果 | 说明 |
|---|---|---|
| `uv run pytest src/backend/tests/test_chat.py::test_run_claim_accepts_source_workspace_identity src/backend/tests/test_chat.py::test_run_claim_migrates_legacy_copy_workspace_to_source src/backend/tests/test_chat.py::test_execution_setup_failure_is_failed_and_releases_reservation src/backend/tests/test_chat.py::test_execution_disconnect_after_external_turn_keeps_unknown_lock_and_reservation -q` | 4 passed | 覆盖 source 身份、旧 copy 迁移、启动前 failed、启动后 unknown |
| `uv run pytest src/backend/tests/test_chat.py src/backend/tests/test_chat_platform.py tests/unit/test_change_identity.py -q` | 59 passed，1 skipped | 覆盖 Chat 平台、执行器和 Change 身份回归 |

### 文档同步判断

- BUG `acceptance.md`：已更新 AC-001，补充旧 copy 会话迁移到 source 的合成回归证据。
- Change `tasks.md`：已追加 AF-002 返修任务和台账链接。
- Change `trace.md`：已追加 AF-002 返修摘要、证据入口和验证摘要。
- Sprint `acceptance-report.md`：已追加 AF-036 验收返修摘要。
- 长期 API、DB、UI、部署、安全文档：无需更新。本次只收敛 Chat 执行器内部 workspace 身份迁移，不新增接口、表结构、页面、部署变量或权限 profile。

### BUG 子文档一致性扫尾检查

BUG 来源 Change 已复查 `bug.md`、`root-cause.md`、`acceptance.md`、`trace.md`、`workaround.md`。本次返修不改变原缺陷根因和 workaround；只需更新 `acceptance.md` 与 Change/Sprint 返修证据。`trace.md` 由 Workflow Sync 继续维护。

## AF-003 source 快照排除 Git ignored 运行时数据返修

### 验收反馈

重建并重试 BUG-0024 archive 后仍失败。Firefox 轨迹最新轮次 `2026/10/4 22:24:47` 原始事件显示 `workspace_prepare` 阶段返回 `execution_access_or_workspace_error`。

### 偏差证据

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| AF-003-E1 | browser_trace | Firefox Chat 工作台轨迹页 | 最新原始事件为 `status: failed`、`error_code: execution_access_or_workspace_error`、`stage: workspace_prepare` | AF-002 已改变旧 binding mismatch 路径，但准备阶段仍失败 |
| AF-003-E2 | container_probe | `docker exec moonbox-chat-worker ... snapshot(source_root)` | 容器内 source/workspace/governance 目录均存在且非 symlink；`snapshot(source_root)` 抛出 `WorkspaceError: 工作区超过快照容量边界` | 失败点是 source 快照容量边界，不是容器未更新或路径不存在 |
| AF-003-E3 | disk_usage | `du -sh data/runtime/chat-platform data/runtime/backend .` | `data/runtime/chat-platform` 约 8.0G，`data/runtime/backend` 约 209M，仓库总量约 9.1G | source 快照扫描 ignored 运行态数据会稳定超过 512MB 边界 |
| AF-003-E4 | git_ignore | `git check-ignore -v data/runtime ...` | `.gitignore` 已忽略 `data/runtime/**`，但旧 `snapshot()` 直接遍历目录树，只跳过 `.git` | 快照策略未尊重 Git ignored 文件，和 source 模式真实仓库语义不一致 |

### 调整内容

- `snapshot()` 检测到当前工作区是 Git 仓库时，改用 `git ls-files -co --exclude-standard -z` 取得 tracked 与未被忽略的 untracked 文件清单。
- 保留原有 no-follow 安全读取、硬链接/特殊文件拒绝、容量边界、文本边界和 rename diff 逻辑；非 Git 普通目录仍沿用完整目录遍历。
- 新增 `test_git_snapshot_skips_ignored_runtime_data`，覆盖 `.gitignore` 忽略 `data/runtime/**` 大文件时，快照仍保留 tracked 与未忽略 untracked 文件。

### 验证证据

| 命令 | 结果 | 说明 |
|---|---|---|
| `uv run pytest src/backend/tests/test_chat_workspace.py -q` | 6 passed | 覆盖 workspace 快照、差异、链接安全、容量边界和 ignored runtime 数据排除 |
| `PYTHONPATH=src/backend python - <<'PY' ... snapshot(repo_root) ...` | `has_runtime: False`，`has_backend: True` | 本地真实仓库根目录快照排除 `data/runtime/**`，仍包含后端源码 |
| `uv run pytest src/backend/tests/test_chat_workspace.py src/backend/tests/test_chat.py::test_run_claim_accepts_source_workspace_identity src/backend/tests/test_chat.py::test_run_claim_migrates_legacy_copy_workspace_to_source src/backend/tests/test_chat.py::test_execution_setup_failure_is_failed_and_releases_reservation src/backend/tests/test_chat.py::test_execution_disconnect_after_external_turn_keeps_unknown_lock_and_reservation -q` | 10 passed | 覆盖 workspace 快照与 source `run_claim` 身份、旧 copy 迁移、准备失败状态回归 |

### 文档同步判断

- BUG `acceptance.md`：已更新 AC-001，补充 source 快照排除 ignored runtime 数据的合成回归证据。
- Change `tasks.md`：已追加 AF-003 返修任务和台账链接。
- Change `trace.md`：已追加 AF-003 返修摘要、证据入口和验证摘要。
- Sprint `acceptance-report.md`：已追加 AF-037 验收返修摘要。
- 长期 API、DB、UI、部署、安全文档：无需更新。本次只调整 Chat workspace 快照内部文件枚举策略，不新增 API/DB/UI/部署配置、安全权限或对象存储边界。

### BUG 子文档一致性扫尾检查

BUG 来源 Change 已复查 `bug.md`、`root-cause.md`、`acceptance.md`、`trace.md`、`workaround.md`。本次返修细化了 source 工作区准备失败的直接原因，但不推翻原 BUG 的 archive 权限与状态诊断根因链；只需更新 `acceptance.md` 与 Change/Sprint 返修证据。`trace.md` 由 Workflow Sync 继续维护。

## AF-004 source 模式容器 runtime 挂载重叠返修

### 验收反馈

重建并重试 BUG-0024 archive 后仍失败。最新 turn `77b317c7-31a5-47a4-b1aa-adacce0441bb` 在 `workspace_prepare` 阶段返回 `container_mount_overlap`。

### 偏差证据

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| AF-004-E1 | database_event | `chat_turns` / `chat_events` | 最新 turn 状态为 `failed`，`error_code: container_mount_overlap`，原始事件 stage 为 `workspace_prepare` | AF-003 后已越过快照容量边界，新阻塞点是容器挂载安全检查 |
| AF-004-E2 | container_code | `ContainerAppServer.__init__` | 容器适配拒绝 `workspace == runtime`、`workspace in runtime.parents` 或 `runtime in workspace.parents` | source 模式 workspace 为仓库根，runtime 若在仓库内会被安全拒绝 |
| AF-004-E3 | env_config | 本地 `.env` 摘要 | `MOONBOX_CHAT_SOURCE_ROOT` 指向仓库根，`MOONBOX_CHAT_HOST_ROOT` 指向仓库内 `data/runtime/chat-platform` | runtime root 位于 source root 内，执行容器会同时挂载父 `/work` 与子 `/runtime` |
| AF-004-E4 | preflight | `bash scripts/docker-up.sh self-storage-sqlite --check` | 脚本输出已自动使用源仓库同级私有目录，Chat 与治理预检通过 | 自动迁移旧仓库内私有根目录后，部署预检可通过 |

### 调整内容

- `platform_deployment.check()` 明确拒绝 Chat 私有执行数据目录位于 source root 内，避免 runtime/auth/state/backups 暴露在 `/work` 挂载下。
- `scripts/docker-common.sh` 在 Chat Platform 模式下检测到旧配置将 `MOONBOX_CHAT_HOST_ROOT` 放在 source root 内时，自动改用源仓库同级私有目录，并输出不含具体路径的提示。
- 部署文档更新为：Chat 私有根目录必须位于源仓库外，旧仓库内配置会自动迁移到同级私有目录。
- 新增 `test_platform_deployment_rejects_private_root_inside_source`，覆盖平台预检拒绝 source 内私有根目录。

### 验证证据

| 命令 | 结果 | 说明 |
|---|---|---|
| `uv run pytest src/backend/tests/test_chat_platform.py src/backend/tests/test_chat_workspace.py -q` | 15 passed | 覆盖平台预检、source 挂载配置和 workspace 快照回归 |
| `bash scripts/docker-up.sh self-storage-sqlite --check` | 通过 | 当前本地旧 `.env` 配置会自动迁移到源仓库同级私有目录，Chat 常驻部署和治理预检通过 |
| `bash scripts/docker-down.sh self-storage-sqlite && bash scripts/docker-up.sh self-storage-sqlite` | 服务重建完成，backend、web、chat-worker、governance-controller、minio 均 healthy | 当前运行态已加载 AF-004 迁移逻辑 |
| `docker exec moonbox-chat-worker ... repository_binding/runtime` | `host_inside_source: false`，`runtime_inside_source: false` | chat-worker 当前私有根目录与 runtime root 已位于 source root 外，不再触发 `/work` 与 `/runtime` 挂载重叠 |

### 文档同步判断

- BUG `acceptance.md`：已更新 AC-001，补充 source 模式 runtime 挂载不重叠的预检和脚本迁移证据。
- Change `tasks.md`：已追加 AF-004 返修任务和台账链接。
- Change `trace.md`：已追加 AF-004 返修摘要、证据入口和验证摘要。
- Sprint `acceptance-report.md`：已追加 AF-038 验收返修摘要。
- `docs/02-deployment.md`：已更新 Chat Platform 私有根目录边界，明确必须位于 source root 外。
- API、DB、UI、安全、对象存储文档：无需更新。本次改变部署预检和脚本默认路径选择，不改变 API、表结构、页面、安全 profile 或对象存储契约。

### BUG 子文档一致性扫尾检查

BUG 来源 Change 已复查 `bug.md`、`root-cause.md`、`acceptance.md`、`trace.md`、`workaround.md`。本次返修补齐容器挂载安全边界，仍属于原 BUG 的 source 工作区 archive 执行准备链路；只需更新 `acceptance.md` 与 Change/Sprint/部署文档证据。`trace.md` 由 Workflow Sync 继续维护。

## AF-005 旧版 source_bug trace 归档写权限返修

### 验收反馈

BUG-0024 的 `/opsx-archive BUG-0024-login-expired-refresh-not-redirect-login` 最新轮次执行已完成但输出为空，轨迹仍显示失败；执行摘要显示归档目标 `openspec/archive/` 与 `openspec/specs/` 在会话中只读。

### 偏差证据

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| AF-005-E1 | runtime_event | `chat_turns` / `chat_events` | 最新 turn `0546a6cd-2c3b-46c8-91b5-b68d5bf8b502` 为 `completed`，但前端无 assistant message，terminal event 为 `reconciled_usage_pending` | 执行过程实际有输出，但恢复完成态没有形成可见回复，用户看到空输出 |
| AF-005-E2 | execution_output | 最新 turn `execution.output` 摘要 | 执行器报告 `openspec/archive/`、`openspec/specs/` 只读，未修改文件、未推进状态 | 当前归档轮次没有拿到 `moonbox-archive` 写权限 |
| AF-005-E3 | code_path | `src/backend/app/chat/policy.py` 与 `openspec/changes/fix-chat-auth-expired-redirect-login/trace.md` | 策略只识别 `bug` / `requirement`，而旧 Change trace 使用 `source_bug: BUG-0024-login-expired-refresh-not-redirect-login` | 旧版 BUG Change 被误判为普通治理写权限，无法写入归档目录 |
| AF-005-E4 | ui_contract | `src/backend/app/chat/api.py` / `src/web/src/components/chat/Composer.tsx` | 响应 schema 和前端标签原本未声明 `archive_write` | 即使后端授予归档权限，也需要 API 与 UI 能正确展示该权限状态 |

### 调整内容

- `write_policy` 的 archive 判定兼容旧版 trace 字段：`source_bug` 与 `source_requirement` 和新版 `bug` / `requirement` 等价参与归档资格判断。
- `ConversationRead.write_scope` 响应 pattern 增加 `archive_write`，并同步 OpenAPI/前端生成注释。
- Composer 权限 badge 增加 `归档可写` 标签和 `archive_change_applied` 原因说明，避免归档轮次在界面上退化为“完全只读”或普通治理写。
- 新增 `test_write_policy_grants_archive_scope_for_legacy_source_bug_trace`，覆盖真实 BUG 主对象 + 旧 `source_bug` trace 的 `/opsx-archive BUG-*` 授权路径。

### 验证证据

| 命令 | 结果 | 说明 |
|---|---|---|
| `uv run pytest src/backend/tests/test_chat.py::test_write_policy_grants_archive_scope_only_for_opsx_archive_turn src/backend/tests/test_chat.py::test_write_policy_grants_archive_scope_for_legacy_source_bug_trace src/backend/tests/test_chat.py::test_conversation_read_includes_write_scope -q` | 3 passed | 覆盖新版归档权限、旧 `source_bug` trace 兼容和会话读取响应 schema |
| `./node_modules/.bin/vitest run chat-composer.test.tsx` | 17 passed | 覆盖 Composer 对 `archive_write` 的可见标签和原因说明 |

### 文档同步判断

- BUG `acceptance.md`：更新 AC-001，补充旧版 `source_bug` trace 可获得 `archive_write` 的回归证据。
- Change `tasks.md`：追加 AF-005 返修任务和台账链接。
- Change `trace.md`：追加 AF-005 返修摘要、证据入口和验证摘要。
- Sprint `acceptance-report.md`：追加 AF-039 验收返修摘要。
- `docs/03-api-index.md`：同步 Chat 会话 `write_scope` 的 `archive_write` 响应语义。
- DB、部署、安全、对象存储文档：无需更新。本次调整 Chat 写策略、响应 schema 和前端展示，不新增表结构、部署变量、安全 profile 或对象存储契约。

### BUG 子文档一致性扫尾检查

BUG 来源 Change 已复查 `bug.md`、`root-cause.md`、`acceptance.md`、`trace.md`、`workaround.md`。本次返修继续收敛同一归档权限链路，不改变原缺陷根因、workaround 或 BUG 复现描述；只需更新 `acceptance.md` 与 Change/Sprint/API 文档证据。`trace.md` 由 Workflow Sync 继续维护。

## AF-006 产品归档入口语义纠正与 Agent 链路诊断返修

### 验收反馈

按 Chat 内人工确认与 `/opsx-archive <REQ-full-id>` 的方案在产品上仍不可行。用户补充确认：需求中心点击归档按钮的产品意图就是跳转到 Chat 并塞入 prompt，通过 Agent 完成归档；不得改成产品后端直接归档。

### 偏差证据

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| AF-006-E1 | data_sample | `chat_turns` / `chat_events` 脱敏查询 | REQ-0039 对象会话最新归档轮次为 `failed`，`executor_turn_id` 为空，原始事件只有 `workspace_prepare` 阶段 `execution_internal_error` | Agent 归档路径仍在启动前失败，需要修执行准备链路和诊断，而不是绕过 Chat |
| AF-006-E2 | runtime_log | `moonbox-chat-worker` 脱敏日志 | worker 仅输出 `chat.workspace_prepare_failed` 与 `exception_type: SetupFailure`，真实 cause 被 wrapper 吞掉 | 失败诊断仍不足，无法从产品轨迹判断底层异常类型 |
| AF-006-E3 | product_intent | 用户验收反馈 | 用户明确说明“点击需求中心的归档按钮，就是希望跳转到Chat并塞prompt，通过Agent进行归档” | 产品入口应保留对象会话 + prompt 语义，不能新增后端直归档捷径替代 Agent |
| AF-006-E4 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx` | 归档动作应走 `/api/v1/chat/object-sessions` 与 `sessionStorage` prompt，然后跳转 Chat | 前端验收重点是能打开对象 Chat 并填入 `/opsx-archive <object-id>` |
| AF-006-E5 | fact_source | `issues/requirements/review/REQ-0039-requirement-center-card-chat-session-reuse/acceptance.md` | Chat 中“接受现有验证证据”没有修改 `acceptance_status` 或验收事实源 | 人工确认聊天消息可作为 Agent 上下文，但不应被产品后端静默解释成直归档授权 |
| AF-006-E6 | container_probe | `persistent_container_server(...).connect(None)` 与 DB rollback 探针 | source root 连接和 DB 写入探针均通过，未复现挂载或基础连接失败 | 本轮产品失败不是 AF-004 的挂载重叠或 source root 不可达 |

### 调整内容

- 移除产品后端直归档方案，避免绕过 Chat/Agent 归档产品意图。
- 需求中心 `opsx-archive` 卡片动作保持对象会话路径：调用 `/api/v1/chat/object-sessions`，把 `/opsx-archive <object-id>` 写入 `sessionStorage`，并跳转到 `/chat?space_id=...&conversation_id=...`。
- `workspace_prepare` 失败日志增加 `cause_type`，保留安全错误码的同时暴露 wrapper 内层异常类型，提升下一次诊断效率。

### 验证证据

| 命令 | 结果 | 说明 |
|---|---|---|
| `uv run pytest src/backend/tests/test_chat_preparation_failure.py src/backend/tests/test_governance_candidates.py -q` | 46 passed | 覆盖 setup 失败诊断与治理准备回归 |
| `node_modules/.bin/vitest run src/requirement-center.test.tsx` | 112 passed | 覆盖需求中心归档按钮调用 `/api/v1/chat/object-sessions`、写入 `/opsx-archive` prompt 并跳转 Chat |
| `node_modules/.bin/tsc --noEmit` | 通过 | 覆盖前端类型检查 |
| `uv run python -m py_compile src/backend/app/governance/api.py src/backend/app/chat/execution.py src/backend/app/chat/preparation_failure.py` | 通过 | 覆盖后端归档入口相关模块语法 |

### 文档同步判断

- `docs/03-api-index.md`：同步 `opsx-archive` 继续使用对象会话进入 Chat 并填充 prompt 的产品契约。
- BUG `root-cause.md`：补充产品入口应保留 Agent 归档语义和 setup cause 丢失的根因证据。
- BUG `acceptance.md`：补充 AC-007 产品卡片归档跳转 Chat 验收项，并更新 AC-001 / AC-006 证据。
- Change `tasks.md` / `trace.md`：追加 AF-006 返修任务和验证摘要。
- Sprint `acceptance-report.md`：追加 AF-040 验收返修摘要。
- DB、部署、安全、对象存储文档：无需更新。本次纠正产品入口语义并增强诊断，不新增数据库表、部署变量、安全 profile 或对象存储契约。

### BUG 子文档一致性扫尾检查

BUG 来源 Change 已复查 `bug.md`、`root-cause.md`、`acceptance.md`、`trace.md`、`workaround.md`。本次返修扩展并细化根因：source 工作区权限链路之外，产品卡片归档入口必须保持 Chat/Agent 执行语义，阻塞点应继续在 Agent 准备链路和权限诊断中闭环；已更新 `root-cause.md` 与 `acceptance.md`。`trace.md` 由 Workflow Sync 继续维护。

## AF-007 source baseline 多对象会话兼容返修

### 验收反馈

source 模式下 `chat_workspace_baselines.workspace_id` 的唯一约束导致多个对象会话共享 `workspace_id=source` 时触发 `IntegrityError`。BUG-0027 执行 `/opsx-archive` 在 `workspace_prepare` 阶段失败，无法进入模型执行。

### 偏差证据

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| AF-007-E1 | runtime_log | `moonbox-chat-worker` 脱敏日志 | BUG-0027 最新归档轮次记录 `workspace_prepare_failed`，外层异常为 `SetupFailure`，内层 `cause_type=IntegrityError` | 失败发生在模型启动前的工作区准备阶段，且与数据库唯一约束冲突相关 |
| AF-007-E2 | data_sample | `chat_workspace_baselines` 脱敏查询 | 已存在 source 模式对象会话 baseline 使用 `workspace_id=source` | 后续 source 对象会话继续插入同一 `workspace_id` 会命中唯一约束 |
| AF-007-E3 | code_path | `src/backend/app/chat/schema.py` / `src/backend/app/chat/execution.py` | baseline 表以 `conversation_id` 为主键，但 `workspace_id` 仍有唯一约束；`run_claim` 对 source 模式直接写入 `workspace_id=source` | source 模式把多个对象会话映射到同一个 baseline workspace key，与历史唯一约束冲突 |
| AF-007-E4 | regression_test | `test_run_claim_allows_multiple_source_conversation_baselines` | 连续两个 source 对象会话共享同一 source root 完成 `run_claim`，各自 baseline 使用会话 ID，conversation 仍记录 `workspace_id=source` | 证明修复后 source 模式支持多对象会话，不再触发唯一约束 |

### 调整内容

- 新增 `_baseline_workspace_id()`，source 模式下 baseline 私有存储键使用 `conversation_id`，非 source 模式继续使用原 workspace id。
- `chat_conversations.workspace_id` 仍保存 `source`，保留执行器对真实 source root 的语义判断和前端/服务端会话状态语义。
- 旧 copy 会话迁移到 source 时，既有 baseline 保持会话级 key，不再更新为共享 `source`。
- 新增 `test_run_claim_allows_multiple_source_conversation_baselines`，覆盖两个对象会话共享同一 source root 的连续执行。

### 验证证据

| 命令 | 结果 | 说明 |
|---|---|---|
| `uv run pytest src/backend/tests/test_chat.py::test_run_claim_accepts_source_workspace_identity src/backend/tests/test_chat.py::test_run_claim_allows_multiple_source_conversation_baselines src/backend/tests/test_chat.py::test_run_claim_migrates_legacy_copy_workspace_to_source -q` | 3 passed | 覆盖 source baseline 存储键、新多会话兼容与旧 copy 迁移 |
| `uv run pytest src/backend/tests/test_chat.py src/backend/tests/test_chat_platform.py src/backend/tests/test_chat_workspace.py -q` | 60 passed，1 skipped | 覆盖 Chat 执行器、平台预检、workspace 快照和既有权限/状态回归 |

### 文档同步判断

- BUG `root-cause.md`：补充 baseline 唯一约束与 source 多对象会话冲突的直接证据和修复方向。
- BUG `acceptance.md`：更新 AC-001，补充 source baseline 多会话兼容回归。
- Change `tasks.md` / `trace.md`：追加 AF-007 返修任务和验证摘要。
- Sprint `acceptance-report.md`：追加 AF-041 验收返修摘要。
- API、DB、UI、部署、安全、对象存储长期文档：无需更新。本次不改变公开 API、表结构或部署变量，只调整 Chat 执行器内部 baseline 身份语义；既有唯一约束保持，source baseline 改为按会话落键。

### BUG 子文档一致性扫尾检查

BUG 来源 Change 已复查 `bug.md`、`root-cause.md`、`acceptance.md`、`trace.md`、`workaround.md`。本次返修补充新的直接 setup 失败根因，仍属于原 BUG 的 source 工作区归档准备链路；已更新 `root-cause.md` 与 `acceptance.md`。`trace.md` 由 Workflow Sync 继续维护。

## AF-012 Issue 验收项可计数格式返修

### 偏差与视觉对照

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户前轮 BUG-0026 卡片截图及本轮文字反馈 | `/requirements` 深色主题、验收中 | BUG-0026 卡片测试后的验收进度与提示 | 可识别的 Issue AC 显示“验收 已勾选数/总数”，pending 保持归档阻断 | 表格 AC-001～007 不被复选框计数器识别，显示“验收结论待核实”而没有分母 | 文档格式与投影读取约定不一致 | 对照 Issue `acceptance.md`、后端 `_acceptance_readiness` 和现有卡片 | 本次修正文档格式，不替代验收签认 | 用户截图、`src/backend/app/services/requirement_center.py` |
| 同一验收文档 | AF-009、全仓工具目录补充验收 | 待复验事项 | 纳入可计数 AC 核对清单，仍未勾选 | 当前作为章节文字，不在 AC 表格或复选框中 | 待验证范围可能被遗漏 | 逐项梳理章节与既有 AC，保留详细证据表 | 本次补齐独立核对项 | Issue `acceptance.md`、AF-009/AF-011 记录 |

按钮族检查：研发、测试仍打开关联 Change `tasks.md`；验收仍打开 Issue `acceptance.md`。本批次只改变 BUG-0026 文档的可识别 AC 结构，不改前后端计数器、颜色、权限、归档动作或状态。表格“通过”表示既有测试/隔离证据，不等于产品验收签认。

### 实施与验证

- Issue `acceptance.md` 增加 AC-001～009 九条未勾选核对项：原七条保留表格操作、预期和已知执行结果，新增 AC-008/009 对应全仓目录和真实归档复验。全部未勾选，`acceptance_status: pending` 和最终回填仍不变。
- 使用当前后端 `_acceptance_readiness` 直接读取该 Issue 文档，返回待验证 9、总数 9、阻断摘要“验收未完成：9 项待验证”。无需改解析器、API 或客户端生成。
- Firefox 本地真实 `/requirements` 页面观察 BUG-0026 研发 7/7、测试 17/17、验收 0/9；原“验收结论待核实”在该卡片不再出现，点击验收打开 `BUG-0026 · acceptance.md`，AC-009 可读且未勾选。当前浏览器 1440px 响应式视口；产品验收签认和归档动作均未执行。
- BUG 子文档一致性扫尾：`root-cause.md` 补记独立的验收投影格式原因；`bug.md`、`workaround.md` 描述的归档权限与状态诊断事实未变，无需更新；Issue `trace.md` 由 Workflow Sync 维护。Change 设计与 delta spec 不变，因为本批次只校正现有通用验收投影所消费的 Issue 文档格式，不改变功能边界。Sprint 验收报告和发布说明记录新的卡片展示与未签认边界。

## 2026-10-10 BUG-0026 逐项产品复验

Issue `acceptance.md` 已逐项记录 AC-001～009 的本轮直接产品观察、既有真实产品轮次与仍缺的证据。Firefox 需求中心确认 BUG-0026 为“验收 0/9”；`add-git-sync-skill` 的“完成 / 归档”按钮实际进入主对象 Chat，并预填 `/opsx-archive add-git-sync-skill`。未发送该命令，故只能证明 AC-007 的入口与预填。既有 BUG-0027 轮次 `12822d4c-c26d-4c3a-8ab3-8050d3103dd1` 证明半归档恢复，不证明全新 Change 首次归档。AC-002/003/005/006 的负向或 copy 条件在本轮产品中未触发，AC-004 仅宿主脚本通过，AC-008/009 缺产品新轮次的沙箱和宿主目录对照。九项继续未勾选，不将旧回归标成产品签认。

当前宿主目录校验另因未跟踪的 `openspec/changes/archive/2026-10-09-enable-agent-browser-product-evidence` 失败；该旧路径不是空工具目录，已保留原状，不能并入 AC-008 的安全清理结果。本批次仅补验收证据，不修改代码、规格、API、数据库、UI 行为、部署或权限边界。

## AF-013 专用样本产品归档返修

### 偏差证据与根因

| 证据 | 类型 | 事实 | 判断 |
|---|---|---|---|
| E1 | 产品轮次 | `12006fe2-c44b-451a-8642-e3b77a3b495f` 在 executor turn 创建前以 `container_toolchain_unavailable` 失败；worker 仅报告 `pnpm` | 首次冷启动预检在 10 秒限时内误判，未触及 Change |
| E2 | 产品轮次 | `1ba87aed-1cbd-4639-baa7-c870a6935e6d` 在重建镜像后同样于准备期失败，worker 报告 `openspec` | 问题属于包工具 CLI 冷启动限时，而非某个单一工具缺失 |
| E3 | 受限容器复现 | 同款只读非 root 容器的工具清单一次返回 `pnpm` 不可用、再次返回 `ready=true`；单独 `pnpm --version` 返回固定版本 | 支持启动耗时不稳定的判断；固定版本要求仍有效 |
| E4 | 标准部署 | 首次标准部署中治理控制器健康探针连续超过 3 秒，手动就绪命令成功；延长探针后标准部署全部服务健康 | 健康探针限时过紧，不能以一次 unhealthy 代替功能不可用 |
| E5 | 产品轮次 | `188f3bf2-eea4-4f33-b211-0349ee619f93` 通过工具链与沙箱预检，executor turn 已创建；OpenSpec CLI 合并规格并将样本移至 `openspec/changes/archive/` 后，轮次成为 `unknown/write_permission_revoked` | 权限循环在 CLI 旧目录到标准目录的短暂迁移间隙失去主对象解析，导致脚本不能继续同步 |
| E6 | 事实源恢复 | 对唯一旧归档运行标准 `archive-change.sh --finalize`，迁至 `openspec/archive/`，不重复合并规格；归档证据、目录、环境 ignore、Workflow Sync 均通过 | 宿主恢复闭环成功，但不能计入产品同轮端到端成功 |

### 调整

- 执行镜像为 npm、pnpm、OpenSpec 版本探测设置 45 秒冷启动限时，仍严格核对固定版本；外围工具清单预检限时增至 180 秒，其余 OS 工具保持 10 秒。
- Chat worker 与治理控制器健康探针限时设为 10 秒；`docs/02-deployment.md` 同步部署说明。
- `archive_write` 只在同一 `/opsx-archive` 活动轮次、已应用纯治理 Change、唯一同名旧归档目录、无 active/canonical 冲突、有效 trace 与 Sprint 绑定时跨过 CLI 临时目录间隙；其他命令、关联 Issue、错误 trace 均不继承此权限。最终目录校验仍禁止 `openspec/changes/archive/`。
- 增加迁移间隙权限回归，覆盖有效旧目录、错误关联 BUG、标准目录迁入及命令变化后的权限撤销。

### 验证与状态

`test_chat_toolchain.py` 与聚焦归档权限测试共 18 passed；标准 `docker-down.sh` / `docker-up.sh self-storage-sqlite` 再部署后全部服务健康。AF-013 的产品修复尚需一个全新样本同轮完成移动、规格合并、验证和 Workflow Sync 才能签认；BUG 九项 AC 与 `acceptance_status: pending` 不变。API、DB、Web UI、客户端生成、对象存储字段无变化；部署探针和执行器权限内部判断有变化，已同步部署文档与回归测试。

### 后续产品复验（未通过）

替代纯治理样本 `verify-chat-archive-transition-window` 已应用且任务 3/3。需求中心对象 Chat 会话 `1bfe0dbf-97ea-5324-8d8e-edf2c11a3fcb` 成功预填并提交归档命令；轮次 `b708c17e-11f7-4fe0-95a2-183689400dc2` 显示“归档可写”，进入 running，完成三次规则与 Change 材料读取后转 stopped，`error_code=reconciled_usage_pending`。此轮没有归档脚本事件；活动目录仍在，标准归档目录未创建。期间后端需求中心请求曾耗时 27–57 秒并出现 SQLite `database is locked`，Chat worker 一度因工具链冷启动预检不健康；停止看板轮询、重启本地后端和 worker 后服务均恢复健康，镜像离线工具链自检为 ready。浏览器随后因 Mac 锁屏无法观察最终界面。停止原因尚不能归因于 AF-013 权限修复；保留活动样本，待产品连接和轮次诊断证据恢复后再试，不以宿主归档代替产品通过。

## AF-014 跨挂载复制中间态权限返修

### 偏差证据与根因

2026-10-12 Firefox 重新登录后，原轮次重试在执行前以 `workspace_prepare_failed` 结束；同一对象会话的新轮次 `5cf62853-c01e-4620-9317-c00e6ed55ab6` 通过预检，产品显示“归档可写”，前置工具命令成功。随后轮次成为 `unknown/execution_access_or_workspace_error`。宿主事实源显示 Change 已移至唯一标准目录 `openspec/archive/2026-10-12-verify-chat-archive-transition-window/`，其 trace 仍为 applied、Sprint 仍列 applied；归档证据和目录校验通过，Workflow Sync 尚未完成。产品同轮归档不通过。

`scripts/archive-change.sh` 使用 `shutil.move` 从 CLI 旧目录迁往标准目录。跨挂载时目标目录会在其中 `trace.md` 复制完成前出现，而完整旧源仍存在。现有 `_legacy_archive_transition_ready` 一看到标准目标就撤销过渡授权；`resolve_object` 又会读取尚未复制的目标 trace，因此重检返回只读。聚焦测试先复现 `governance_facts_invalid`，再修正为仅在同一归档轮次、完整唯一旧源、最多一个同名且非符号链接的标准目标期间继续授权；不同日期的第二目标仍阻断。此证据解释本次再次失权的触发窗口，轮次缺失归档命令完成事件，保留该事件边界的可观测性缺口。

### 调整与验证

`src/backend/app/chat/policy.py` 扩展旧源过渡授权到跨挂载复制的部分标准目标；`test_chat.py` 增加先失败后通过的中间态和目标冲突断言。未改变普通治理命令、其他对象、关联 Issue 或最终归档身份门禁。设计与 delta spec 同步该中间态规则。聚焦测试 1 passed；产品首次归档仍需全新样本同轮完成归档脚本、规格合并和 Workflow Sync 才能签认。API、DB、UI、Docker 拓扑、客户端生成无变化；内部归档权限判断变化，需重建运行中的 backend 和 Chat worker。

## AF-015 历史引用过渡授权与中断原因保留

第四个专用样本 `verify-chat-archive-finalize-window` 在产品对象会话 `aa2b76db-4fae-52c4-b270-999d5041b74f` 执行轮次 `047b4f26-6785-4f6e-bf06-10d31b158d88`。产品权限已选中归档写入，轮次在 OpenSpec CLI 生成唯一旧目录后成为 `unknown/execution_access_or_workspace_error`；标准目标尚未出现。这次保留下来的原始错误码与完整旧目录证明中断发生在 CLI 旧目录阶段。宿主标准恢复把唯一旧目录迁至标准目录并完成同步，仍不算产品同轮成功。

执行器每轮循环先调用 `authorize_history` 重新解析不可变引用快照；该函数只认活动 Change 或标准归档目录，旧目录阶段抛出访问错误，比归档权限重检更早中断。现改为仅当快照对象是主对象、活动轮次首行精确匹配 `/opsx-archive`、旧目录完整唯一、trace 已应用、Sprint 绑定有效且标准目标无冲突时，沿用现有过渡门禁。其他对象或冲突目录仍拒绝。`test_chat.py` 覆盖旧目录、复制中的同名目标和冲突目标；`execution.py` 在日志记录安全原因码，并使未知轮次对账保留原错误码。新样本产品同轮收尾仍待复验。

### 全新样本产品复验

用户授权的第五个纯治理样本 `verify-chat-archive-history-transition` 在 Firefox 需求中心卡片进入对象 Chat 会话 `b9366706-35a6-5703-94ce-1b5faaebdc5c`，预填并发送准确归档命令。轮次 `d720688b-5667-43a7-a891-ed26e31197e3` 的标准归档脚本命令事件 127 为 `completed`、退出码 0；在该轮次内形成唯一标准归档目录、合并验收规格、将 sprint-009 中该 Change 同步为 archived，且没有宿主恢复。轮次事件 400 和数据库终态均为 `completed`。产品对话与轨迹截图见 `evidence/20261012-product-archive-success.png` 和 `evidence/20261012-product-archive-trace-completed.png`。脚本报告 AI 用量输入不可用、沙箱空挂载点警告，均未阻断归档；产品 Agent 后续严格校验和中文校验通过。该样本无关联 Issue，故不证明首次同轮 Issue promote；BUG 的 AC-001、AC-003、AC-005 仍有独立证据缺口。

## AF-016 关联 Issue 首次归档产品验收闭环

BUG-0040 的产品归档轮次在 SQLite 写锁冲突后停止；BUG-0041 的产品轮次在 OpenSpec CLI 临时目录迁移窗口被误判为归档权限撤销，最终 stopped。两者均未计为 AC-001 成功，已通过标准脚本恢复治理归档，保留各自失败事实。针对迁移窗口，Chat worker 在已确认的 `archive_write` 轮次中对治理事实短暂不可读提供 15 秒有界重检；空间或操作者授权变化仍立即撤权。SQLite 连接锁等待设为 30 秒并同步数据库设计文档。归档权限聚焦测试 3 passed，后端与 worker 重新构建并启动。

用户已授权的第三份独立虚拟样本 BUG-0042 / `fix-chat-archive-issue-promote-retest-2` 完成 Sprint、OpenSpec strict、交付证据与身份门禁。产品对象 Chat 会话 `cdebda67-4749-5b70-b24a-b73688b43428` 首次归档轮次 `489d335c-a077-4734-b0b0-4fcc4babfb1b` 为 `completed`；命令 `bash scripts/archive-change.sh fix-chat-archive-issue-promote-retest-2 --finalize` 事件序号 43 started、47 completed/exit_code=0。规格合并新增 1 项，Change 唯一标准归档目录形成，Workflow Sync 0 errors，BUG-0042 promote 至 archive/done。Firefox 最终画面和脱敏对账见 `evidence/20261012-bug0042-product-archive-completed.png`、`evidence/20261012-bug0042-ac001-product-proof.md`。BUG-0026 AC-001 签收，九项 AC 为 9/9。

归档 Change `trace.md` 的 `status: applied` 保留 apply 执行事实；仓库既有归档 Change 同样如此。本次归档阶段以标准目录、Issue 当前态和 Workflow Sync 报告核对，未将该字段当作产品轮次终态。AI Usage hook 返回 unavailable/warning，未影响标准脚本退出码。

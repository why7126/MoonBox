---
bug_id: BUG-0026-chat-platform-opsx-archive-source-permission
title: Chat 平台无法归档 source 工作区 Change 且状态未知回归验收方案
created_at: 2026-10-04 11:11:31
updated_at: 2026-10-17 16:45:27
acceptance_status: passed
---

# Chat 平台无法归档 source 工作区 Change 且状态未知回归验收方案

## AF-009 追加复验

- Chat worker 在归档前后清理真实工作区四个同名空目录，非空目录、文件和符号链接仍拒绝；沙箱仅在私有 Chat 命令标记下允许四个精确空路径以警告通过。
- 标准归档脚本在移动 Change 前运行目录校验；已移动且唯一归档存在时只恢复验证、Workflow Sync 和 Issue promote。
- 用隔离容器观察实际挂载路径及归档全过程；合成挂载信息回归不能替代真实产品复验。

## 全仓工具目录补充验收（待验证）

- 对仓库自有目录递归检查：除根目录 `.agents/` 外，不允许 `.agents/`、`.codex/` 残留；被 Git 忽略的第三方依赖、虚拟环境和运行时数据不在自动清理范围。
- 在隔离工作区分别运行治理写入、归档写入和重复执行，核对沙箱运行期间的临时路径与退出后的宿主路径；具体创建路径与本次八个目录的来源须补证。
- 清理仅作用于确认为空的宿主目录；非空目录、文件和符号链接阻断并保留内容。验证目录校验覆盖新增路径，且不会把合法的运行中临时挂载误判为持久残留。
- 不得以既有四路径回归结果标记全仓验收通过；须分别记录隔离回归与真实产品复验。

实现和隔离验证记录：AF-011 已覆盖全仓校验、安全清理、12 个执行时空路径与退出后宿主无残留的离线探针；真实产品新轮次仍待观察，因此本项保持待复验，不提前标记通过。详见当前 Change 的 `acceptance-fixes.md` AF-011。

## AF-008 追加复验

- 产品对象 Chat 归档优先标准脚本；跨挂载不使用 Path.rename，目录移动后权限仍有效。
- active 已消失且唯一 archive 存在时，同一归档命令恢复验证、Workflow Sync 与 Issue promote，不重复合并规格。
- command completion 的退出码可见，可信用量收据幂等结算；缺失收据保持待对账。
- 验证失败、关联错误、权限撤销或多个归档目录不推进完成态；自动回归与真实产品复验分开记录。

## 验收 AC 清单

下列复选框是需求中心卡片“验收 已勾选数/总数”的唯一计数入口。已勾选项具有产品轮次与对应隔离回归证据；AC-001 已由 BUG-0042 关联 Issue 首次归档产品轮次、规格合并、同轮 Workflow Sync 与 promote 证据补齐；`acceptance_status` 为 `passed`。

- [x] AC-001 source 模式的 Chat 对象归档完成真实写入、同步与 Issue promote，并在产品端端到端复验。
- [x] AC-002 归档权限不足或工具链缺失时给出可诊断的失败或恢复状态。
- [x] AC-003 普通治理写命令与非归档命令不获得额外归档写权限。
- [x] AC-004 Change 身份校验忽略运行环境系统目录，不误判为业务 Change。
- [x] AC-005 copy 模式归档前置检查保持工作区隔离、候选应用与成果保护语义。
- [x] AC-006 setup 阶段的 workspace、container、auth、toolchain 异常可诊断且轨迹脱敏。
- [x] AC-007 需求中心“完成 / 归档”进入对象 Chat 并填入归档命令，由 Agent 执行。
- [x] AC-008 全仓自有目录的空工具残留可安全清理，非空、文件、符号链接保持阻断；隔离验证与真实产品新轮次分别留证。
- [x] AC-009 真实产品归档链路能区分沙箱临时空挂载与宿主残留，移动前完成目录预检；半归档恢复不重复合并，产品新轮次复验通过。

### 操作与证据明细

| 编号 | 条件与操作 | 期望结果 | 执行结果 |
|---|---|---|---|
| AC-001 | source 模式本地 Chat 平台执行已 applied 且已纳入 Sprint 的 `/opsx-archive <BUG/REQ-full-id>` | 可以写入 `openspec/specs/`、移动到 `openspec/archive/`，并完成 Workflow Sync 与 Issue promote | 合成回归已覆盖权限、挂载、身份与多会话等路径；BUG-0027 的产品轮次已完成半归档恢复、同步和 Issue promote。BUG-0042 产品首次归档同轮完成，见下方 2026-10-12 证据 |
| AC-002 | archive 命令在权限不足或工具链缺失时失败 | turn 进入 failed 或可恢复阻断状态，展示安全错误摘要，不停留不可诊断 unknown | 通过：启动前 `ExecutorError` 标记 failed、释放会话和预留；启动后断连仍保留 unknown |
| AC-003 | 普通治理写命令或非 archive 命令执行 | 不因 archive 写权限放宽而获得额外 `openspec/specs` / `openspec/archive` 写能力 | 通过：`moonbox-governance` 不含 specs/archive 写权限，非 archive prompt 回落普通治理写权限 |
| AC-004 | Change 身份校验运行于 Chat 平台工作区 | 不把 `.agents`、`.codex`、`.git` 等运行环境目录当作 active Change ID | 通过：隐藏系统目录忽略测试与 `validate-change-identity.py` 均通过 |
| AC-005 | copy 模式隔离工作区执行 archive 前置检查 | 仍保持副本隔离、候选应用和未应用成果保护语义 | 未改动 copy 同步路径；本轮以回归未破坏 Chat 基础套件为证据，端到端 copy archive 未单独运行 |
| AC-006 | setup 阶段发生 workspace/container/auth/toolchain 类异常 | `chat_turns.error_code` 或扩展字段能区分失败阶段，轨迹或错误摘要可指导修复 | 通过：启动前失败保留安全错误码，例如 `executor_disconnected`；worker 日志额外记录 `cause_type` 以定位 wrapper 内层异常 |
| AC-007 | 需求中心卡片点击“完成 / 归档” | 前端准备对象 Chat 会话并填入 `/opsx-archive <object-id>` prompt，跳转 Chat 后由 Agent 执行归档 | 前端 112 项回归通过；本轮真实产品确认点击 `add-git-sync-skill` 卡片按钮后进入对应对象 Chat 并预填准确命令。该命令未发送，Agent 执行仍待复验 |
| AC-008 | 全仓自有目录残留及清理 | 除根目录 `.agents/` 外不留工具目录；仅安全清理宿主空目录，非空及符号链接阻断；真实产品新轮次单独复验 | AF-011 离线探针与隔离回归通过；真实产品新轮次待观察 |
| AC-009 | 真实 source 归档和半归档恢复 | 沙箱临时空挂载不误判，宿主残留在移动前阻断；唯一归档恢复验证、同步和 promote | AF-009/010 隔离回归及部分宿主续跑有证据；产品新轮次仍待复验 |

## 2026-10-10 真实产品逐项复验记录

本轮在本地运行的 MoonBox 产品 `http://localhost:39002`、Firefox 已登录的项目空间中直接观察需求中心与对象 Chat；未发送归档命令、未改变业务 Change 状态。浏览器页面观察与既有 BUG-0027 真实产品执行记录分开记载；自动回归、离线探针和源码检查均不冒充本轮产品观察。

| AC | 本轮直接观察及可追溯证据 | 结论与仍缺的证据 |
|---|---|---|
| AC-001 | 需求中心 BUG-0026 仍处“验收中”，卡片无可执行归档按钮；既有 BUG-0027 对象 Chat 轮次 `12822d4c-c26d-4c3a-8ab3-8050d3103dd1` 已记录脚本退出码 0、turn completed、Workflow Sync 和 Issue promote。 | **部分覆盖，未通过本项**：既有轮次是半归档恢复；尚无全新 source Change 在产品端首次移动、规格合并、同步和 promote 的同轮闭环证据。 |
| AC-002 | 本轮未对运行中产品故意撤销归档权限或卸载工具链。既有启动前 `ExecutorError` 回归及历史失败轮次详见 Change `acceptance-fixes.md`。 | **待复验**：缺产品端受控失败轮次的安全错误摘要、状态和恢复记录。 |
| AC-003 | 对象 Chat 入口显示普通“治理可写”提示；本轮未尝试对 `openspec/specs/` 或 `openspec/archive/` 越权写入。 | **待复验**：UI 提示不证明实际文件系统拒绝；需隔离对象的普通命令执行和拒绝证据。 |
| AC-004 | 当前工作区执行 `python scripts/validate-change-identity.py` 返回“Change 身份校验通过”。 | **脚本通过，产品待复验**：这是宿主命令结果，未取得 Chat 执行沙箱内对系统目录的身份校验轨迹。 |
| AC-005 | 本轮产品对象 Chat 为 source 工作区；未建立 copy 模式的隔离产品会话。 | **待复验**：缺 copy 模式前置检查、候选应用与未应用成果保护的实际产品证据。 |
| AC-006 | 本轮产品正常进入对象 Chat，未触发 workspace/container/auth/toolchain setup 故障；既有故障回归及历史失败证据详见 Change 台账。 | **待复验**：缺受控产品故障的 error_code、用户可见摘要与脱敏轨迹对应记录。 |
| AC-007 | Firefox 需求中心 `add-git-sync-skill` 卡片有“完成 / 归档 →”按钮。点击后进入对象 Chat 会话 `da03406e-6450-573c-8945-f7d653effbab`，主对象为 `add-git-sync-skill`，输入框预填 `/opsx-archive add-git-sync-skill`，未点击发送。 | **入口与预填已由真实产品确认，整项待复验**：尚无该入口触发的 Agent 归档执行结果；未归档这个无关业务 Change。 |
| AC-008 | 本轮 `python scripts/validate-directory-structure.py --help` 实际运行了目录校验并以错误退出：发现禁用旧路径 `openspec/changes/archive/`。该路径含未跟踪的 `2026-10-09-enable-agent-browser-product-evidence`，保留原状。 | **待复验**：此失败是旧归档路径，不是空 `.agents`/`.codex` 残留；本轮未有新 Chat 执行前后宿主目录对照，也未进行非空/文件/符号链接产品试验。 |
| AC-009 | 既有 BUG-0027 真实产品轮次证明唯一归档的恢复闭环；本轮产品未启动新的归档执行。 | **部分覆盖，未通过本项**：缺新轮次的沙箱临时挂载与宿主目录对照、移动前预检记录及首次归档结果。 |

本轮产品可直接确认 AC-007 的前半段；其余证据不足以勾选任何完整 AC，九条复选框和 `acceptance_status: pending` 均保持不变。旧归档路径由其内容归属流程单独处理，不能为通过目录校验而直接删除。

## 2026-10-11 产品首次归档复验

用户明确授权以纯治理 Change `add-git-sync-skill` 作为真实归档样本。Firefox 需求中心点击“完成 / 归档”后进入对象会话 `da03406e-6450-573c-8945-f7d653effbab`，预填并发送 `/opsx-archive add-git-sync-skill`；产品显示“归档可写”，轮次开始于 07:23:21。Agent 在产品内确认任务 4/4、交付证据与三条新增规格，随后把 Change 移至 `openspec/archive/2026-10-10-add-git-sync-skill/` 并合并 `git-sync-governance` 三条规格。

该轮次在最后一个命令事件仍显示“执行中”时转为“已停止”，产品显示“用量尚待核实，额度预留暂未释放”；“重试原轮次”返回“请求失败，请稍后重试”。当时 Sprint 仍为 applied。按唯一归档恢复流程，在宿主对已归档目录运行 `archive-change.sh --finalize`，明确报告不重复合并规格；归档证据、目录结构、环境 ignore、Workflow Sync 均通过，Sprint 后续显示 archived。此成功是宿主恢复，不是产品轮次成功。

AC-001、AC-007、AC-009 获得首次归档的部分产品证据，但因轮次已停止且未在产品内完成同步，仍不勾选；AC-008 的宿主全仓目录复查通过且无新增工具目录，沙箱临时路径与非空阻断未在本轮直接观察，仍不勾选。AC-002/003/004/005/006 的受控负向、copy 和沙箱内身份场景尚未由本轮覆盖。九项与 `acceptance_status: pending` 保持不变。

## 数据采集与链路观测

## 2026-10-11 专用样本复验与 AF-013

纯治理样本 `verify-chat-source-archive-e2e` 已由用户授权创建并纳入 sprint-009。产品对象 Chat 的前两轮 `12006fe2-c44b-451a-8642-e3b77a3b495f`、`1ba87aed-1cbd-4639-baa7-c870a6935e6d` 分别在冷启动预检报告 `pnpm`、`openspec` 不可用，均未创建 executor turn。第三轮 `188f3bf2-eea4-4f33-b211-0349ee619f93` 通过预检并开始执行，CLI 合并规格、移动到旧路径 `openspec/changes/archive/` 后成为 `unknown/write_permission_revoked`，未在同轮完成 Workflow Sync。宿主标准恢复脚本将唯一旧目录迁至 `openspec/archive/` 并完成证据校验与同步，不计入产品同轮成功。详见 Change `acceptance-fixes.md` AF-013。

AF-013 已修复包工具冷启动探针、部署健康探针与严格限定的旧目录迁移权限；聚焦 18 项测试通过，标准部署全部服务健康。AC-002、AC-006 得到真实失败状态和诊断证据，AC-001、AC-009 仍缺全新产品样本同轮闭环，AC-003/005/008 的负向与隔离场景仍需逐项证据。九项复选框保持未勾选，`acceptance_status: pending`。

### 专用替代样本轮次（未通过）

用户授权后创建并应用纯治理 Change `verify-chat-archive-transition-window`，纳入 sprint-009，任务 3/3 与归档前验证通过。Firefox 需求中心卡片实际进入主对象 Chat 会话 `1bfe0dbf-97ea-5324-8d8e-edf2c11a3fcb`，预填并发送 `/opsx-archive verify-chat-archive-transition-window`。轮次 `b708c17e-11f7-4fe0-95a2-183689400dc2` 通过连接和预检，显示“归档可写”，但仅完成三次前置读取命令后转为 `stopped`，错误码 `reconciled_usage_pending`；未运行归档脚本，活动 Change 仍存在，标准归档目录不存在。浏览器随后因 Mac 锁屏无法继续观察，产品界面最终回执和停止原因仍待补证。

本轮直接证明 AC-007 的入口、预填和 Agent 执行启动；不证明归档成功，也不替代 AC-001/008/009。九项复选框与 `acceptance_status: pending` 保持不变。

### 2026-10-12 新轮次与 AF-014（未通过）

原轮次重试 `2cce3f13-f626-4dab-abbe-90af4b59d508` 在执行前以 `workspace_prepare_failed` 结束。Firefox 同一对象 Chat 新轮次 `5cf62853-c01e-4620-9317-c00e6ed55ab6` 显示“归档可写”，前置验证工具命令成功；随后状态成为 `unknown/execution_access_or_workspace_error`。事实源已出现唯一标准目录 `openspec/archive/2026-10-12-verify-chat-archive-transition-window/`，但 trace 和 sprint-009 仍为 applied，未完成 Workflow Sync。归档证据与目录校验通过不等于产品同轮成功。

AF-014 的失败测试复现跨挂载复制中“完整旧归档源和未完成标准目标并存”时权限误撤销；修复后同名唯一目标保留同轮授权，冲突目标仍阻断。该修复仍需部署与全新样本产品复验。AC-001/008/009 不勾选，其他 AC 的剩余证据范围不变，`acceptance_status: pending`。

### 2026-10-12 AF-014 产品复验结果（未通过）

在重建后的 MoonBox 产品中，Firefox 需求中心卡片 `verify-chat-cross-mount-copy-archive` 的“完成 / 归档”进入对象会话 `3f39f293-1ec9-52fb-9189-969f932612c2`，准确预填并发送归档命令。轮次 `cd2e1318-2927-4208-bb9e-dcdef408ae19` 取得 `archive_write` 的 selected 与 acknowledged 事件，完成前置检查并启动标准归档脚本。文件事实源显示唯一标准归档目录及已合并规格，但产品轮次在命令事件尚为 `started` 时成为 `stopped/reconciled_usage_pending`，Sprint 当时仍为 applied。宿主随后对唯一目录执行 `archive-change.sh --finalize`，证据校验和 Workflow Sync 通过；这是恢复，不是产品同轮完成。

当前产品事件没有保留中断前的原始错误码，不能据此确认再次中断的根因。AF-015 先在执行日志记录安全的内部原因码，并在未知轮次对账时保留原错误码，便于下一轮定位。AC-001、AC-008、AC-009 仍待首次产品归档同轮闭环；全部九项保持未勾选。

### 2026-10-12 AF-015 产品诊断与返修

第四个专用样本 `verify-chat-archive-finalize-window` 从 Firefox 需求中心卡片进入对象 Chat，预填并发送准确命令。轮次 `047b4f26-6785-4f6e-bf06-10d31b158d88` 获得归档写入权限，OpenSpec CLI 生成唯一旧目录后成为 `unknown/execution_access_or_workspace_error`，没有标准目标和命令完成事件。诊断改进保留了原始错误码；`authorize_history` 在旧目录过渡期不能解析引用快照，是本次已确认的中断点。宿主唯一目录恢复、证据校验、Workflow Sync 成功，仍不计为产品通过。

AF-015 将历史引用检查限定到同一主对象的完整唯一旧目录、精确归档轮次及有效 Sprint 事实；冲突目录仍拒绝。隔离测试已覆盖过渡期与冲突场景；修复部署和全新产品样本首次归档仍待完成。九项复选框和 `acceptance_status: pending` 保持不变。

### 2026-10-12 首次产品归档成功与逐项判定

AF-015 修复重建后，Firefox 需求中心将纯治理样本 `verify-chat-archive-history-transition` 的“完成 / 归档”准确预填到对象 Chat 会话 `b9366706-35a6-5703-94ce-1b5faaebdc5c`。轮次 `d720688b-5667-43a7-a891-ed26e31197e3` 的标准归档脚本事件 127 为 `completed/exit_code=0`，唯一标准目录存在、旧目录消失、规格合并、Workflow Sync 0 errors；轮次事件 400 和 `chat_turns` 均为 `completed`，没有宿主恢复。产品截图已转存到 Change 的 `evidence/20261012-product-archive-success.png` 和 `evidence/20261012-product-archive-trace-completed.png`。沙箱临时空挂载点被标记为非阻断警告，宿主目录校验通过。

| AC | 本次判定 | 证据与边界 |
|---|---|---|
| AC-001 | 待验收 | 首次归档、规格和同步已由本轮产品闭环；既有 BUG-0027 产品恢复轮次有 Issue promote，但仍缺**关联 Issue 的首次归档与 promote 同轮**证据。 |
| AC-002 | 通过 | 早前产品冷启动 `container_toolchain_unavailable`、工作区准备失败和过渡期 `unknown` 轮次保留安全错误码；修复后成功轮次完成，失败与恢复状态可区分。 |
| AC-003 | 通过 | BUG-0026 主对象普通治理轮次 `5bd89de0-9b52-4d62-b5dc-f0759c06fea2` 选中并确认 `governance_write`，两处 `touch` 探针均返回 `WRITE_DENIED / Read-only file system`，命令 completed/exit_code=0，轮次经对账完成；截图见 Change `evidence/20261012-product-governance-write-denied.png`。 |
| AC-004 | 通过 | 本轮产品标准脚本中的 Change 身份校验返回通过；隐藏系统目录回归及宿主身份校验通过。 |
| AC-005 | 通过 | 独立 39021 copy 产品环境中，对象 Chat 轮次 `3fc0a05b-ba6c-46a9-a286-6c1b1deb2cdd` 完成只读预检，因 Change 未 applied 阻断归档；源仓库与会话副本 `counter.txt` 哈希同为 `9a271f2a916b`，归档目录、候选与应用记录均为 0，截图 `evidence/20261012-product-copy-preflight-blocked.png`。候选应用成功路径与未应用成果保留由 5 项聚焦回归单独覆盖，未将回归冒充产品正向观察。 |
| AC-006 | 通过 | 前述真实 setup 失败轮次与聚焦测试保留阶段和错误码，不含凭证或原始敏感路径；本轮正常启动形成对照。 |
| AC-007 | 通过 | 需求中心卡片进入主对象 Chat、准确预填命令，Agent 在产品内执行归档成功；截图和轮次可复核。 |
| AC-008 | 通过 | AF-011 隔离探针覆盖空目录清理与非空、文件、符号链接阻断；本轮产品明确报告沙箱临时空挂载点，退出后宿主目录校验无残留。 |
| AC-009 | 通过 | 本轮真实首次归档含移动前预检、同轮成功与空挂载点警告；前四个样本的唯一归档宿主恢复分别验证不重复合并。 |

该阶段为 **8/9**，后续由关联 Issue 专用 BUG-0042 样本补齐 AC-001；见下方最终证据。

### 2026-10-12 关联 Issue 专用样本复验（终态待恢复）

用户授权建立虚拟 BUG `BUG-0040-chat-archive-issue-promote-fixture` 及关联 Change `fix-chat-archive-issue-promote-fixture`，用于首次归档和 Issue promote 同轮验收。样本完成 Sprint 纳入、OpenSpec、apply、交付证据和归档前门禁；它是验收夹具，不代表新增生产缺陷。Firefox 对象 Chat 会话 `0bec2076-17e8-5fc7-a10d-c9adf29d9ec6` 发送 `/opsx-archive BUG-0040-chat-archive-issue-promote-fixture`，轮次 `7fcb3bd0-96bc-4518-ba85-0fba232bf7e1` 选中并确认 `archive_write`。文件事实源随后出现唯一标准归档目录，BUG-0040 迁入 `issues/bugs/archive/`，当前态索引更新，归档证据校验通过。

产品 worker 在执行中记录 `OperationalError` 并重启；轮次最终对账为 `stopped/execution_internal_error`，事件流止于两个前置命令的 `started`，尚无归档脚本 `completed/exit_code=0` 或产品终态。Firefox 后续 Chat 请求出现 504，页面证据保存于 Change `evidence/20261012-product-bug0040-504.png`。文件迁移和 Issue promote 不能单独证明同一轮端到端成功。该轮不计入 AC-001；后续使用独立样本复验。

普通治理权限轮次先短暂进入 `unknown/execution_internal_error`，服务重建后对账为 `completed`，工具事件 `completed/exit_code=0`。产品正文明确报告两个目录实际只读。未知态与最终执行事实分开记录；错误码仍保留诊断历史，不将其当作权限拒绝本身。


```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - request_logs
    - task_traces
    - task_trace_spans
    - usage_events
  reason: 修复涉及 Chat 平台执行器、治理命令写权限、执行状态和失败诊断，影响请求结果、任务轨迹和执行 span 摘要。
  validation: 验证 archive 成功链路、权限不足失败链路、setup 失败错误码和脱敏轨迹摘要；不得记录 Prompt 全文、完整 candidate、密钥、Cookie、Authorization、本机绝对路径或未脱敏日志。
```

## 2026-10-12 AC-001 最终产品复验

BUG-0040 与 BUG-0041 的产品轮次均为 stopped，不纳入成功证据。BUG-0042 专用关联 Issue 首次归档轮次 `489d335c-a077-4734-b0b0-4fcc4babfb1b` 在产品 Chat 显示“已完成”，数据库终态 `completed`；同轮归档脚本事件 `completed/exit_code=0`，规格新增 1 项、唯一标准归档目录形成、Workflow Sync 0 errors、BUG-0042 promote 至 archive 且当前态为 done。AC-001 **通过**，九项 AC **9/9**。证据：Change `evidence/20261012-bug0042-ac001-product-proof.md` 与 `evidence/20261012-bug0042-product-archive-completed.png`。归档 Change trace 保留 `applied` 执行事实，阶段以目录、Issue 和同步结果核对。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-17 16:45:27
accepted_by: workflow-sync
source_change: fix-chat-platform-opsx-archive-source-permission
source_sprint: sprint-008
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

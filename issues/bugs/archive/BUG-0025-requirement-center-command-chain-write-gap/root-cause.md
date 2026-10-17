---
bug_id: BUG-0025-requirement-center-command-chain-write-gap
title: 需求中心看板治理命令真实写入链路缺口根因分析
status: confirmed
created_at: 2026-09-29 15:56:27
updated_at: 2026-09-30 15:35:00
owner: user_f694abc671d548b48d9eb897f720ba4d
---

# 需求中心看板治理命令真实写入链路缺口根因分析

## 根因状态

status: confirmed

## 现象

AF-028 confirmed：重复 complete 的完整工作区差异为零且源文件一致，validate_completion 的 not changed 分支仍抛 scope 错误，collect 归为 governance_validation_failed；前端还优先选择历史 rejected。需用完整核验后的 unchanged 终态区分无需写入与校验失败，历史只呈现当前或最新候选。

AF-027 confirmed：BUG-0024 完善轮次没有候选，权限读取历史 applied generate 后判定 invalid，导致 /work 只读、成果仅在临时目录。证据为运行态 DB、policy.write_policy 与 prepare_command_snapshot；须使用当前轮绑定并补齐 bug-complete 收集回写，根因业务门禁仍保留。

AF-026 confirmed：治理权限配置未包含可写临时目录，真实续接轨迹在 Workflow Sync 的 tempfile/sync_lock 阻断；req-complete 仅准备命令快照而未创建候选，collect 因无候选返回，后续工作区保护持续阻断。解决必须同时补齐锁预检、原基准续接与 controller 自动应用，不得清空文件或跳过门禁。

AF-025 补充：准备阶段异常在 platform_worker 被统一转为 unknown，丢失具体原因；尚未创建执行器任务也展示无限等待。证据为 14:08 轮次一秒内 platform_workspace_unavailable 且 executor_turn_id=null，代码 catch 位于 initialize_workspace 后、执行线程启动前。当前重验版本及对象校验通过，工作区有未应用文件且无候选，命中成果保留门禁；历史原始异常未记录，不能反推原异常文本。修复与恢复证据见关联 Change acceptance-fixes.md。

需求中心看板展示完整治理命令链，包含 `bug-generate`、complete、review、sprint-propose、opsx 等动作，但产品内真实治理候选、应用和事实源写入链路目前只覆盖采集池需求的 `req-generate`。

用户在看板或 Chat 中看到 Bug Generate 等动作时，会预期产生 Codex 命令同等效果，例如生成 `bug.md`、更新 trace、registry 和 CHANGELOG，并推进阶段投影。但多数命令当前没有对应的产品写入链路。

## 证据链

AF-023：截图 DevTools 与 ConversationMessages 分支确认，尚无 assistant 消息时 TurnActivity 原来挂在 turn-user 下，触发 720px/72% 子节点与 1120px 容器上限。旧宽度脚本手工构造 assistant DOM，未覆盖此真实分支。返修将临时输出改为独立 assistant 兄弟块，以真实页面接口驱动落库前后验证。

AF-022 补充根因：Worker 心跳与阻塞维护共用主循环，运行态 24 次采样中 5 次超过 5 秒门禁；Chat capabilities 仅在 space/boot 变化时获取，使一次未就绪持续阻断发送。独立心跳与能力轮询返修后，部署采样最大年龄 0.551 秒、0 次超时；浏览器合成故障验证保留草稿并恢复发送。详细边界和证据见 Change acceptance-fixes.md AF-022。

AF-020 补充根因：产品 preflight 以全治理目录 Git dirty 代替内容版本检查，普通写入命令缺少 generate 已有的工作树覆盖路径，导致未提交的新文档阻断后续 complete。证据为 preparation.py 的旧 status 检查及 candidate 限定的 initialize_workspace；返修已改为 manifest/revision 和通用命令同步。详细回归见关联 Change acceptance-fixes.md 的 AF-020。

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | code_path | `src/backend/app/governance/api.py` `PreparationRequest` | `object_id` 只允许 `REQ-*`，`action` 只允许 `req-generate` | 后端治理准备接口没有开放 BUG 或其他命令类型 |
| E2 | code_path | `src/backend/app/governance/preparation.py` `prepare()` | 非 `REQ-*` 或非 `issues/requirements/plan/<REQ>` 会抛出“首版仅支持采集池需求的 req-generate” | 产品内治理会话准备被硬编码限制在采集池需求生成 |
| E3 | code_path | `src/backend/app/governance/candidates.py` `validate()` | 校验器声明为纯 `req-generate`，仅允许写入 `requirement.md`、`trace.md`、需求 registry 和需求 CHANGELOG | 治理候选应用边界没有覆盖 `bug.md` 或 complete / review / opsx 产物 |
| E4 | code_path | `src/backend/app/governance/writer.py` `apply_candidate()` | 候选应用记录固定写入 `kind: req-generate` | 产品内候选应用没有命令族分发或 BUG 生成写入分支 |
| E5 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx` `openIssueActionDialog()` | 非 demo 模式下，非 requirement、非 capture 或辅助动作都会提示“当前仅支持采集需求的生成动作” | 前端真实产品路径主动拦截 BUG 和后续治理动作 |
| E6 | code_path | `src/backend/app/services/requirement_center.py` `_stage_action()` | 看板 action hint 为各阶段展示 `/bug-generate`、`/bug-complete`、`/bug-review`、`/sprint-propose`、`/bug-opsx`、`/opsx-apply`、`/opsx-archive` | 看板展示层已经暴露完整命令链，但这只是提示，不等于后端已实现写入链路 |
| E7 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx` `runIssueAction()` | demo/模拟分支通过本地 state 更新阶段、追加文档名和“执行成功”消息 | 部分交互可产生模拟流转感，但不会形成真实治理候选和仓库事实源写入 |
| E8 | data_sample | `governance_candidates` / `governance_applications` 查询结果 | 针对 BUG-0024 的 Bug Generate Chat 未产生 governance candidate 或 application 记录 | 用户看到的 Chat 回复没有进入真实治理写入队列 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| BUG 生成链路已经实现，只是某个 BUG 数据异常 | E1-E5 显示后端 schema、prepare、candidate validate、writer 和前端非 demo 分支均只支持 `req-generate` |
| 看板按钮能执行所有命令，只是文档同步失败 | E6 证明完整命令链来自 action hint；E1-E4 证明真实候选应用链路没有对应写入分支 |
| Chat 回复等同于治理写入候选 | E8 显示相关会话没有 governance candidate/application 记录 |
| 只需要补一个前端按钮放行 | E2-E4 显示后端准备、校验和写入应用都需要扩展，单独放行前端会产生不可应用或越界成果 |

## 已确认根因

需求中心产品把“命令链展示”和“命令真实写入链路”混在同一个看板体验中，但目前真正实现的治理写入链路只有 `req-generate`。

后端治理准备、候选校验和应用写入均围绕 `req-generate` 固化；前端非 demo 路径也只允许采集池需求生成。与此同时，看板 action hint 和 demo 数据展示了完整 REQ / BUG / Sprint / Opsx 命令链，导致用户看到的可执行意图超过了产品真实能力边界。

## 修复方向

1. 建立产品命令能力矩阵，区分“仅展示”“demo 模拟”“真实候选写入”“真实应用写入”四种状态。
2. 先补齐 `/bug-generate` 产品链路，与 `/req-generate` 对称支持 BUG capture 到 `bug.md` / draft 投影。
3. 后续按风险分批补齐 complete、review、sprint-propose、req-opsx / bug-opsx、opsx-apply / opsx-archive。
4. 对尚未接入真实写入的命令，前端应明确标注不可执行或提示“尚未接入产品写入链路”，避免显示为成功执行。
5. 每个新增命令链路都应包含后端 prepare、candidate validate、writer kind、前端触发、应用状态查询和回归测试。

## 验证闭环

- 对 `BUG-*` capture 卡片点击 Bug Generate 时，应进入受控治理会话，生成 `bug.md` 候选，并在应用后同步 trace、registry 和 CHANGELOG。
- 对未实现的 complete / review / sprint / opsx 命令，产品应显示明确不可执行状态或接入对应真实写入链路，不得只做本地模拟流转。
- 后端测试覆盖 `governance-preparations` 对 REQ / BUG / 不支持命令的分支。
- 前端测试覆盖非 demo 路径下 BUG 生成入口、未实现命令提示和已实现命令跳转。
- 数据库应产生对应的 governance candidate / application 记录，不能只有普通 Chat turn。

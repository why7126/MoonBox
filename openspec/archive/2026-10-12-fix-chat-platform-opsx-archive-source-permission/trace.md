---
change_id: fix-chat-platform-opsx-archive-source-permission
title: Chat 平台 source 工作区归档权限与状态诊断修复
status: applied
created_at: '2026-10-04 11:17:53'
updated_at: 2026-10-10 07:33:22
bug: BUG-0026-chat-platform-opsx-archive-source-permission
requirement: null
sprint: sprint-008
product_data_collection_observability:
  status: applicable
  affected_layers:
    - request_logs
    - task_traces
    - task_trace_spans
    - chat_turns
    - usage_events
  reason: 修复涉及 Chat 执行状态、错误码、执行事件和治理事实源归档链路。
  validation: 已运行相关 pytest、Change 身份校验和中文校验；AF-015 产品轮次 d720688b-5667-43a7-a891-ed26e31197e3 首次归档完成，脚本退出 0，Workflow Sync 0 errors，Chat 终态 completed；既有观测层契约不变。关联 Issue promote、普通命令负向及 copy 模式独立产品验收仍待完成。
execution:
  schema_version: 1
  started_at: 2026-10-04 11:21:57
  completed_at: 2026-10-04 12:39:26
  last_event: opsx.apply
---

# Chat 平台 source 工作区归档权限与状态诊断修复

## 来源

- 缺陷：`BUG-0026-chat-platform-opsx-archive-source-permission`
- 迭代：`sprint-008`

## 初始证据

- Chat turn `2ba76ae6-c0ad-4f30-a2d1-b8b10486e15c` 为 `unknown/platform_execution_setup_failed`，且 `executor_turn_id` 为空。
- 上一轮执行端已报告 `openspec/specs/` 与 `openspec/archive/` 无写权限。
- Docker Compose 渲染显示 source 模式已生效，但 worker 源仓库挂载为只读。
- `moonbox-governance` permission profile 不包含归档所需写入路径。

## 验证记录

AF-015：产品专用样本 `verify-chat-archive-history-transition` 从 Firefox 需求中心卡片进入对象 Chat，轮次 `d720688b-5667-43a7-a891-ed26e31197e3` 首次归档完成。标准脚本命令事件 127 为 completed/exit_code 0，唯一标准目录、规格单次合并和 sprint-009 Workflow Sync 为 archived；轮次事件 400 与数据库终态均为 completed，未执行宿主恢复。产品对话和轨迹截图见 `evidence/20261012-product-archive-success.png`、`evidence/20261012-product-archive-trace-completed.png`。本轮没有关联 Issue，故不证明同轮 Issue promote；普通治理命令负向与 copy 模式产品证据仍待补齐。完整返修与前序失败证据见 `acceptance-fixes.md` AF-015。

AF-013：专用样本 `verify-chat-source-archive-e2e` 的前两次产品轮次在 executor 前因 `pnpm` / `openspec` 冷启动预检误判失败；第三轮通过预检并完成 CLI 规格合并、旧目录移动后在标准目录迁移间隙成为 `unknown/write_permission_revoked`。宿主唯一归档恢复成功，不计为产品同轮验收。已延长包工具和部署健康探针限时，并为同一授权归档轮次增加严格限定的旧目录迁移权限；18 项聚焦测试及标准部署通过，仍待新产品轮次复验。完整证据见 `acceptance-fixes.md` AF-013；九项 AC 保持 pending。

AF-014：替代样本 `verify-chat-archive-transition-window` 的新产品轮次在标准目录已出现但 Workflow Sync 尚未完成时成为 `unknown/execution_access_or_workspace_error`。失败测试复现“完整 CLI 旧源 + 部分标准目标”被误判只读；已将同轮唯一同名部分目标纳入过渡权限，冲突目标仍阻断。聚焦回归通过，完整证据见 `acceptance-fixes.md` AF-014。样本现为半归档，宿主恢复与新样本首次产品归档须分别记录；BUG 九项 AC 保持 pending。

2026-10-11 产品首次归档取证：`add-git-sync-skill` 对象 Chat 获得归档可写权限并完成真实目录移动与三条规格合并，但轮次在最后命令未返回完成结果时停止，用量待核实；产品原轮次重试请求失败。宿主唯一归档续跑完成验证和 Workflow Sync，不算产品轮次成功。BUG-0026 九项验收继续 pending；详见 `acceptance-fixes.md` 与 Issue `acceptance.md` 的本日记录。

AF-011：BUG-0026 新增全仓自有目录空工具残留反馈，宿主发现并确认八个目标为空；扩展目录校验后先报告八项失败，安全移除后通过。工具路径单元测试 3 项、Chat 后端全套 48 passed/1 skipped、同款执行器镜像离线隔离探针 1 项通过，探针确认 12 个执行时空路径及退出后宿主清理无残留。OpenSpec strict、中文优先、目录结构、Agent 上下文预算、Sprint Scope 和产品数据采集与链路观测聚焦校验均通过；Workflow Sync `opsx.modify` 0 errors/0 blockers，BUG 验收保持 pending，AI Usage hook warning/unavailable。真实产品新轮次尚未观察，保持待复验。完整证据见 `acceptance-fixes.md` AF-011。该新增范围未改变 canonical `applied`、首次 `execution.completed_at` 或原归档验收结论。

AF-012：Issue `acceptance.md` 原七条 AC 仅在表格中，需求中心复选框计数得到零，显示“验收结论待核实”。现增加九条未勾选 AC 核对清单（原七条加全仓工具目录与真实归档复验两条），保留表格执行证据和 `pending` 结论；本地真实页面显示“验收 0/9”，点击打开 Issue 验收文档，归档门禁保持阻断。直接调用后端投影得 `(9, 9)`，完整对照与验证见 `acceptance-fixes.md` AF-012。未修改前后端逻辑或 canonical `applied` 事实。

AF-009：REQ-0043 产品截图确认移动后目录校验阻断；宿主四路径均不存在，唯一 archive 已存在但 Issue 尚未同步。执行沙箱空挂载点采用独立设备判定；真实空目录会被遮蔽，故 worker 启动归档沙箱前从真实工作区视图阻断。标准脚本在移动前预校验。聚焦测试 15 项、宿主目录校验及同款归档沙箱真实目录校验通过，后者只报告四项临时挂载警告。产品端归档复验待完成；完整证据及 BUG 子文档扫尾见 `acceptance-fixes.md` AF-009。首次 apply 时间不变。

AF-009 部署补证：标准部署完成，五个服务健康；运行中的 chat-worker 已加载新预检，Chat 模块全套 46 passed、1 skipped。Workflow Sync `opsx.modify` 成功且验收保持 pending；AI Usage warning/unavailable。真实 REQ-0043 的半归档收尾尚未续跑。

AF-008：标准脚本跨设备安全迁移与半归档续跑；权限支持唯一同身份 archive 与 Issue promote 迁移间隙；保留命令完成、可信收据幂等结算；修复流式队列溢出与无 HOME 用量发现。相关测试 88 passed，1 skipped。真实产品轮次 `12822d4c-c26d-4c3a-8ab3-8050d3103dd1` completed、脚本 exit_code=0、结果可见、最终用量 242062 已 settled；验证已有目录恢复，不重复合并。完整证据见 `acceptance-fixes.md` AF-008；首次 apply 完成时间保持不变。

- `python scripts/validate-change-identity.py`：通过。
- `uv run pytest src/backend/tests/test_chat.py src/backend/tests/test_chat_platform.py tests/unit/test_change_identity.py -q`：57 passed，1 skipped。
- `python scripts/validate-openspec-language.py --change fix-chat-platform-opsx-archive-source-permission --residual-report`：当前 Change 中文校验通过，全仓残留分离报告未发现非当前 Change 中文残留。

## 运行态说明

本次已覆盖策略、权限 profile、source 挂载配置、启动前失败终态和 Change 身份脚本回归。真实 Docker worker 需要在重建 `chat-worker` 后复验 `/opsx-archive` 端到端归档。

## 验收返修记录

| 时间 | 批次 | 反馈摘要 | 调整摘要 | 验证摘要 | 台账 |
|---|---|---|---|---|---|
| 2026-10-04 14:43:02 | AF-001 | source 工作区 `run_claim` 在 `_workspace_identity` 前被旧目录名校验拒绝 | 移除旧前置校验，source/copy 均由 `_workspace_identity` 统一判定；新增 source 模式 `run_claim` 回归测试 | 3 项聚焦 pytest 通过 | `acceptance-fixes.md` |
| 2026-10-04 15:11:36 | AF-002 | 重启后 BUG-0024 archive 新轮次仍在 `workspace_prepare` 报 `workspace_binding_mismatch` | source root 验证通过后允许旧 copy 会话 `workspace_id == conversation_id` 迁移为 `source`，并同步既有 baseline | 4 项聚焦 pytest 通过；Chat 平台相关套件 59 passed，1 skipped | `acceptance-fixes.md` |
| 2026-10-04 22:37:41 | AF-003 | BUG-0024 最新 archive 轮次在 `workspace_prepare` 报 `execution_access_or_workspace_error`，容器内复现为 source 快照超过容量边界 | Git 仓库快照改用 `git ls-files -co --exclude-standard` 枚举 tracked 与未忽略 untracked 文件，排除 ignored runtime 数据 | workspace 6 项通过；workspace + source run_claim 聚焦 10 项通过；真实仓库探针显示 `data/runtime/**` 被排除 | `acceptance-fixes.md` |
| 2026-10-04 22:52:15 | AF-004 | BUG-0024 最新 archive 轮次在 `workspace_prepare` 报 `container_mount_overlap` | Chat 私有执行数据目录禁止位于 source root 内；启动脚本自动将旧仓库内配置迁移到源仓库同级私有目录 | 平台与 workspace 15 项通过；`docker-up --check` 通过 | `acceptance-fixes.md` |
| 2026-10-04 23:31:06 | AF-005 | BUG-0024 最新 archive 轮次已完成但输出为空，执行摘要显示 archive/specs 仍只读 | 归档写策略兼容旧版 `source_bug` / `source_requirement` trace 字段；API schema 与前端标签同步 `archive_write` | 归档策略聚焦 3 项通过；Composer 17 项通过 | `acceptance-fixes.md` |
| 2026-10-05 00:42:18 | AF-006 | 产品卡片执行 `/opsx-archive` 仍失败；确认产品意图是跳转对象 Chat 并由 Agent 归档 | 移除产品直归档 API 方案；需求中心归档按钮继续使用对象会话并填入 `/opsx-archive` prompt；setup 失败日志补充 `cause_type` | 后端 46 项通过；前端 112 项通过；TypeScript 与后端 py_compile 通过 | `acceptance-fixes.md` |
| 2026-10-05 12:13:08 | AF-007 | BUG-0027 source 对象会话在 `workspace_prepare` 阶段因 baseline `workspace_id=source` 唯一约束冲突失败 | source 模式 baseline 存储键改为按会话独立，conversation 仍记录 `workspace_id=source`；补充两个 source 对象会话共享 source root 的回归测试 | source 聚焦 3 项通过；Chat 平台相关套件 60 passed，1 skipped | `acceptance-fixes.md` |

AF-010：17:33 真实产品复验再次证实目录校验 exit 1；根因为命令环境清空继承变量，且宿主出现执行时空目录。改由私有 Chat 命令标记识别并由 worker 归档前后清理空残留；非空与符号链接仍阻断。60 passed、1 skipped；OpenSpec strict 通过。完整台账见 `acceptance-fixes.md`。

AF-016 验收结论：BUG-0042 关联 Issue 专用虚拟样本在 MoonBox source 对象 Chat 中首次归档，产品轮次 `489d335c-a077-4734-b0b0-4fcc4babfb1b` 为 completed；标准脚本命令 completed/exit_code=0，规格新增、唯一标准目录、Workflow Sync 0 errors 与 Issue promote 至 archive/done 同轮完成。BUG-0026 AC-001 签收，九项 AC 9/9。BUG-0040/0041 的 stopped 轮次单独留证，不计成功。完整事实与截图见 `acceptance-fixes.md` AF-016 及 `evidence/20261012-bug0042-ac001-product-proof.md`。

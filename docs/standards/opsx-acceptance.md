---
purpose: OpenSpec 自动验收与证据包标准
created_at: 2026-10-12 14:59:30
updated_at: 2026-10-17 16:40:21
---

# OpenSpec 自动验收与证据包

## 事实源

`acceptance-plan.json` 是 Change 的逐 AC 执行计划；`evidence/acceptance/<run-id>/manifest.json` 是一次运行的机器结论；同目录 `summary.md` 是人类摘要。Issue `acceptance.md` 保存最终签认与链接，Change `trace.md` 保存简短入口，Sprint `acceptance-report.md` 只做聚合。原始产品 Chat、事件、数据库和本地 `logs/` 保持在其授权来源，不直接提交；长期证据仅保留脱敏投影。归档时整个证据目录随 Change 迁移。

已归档 Change 的原完整 manifest 不因后续单个附件变化而改写。若命令型 AC 的附件在归档后变化，可运行 `python scripts/create-archived-acceptance-supplement.py --change <change-id> --check <AC-id>` 重跑原计划命令并在 `evidence/acceptance/supplements/` 生成独立补证。生成前要求原 manifest 为完整 passed、目标 AC 为命令型 passed，且其余 AC 附件仍匹配。Workflow Sync 复核补证绑定的原运行、命令、当前输入指纹、旧/新附件哈希和退出码；任何字段或文件变化均使补证失效。补证仅确认该 AC 的变更附件，不声明其他 AC 在本轮重跑，也不适用于产品轮次或视觉 AC。

## 计划格式

计划 JSON 必填 `schema_version: 1`、`change_id` 和非空 `checks`。每条检查包含唯一 `AC-*` ID、`kind`、非空项目相对路径 `inputs`；命令检查用 `argv` 数组，产品轮次检查用 `turn_id` 与 `command_contains`。可声明环境标签 `environment`、`preflight` argv、`timeout_seconds`、安全命令的 `safe_retries`（最多 2）、`effects`（`exists`、`absent`、`contains`）及经脱敏的 `artifacts`。证据文件记录 SHA-256，缺失、过大或后续被改动均使结论过期；本地 `data/`、`logs/`、`tmp/` 不可作为长期证据路径。只有确认互不写同一状态的命令检查才能声明 `parallel_safe: true`，最多三个并行；产品归档、Sprint/Issue 状态写入和样本生成必须串行。预检失败阻断依赖项；脚本不使用 shell 执行字符串。

编制计划时逐项列出 AC 的证据类型（命令回归、真实产品轮次、UI 截图与 computed style、文件状态）及必要样本范围；可在检查中声明 `evidence_kinds`（`command`、`product_turn`、`visual`、`file_state`）。声明 `visual` 时还须声明非空 `artifacts`、`coverage.stages`、`coverage.viewports` 和 `coverage.samples`。每个 `samples` 条目用 `stage`、`viewport` 和非空 `artifacts` 将一个阶段×视口组合映射到该 AC 已声明的脱敏文件；不适用组合用 `not_applicable: true` 和非空 `reason` 说明。所有组合必须恰好有一个映射，不能只填阶段、视口两个列表。视觉计划还须提供可执行的计划级 `preflight`，检查浏览器依赖及目标环境。文件存在、哈希和矩阵完整性由脚本检查；截图内容、计算样式与产品语义仍由验收者目视核对，命令退出 0 不替代视觉事实。

执行 AC 前，脚本检查命令可用性、授权产品 SQLite 数据源、声明的证据文件和视觉矩阵，再执行计划预检。任一项未就绪时，不执行目标 AC；本轮只发布 `blocked / diagnostic` 清单并列出缺口，不把缺浏览器或缺证据记成功能失败，也不覆盖最近完整清单。旧视觉计划若只有阶段与视口列表，在新运行中报 `legacy-coverage-unmapped`，补齐映射后才继续；已归档历史清单不追写。摘要逐 AC 显示检查来源、证据类型、脱敏证据路径和缺口；文件路径只是入口，人工视觉核对仍须在 Issue 验收记录或 Change trace 中签认。

产品轮次正向检查需同时满足：轮次 `completed`、同轮 `execution.tool` 中目标命令 `completed/exit_code=0`、所有声明的文件效果成立。负向归档门禁检查可显式声明 `expected_exit_code: 1` 与 `require_acceptance_gate_blocked: true`；此时只有同轮目标命令以 1 退出且工具结果含 `ACCEPTANCE_GATE_BLOCKED` 标记，并且 Change 仍存在等文件效果成立才通过。普通命令失败或仅模型口头拒绝不算命中门禁。`stopped`、`unknown`、命令未完成或仅宿主恢复均不通过。UI 场景仍需按原型或参考稿门禁补截图和 computed style 证据；不能用数据库事件替代视觉事实。

负向 AC 的计划预检必须确认预期退出码为 1、启用专属标记判定，并声明至少一个保持原状态的 `effects`。执行前先排除任务未完成、规格校验失败等更早阻断；若命令虽失败却未触达目标门禁，不签认该 AC。副作用命令只在既有授权范围内执行，不自动重试。

## 增量与归档

每条 AC 的计划片段与 `inputs` 文件内容生成指纹。清单保留 Git HEAD 供定位，未提交改动仍以逐 AC 输入指纹为准。旧 AC 只有在原结论 passed、指纹未变、效果仍成立且证据文件哈希匹配时才能复用。`/opsx-modify` 后重跑受影响 AC；没有 `inputs` 的计划无效。`--readiness` 只读核对最新清单与当前输入，不运行检查。新计划存在时归档门禁要求 ready；历史 Change 不补造计划或验收结论，仍按原有交付证据规则处理。

若检查声明 `required_sample.status`，仅 `passed` 可让该 AC 通过和复用；`partial`、`pending` 即使命令退出 0、证据路径存在，也在报告中标为 `blocked / sample-incomplete`，readiness 保持未就绪。该字段记录逐项产品或视觉证据的签认状态，命令探针不替代整项签认。

Issue `acceptance.md` 作为输入时，指纹包含验收条件、复选框和人工正文；排除 Workflow Sync 派生的 frontmatter `updated_at`、`acceptance_status` 及 `## 验收结果回填` 整段。同步时间与证据包链接刷新因此不会使刚完成的清单失效；验收条件或勾选状态变化仍会使对应 AC 过期。

清单有 `scope: complete | diagnostic`：仅当每条 AC 本轮执行或有效复用、没有 `not-selected` 时才是 `complete`。`--only` 缺少其他有效 AC 结论时生成 `diagnostic`；该清单保留单项证据，但不替代最新完整清单，也不能独自提升整体 ready。较新的诊断若明确测出某项失败且输入指纹仍匹配，则撤销该项较早的完整通过结论；`not-selected` 不构成失败。后续完整运行可以分别复用诊断和完整清单中指纹、效果及证据哈希仍有效的通过项。旧清单缺 `scope` 时按完整清单兼容，但含 `not-selected` 的旧清单不作为完整基线。生成器先写暂存目录，核对清单 JSON、摘要标题、逐 AC 行与总状态一致，再原子发布；不完整报告不得成为最新清单。

产品样本应优先使用已授权的隔离验证环境和已有会话。需要正式 BUG/Change 首次归档时，须遵守评审、Sprint、Change 身份和用户授权；同一失败轮次不通过文件事后迁移冒充成功。样本生成应幂等，失败轮次保留原因，并限制重试次数。共享 Docker/OrbStack 重启等影响其他项目的动作不属于自动验收的默认权限。

## 数据采集与安全

`product_data_collection_observability: applicable`，`affected_layers: [agent_workflow, chat_events]`。脚本只读提取轮次 ID、会话 ID、终态、错误码、目标命令事件序号与退出码；负向门禁仅记录标记是否出现，不保存工具原始结果。usage_events、request_logs、task_traces、task_trace_spans 的新增或修改均 N/A，不新增 API 或 DB schema。校验：产品终态与命令事件同轮关联、失败轮次不通过、无原始 prompt/消息/事件正文入库或入仓。若产品数据源是 MySQL，需提供等价的授权只读适配器或既有 API 导出，不能把 SQLite 检查冒称覆盖 MySQL。

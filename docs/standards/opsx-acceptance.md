---
purpose: OpenSpec 自动验收与证据包标准
created_at: 2026-10-12 14:59:30
updated_at: '2026-10-20 20:09:32'
---

# OpenSpec 自动验收与证据包

## 事实源

`acceptance-plan.json` 是 Change 的逐 AC 执行计划；`evidence/acceptance/<run-id>/manifest.json` 是一次运行的机器结论；同目录 `summary.md` 是人类摘要。Issue `acceptance.md` 保存最终签认与链接，Change `trace.md` 保存简短入口，Sprint `acceptance-report.md` 只做聚合。原始产品 Chat、事件、数据库和本地 `logs/` 保持在其授权来源，不直接提交；长期证据仅保留脱敏投影。归档时整个证据目录随 Change 迁移。

已归档 Change 的原完整 manifest 不因后续单个附件变化而改写。若命令型 AC 的附件在归档后变化，可运行 `python scripts/create-archived-acceptance-supplement.py --change <change-id> --check <AC-id>` 重跑原计划命令并在 `evidence/acceptance/supplements/` 生成独立补证。生成前要求原 manifest 为完整 passed、目标 AC 为命令型 passed，且其余 AC 附件仍匹配。Workflow Sync 复核补证绑定的原运行、命令、当前输入指纹、旧/新附件哈希和退出码；任何字段或文件变化均使补证失效。补证仅确认该 AC 的变更附件，不声明其他 AC 在本轮重跑，也不适用于产品轮次或视觉 AC。

## 计划格式

计划 JSON 必填 `schema_version: 1`、`change_id` 和非空 `checks`。每条检查包含唯一 `AC-*` ID、`kind`、非空项目相对路径 `inputs`；命令检查用 `argv` 数组，产品轮次检查用 `turn_id` 与 `command_contains`。可声明环境标签 `environment`、`preflight` argv、`timeout_seconds`、安全命令的 `safe_retries`（最多 2）、`effects`（`exists`、`absent`、`contains`）及经脱敏的 `artifacts`。证据文件记录 SHA-256，缺失、过大或后续被改动均使结论过期；本地 `data/`、`logs/`、`tmp/` 不可作为长期证据路径。旧 `parallel_safe` 作为兼容提示保留；当前调度按依赖串行执行，产品归档、Sprint/Issue 状态写入和样本生成必须串行。预检失败只阻断依赖项；脚本不使用 shell 执行字符串。

编制计划时逐项列出 AC 的证据类型（命令回归、真实产品轮次、UI 截图与 computed style、文件状态）及必要样本范围；可在检查中声明 `evidence_kinds`（`command`、`product_turn`、`visual`、`file_state`）。声明 `visual` 时还须声明非空 `artifacts`、`coverage.stages`、`coverage.viewports` 和 `coverage.samples`。每个 `samples` 条目用 `stage`、`viewport` 和非空 `artifacts` 将一个阶段×视口组合映射到该 AC 已声明的脱敏文件；不适用组合用 `not_applicable: true` 和非空 `reason` 说明。所有组合必须恰好有一个映射，不能只填阶段、视口两个列表。视觉计划还须提供可执行的公共或逐项 `preflight`，检查浏览器依赖及目标环境。文件存在、哈希和矩阵完整性由脚本检查；截图内容、计算样式与产品语义仍由验收者目视核对，命令退出 0 不替代视觉事实。

执行 AC 前，脚本检查命令可用性、授权产品 SQLite 数据源、声明的证据文件和视觉矩阵，再执行计划预检。单项未就绪时仅阻断该 AC 与依赖项，其他就绪项继续；缺口发布 `blocked / diagnostic` 清单并列出缺口，不把缺浏览器或缺证据记成功能失败，也不覆盖最近完整清单。旧视觉计划若只有阶段与视口列表，在新运行中报 `legacy-coverage-unmapped`，补齐映射后才继续；已归档历史清单不追写。摘要逐 AC 显示检查来源、证据类型、脱敏证据路径和缺口；文件路径只是入口，人工视觉核对仍须在 Issue 验收记录或 Change trace 中签认。

产品轮次正向检查默认需同时满足：轮次 `completed`、同轮 `execution.tool` 中目标命令 `completed/exit_code=0`、所有声明的文件效果成立。直接受控 Sprint 归档不产生模型工具事件；此类计划须显式声明 `execution_proof: trusted_archive_v1`、精确 `trusted_archive_object_id` 与 `/sprint-archive sprint-xxx` 命令，核对同轮受控归档开始、零模型用量、完成事件、主对象身份及持久归档操作 `completed`，不能伪造命令事件。负向归档门禁检查可显式声明 `expected_exit_code: 1` 与 `require_acceptance_gate_blocked: true`；此时只有同轮目标命令以 1 退出且工具结果含 `ACCEPTANCE_GATE_BLOCKED` 标记，并且 Change 仍存在等文件效果成立才通过。普通命令失败或仅模型口头拒绝不算命中门禁。`stopped`、`unknown`、命令未完成或仅宿主恢复均不通过。UI 场景仍需按原型或参考稿门禁补截图和 computed style 证据；不能用数据库事件替代视觉事实。

负向 AC 的计划预检必须确认预期退出码为 1、启用专属标记判定，并声明至少一个保持原状态的 `effects`。执行前先排除任务未完成、规格校验失败等更早阻断；若命令虽失败却未触达目标门禁，不签认该 AC。副作用命令只在既有授权范围内执行，不自动重试。

## 增量与归档

每条 AC 的计划片段与 `inputs` 文件内容生成指纹。清单保留 Git HEAD 供定位，未提交改动仍以逐 AC 输入指纹为准。旧 AC 只有在原结论 passed、指纹未变、效果仍成立且证据文件哈希匹配时才能复用。`/opsx-modify` 后重跑受影响 AC；没有 `inputs` 的计划无效。`--readiness` 只读核对最新清单与当前输入，不运行检查。新计划存在时归档门禁要求 ready；历史 Change 不补造计划或验收结论，仍按原有交付证据规则处理。

若检查声明 `required_sample.status`，仅 `passed` 可让该 AC 通过和复用；`partial`、`pending` 即使命令退出 0、证据路径存在，也在报告中标为 `blocked / sample-incomplete`，readiness 保持未就绪。该字段记录逐项产品或视觉证据的签认状态，命令探针不替代整项签认。

Issue `acceptance.md` 作为输入时，指纹包含验收条件、复选框和人工正文；排除 Workflow Sync 派生的 frontmatter `updated_at`、`acceptance_status` 及 `## 验收结果回填` 整段。同步时间与证据包链接刷新因此不会使刚完成的清单失效；验收条件或勾选状态变化仍会使对应 AC 过期。

清单有 `scope: complete | diagnostic`：仅当每条 AC 本轮执行或有效复用、没有 `not-selected` 时才是 `complete`。`--only` 缺少其他有效 AC 结论时生成 `diagnostic`；该清单保留单项证据，但不替代最新完整清单，也不能独自提升整体 ready。较新的诊断若明确测出某项失败且输入指纹仍匹配，则撤销该项较早的完整通过结论；`not-selected` 不构成失败。后续完整运行可以分别复用诊断和完整清单中指纹、效果及证据哈希仍有效的通过项。旧清单缺 `scope` 时按完整清单兼容，但含 `not-selected` 的旧清单不作为完整基线。生成器先写暂存目录，核对清单 JSON、摘要标题、逐 AC 行与总状态一致，再原子发布；不完整报告不得成为最新清单。

产品样本应优先使用已授权的隔离验证环境和已有会话。需要正式 BUG/Change 首次归档时，须遵守评审、Sprint、Change 身份和用户授权；同一失败轮次不通过文件事后迁移冒充成功。样本生成应幂等，失败轮次保留原因，并限制重试次数。共享 Docker/OrbStack 重启等影响其他项目的动作不属于自动验收的默认权限。

## 数据采集与安全

`product_data_collection_observability: applicable`，`affected_layers: [agent_workflow, chat_events]`。脚本只读提取轮次 ID、会话 ID、终态、错误码与所声明的执行证明：旧式工具路径记录目标命令事件序号与退出码，直接受控归档路径记录归档操作阶段和零模型用量；负向门禁仅记录标记是否出现，不保存工具原始结果。usage_events、request_logs、task_traces、task_trace_spans 的新增或修改均 N/A，不新增 API 或 DB schema。校验：产品终态与所选证明同轮关联、失败轮次不通过、无原始 prompt/消息/事件正文入库或入仓。若产品数据源是 MySQL，需提供等价的授权只读适配器或既有 API 导出，不能把 SQLite 检查冒称覆盖 MySQL。

## 连续执行与恢复契约

`/opsx-accept` 是 Agent 编排入口，`opsx_acceptance.py` 是确定性检查器。先用 `--queue` 只读生成逐 AC 下一动作；Agent 在已有授权内完成样本准备、产品动作、截图与签认，再运行检查器。检查器不创建产品对象、不自动授予写权限，不把已有 turn 核验声称为新产品操作。

只要仍有可执行 AC 或可自主补齐的证据，就继续当前命令。缺少本轮应生成的证据为 `pending_collection`，不是结束条件；只有无可行替代的必要环境、授权或人工输入缺失才停止相关项。用户停止立即停止。副作用操作不原样自动重试，不自动创建正式 follow-up Issue/Change。环境恢复、取证、范围内返修和复验均保留检查点，不要求用户反复输入“继续”。

公共 `preflight` 只放真正影响整个执行环境的检查；单项 `preflight` 与 `depends_on` 只影响当前 AC 和依赖项。未知依赖和依赖环直接拒绝。脚本当前顺序执行拓扑就绪项；保留旧 `parallel_safe` 字段兼容读取，但不以该字段启动并行副作用。每项完成后在 `evidence/acceptance/checkpoints/` 发布 diagnostic 检查点，恢复时按指纹、效果和附件哈希复用。检查点不单独构成整体 ready，较新的真实失败仍撤销旧通过。

`collection.state` 可选 `pending|collecting|collected|blocked`，未 collected 不签认；产品 `turn_id` 可为 null，表示等待采集，不能伪造 pending ID。结果 `collection_state` 为 passed、failed、blocked 或 pending_collection；stale 由 readiness 与指纹计算。`--queue` 输出下一动作和局部缺口，不推进状态。人工签认仍由 Agent 按证据完成，collection 字段不构成权限证明。

命令生成的证据可以用 `produces_artifacts` 声明，必须是当前 command 的 artifacts 子集；这些文件不要求运行前存在，运行后仍检查存在性和哈希。已有产品证据、视觉截图不能靠该字段豁免真实采集或签认。失败清单保留证据，不删除历史失败以换取通过。

## 精确输入与执行去重

`inputs` 默认仍采用全文内容指纹；可选 `input_sections` 为路径到精确 Markdown 标题列表的映射，仅对被选章节及其下级正文取指纹。标题缺失或重复时拒绝，禁止用过窄切片忽略代码、验收条件或公共契约变化。每项必须列出全部实际实现依赖；不要把追加式 trace、tasks 进度或整份 acceptance 当成所有 AC 的共同输入。代码文件继续使用全文。依赖 AC 的定义与输入递归参与下游指纹，新计划声明 `orchestration_version: 1`，环境标签与公共预检参与指纹；环境契约及依赖定义始终参与。旧计划不回写、不改变原有指纹算法，避免历史归档证据被追溯失效。

无副作用且可共享执行的命令显式声明 `deduplicate: true`。只有同一轮内 argv、输入内容、环境契约、超时、重试和局部预检相同且命令成功才复用执行结果；每项仍单独检查 effects、artifacts 和 required_sample。失败不缓存。测试执行中输入变化使结果 blocked，不发布虚假通过。不同产品轮次不可拼接冒充同轮完成。

## 环境、样本与浏览器

需要真实产品或视觉采集的新计划应声明 `environment_contract`：deployment（部署别名）、workspace_mode（source/isolated/readonly）、sample_scope（样本范围）、authorization_ref（授权摘要引用）、login_strategy（已有会话或授权测试账号取得方式）、retry_limit（0至2）、cleanup_after（固定 evidence-and-recovery-verified）、browser_capabilities（screenshot/viewport/computed_style/network/console 中的所需项）。这些字段只记录脱敏标签，不保存凭证、本机路径或原始会话。

运行前核对原部署与隔离环境的适用性，不能完成隔离验证后冒称原部署通过。优先复用 Codex 侧边浏览器和登录态；按所需能力实际验证，记录后备入口切换原因。无法自主取得测试账号时才请求协助，不向用户索要密码。授权覆盖环境、动作与额度；已有授权内续接不重复询问，超范围才补充确认。测试样本在证据提取、完整验收与恢复验证完成后清理；失败样本先保留脱敏诊断，临时数据库不提交。纯治理检查不要求产品视觉证据。

## 归档预检与收尾

AC 全部通过后，执行 `python scripts/archive-recovery-guard.py CHANGE --preview`，在临时副本检查 delta 分类、Requirement 匹配和实际规格合并。`CHANGE` 是已解析的实际 Change ID。预演不写正式规格、归档目录、恢复日志或 Issue；不代表归档授权。分别报告 AC 结论、归档预检结论和是否已获正式归档授权。

正式归档继续使用 `archive-change.sh --finalize` 串行闭环。成功后只核对结果，不重复执行技能中列出的底层同步、晋级与 usage hook。中断时依据恢复日志核对已合并/已迁移状态，重跑 wrapper 续接；现有幂等收尾步骤可为核对当前状态再次运行，不承诺外部副作用 exactly-once。未知外部规格变化仍阻断，不直接修饰已归档事实。

## 耗时与质量指标

manifest.metrics 记录本轮 duration_ms、preflight_ms、command_executions、deduplicated、reused、blocked、failed；复用项 duration_ms 为0，避免把历史时长累计为本轮耗时。可选 `--activity-file` 读取仅含 phase、duration_ms、human_intervention 的数组，phase 只能为 environment/collection/testing/repair/waiting/archive；拒绝原文和任意额外字段。聚合结果标记 reported，与脚本实测指标分开；未提供时 unavailable，不猜测浏览器、模型思考和人工等待耗时。

同组夹具分别比较优化前的执行次数、局部阻塞和优化后的结果；记录合成回归与实际脚本运行，不能推算真实产品全链路提速比例。交付状态、证据状态、AI Usage 状态独立报告；用量无法归因只聚合一次 warning，可用已有 extractor 的显式 session 参数回填，不为采集用量重复执行验收。

## 稳定批次与增量复验契约

### 完整入口前置检查

高成本测试、真实模型样本或部署前，MUST 在现有 Change trace、test-plan 或返修台账记录最小入口矩阵，不额外复制一套报告。每行包含入口、事实源/字段形态、工作区与部署版本、正向/拒绝场景、最小探针、对应 AC 和证据入口。按实际影响覆盖 CLI、产品展示、执行准备、执行器权限、完成证明和归档；不适用项说明原因。覆盖正式对象使用的字段别名、旧数据和 source/isolated/投影目录差异。先运行低成本、只读或已授权的最小探针；未实现路径记录待验证，不能伪造通过。

隔离样本应代表目标数据形态；隔离成功不能替代正式入口只读核验。正式写操作、模型发送和额外调用额度仍按既有授权，入口矩阵不扩大权限。前置探针不替代最终全链路与负向验收。

### 修改稳定后集中验证

将工作组织为：入口检查 → 实现与文档修改 → 定向回归 → 本批输入稳定 → 必要构建/部署与版本核对 → 集中验收 → 串行 Workflow Sync → 当前 readiness 与产品入口复核。开发期间允许快速测试；长测试、模型样本和部署尽量在相关输入稳定后执行。按依赖选择测试环境，不强制所有测试等待部署。纯治理无产品部署时记录 N/A。

稳定批次记录输入范围、指纹或版本、目标环境及待执行检查；不是 Git 提交要求，不冻结无关工作。MUST 避免同时修改正在验证或构建的输入。确有修改时标记受影响结果失效，完成修改后复验，不把旧镜像或旧证据算作当前版本。共享 Sprint/Issue 写入与正式入口核验串行；互不影响的只读检查可并行。不得因优化顺序跳过必要部署、真实视觉或归档预演。

### 受影响范围增量复验

每次修复先列变更文件/契约 → AC → 下游依赖闭包 → 环境和附件，给出复用或重跑理由。代码输入保持全文；公共权限、状态机、执行器、环境契约变化应扩大到所有相关入口。无法可靠界定影响时扩大验证，不以缩窄 inputs 换取通过。文档语义变化照常失效；仅既有标准明确排除的派生字段可免失效。

优先使用当前检查器的逐 AC 成功清单/检查点复用；复用仍要求指纹、环境、effects、附件哈希与签认有效，较新的真实失败撤销旧通过。`--only` 是诊断，不替代完整 readiness；最终所有 AC 必须有当前有效证据。不重复执行已有效的独立项，也不把未选项记作失败。

命令去重仍遵守“精确输入与执行去重”：当前只支持单轮成功命令共享，不承诺跨轮或跨 Change 命令缓存。出现相同失败命令时先保留脱敏失败摘要、退出码、输入版本与日志入口，定位和修复共同原因后再调度；不得把失败缓存成通过、自动重试副作用或删除失败证据。原始日志仅保留在授权且被忽略的本地位置。跨轮成功证据复用与命令结果缓存必须区别报告。

### 里程碑进度反馈

进度区分实现完成、定向回归通过、部署版本核对、产品入口通过、联合验收完成；只在对应证据齐全后使用该结论。未完成完整入口验证时不得称“最终完成”，不反复承诺“最后一次”。新发现、阶段变化、真实阻塞与授权需求及时说明；长时间无变化时按客户端要求给简短状态，合并重复消息，不逐条转述轮询或完整日志。

优先事件/完成通知，持续运行任务采用适度退避的有界等待，避免无变化时高频短轮询；不得以减少消息为由失联、停止可执行工作或延迟报告失败。耗时只报告实测范围，区分并行墙钟、命令累计与人工等待；不能相加并行时长或宣称未经测量的提速比例。

本契约只优化编排，不降低指纹、真实产品与视觉证据、失败撤销、权限、完整 readiness、归档预演或正式归档授权门禁。

## 归档预演完成事实

预演不得仅依赖退出码：必须拒绝 CLI 明示的失败/Aborted，确认临时 active 消失且归档唯一、内容完整、增量要求实际合入或移除。`scripts/archive-recovery-guard.py --preview` 统一执行该门禁。失败记录不自动删除；显式 `--reprepare` 仅允许正式规格仍匹配旧 baseline，或具有连续、唯一、已完成且增量结果有效的独立归档哈希链；每条边的规格范围不得与当前 Change 重叠。active 必须存在且无归档，修复后预演通过，保存 previous_record 与 baseline_transition。断链、相关范围冲突、未知改动及并发变化继续阻断；已合并结果只允许续接，不自动重置恢复保护。产品和 CLI 共用此只读准入，缺少证据不得仅以 acceptance ready 放行。

## 跨环境输入与目录指纹

产品治理投影仅从配置的可信 source_root 补读 src、scripts、tests 及显式根级输入 AGENTS.md、.gitignore；issues/openspec 等治理内容始终读取当前投影。目录输入按相对成员路径、类型、文件 SHA-256 和空目录确定性编码，增删改名均失效；目录内符号链接、特殊文件和读取失败拒绝。旧单文件指纹保持兼容，旧目录 missing 指纹必须重新验收。部署后核验真实发送准备接口与 CLI 一致，不能仅凭宿主机 ready 声称产品可发送。

## REQ-0046 / BUG-0052 再次验收后归档

再次验收产生的报告与 trace 运行正文属于派生输出，不得使归档恢复记录自失效；交付输入、链路身份、真实证据完整性及并发变化仍受门禁保护。验收收尾后必须通过产品与 CLI 共用的正式准入，验收 passed 不等于归档 ready。错误须区分交付输入变化、旧记录过期、规格基线缺证、身份冲突和记录损坏。
收尾命令使用 `scripts/opsx_acceptance.py --archive-readiness` 指定当前 Change。不新增 API 路由、DB schema 或权限；归档恢复读操作不写记录。

关联链路先归档后，验收证据按唯一已完成归档身份定位，继续核对原内容哈希；活动目录仍存在、归档身份歧义、未完成或证据被篡改时仍阻断。 不修改历史证据清单或将内容差异解释为单纯路径变化。


## 归档条文冲突与验收事实分离

归档连续证明以模块与Requirement标题组合判定冲突，同模块独立条文可承接；同条文修改或删除、重命名、重复标题、未知操作及无法解析的delta拒绝。完整哈希链、唯一已完成归档、交付完整性、最终条文效果与并发复读继续校验，不修改旧manifest或journal。

已归档AC的有效进度与恢复准入分别计算。恢复失败保留有效done/total及具体恢复原因，真实附件损坏只减少受影响有效项；整体ready仍要求全部门禁及人工签认通过。Sprint预检、产品和Workflow Sync共用深层判定，同步在任何终态投影写入前返回失败；Sprint预检的force选项也不豁免深层验收或恢复阻断。无结构化计划的历史Change保持明确的任务/trace fallback，不宣称具备完整自动验收证据。

## 受控兼容追加例外

同条文原要求及原场景完整保留时，可按版本化兼容证明承接新增场景。需要独立审查与回归证据绑定当前 delta、后继验收与完整已完成归档链；读取期间复查引用文件，符号链接、缺证、语义矛盾、不支持结构与并发变化仍拒绝。候选在验收/归档准入执行影响预检，不作为已完成事实。原约束的显式替代不属于本例外。独立证明不改写历史 manifest/journal；产品 API 分项解释条文与签署门禁。

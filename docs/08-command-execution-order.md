---
purpose: 命令执行顺序速查
content: MoonBox REQ/BUG、Sprint、OpenSpec、发布、镜像与产品手册命令的推荐顺序、串行门禁和执行复盘 Hook
created_at: 2026-08-07 23:20:00
updated_at: '2026-09-15 09:46:43'
owner: MoonBox 产品团队
---

# 命令执行顺序速查

本文用于约束 AI 在 MoonBox 中推荐和执行工作流命令的顺序。原则是先评审、再纳入 Sprint、再创建 Change、再实现、再归档，发布链路位于交付闭环之后。

## 标准链路

```text
/req-capture 或 /bug-capture
→ /req-generate 或 /bug-generate
→ /req-complete 或 /bug-complete
→ /req-review 或 /bug-review
→ /sprint-propose
→ /req-opsx 或 /bug-opsx
→ /opsx-apply
→ /opsx-modify（可选）
→ /opsx-archive
→ /sprint-archive
→ /sprint-exps
→ /release-propose
→ /release-prepare
→ /usage-docs-generate 或 /usage-docs-update 或 /usage-docs-validate
→ /image-prepare
→ /image-build
→ /release-publish
```

## REQ / BUG 到 OpenSpec

- 未评审的 REQ/BUG 不得进入 Sprint、不得转 OpenSpec、不得执行开发。
- 已评审 REQ/BUG MUST 先通过 `/sprint-propose` 纳入 Sprint 正式范围，并由 Workflow Sync 同步为 `in_sprint`，再通过 `/req-opsx` 或 `/bug-opsx` 创建 Change。
- `/req-review <REQ-full-id>` 无 flag 时默认评审通过，下一步 MUST 是 `/sprint-propose --req <REQ-full-id>`；`/bug-review <BUG-full-id>` 同理，下一步 MUST 是 `/sprint-propose --bug <BUG-full-id>`。`--approve` 仅作为兼容别名，拒绝或延后必须显式使用反向 flag。
- `/req-opsx` 和 `/bug-opsx` 遇到 `status: approved` 但尚未 `in_sprint` 时 MUST 停止，并提示先运行对应 `/sprint-propose`。
- `/req-opsx` / `/bug-opsx` 完成后 MUST 运行 Workflow Sync，把新 Change 回填到同一个 Sprint 的 `changes[]` 与 `scope_estimates[].change`。
- `/req-opsx` / `/bug-opsx` 生成 Change 后 MUST 运行 `python scripts/validate-openspec-language.py --change <change-id> --residual-report`；当前 Change 中文优先问题阻断当前链路，其他 active Change 残留只进入分离报告和复盘 warning。
- 如果 REQ/BUG 已经纳入 Sprint，但 `/opsx-apply --dry-run` 仍解析不到 Sprint，优先修复 `sprint.yaml` 机器事实源，不要求用户重复口头确认。

## Apply / Modify / Archive

- `/opsx-apply` 前 MUST 通过 `python scripts/sync-workflow-status.py --event opsx.apply --change <change-id> --sprint auto --dry-run` 确认目标 Change 位于 Sprint scope。
- `/opsx-modify` 只用于 `/opsx-apply` 之后、`/opsx-archive` 之前的验收返修；超出原 Change 范围时应创建新 REQ/BUG 或新 Change。
- `/opsx-modify` 执行返修期间用户可见阶段展示为“研发中”；返修完成、验证和 Workflow Sync 通过后自动回到“验收中 / 待复验”。该展示属于返修投影语义，不得用普通 `in_progress` 覆盖 Change 的 `applied` 事实或首次 apply 的 `execution.completed_at`。
- `/opsx-archive` 只能归档已完成 tasks 且 artifact 完整的 Change。
- 归档步骤必须严格串行：归档脚本或 OpenSpec archive → 目录校验 → env ignore 校验 → archive evidence → Workflow Sync → Issue promote → AI Usage。

## Apply 连续执行契约

本节是 `opsx-apply` 与 `openspec-apply-change` 的共同事实源；两份技能 MUST 读取本节。连续执行不豁免 Sprint、根因证据、UI Skeleton 首轮人工确认、权限、安全及必要验收门禁。

### 连续推进

- 一次 apply 授权覆盖当前 Change 范围内实现、补证、自检修复、相关验证、文档回填与状态同步。MUST 按依赖持续推进到完成门禁通过或真实硬阻塞，不得仅因完成一批任务、输出阶段总结、耗时较长或上下文压缩而主动结束等待“继续”。
- 阶段进度使用 commentary；final 只用于完整完成、无法继续的硬阻塞或用户明确停止。用户询问进度或补充信息不等于取消，简短回应后继续承接原目标。
- 范围内编译失败、测试失败、视觉或 computed style 偏差、可补齐的证据和文档缺项，MUST 查明证据后在当前 apply 内修复并重跑受影响检查。自检修复不切换 `/opsx-modify`；该命令留给 apply 已完成后的用户验收返修。
- 实现细节可从已确认设计、现有代码和项目惯例合理推导时自主处理并记录必要假设；不得把普通实现选择升级成用户确认。不得通过删除验收项、降低断言或伪造证据消除失败。

### 硬阻塞与停止

- 只有缺少关键业务或范围决策、必要权限或外部服务、必需人工确认/证据，或与已批准设计存在无法在当前授权内解决的实质冲突，才阻断依赖工作。前置门禁未通过时不得越过门禁实现；已授权且可自主补齐的事实源缺项先修复再复核。
- 遇到工具错误先检查错误证据、已有权限和可行替代路径；重复失败且没有新的有效修复路径时记录阻塞，不得无限原样重试。不得把一次可修复错误直接解释为等待用户指导。
- 局部硬阻塞时继续不依赖它且符合前置门禁的任务；确需输入时一次聚焦 1-3 个关键问题，说明阻塞任务、证据、尝试结果、所需输入及推荐处理路径。已有授权和已回答事项不得重复询问。
- 用户明确停止或撤销授权时立即停止，不为完成剩余独立工作或写检查点而继续操作。平台强制终止、额度或工具不可用如实报告，不承诺自动恢复、自动唤醒或绕过限制。

### 完成门禁

- 每项任务 MUST 在实现及相关验证通过、证据可定位后才勾选；检查失败时保留未完成，已有勾选被新证据推翻时撤回相关勾选。`all_done` 只是任务状态，不能直接作为完成或可归档结论。
- 宣布 apply 完成前 MUST 确认：全部范围内任务完成；必要测试和验收通过；受影响文档与 REQ/BUG 子文档已同步或给出具体不适用原因；无未解决的必需证据缺口；Workflow Sync 串行完成且目标状态正确。任何必要验证无法运行时报告未完成/阻塞及补证路径，不得报已通过。
- 收尾顺序为实现与验证 → 文档和任务回填 → Workflow Sync → AI Usage Hook → 最终报告。收尾任务可以在其他工作通过后进入同步阶段，但同步失败时不得保留虚假的完成勾选或宣布完成，必须修复后重跑；若无法修复则回退该收尾任务为未完成。AI Usage 是最佳努力，用量不可归因只记 warning，不要求用户再次授权继续。
- 部分实现、暂停或中断不得执行会把当前 Change 提升为 `applied` 的完成同步；允许只读 dry-run 诊断。完成后可建议 archive，未经授权不自动归档、发布或创建 follow-up Issue/Change。

### 中断续接

- 预见环境或上下文限制且仍可执行时，在当前 Change `trace.md` 的 Workflow Sync marker 外维护简洁检查点：完整 Issue/Change 与 Sprint 身份、已确认范围/决策、已完成任务和验证证据、剩余任务与依赖、失败命令摘要、硬阻塞、下一可执行动作和相关文件。不得保存原始会话、凭证、本机绝对路径或未经核实的完成状态。
- 上下文压缩后在当前运行内继续；真实强制中断可能来不及写检查点，恢复时 MUST 以当前 `tasks.md`、trace、聚焦 diff、CLI 状态与实际证据交叉核实，不能只信上一轮口头总结或陈旧勾选。已有文件由其他工作改动时只重验受影响部分，不覆盖无关修改。
- 从首个依赖满足的未完成任务继续；摘要复用已读且未变更规则，不重新启动整个流程，不重复询问已有授权。检查点帮助续接，不保证跨平台自动重启；缺失关键输入时遵守硬阻塞规则。

### 停止前决策

每次准备发送 final 前 MUST 按下列顺序判定，不得把阶段输出格式当成停止理由：

1. 用户明确停止：立即停止；用户询问进度、补充约束、回答问题均不属于停止。
2. 环境强制终止且无可行替代：如实报告，不承诺自动重启。
3. 全部任务及完成门禁通过：完成并报告。
4. 尚有可执行任务：继续，包括排障、修复、补证、文档和同步；仅更新commentary。
5. 无可执行任务且剩余任务全部直接或间接依赖有证据的必要外部输入：允许等待，列出阻塞任务、依赖链、已尝试路径、所需输入和恢复动作。

任务依赖判定 MUST 区分已完成、可执行、依赖任务未完成、必要外部输入缺失。依赖环和未知依赖属于需排查的计划错误，不是向用户请求“继续”的理由。测试失败、缺少可推导文档、普通实现选择不得标为外部输入。
问题可异步提出；在等待回复期间继续独立任务，用户回复后直接恢复依赖任务。已有授权在上下文压缩后继续有效；范围或风险实质变化才重新确认。安全、权限及已明确约定的人工确认不得伪造通过。
OpenSpec CLI 的动态提示（包括 Pause if you hit blockers or need clarification）按本节解释，不能仅凭提示直接结束。两份技能、任务分批和输出模板均不得覆盖此判定顺序。

### 行为验收

按 [Apply行为验收](standards/apply-behavior-acceptance.md) 记录最小脱敏轨迹并用 `python scripts/validate-apply-behavior.py --trace` 校验；脚本完整用法见该标准。`--self-test` 是合成正反例，真实会话必须标记observed并保留可复核证据。静态契约、合成回归、真实行为观察分别报告；不得把脚本通过等同于Agent全部场景通过。

### 契约校验

`python scripts/validate-agent-context-budget.py` 检查两份技能对本节及四个子契约的引用，阻断已知宽泛暂停、仅任务完成即归档和自检切换 modify 文案回退。脚本级回归测试覆盖删除引用与恢复旧文案的反例；静态校验不替代真实 Agent 任务运行观察。

## 治理脚本门禁矩阵

| 变更触达面 | 必跑或优先校验 | 说明 |
|---|---|---|
| `.agents/skills/**`、`rules/agent-context-budget.md` | `python scripts/validate-agent-context-budget.py` | 校验 Skill 是否保留上下文预算、执行复盘、下一步输出等共享契约。 |
| OpenSpec Change 文档 | `bash scripts/validate-openspec.sh --change <change-id> --residual-report` | 当前 Change 中文优先与结构校验；其他 active Change 残留只作为分离报告，归档前还需校验合并后的正式规格。 |
| 目录边界、ignore、临时证据 | `python scripts/validate-directory-structure.py`、必要时 `python scripts/validate-env-ignore-policy.py` | 校验顶层目录、legacy 路径、运行时数据和环境变量 ignore 策略。 |
| Sprint scope | `python scripts/validate-sprint-scope.py --sprint <sprint-id>` | 校验 `sprint.yaml`、派生表和范围估算一致性。 |
| Workflow Sync 行为 | `python scripts/sync-workflow-status.py --event <event> ... --dry-run`，必要时运行 focused pytest | 先 dry-run 定位派生影响，再执行写入；脚本变更必须跑对应测试或自检。 |
| REQ/BUG 文档质量 | Workflow Sync 聚焦命令、`--scan-issue-subdocuments` 或对应根因证据校验 | 恢复 trace、registry、CHANGELOG、验收和子文档一致性，不手工编辑派生 marker。 |
| 产品手册/Mintlify | `python scripts/validate-mintlify-docs.py` | 仅在触达 `mintlify/` 或产品手册投影时必跑。 |
| 发布产物与构建记录 | `/release-prepare`、`/image-prepare`、`/image-build`、`/release-publish` 对应校验，必要时 `python scripts/validate-release.py` 或 `python scripts/validate-release-upgrade.py` | 校验 release input、manifest、input hash、产物摘要、外部证据和发布写入边界。 |
| 慢测试、覆盖率、浏览器验收或 Docker smoke 调度 | 聚焦测试命令、分区/worker 配置说明、失败分区摘要和必要 CI 补跑命令 | 串行高风险用例先跑；并行池必须可复跑，不得降低断言或隐藏受影响文件。 |

若某项校验因当前变更不触达对应面而不适用，最终回复、trace、学习报告或治理日志 MUST 明确说明“不适用原因”；若校验失败但属于既有工作区漂移，MUST 记录失败摘要和本次未处理范围。

## Sprint

- `sprint.yaml` 是 Sprint scope 的机器事实源；不得只手工编辑 `sprint.md` 或 Workflow Sync marker 块。
- 已存在 Sprint 追加范围时，先运行 `scripts/add-sprint-scope-item.py` 更新 `sprint.yaml`，再运行 Workflow Sync 和 `validate-sprint-scope.py`。
- 多个范围项写入同一个 Sprint 时必须串行运行，不得并行写同一个 `sprint.yaml`。
- `/sprint-archive` 前必须确认 Sprint 中全部 Change 已归档，并通过 readiness、归档路径残留和 stale scan 门禁。

## 发布、镜像和产品手册

- `/release-propose` 可在 Sprint 接近完成时创建计划，但 `/release-prepare` 和 `/release-publish` 不得伪造未完成门禁为通过。
- `usage-docs-*` 属于公开产品手册链路，必须遵守公开安全和截图/manifest 门禁。
- `/image-prepare` 和 `/image-build` 基于 release 对象和镜像计划执行；不得读取或输出真实 `.env`、密钥、连接串或私有地址。
- `/release-publish` 位于发布公告、产品手册、镜像、部署验证完成之后。

## 下一步参数规则

- “原始 Issue ID”指完整目录 ID，包含编号和 slug，例如 `REQ-0100-mintlify-docs-site-ia-content-experience`、`BUG-0125-miniapp-sku-detail-media-original-load`。
- REQ 来源链路的所有 `/req-*` 和后续 `/opsx-*` 下一步命令 MUST 使用同一个完整 `REQ-xxxx-slug`，不得在 `/opsx-apply`、`/opsx-modify` 或 `/opsx-archive` 中改用 `<change-id>`。
- BUG 来源链路的所有 `/bug-*` 和后续 `/opsx-*` 下一步命令 MUST 使用同一个完整 `BUG-xxxx-slug`，不得在 `/opsx-apply`、`/opsx-modify` 或 `/opsx-archive` 中改用 `<change-id>`。
- 无 REQ/BUG 来源的纯治理 Change 才使用 `<change-id>` 作为 `/opsx-*` 参数。
- `/explore` 与 `/opsx-explore` 输出下一步 `/opsx-*` 命令时同样适用上述规则；若用户只提供 `<change-id>`，必须先从 Change 文档和 Sprint `scope_estimates` 识别是否存在 `requirement` 或 `bug` 来源。
- 「下一步」只放可直接执行的命令；「待用户决策/处理」只放缺失输入、范围选择、证据补充、验收或发布确认、阻塞项。

## 命令执行复盘 Hook（Command Execution Review Hook）

所有 workflow 命令完成后 MUST 输出一段「执行链路复盘」，用于把本次执行是否顺畅、问题是否有证据、是否值得沉淀规范优化讲清楚。

```text
执行链路复盘：
- 链路状态：正常 / warning / blocked
- 问题证据：无 / <脚本输出、文件路径、校验报告、日志摘要或用户证据>
- 规范优化建议：无明显优化点 / <建议命令或建议 capture 文案>
- follow-up 状态：未自动创建 Issue/Change
```

- `正常` 只能用于必需校验、Workflow Sync 与 AI Usage hook 通过，或该命令明确不适用对应 hook 的情况。
- `warning` 用于存在非阻塞问题、可选 hook 跳过、证据 stale、局部校验未覆盖或发现可优化规范点但不影响本次完成。
- `blocked` 用于必需门禁失败、缺少用户补证导致无法定根因或验收、或脚本输出显示事实源不一致。
- 问题证据必须来自脚本输出、失败摘要、文件路径、校验报告、日志摘要、截图、UI 验收证据或用户补充证据；不得凭感觉定性。
- 规范优化建议必须基于本次执行链路的证据；无明确可复用沉淀时写「无明显优化点」。
- 默认不自动创建 follow-up Issue/Change；如需沉淀新问题，只输出建议命令或 capture 文案，等待用户明确授权。

### 示例

```text
正确：下一步：/opsx-apply REQ-0012-frontend-requirement-center
错误：下一步：/opsx-apply add-frontend-requirement-center
```

```text
正确：下一步：/opsx-modify BUG-0009-frontend-admin-sidebar-version-mismatch
错误：下一步：/opsx-modify fix-frontend-admin-sidebar-version-mismatch
```

```text
正确：下一步：/opsx-apply optimize-explore-chain-identity
前提：该 Change 为无 REQ/BUG 来源的纯治理 Change，且已纳入 Sprint。
```

## 串行写入边界

以下步骤写入同一事实源，MUST 严格串行执行：

- 多次运行 `scripts/add-sprint-scope-item.py` 写同一个 `sprint.yaml`。
- Workflow Sync 写 Sprint 派生表、Issue trace、registry 或验收回填。
- `promote-issues-for-archive.py` 迁移 Issue 阶段。
- AI Usage hook 刷新同一 Sprint 或 release snapshot。
- AI Usage hook 普通执行先尝试本地 session 自动发现：显式 `--session-jsonl`、session 环境变量、`AI_USAGE_SESSIONS_DIR`、默认本地 Codex sessions 目录 `~/.codex/sessions`；失败后再输出 `usage_mode: unavailable` 或 `estimated_fallback`。历史回填或审计仍需显式 session 和必要的 `--manual-map`。

不得用并行工具同时运行上述写入步骤；每一步必须基于前一步写入后的最新文件状态继续。

## 研发执行事件契约

apply通过实施前门禁后先运行opsx.start；每批验证后运行opsx.progress；完成门禁通过后运行opsx.apply。两份apply技能与Sprint编排使用相同事件链。启动与进度不受仅收尾时执行完成态同步的限制。零完成数不等于未启动；全勾选不替代完成门禁；执行事实不代表进程在线。

Sprint容量遵循 `rules/iterations-lifecycle.md`：默认30人天，已有有效显式值保留，覆盖需明确请求；容量工具为 `scripts/add-sprint-scope-item.py --capacity-person-days`，修改后重算门禁与派生文档。

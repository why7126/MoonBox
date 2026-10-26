---
name: opsx-accept
description: 在 apply 后自动执行逐 AC 验收、采集脱敏产品证据并生成归档就绪结论
updated_at: 2026-10-25 22:25:00
---

## 验收收尾后的归档准入

验收报告、trace、Workflow Sync 和 AI Usage 收尾完成后，执行
`bash scripts/project-python.sh scripts/opsx_acceptance.py --change <change-id> --archive-readiness`。
仅该共享产品/CLI 门禁返回 ready 后才推荐归档；AC passed、证据 readiness
和规格合并预演不能替代最终准入。阻断时保留已通过的验收证据，报告具体
`recovery_reason`，不得把旧记录过期或交付输入变化描述成规格基线变化。
归档恢复 schema v4 排除明确的派生验收报告与 trace 运行正文，其他交付输入
仍受保护；旧记录迁移不能绕过自身已合并证明与并发保护。

# opsx-accept

## 浏览器自主取证（MUST）

按 `rules/root-cause-evidence.md` §5.0：浏览器清单失败后检查现有标签页、直接连接窗口并尝试替代入口；终端或单个工具失败不能单独证明产品不可达。需要产品运行态证据时可在已有权限内直接通过浏览器自主取证，优先复用 Codex 侧边浏览器，无需人工二次确认。只有无法访问、权限不足、操作超出已授权边界或关键证据仍不足时才请用户补证，并区分旧页面与当前服务。

## Context Budget Guardrails（MUST）

遵守 `rules/agent-context-budget.md`；已在同一会话读取且无变更的规则与 Skill 用摘要复用，优先目标 Change、Issue AC、最新证据清单的片段，不全量读取历史归档、原始 session 或产品消息。成功路径只输出计数与证据入口。

### Guided User Feedback Contract

需要用户选择、确认或补证时，优先原生交互卡片；不支持时先声明降级原因，再降级为文本结构化选项。两种形态都包含「结构化选项 + 推荐项 + 可补充说明」。每轮只聚焦 1-3 个关键决策，标注推荐理由，允许可补充说明；根据已有答复动态收敛，不重复追问。

### Force-proceed Follow-up Guardrails

`force-proceed` 仅继续非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；应明确「未自动创建 Issue」。建议 capture 文案逐条包含建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令。只有用户明确授权自动 capture 时才执行 `/req-capture`、`/bug-capture` 或 `/capture`，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

适用于 `/opsx-accept <REQ-full-id|BUG-full-id|change-id>`，也由 `/opsx-apply` 完成后自动续接。来源于 REQ/BUG 时沿用完整 Issue ID；纯治理 Change 才使用 Change ID。只处理已 applied 且未归档的 Change。

## 读取与边界

先读 `AGENTS.md`、`openspec/project.md`、`rules/global.md`、`rules/language.md`、`rules/agent-context-budget.md`、`rules/document-governance.md`、`rules/root-cause-evidence.md`、`docs/standards/opsx-acceptance.md`、目标 Change 的 proposal、design、tasks、trace、Issue acceptance（如有）和 `acceptance-plan.json`。遵守 `.agents/skills/workflow-sync/SKILL.md` 的状态同步与复盘规则。

只在既有授权内执行。产品对象 Chat 可用于自主取证，优先复用 Codex 侧边浏览器；需要产品运行态时先复用现有会话与环境。对真实首次归档、正式 BUG/Change 样本、容器运行时重启、生产数据等有副作用行为，先核对已有授权和治理门禁，不因本技能自动扩大权限。不把合成回归、旧页面或宿主恢复写成真实产品轮次通过。

## 连续执行

1. 解析目标 Change 与关联 Sprint，检查 applied、全部任务、交付证据和 `acceptance-plan.json`。缺计划时根据 Issue AC 与 Change 验收目标生成逐项计划；每项声明 `inputs`、检查方式、必要效果、产品轮次要求和超时。逐 AC 核对证据类型与样本覆盖范围；视觉 AC 在 `coverage.samples` 中逐项映射阶段×视口到脱敏文件，确实不适用的组合写明原因，并声明检查浏览器依赖的计划级 `preflight`。负向归档用例须写预期退出码、专属门禁标记和保持原状态的效果，并先排除更早的任务或规格阻断。
2. 遵循 `docs/standards/opsx-acceptance.md` 的“连续执行与恢复契约”：先运行 `--queue`，区分公共环境预检与逐 AC 前置条件；局部阻塞不停止独立项。缺少应生成的证据标记 pending_collection 并自主采集，不能只输出诊断后结束。有可执行项就继续，只有真实硬阻塞才请求必要输入。对有产品轮次要求的 AC，先在授权产品对象 Chat 发起对应动作，记下 turn ID，再用只读产品数据源核对同轮终态、目标命令完成和效果。浏览器截图只存必要脱敏画面；命令成功不能替代视觉观察。
3. 运行 `bash scripts/project-python.sh scripts/opsx_acceptance.py --change <change-id> [--db <authorized-local-sqlite>]`。命令检查按显式 argv 运行；失败或受阻立即记录原因。`--only` 是单项诊断入口；若其他 AC 无有效可复用证据，生成的诊断清单不参与整体 readiness，须补一次完整运行。仅对明确声明安全的瞬态命令最多重试两次；有副作用产品动作不自动原样重试。
4. 证据写入 `openspec/changes/<change-id>/evidence/acceptance/<run-id>/`。报告经结构校验后发布；核对 `manifest.json` 的 `scope` 与 `summary.md` 的标题、逐 AC 状态、检查来源、证据类型、入口、缺口及结论；视觉文件的语义由验收者目视签认，不因路径存在自动宣称产品视觉通过。不保存聊天原文、prompt、原始事件、密钥、数据库或未脱敏日志。Issue `acceptance.md` 保存逐 AC 结论及相对证据入口；Change trace 保存摘要与入口。
5. 全部 AC 通过后按标准运行归档临时副本 `--preview`；预演不构成正式归档授权。随后运行 `bash scripts/project-python.sh scripts/opsx_acceptance.py --change <change-id> --readiness`，再运行 `bash scripts/project-python.sh scripts/sync-workflow-status.py --event opsx.accept --change <change-id> --sprint auto`。复核 Issue 验收状态。执行 AI Usage hook；无可归因输入只记 warning。
6. 失败时在原 Change 范围内用 `/opsx-modify` 自修并重验受影响 AC；超范围变化走新 Issue/Change。环境或权限硬阻塞集中提出 1–3 个结构化决策，推荐项和补充说明齐全。不得无限循环创建验收样本。

## 输出

报告通过、失败、受阻、待采集、复用与命令去重数量，以及证据入口、AC就绪、归档预检、授权状态和最短恢复动作。运行前核对 environment_contract、浏览器能力与样本生命周期；按逐项检查点续接。交付、证据与 AI Usage 分开报告。输出「下一步」「待用户决策/处理」和「执行链路复盘」；无事项写“无”。无需归档授权时只到可归档状态，不自动执行真实归档。

## Command Execution Review Hook（MUST）

按 `.agents/skills/workflow-sync/SKILL.md` 输出「执行链路复盘」：链路状态、问题证据、规范优化建议、follow-up 状态（默认「未自动创建 Issue/Change」）。无改进点写「无明显优化点」。「下一步」与「待用户决策/处理」不得重复；已在下一步列出的命令不得在「待用户决策/处理」中重复。

## 稳定验证编排

遵循 [稳定批次与增量复验契约](docs/standards/opsx-acceptance.md#稳定批次与增量复验契约)：完整入口前置检查、修改稳定后集中验证、受影响范围增量复验和里程碑进度反馈。保留现有正确性门禁；未完成入口验证不提前宣布最终完成。

## 面向用户的表达

面向用户的输出遵循 `rules/language.md` 的“产品经理视角沟通”：先讲业务结果和用户影响，优先日常语言，必要技术术语随文解释；决策说明体验、成本、时间和风险。

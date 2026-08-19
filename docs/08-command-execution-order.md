---
purpose: 命令执行顺序速查
content: MoonBox REQ/BUG、Sprint、OpenSpec、发布、镜像与产品手册命令的推荐顺序、串行门禁和执行复盘 Hook
created_at: 2026-08-07 23:20:00
updated_at: 2026-08-19 12:10:48
owner: MoonBox 产品团队
---

# 命令执行顺序速查

本文用于约束 AI 在 MoonBox 中推荐和执行工作流命令的顺序。原则是先评审、再纳入 Sprint、再创建 Change、再实现、再归档，发布链路位于交付闭环之后。

## 标准链路

```text
/req-capture 或 /bug-capture
→ /req-generate 或 /bug-generate
→ /req-complete 或 /bug-complete
→ /req-review --approve 或 /bug-review --approve
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
- `/req-review --approve` 的下一步 MUST 是 `/sprint-propose --req <REQ-full-id>`；`/bug-review --approve` 的下一步 MUST 是 `/sprint-propose --bug <BUG-full-id>`。
- `/req-opsx` 和 `/bug-opsx` 遇到 `status: approved` 但尚未 `in_sprint` 时 MUST 停止，并提示先运行对应 `/sprint-propose`。
- `/req-opsx` / `/bug-opsx` 完成后 MUST 运行 Workflow Sync，把新 Change 回填到同一个 Sprint 的 `changes[]` 与 `scope_estimates[].change`。
- 如果 REQ/BUG 已经纳入 Sprint，但 `/opsx-apply --dry-run` 仍解析不到 Sprint，优先修复 `sprint.yaml` 机器事实源，不要求用户重复口头确认。

## Apply / Modify / Archive

- `/opsx-apply` 前 MUST 通过 `python scripts/sync-workflow-status.py --event opsx.apply --change <change-id> --sprint auto --dry-run` 确认目标 Change 位于 Sprint scope。
- `/opsx-modify` 只用于 `/opsx-apply` 之后、`/opsx-archive` 之前的验收返修；超出原 Change 范围时应创建新 REQ/BUG 或新 Change。
- `/opsx-archive` 只能归档已完成 tasks 且 artifact 完整的 Change。
- 归档步骤必须严格串行：归档脚本或 OpenSpec archive → 目录校验 → env ignore 校验 → archive evidence → Workflow Sync → Issue promote → AI Usage。

## 治理脚本门禁矩阵

| 变更触达面 | 必跑或优先校验 | 说明 |
|---|---|---|
| `.agents/skills/**`、`rules/agent-context-budget.md` | `python scripts/validate-agent-context-budget.py` | 校验 Skill 是否保留上下文预算、执行复盘、下一步输出等共享契约。 |
| OpenSpec Change 文档 | `python scripts/validate-openspec-language.py`、`openspec validate <change-id>` | 中文优先与目标 Change 结构校验；归档前还需校验合并后的正式规格。 |
| 目录边界、ignore、临时证据 | `python scripts/validate-directory-structure.py`、必要时 `python scripts/validate-env-ignore-policy.py` | 校验顶层目录、legacy 路径、运行时数据和环境变量 ignore 策略。 |
| Sprint scope | `python scripts/validate-sprint-scope.py --sprint <sprint-id>` | 校验 `sprint.yaml`、派生表和范围估算一致性。 |
| Workflow Sync 行为 | `python scripts/sync-workflow-status.py --event <event> ... --dry-run`，必要时运行 focused pytest | 先 dry-run 定位派生影响，再执行写入；脚本变更必须跑对应测试或自检。 |
| REQ/BUG 文档质量 | Workflow Sync 聚焦命令、`--scan-issue-subdocuments` 或对应根因证据校验 | 恢复 trace、registry、CHANGELOG、验收和子文档一致性，不手工编辑派生 marker。 |
| 产品手册/Mintlify | `python scripts/validate-mintlify-docs.py` | 仅在触达 `mintlify/` 或产品手册投影时必跑。 |

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

不得用并行工具同时运行上述写入步骤；每一步必须基于前一步写入后的最新文件状态继续。

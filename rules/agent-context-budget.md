---
purpose: Agent 上下文预算治理
content: 约束 AI 读取范围、搜索排除、Harness/模板工程噪音、生成物与大输出处理
source: 实际项目 Token 复盘后迁移为 Harness 模板规则
update_method: Agent 工作流、Harness 模板、技能命令或上下文预算策略变化时更新
created_at: 2026-07-08 09:26:36
updated_at: 2026-08-08 21:08:00
note: 所有 Agent 命令与普通开发任务均应遵守，优先级高于单个技能中的宽泛读取建议
---

# Agent 上下文预算治理

## 1. 目标

降低 AI 在需求、BUG、Sprint、OpenSpec 与 Harness 相关任务中的无效 token 消耗，避免重复读取大规则、大目录、历史归档、生成物和模板工程资产。

核心原则：先定位，再摘要，再片段读取；只有证据不足或任务明确要求时才扩大范围。

## 2. 默认读取边界

AI 执行任务时 MUST：

- 已在同一会话读取过且无变更的规则文件，用摘要承接，不重复全量读取。
- 先用 `rg -l`、`rg --files`、`find ... -maxdepth`、`git diff --name-only` 或 `git diff --stat` 定位，再读取必要片段。
- 对 Markdown、Spec、代码文件优先使用 `sed -n '<start>,<end>p'` 或 `nl -ba ... | sed -n` 分段读取。
- 命令输出默认控制在合理范围；预期更大时先输出文件清单、命中数、失败摘要或 diff stat。
- 不默认全量读取 `docs/**`、`issues/**`、`iterations/**`、`openspec/specs/**`、`openspec/archive/**`。

AI 执行任务时 MUST NOT：

- 默认运行 `cat rules/*.md`、`cat docs/**`、`ls -R` 或无边界 `rg <keyword> .`。
- 为确认一个字段或状态读取整个目录或整个历史归档。
- 在成功路径中输出完整测试日志、完整 Workflow Sync 派生块或完整 generated 文件。

## 2.1 已读摘要复用

同一会话中，AI 已经读取过且无变更的规则和 Skill 文件 SHOULD 用摘要承接，避免重复全量展开。适用范围包括：

- `AGENTS.md`、`openspec/project.md`。
- 当前任务相关的 `rules/*.md`。
- 当前命令 Skill、共用 Skill（如 `.agents/skills/workflow-sync/SKILL.md`）以及 `.agents/skills/{req,bug,opsx,sprint,release,image,build}-*`、`.agents/skills/capture`、`.agents/skills/explore`、`.agents/skills/spec-opt`、`.agents/skills/spec-study`、`.agents/skills/initialize-project`。

可复用摘要 SHOULD 至少表达以下信息，字段名可等价：

```yaml
path: <规则或 Skill 路径>
version_hint: <updated_at、mtime、hash 或本会话已读时间线索>
summary: <与当前任务相关的规则、步骤和门禁摘要>
applicability: <本摘要适用的命令、阶段或风险范围>
refresh_reason: <本次继续复用或需要补读的原因>
```

摘要默认只存在于同一对话上下文中，MUST NOT 写入仓库或持久化原始 prompt、系统/developer 指令、完整 session JSONL、工具输出正文、密钥、Cookie、Authorization header、`.env` 内容或真实客户数据。

以下情况 MUST 补读目标文件或必要片段，不能仅凭旧摘要继续执行：

- 文件内容、mtime、hash、`updated_at` 或等价版本线索显示已变化。
- 用户明确要求重新读取、复核原文或引用精确文本。
- 当前命令从 capture、explore、generate 等轻量阶段升级到 apply、archive、release、req-opsx、bug-opsx、sprint-propose 等高风险阶段。
- 当前任务涉及 OpenSpec 红线、Issue lifecycle、权限、安全、API、DB、上传、Docker、发布、Workflow Sync Final Step 或 AI usage hook。
- 摘要不足以覆盖当前门禁，或 Workflow Sync、测试、校验脚本、OpenSpec CLI 返回失败。

成功路径输出 SHOULD 保持紧凑，只报告摘要复用状态、补读片段、计数、warning 或 recommended action；不得默认转述完整规则、完整 Skill、完整测试日志、完整 Workflow Sync 派生块或完整 generated diff。

## 3. 默认搜索排除

大范围搜索和文件清单默认排除：

```text
--glob '!pm-harness*/**'
--glob '!**/assets/**'
--glob '!**/.git/**'
--glob '!**/node_modules/**'
--glob '!**/dist/**'
--glob '!**/coverage/**'
--glob '!openspec/archive/**'
--glob '!src/**/generated/**'
--glob '!.agents/**'
```

如当前任务明确要求分析 Harness、模板工程、agent 资产、历史归档或生成物，MAY 放开对应排除项，但 MUST 先说明原因，并优先输出清单或命中数。

## 4. Harness 与模板工程

- `pm-harness*/`、Harness 模板 assets、`.agents/skills/` 默认视为高噪音上下文。
- 非 Harness 任务不得读取 Harness 模板资产全文。
- 需要清理或校验 Harness 资产时，先限定具体路径与文件类型，再分段读取。
- 不应把长脚本、长批准命令或模板资产内容复制进技能文件；应引用脚本路径或规则文档。

## 5. 生成物与大文件

- API 变更仍 MUST 同步 OpenAPI / 客户端生成物 / docs / tests，但复核方式应节制。
- 默认使用 `git diff --stat`、`git diff --name-only` 或目标 schema 片段。
- 不默认输出 OpenAPI JSON、客户端 generated 文件、bundle、coverage、日志全文。
- 需要确认生成类型时，只读取相关接口、Schema 或导出函数片段。

## 6. Git Diff 与测试输出

- 普通复核优先 `git diff --stat` 与 focused diff。
- 大 diff 先看文件列表；只对手写源码、文档或任务文件展开必要片段。
- 测试通过时只报告命令与摘要；测试失败时只展开失败用例、堆栈关键段和相关文件片段。
- Workflow Sync 成功时只报告摘要；失败时按报告定位具体 marker 或文件片段。

## 7. 技能文件要求

Agent 命令技能 SHOULD：

- 引用本文件或内置等价上下文预算章节。
- 包含 `force-proceed` follow-up 门禁：不得默认自动创建 follow-up REQ/BUG，除非用户明确授权；未授权时只输出可复制的 capture 文案并说明未自动创建 Issue。
- 明确区分「下一步」与「待用户决策/处理」，同一事项不得重复出现在两处。
- 保留命令特定的 Must Read 与业务门禁，但不得要求默认宽泛读取整目录。
- 对 apply/archive/sprint 类高消耗命令，明确要求先读取 OpenSpec CLI `contextFiles`、任务文件、trace/status 片段，再按需扩展。
- 对工作流命令顺序，MUST 遵守 `docs/08-command-execution-order.md`：先评审、再纳入 Sprint、再创建 Change、再 apply/modify/archive，发布、镜像和产品手册位于交付闭环之后；写同一事实源的步骤不得并行。
- 对 REQ/BUG 评审后的下一步，MUST 先输出 `/sprint-propose --req <REQ-full-id>` 或 `/sprint-propose --bug <BUG-full-id>`；只有 Workflow Sync 将 Issue 同步为 `in_sprint` 后，才能输出或执行 `/req-opsx` / `/bug-opsx`。
- 对下一步可执行命令，MUST 保留完整链路身份：REQ 链路使用完整 `REQ-xxxx-slug`，BUG 链路使用完整 `BUG-xxxx-slug`；即使命令进入 `/opsx-apply`、`/opsx-modify` 或 `/opsx-archive`，也不得把来源于 REQ/BUG 的下一步参数降级为 `<change-id>`。只有非 REQ/BUG 的纯治理 Change 才使用 `<change-id>`。
- 对 `/spec-study` 跨项目 Harness 学习应用命令，MUST 明确先学习并输出候选内容、等待用户确认后再应用；学习范围 MUST 横向覆盖项目入口、`rules/`、`docs/`、Agent 目录、`scripts/`、部署与环境示例；学习对象 MUST 全程只读且绝不允许被改动；应用阶段 MUST 遵守 active OpenSpec Change 与 Sprint Inclusion Gate，并禁止修改业务 `src/`；同一次学习应用流程只生成一份正式学习报告，学习报告 MUST 统一写入 `docs/spec-logs/YYYYMMDDhhmmss-study-xxx.md`，并承载本次学习触发的治理资产应用结果；不得额外生成内容重复的 `YYYYMMDDhhmmss-governance-xxx.md`，且不得包含用户隐私数据、真实客户数据、密钥、访问令牌、未脱敏日志、订单原文、聊天原文、工单原文、截图中的个人信息、学习对象源码、本机绝对路径、系统用户名或用户主目录；本地学习对象在持久化文档中 MUST 使用项目名或脱敏占位符描述。
- 对 `/spec-opt` 规范优化命令，MUST 在完成本项目规范、技能、脚本、目录边界或校验规则迭代后写入 `docs/spec-logs/YYYYMMDDhhmmss-governance-xxx.md` 治理迭代日志，且不得包含用户隐私数据、真实客户数据、密钥、访问令牌、未脱敏日志、订单原文、聊天原文、工单原文、截图中的个人信息或学习对象源码。
- 对带 `prototype/` 的 UI 页面，`/req-complete`、`/req-opsx`、`/opsx-apply`、`/opsx-modify`、`/opsx-archive` 和 Workflow Sync MUST 只读取当前 REQ/Change 的 prototype 片段、UI Skeleton、AC-PROTOTYPE 和相关 best-practice；不得为做 1440px 视觉验收而全量读取无关 UI、历史归档或生成物。

## 8. 校验

如项目提供上下文预算校验脚本，推荐命名为：

```bash
python scripts/validate-agent-context-budget.py
```

该脚本用于检查 Agent 技能是否引用本规则，并阻止常见宽泛读取模式回退。

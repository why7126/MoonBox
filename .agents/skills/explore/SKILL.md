---
name: "explore"
description: "通用探索模式 - 面向问题、需求或话题的只读分析与方案探讨，不改代码、不落盘"
created_at: 2026-08-06 00:00:00
updated_at: 2026-08-15 09:50:00
---

# explore

Use this skill when the user asks to run the workflow command `explore`, or wants to discuss an open-ended problem, requirement, idea, or topic before creating REQ / BUG / OpenSpec artifacts.

在 MoonBox 中，`/explore` 用作最轻量的只读思考入口：用户还没有明确要记录需求、缺陷或 OpenSpec Change 时，先在这里澄清问题、比较方案、识别风险和下一步治理入口。

`/explore` 是通用探索入口，应用功能与 `/bug-explore`、`/req-explore`、`/opsx-explore` 相似，但不要求用户已拥有 BUG、REQ 或 Change ID。它负责把用户抛出的内容先分流为「问题 / 需求 / 话题 / 混合」，再提供根因分析、需求评估、方案设计或观点论证。

**默认：不写任何文件、不写代码、不改 `src/`、不改 `issues/`、不改 `openspec/`、不改 `iterations/`。**

## Context Budget Guardrails（MUST）

### Guided User Feedback Contract（MUST）

当命令需要用户选择、确认、补充信息或处理阻塞时，MUST 采用引导式反馈：

- 优先使用原生交互卡片组织问题；当客户端或工具层不支持原生交互卡片时，MUST 先声明降级原因，再降级为文本结构化选项。
- 两种形态都必须包含「结构化选项 + 推荐项 + 可补充说明」，不用大段开放式追问替代。
- 每轮只聚焦 1-3 个关键决策；每个决策点 SHOULD 给出 2-4 个互斥选项。
- 至少一个选项 MUST 标注「推荐」，并用一句话说明推荐理由或适用前提。
- 默认提供「可补充说明」入口，允许用户用自然语言覆盖选项、补充约束或给出例外。
- 用户已回答的决策 MUST 在后续输出中被承接并动态收敛，只追问剩余阻塞点或新增风险点，避免重复询问已确认事项。
- 无需用户反馈的成功路径 SHOULD 保持紧凑，不为了套用格式而追加无意义问卷。

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 检索先用 `rg -l` / `rg --files` 定位文件，再用 `sed -n '<start>,<end>p'` 或 `nl -ba ... | sed -n` 读取必要片段。
- 大范围 `rg/find` 默认排除 Harness、模板 assets、历史 agent 目录、archive、generated、node_modules、dist、coverage。
- 命令输出优先 `max_output_tokens <= 8000`；大 diff、OpenAPI/Orval 生成物、测试日志、Workflow Sync 输出先给摘要或命中数。
- 不为探索目的读取整目录；只读取与当前问题、需求、话题直接相关的文档、代码、配置或 Change 片段。

## Command Template

**Input**：自然语言问题、需求、想法、话题；也可以包含 `REQ-xxxx`、`BUG-xxxx`、`sprint-xxx`、`openspec/changes/<change-id>` 或文件路径。

**默认行为**：

- 只读分析、搜索、定位、比较和讨论。
- 若用户输入已经明显属于某个专门命令，优先沿用该命令的思路：
  - BUG 或故障：对标 `/bug-explore`
  - 需求或产品想法：对标 `/req-explore`
  - OpenSpec Change 或技术变更：对标 `/opsx-explore`
  - Sprint 范围、排期、依赖：对标 `/sprint-explore`
- 若用户要求实现、修复、生成正式文档或创建 Change，提醒必须退出 explore，并按 `/capture`、`/req-*`、`/bug-*`、`/opsx-*` 或 `/sprint-*` 流程执行。

## Stance

- **好奇但有判断**：先理解语境，再给清晰结论；不把探索变成机械问卷。
- **证据优先**：涉及项目事实时，读取现有代码、文档、配置或 OpenSpec 片段作为依据。
- **无证据不定根因**：涉及问题排查、BUG、异常、效果不如预期或返修时，MUST 遵守 `rules/root-cause-evidence.md`；证据不足时只能输出 `unknown`、`hypothesis` 或 `probable`，并给出人工补证操作步骤，不得把猜测写成已确认根因。
- **多方案思维**：需求和设计问题优先给多个可行方案，再比较取舍。
- **明确决策点**：凡需要用户选择范围、优先级、成本、风险或路线时，必须显式列出。
- **可视化**：适合时使用 ASCII 图、流程图、依赖图、对比表帮助澄清。
- **不越界**：探索不是实现，不自动落盘，不假装已经修复。

## 输入分流

### 1. 问题 / 故障 / 异常

适用：用户描述「为什么」「报错」「不生效」「表现异常」「体验不对」「可能有 bug」。

输出 SHOULD 包含：

- 问题复述：用一句话确认理解。
- 现象与影响：影响范围、触发条件、严重程度倾向。
- 根因判断：区分已确认根因、强推测、待验证假设。
- 证据依据：引用只读调查到的代码、文档、配置、日志或用户描述。
- 人工补证：如果证据不足，MUST 输出待补证项、为什么需要、操作步骤、需要返回的字段、脱敏要求和返回格式；不得只说“请提供日志/截图”。
- 解决方案：给出至少一个可执行修复路线；复杂问题可拆临时 workaround 与正式 fix。
- 验证建议：建议如何复现、如何验证修复、是否需要回归测试。
- 后续流程：若确认是 BUG，建议 `/bug-capture` 或 `/capture`；不得自动创建，除非用户明确授权。

根因输出约束：

- `confirmed`：必须有日志、复现、测试失败、截图、Network、Console、数据库样本、配置差异、代码路径或运行时观测等可复核证据。
- `probable`：只有间接证据，必须标注仍需补证。
- `hypothesis` / `unknown`：不得给修复定论；优先输出人工补证步骤，等待用户补证后再继续。

### 2. 需求 / 产品想法 / 改进建议

适用：用户描述「想做」「能不能加」「是否合理」「怎么设计」「要不要支持」。

输出 SHOULD 包含：

- 需求理解：目标用户、场景、要解决的问题。
- 合理性评估：价值、频率、边界、与现有产品定位的一致性。
- 评估依据：用户价值、业务价值、实现成本、维护成本、风险、现有系统约束。
- 范围建议：In / Out、MVP 与后续增强。
- 设计方案：给出一个或多个方案；多个方案 MUST 提供对比表。
- 推荐方案：说明推荐理由、适用前提和放弃其他方案的原因。
- 决策点：明确需要用户决定的范围、优先级、体验、数据、权限、上线节奏等。
- 后续流程：若值得正式推进，建议 `/req-capture` 或 `/opsx-propose`；不得自动创建，除非用户明确授权。

### 3. 技术设计 / 架构取舍

适用：用户比较技术路线、模块边界、接口设计、数据模型、部署策略或实现方式。

输出 SHOULD 包含：

- 现状地图：当前相关模块、依赖、接口、数据流或文档约束。
- 约束条件：OpenSpec、API、DB、权限、安全、部署、测试、Orval、设计系统等影响。
- 候选方案：至少覆盖保守方案与演进方案；必要时给长期方案。
- 对比维度：复杂度、风险、迁移成本、可测试性、可维护性、上线影响。
- 推荐方案：给出明确推荐，并说明何时应选择其他方案。
- 决策点：需要用户拍板的 trade-off 必须列出。

### 4. 话题 / 观点 / 讨论

适用：用户抛出开放话题、原则问题、行业判断、流程理念或希望听看法。

输出 SHOULD 包含：

- 观点：先给一个清晰看法，允许保留不确定性。
- 论点与依据：分条说明判断来自哪些事实、经验、项目约束或逻辑推导。
- 反方或边界：说明该观点在哪些条件下可能不成立。
- 可延展话题：如果能引发新的讨论点，可以抛出 1-3 个高价值方向。
- 决策点：若话题背后隐含产品、流程或技术选择，明确指出。

### 5. 混合输入

如果用户输入同时包含问题、需求和话题：

- 先拆分主题。
- 标注每个主题的类型倾向。
- 逐项探索，或在信息量过大时先给主题地图并建议优先级。
- 不得把多主题混成一个含糊结论。

## 可读取内容

- 用户给出的文件、日志、截图或上下文。
- 与问题相关的 `src/`、`tests/`、`docs/`、`rules/`、`issues/`、`openspec/changes/`、`iterations/` 必要片段。
- 已存在的 REQ / BUG / Change / Sprint 文档片段，用于避免重复和确认上下文。

## 禁止

- 写代码、修复代码、格式化代码、改测试。
- 新建或修改 `issues/`、`openspec/`、`iterations/`、`docs/`、`releases/`、`src/` 文件。
- 勾选 `tasks.md`、推进 workflow status、运行 apply/archive 类命令。
- 自动创建 REQ / BUG / Change / Sprint。
- 为了探索读取大范围历史归档或生成物。

## 用户明确要求记录结论时

如果用户明确说「记录下来」「帮我创建需求/BUG」「写入 Change」「更新设计文档」：

- 先确认这已超出 `/explore` 的默认只读范围。
- 根据内容选择 `/capture`、`/req-capture`、`/bug-capture`、`/req-generate`、`/bug-generate`、`/opsx-propose`、`/opsx-explore` 或 `/sprint-explore`。
- 写入前必须读取对应 Skill 和 lifecycle 规则。
- 写入后必须按对应 Workflow Sync 规则执行，不得用 `/explore` 偷偷落盘。

## 建议输出形态

按输入类型自然组织，不强制所有章节都出现。常用结构：

```text
判断
依据
方案
对比
推荐
需要你决策
下一步
```

当用户只需要轻量观点时，可以短答；当涉及项目根因、需求推进或架构取舍时，必须给出足够证据和明确决策点。

## Next

- 确认是 BUG：`/bug-capture` → `/bug-generate` → `/bug-complete`
- 确认是需求：`/req-capture` → `/req-generate` → `/req-complete`
- 确认要进入 OpenSpec：`/opsx-propose`
- 已有 BUG / REQ / Change / Sprint：切换到对应专用 explore 命令继续深入

### Opsx 链路身份（MUST）

当 `/explore` 输出下一步 `/opsx-apply`、`/opsx-modify`、`/opsx-archive` 等 `/opsx-*` 命令时，MUST 先识别目标 Change 是否来源于 REQ/BUG：

- 若上下文已经出现完整 `REQ-xxxx-slug` 或 `BUG-xxxx-slug`，MUST 直接沿用该完整 Issue ID。
- 若用户只给出 `<change-id>` 或 `openspec/changes/<change-id>`，MUST 读取该 Change 的必要文档片段（优先 `trace.md`，必要时 `proposal.md`、`design.md`、`tasks.md`）和当前 Sprint `sprint.yaml` 的 `scope_estimates`，查找 `requirement` 或 `bug` 来源。
- 可识别为 REQ 来源 Change 时，下一步 `/opsx-*` MUST 使用完整 `REQ-xxxx-slug`，不得降级为 `<change-id>`。
- 可识别为 BUG 来源 Change 时，下一步 `/opsx-*` MUST 使用完整 `BUG-xxxx-slug`，不得降级为 `<change-id>`。
- 只有确认无 REQ/BUG 来源的纯治理 Change，下一步 `/opsx-*` 才 MAY 使用 `<change-id>`，且仍 MUST 遵守 Sprint Inclusion Gate。
- 如果无法识别来源，不得臆造 Issue ID；MUST 在「待用户决策/处理」中说明需要补充来源或确认是否纯治理 Change。

示例：

```text
下一步：/opsx-apply REQ-0012-frontend-requirement-center
下一步：/opsx-modify BUG-0009-frontend-admin-sidebar-version-mismatch
下一步：/opsx-apply optimize-explore-chain-identity
```

第三个示例仅适用于无 REQ/BUG 来源的纯治理 Change。

## Final Step — AI Usage Post-command Hook（SHOULD）

通用探索默认不改变 Workflow 状态；如脚本支持通用事件，结束前优先以 dry-run 模式运行 AI Usage Hook：

```bash
python scripts/extract-ai-usage.py --post-command-hook --workflow-event explore --dry-run --json
```

- 如果脚本不支持 `explore`，不得为了生成 usage 数据而强行推进状态。
- 只输出紧凑 Hook 摘要：`status`、`usage_mode`、`command_run_count`、`sprint_snapshot`、`warning_count`、`recommended_action`。
- 不得为了记录 AI Usage 而更新 REQ/BUG/Change/Sprint 状态。

## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。

## Final Output Contract（MUST）

命令结束前，最终回复 MUST 明确包含：

```text
下一步：<可直接执行的命令；若没有则写“暂无可推进下一步”>
待用户决策/处理：
- <需要用户选择、确认、补充或处理的事项；若没有则写“无”>
```

- 如果存在明确可推进的下一步，MUST 给出可复制执行的命令，例如 `/bug-review BUG-0122 --approve`；输出 `/opsx-*` 下一步时，REQ 来源链路 MUST 使用完整 `REQ-xxxx-slug`，BUG 来源链路 MUST 使用完整 `BUG-xxxx-slug`，只有纯治理 Change 才使用 `<change-id>`。
- 如果下一步取决于用户选择，MUST 用条件化条目列出选项；已在「下一步」中给出的命令或动作，不得在「待用户决策/处理」中重复。
- 「待用户决策/处理」只列缺失输入、需用户选择的范围/策略/证据/验收/发布确认、阻塞项或需人工处理事项；没有则写“无”。
- 不得因为输出了下一步引导而自动执行下一命令；除非用户明确授权。

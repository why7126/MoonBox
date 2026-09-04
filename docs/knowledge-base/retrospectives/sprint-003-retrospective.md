---
title: Sprint-003 经验复盘
purpose: 总结 sprint-003 的流程、需求、开发质量、治理沉淀与模型 Token 使用经验
content: Sprint 复盘、行动项、后续 capture 建议和知识库沉淀
source: /sprint-exps sprint-003
owner: MoonBox 产品团队
status: active
created_at: 2026-09-04 16:28:01
updated_at: 2026-09-04 16:28:01
sprint_id: sprint-003
---

# Sprint-003 经验复盘

## Sprint 概况

| 指标 | 结果 |
|---|---|
| Sprint | sprint-003 |
| 生命周期 | completed / archive |
| 时间 | 2026-08-14 17:00:00 至 2026-09-04 15:47:14 |
| 范围 | 4 个 REQ，3 个 BUG，26 个 OpenSpec Change |
| 任务完成 | 288/288 |
| 容量 | 36 人天 / 30 人天，容量占用 120% |
| 归档状态 | 26/26 Change archived；readiness、stale scan、env ignore、product data observability gate 均通过 |

Sprint-003 是一次“产品能力 + 治理工程”混合迭代：产品侧完成空间切换真实数据、创建/加入空间、需求中心卡片动作和 Markdown/Vditor 抽屉增强；治理侧集中补齐根因证据、命令执行复盘、Workflow Sync、OpenAPI 客户端生成依赖、数据采集观测、视觉证据目录和跨项目 Harness 学习落地。最终 26 个 Change 全部归档，288 个 tasks 全部完成，Sprint 已关闭。

## 流程复盘

### 做得好的地方

- 根因证据治理成为可执行规则：问题排查、BUG 完善、验收返修和 BUG 来源实现都要求证据先行，证据不足时输出人工补证步骤，降低“凭感觉定根因”的风险。
- 命令执行复盘 Hook 覆盖范围继续扩大，`sprint-archive`、`sprint-exps`、`workflow-sync` 等命令都开始要求链路状态、证据和规范优化建议，复盘不再只停留在结果。
- REQ-0020 与 REQ-0021 的 UI 返修证据较完整，围绕右侧抽屉、Markdown 阅读/编辑/分栏、按钮门禁、demo 数据和 computed style 多轮收口，最终沉淀出 UI 视觉证据门禁和子文档一致性扫尾规则。
- 数据采集与链路观测被纳入 Sprint 关闭口径：本 Sprint 明确命中 usage_events、request_logs、task_traces、web request wrapper、API governance、object storage 与 agent workflow observability，并通过专项校验。
- 跨项目 Harness 学习不再只是一次性参考，而是沉淀为本项目的 sprint.md、req-review、release-test、data-collection、workflow-sync 等治理 Change。

### 需要修正的地方

- Sprint 范围仍然踩到容量上限：26 个 Change、36 人天、120% 容量占用和 0 人天缓冲说明 sprint-002 的范围压力在 sprint-003 仍然存在，后续应把产品交付、UI 深返修和治理学习拆成更清晰的批次。
- 验收报告中大量历史记录保留“待人工 sign-off”文案，最终结论虽已通过，但中间态文字会干扰复盘判断；关闭前应自动区分历史过程记录与最终状态。
- Fact Sheet warnings 有 62 条 archived-path residual，虽然 stale scan 已通过且不阻断关闭，但说明归档文档中保留历史 active 路径的噪音仍偏多。
- AI Usage 官方快照未形成真实归因：`extract-ai-usage.py` 在显式 session JSONL 和默认 `~/.codex/sessions` 目录下仍返回 `command_run_count=0`，导致 Sprint 级官方数据只能标记为估算回退。

## 模型 Token 使用分析

### Token Usage Fact Sheet

| 指标 | 值 | 证据/说明 |
|---|---:|---|
| 精确 token 统计 | 无 | 官方 Sprint snapshot 非 actual；不得按真实 Sprint 统计声明 |
| AI usage mode | estimated_fallback | `data/ai-usage/sprints/sprint-003.json` 当前 `estimated=true`，`source_data_files=[]` |
| Snapshot status | present but non-actual | 文件存在，但 totals 全为 0 且 `command_run_count=0`，属于覆盖失败后的估算回退 |
| official input_tokens | 0 | 仅表示未观测到 command run，不等同真实 0 |
| official output_tokens | 0 | 仅表示未观测到 command run，不等同真实 0 |
| official total_tokens | 0 | 仅表示未观测到 command run，不等同真实 0 |
| 本地 session token_count 观测 | 有 | 从 `~/.codex/sessions` 中与 `/sprint-archive sprint-003` 匹配的 JSONL 读取 `token_count.total_token_usage` |
| 观测 input_tokens | 6378215 | 本地 session 累计 token_count；覆盖 `/sprint-archive sprint-003` 观测会话，不代表完整 Sprint |
| 观测 cached_input_tokens | 5992960 | 同上 |
| 观测 output_tokens | 20348 | 同上 |
| 观测 reasoning_output_tokens | 3125 | 同上 |
| 观测 total_tokens | 6398563 | 同上 |
| 观测 token_count_events | 45 | 同上 |
| reason | coverage-missing | 当前提取器未能把本地 session JSONL 归因到 Sprint command run |
| impact | high | 无法产出 Sprint 全链路真实 totals、workflow event 矩阵、model_call_count 和 tool_call_count |
| recommended_action | 修复归因链路 | 优先补齐 `~/.codex/sessions` 自动发现、显式 session JSONL、manual-map 与 post-command hook 的一致性验收 |

上表分成两层：官方 Sprint snapshot 仍是 `estimated_fallback`，不能当成真实用量；本地 session `token_count` 是可观测的真实会话累计值，但只覆盖已定位的 `/sprint-archive sprint-003` 会话，不能外推为整个 sprint-003 的总用量。这个边界必须保留，否则复盘会把“归因失败”误写成“真实为 0”。

### 高消耗来源

| 来源 | 影响 | 证据 | 优化方案 |
|---|---|---|---|
| Sprint 四件套与归档材料 | high | Fact Sheet 标记 Sprint 四件套 2 个文件超过 200 行，且验收记录较长 | `/sprint-exps` 默认使用 Fact Sheet 摘要；只有 warnings、focus 或 blocker 时分段读取原文 |
| 26 个 Change 与 288 tasks | high | Fact Sheet: 26 changes、288/288 tasks，large-sprint batch_count=6 | 按 Change 批次读取，复盘只展开异常批次、未完成 tasks 或关键 evidence hints |
| REQ-0020/REQ-0021 多轮 UI 返修 | high | 验收记录集中在需求中心卡片、Markdown 抽屉、Vditor、demo 数据和 computed style | UI 型 Change 先建立截图对照表、动作按钮矩阵、modal 家族和 computed style 清单，减少逐按钮返修 |
| Workflow Sync 与 Fact Sheet 输出 | medium | Fact Sheet warnings=62，完整 JSON 输出容易展开大量矩阵和 evidence hints | 增加 summary/fields 模式；成功路径只输出计数、状态、warnings 和证据路径 |
| 规则与 Skill 重复读取 | medium | sprint-003 同时涉及 spec-opt、workflow-sync、opsx-modify、sprint-archive、sprint-exps | 同一会话复用已读摘要；高风险阶段只补读变更过的规则或目标 Skill |
| 本地 session AI Usage 归因失败 | high | 显式 JSONL 与默认 sessions 目录均未产生 command run | 为提取脚本补测试：session JSONL token_count 存在时能映射 workflow event、sprint 和 change |

### 优化行动项

| ID | 优先级 | 描述 | 建议下一步 | 状态 |
|---|---|---|---|---|
| T3-001 | P1 | 修复 AI Usage 本地 session JSONL 归因，避免 Sprint 关闭和复盘继续落入 `estimated_fallback` | `/bug-capture` 或 `/opsx-propose fix-ai-usage-session-jsonl-command-attribution` | open |
| T3-002 | P1 | 为 Sprint Fact Sheet 增加稳定 summary/fields 输出，默认不展开大型 usage matrices 和 evidence hints | `/opsx-propose optimize-sprint-fact-sheet-summary-fields` | open |
| T3-003 | P2 | 关闭前区分验收报告历史 sign-off 记录与最终结论，减少“最终已通过但过程仍显示待确认”的阅读噪音 | `/opsx-propose normalize-acceptance-history-final-status` | open |
| T3-004 | P2 | 为 UI 验收返修建立截图对照表、动作矩阵与 modal 组件族的一次性收口模板 | `/req-capture` | open |
| T3-005 | P2 | 将本地开发 Compose 写入边界、只读挂载和 Markdown 保存失败态沉淀为开发环境验收 checklist | `/req-capture` | open |
| T3-006 | P3 | 清理或标注归档文档中的 archived-path residual，避免 Fact Sheet warnings 长期噪音化 | `/opsx-propose reduce-archived-path-residual-warnings` | open |

## 需求与设计复盘

- REQ-0018 的空间切换真实数据接入方向清晰，前台空间上下文从静态/模拟过渡到真实列表，为后续空间级权限和需求中心数据过滤打底。
- REQ-0019 的创建空间与加入申请流补齐了空间生命周期入口，但后续还需要持续观察申请状态、审批反馈、默认空间切换和空态引导是否形成闭环。
- REQ-0020 是本 Sprint 的复杂产品核心：需求中心卡片文档入口、动作流转、AI 聊天、workflow demo、缺失文档 Tips、进度抽屉和阶段门禁多次返修，说明“研发流程卡片”应提前拆出更细的状态矩阵。
- REQ-0021 的 Markdown/Vditor 抽屉增强覆盖预览、编辑、分栏、frontmatter、task list、代码复制、图片受控失败和保存异常处理，最终价值高，但也暴露 UI 验收与本地写入边界应前置。

## 开发质量复盘

- 后端与前端验证覆盖较完整：Sprint 关闭前通过归档 readiness、stale scan、env ignore、product data observability、OpenSpec 语言与目录结构类校验。
- Markdown 保存失败的根因被证据化定位到本地开发 Compose 对 `issues/` 的只读挂载，随后同步了后端异常响应和前端失败态保留草稿，这是本 Sprint 根因证据治理的有效样本。
- OpenAPI 客户端生成依赖治理被纳入 Change，后续 API/BFF 变化应继续把 OpenAPI 来源、客户端生成和依赖检查作为同一条验收链。
- 质量风险主要来自多轮 UI 细节返修：按钮文案、分隔符、文档入口、进度区视觉层级、抽屉信息层级和 Markdown 阅读密度都发生过反复，后续应把截图反向工程和 computed style 采样提前到 apply 前段。

## 可复用抽象

| 抽象 | 来源 | 后续复用建议 |
|---|---|---|
| 根因证据状态模型 | `establish-root-cause-evidence-governance` | BUG、返修、问题排查默认区分 confirmed / suspected / unknown，并要求证据路径和补证步骤 |
| 命令执行复盘 Hook | `establish-command-execution-review-hook`、`add-command-execution-review-hook-skill-coverage` | 所有 workflow 命令最终输出链路状态、问题证据、规范优化建议和未自动创建 Issue 说明 |
| 需求中心卡片动作矩阵 | REQ-0020 | 阶段、文档存在性、主动作/辅助动作、AI Chat、进度抽屉和缺失 Tips 应作为卡片状态矩阵维护 |
| Markdown 文档抽屉 | REQ-0021 | 预览/编辑/分栏、frontmatter、task list、代码复制、保存失败草稿和受控上传失败可复用为文档编辑器模板 |
| UI 截图对照门禁 | `add-opsx-modify-ui-screenshot-comparison-gate` | UI 返修先列附件截图逐项视觉对照表，再改组件和补 computed style 证据 |
| 本地开发写入边界 | REQ-0021 返修 | Compose mount、只读目录、保存 API 和失败态应进入环境验收 checklist |
| 跨项目 Harness 学习落地 | `apply-deepseek-*`、`apply-tilesfst-*` | 只读学习、脱敏日志、规则/技能/脚本同步和索引更新作为固定治理流程 |

## 行动项

| ID | 优先级 | 类型倾向 | 标题 | 背景 | 影响范围 | 建议验收要点 | 建议命令 | 状态 |
|---|---|---|---|---|---|---|---|---|
| S3-A001 | P1 | BUG/Change | 修复 AI Usage 本地 session JSONL 归因 | `~/.codex/sessions` 中存在 token_count，但 `extract-ai-usage.py` 未能归因为 Sprint command run，官方 snapshot 仍为估算回退 | `scripts/extract-ai-usage.py`、`data/ai-usage/`、sprint archive/exps token gate | 显式 JSONL、环境变量和默认 sessions 目录均能产出非零 command_run；未匹配时输出原因；矩阵中区分未观测与真实 0 | `/bug-capture` 或 `/opsx-propose fix-ai-usage-session-jsonl-command-attribution` | open |
| S3-A002 | P1 | Change | 优化 Sprint Fact Sheet summary/fields 输出 | sprint-003 large-sprint 且 warnings=62，完整 JSON 容易产生高额上下文输入 | `scripts/generate-sprint-fact-sheet.py`、`sprint-exps` | 支持 summary/fields；默认只输出状态、计数、warnings、token_risks、AI usage 状态；完整矩阵按需展开 | `/opsx-propose optimize-sprint-fact-sheet-summary-fields` | open |
| S3-A003 | P2 | Change | 规范验收报告历史 sign-off 与最终结论的呈现 | 最终结论已通过，但历史验收记录仍大量保留“待人工 sign-off”，复盘读取时容易误判 | `acceptance-report.md`、workflow-sync/sprint-archive 写入逻辑 | 最终状态单独置顶；历史记录保持原文但标注为过程态；Fact Sheet 能识别最终 pass 不受历史文案干扰 | `/opsx-propose normalize-acceptance-history-final-status` | open |
| S3-A004 | P2 | REQ | 建立复杂 UI 返修的一次性收口模板 | REQ-0020/REQ-0021 多次围绕按钮、抽屉、文档入口、进度区和 computed style 返修 | UI REQ、prototype、opsx-modify、视觉验收 | 模板包含截图对照表、动作按钮矩阵、modal/抽屉组件族、selector、状态和证据入口 | `/req-capture` | open |
| S3-A005 | P2 | REQ | 建立本地开发写入边界验收 checklist | Markdown 保存失败由 Compose 只读挂载触发，属于环境约束与功能验收交叉问题 | Docker Compose、本地 dev、文档保存 API、错误态 UX | checklist 覆盖 mount 权限、可写目录、只读目录、失败响应、前端草稿保留和脱敏日志 | `/req-capture` | open |
| S3-A006 | P3 | Change | 降低归档路径残留 warning 噪音 | Fact Sheet 发现 62 条 archived-path residual；虽不阻断关闭，但会增加复盘筛选成本 | archived Change docs、Fact Sheet warnings、stale scan | 区分合法历史引用与应修复残留；支持白名单或迁移脚本；warnings 聚合展示 | `/opsx-propose reduce-archived-path-residual-warnings` | open |

## 标准 Capture 文案

以下事项仅作为后续 capture 建议，当前命令未自动创建 Issue。

1. 建议命令：`/bug-capture` 或 `/opsx-propose`
   类型倾向：BUG/Change
   标题：修复 AI Usage 本地 session JSONL 归因
   背景：`~/.codex/sessions` 中存在真实 `token_count.total_token_usage`，但 Sprint 官方 snapshot 仍显示 `estimated_fallback` 且 command_run_count 为 0。
   影响范围：`scripts/extract-ai-usage.py`、`data/ai-usage/`、`sprint-archive`、`sprint-exps`。
   建议验收要点：显式 session JSONL、环境变量和默认 sessions 目录都能完成 workflow event、sprint、change 归因；未匹配时输出原因；未观测用 `-`，真实零值用 `0`。
   来源 Change/Sprint/命令：sprint-003 / `/sprint-exps sprint-003`。

2. 建议命令：`/opsx-propose`
   类型倾向：Change
   标题：优化 Sprint Fact Sheet summary/fields 输出
   背景：sprint-003 包含 26 个 Change、288 个 tasks 和 62 条 warnings，完整 Fact Sheet JSON 容易产生高上下文输入。
   影响范围：`scripts/generate-sprint-fact-sheet.py`、`sprint-exps`、`sprint-archive`。
   建议验收要点：支持 summary/fields 输出；默认不展开 usage matrices 和长 evidence hints；异常排查仍可按字段展开。
   来源 Change/Sprint/命令：sprint-003 / `/sprint-exps sprint-003`。

3. 建议命令：`/opsx-propose`
   类型倾向：Change
   标题：规范验收报告历史 sign-off 与最终结论的呈现
   背景：sprint-003 已最终通过并关闭，但验收历史中保留大量“待人工 sign-off”过程态文案。
   影响范围：`acceptance-report.md`、Workflow Sync、Sprint Fact Sheet。
   建议验收要点：最终结论与历史过程态可被脚本区分；Fact Sheet 不把历史待确认误判为关闭 blocker；文档保留事实链。
   来源 Change/Sprint/命令：sprint-003 / `/sprint-exps sprint-003`。

4. 建议命令：`/req-capture`
   类型倾向：REQ
   标题：建立复杂 UI 返修的一次性收口模板
   背景：REQ-0020 与 REQ-0021 在动作按钮、右侧抽屉、文档入口、进度展示、Markdown 阅读密度和 computed style 上多轮返修。
   影响范围：UI REQ、prototype、`/opsx-modify`、视觉验收。
   建议验收要点：模板包含截图对照表、动作按钮矩阵、modal/抽屉组件族、selector、状态、1440px 视觉证据和 computed style 采样。
   来源 Change/Sprint/命令：sprint-003 / `/sprint-exps sprint-003`。

5. 建议命令：`/req-capture`
   类型倾向：REQ
   标题：建立本地开发写入边界验收 checklist
   背景：REQ-0021 的 `capture.md` 保存失败由本地开发 Compose 对 `issues/` 的只读挂载触发。
   影响范围：Docker Compose、本地开发环境、文档保存 API、前端失败态。
   建议验收要点：覆盖 mount 权限、可写目录、只读目录、保存失败响应、前端草稿保留、脱敏日志和环境文档同步。
   来源 Change/Sprint/命令：sprint-003 / `/sprint-exps sprint-003`。

6. 建议命令：`/opsx-propose`
   类型倾向：Change
   标题：降低归档路径残留 warning 噪音
   背景：sprint-003 Fact Sheet 发现 62 条 archived-path residual，虽不阻断关闭，但增加复盘筛选成本。
   影响范围：archived Change docs、Fact Sheet warnings、stale scan。
   建议验收要点：区分合法历史引用与应修复残留；支持白名单或迁移脚本；warnings 聚合展示并避免重复噪音。
   来源 Change/Sprint/命令：sprint-003 / `/sprint-exps sprint-003`。

## 后续复用要求

- `/sprint-propose` 下一轮必须读取本复盘的 open 行动项，并在 Sprint 四件套中记录承接、延期或拒绝原因。
- `/req-complete` 处理需求中心卡片、Markdown 文档、空间上下文、复杂 UI 抽屉或本地开发写入边界时，应读取本复盘的可复用抽象。
- `/opsx-apply` 和 `/opsx-modify` 涉及 UI 返修时，必须先建立截图对照表、动作按钮矩阵和 computed style 证据清单。
- `/sprint-archive` 或 `/sprint-exps` 需要真实 token 统计时，必须优先修复或显式说明 AI Usage 归因状态，避免把未观测写成真实 0。

---
purpose: AI 行为入口
content: AI 开发流程入口、规则加载路由、OpenSpec 红线、目录与验证边界
created_at: 2026-07-29 22:55:00
updated_at: 2026-10-25 22:25:00
owner: MoonBox 产品团队
---

# AI Agent 工作指南

## 项目定位

MoonBox 是 AI 原生软件工厂，面向 AI 创业者、小型软件团队和 AI 原生企业团队，帮助他们建立由 Agent 驱动的软件研发组织。

当前启用 Web 端、管理后台、REST API、SQLite、MySQL 生产兼容路径、MinIO/S3 兼容对象存储、Docker Compose 本地/生产部署矩阵、Mintlify 产品手册站点、OpenSpec、需求治理、缺陷治理、Sprint 治理、发布治理和 `.agents/skills/` 技能入口。本地模型、微信小程序、移动端、桌面端暂未启用。

## 执行前读取路由

所有任务先读：

```text
AGENTS.md
openspec/project.md
rules/global.md
rules/language.md
rules/agent-context-budget.md
```

按任务追加读取：

| 任务类型 | 追加读取 |
|---|---|
| REQ / BUG | `rules/requirement-management.md`、`rules/bug-management.md`、`rules/issues-lifecycle.md`、对应 `issues/**` |
| Sprint | `rules/iterations-lifecycle.md`、相关 `iterations/change|archive/<sprint>/` |
| OpenSpec | `openspec/changes/<change-id>/`、`rules/document-governance.md` |
| 代码实现 | `rules/coding.md`、`rules/testing.md`、相关模块 README |
| API | `rules/api.md`、`docs/03-api-index.md`、OpenAPI 来源；涉及请求日志、链路字段、行为埋点、Task Trace 或请求封装时追加读取 `docs/standards/product-data-collection-observability.md` |
| DB | `rules/database.md`、`docs/04-database-design.md`；涉及 `usage_events`、`request_logs`、`task_traces`、`task_trace_spans`、索引、迁移或保留周期时追加读取 `docs/standards/product-data-collection-observability.md` |
| UI | `rules/ui-design.md`、`docs/standards/prototype-ui-acceptance.md`、前端设计 token 和组件入口；涉及附件、HTML、截图、标注图、既有页面或一对一复刻时追加建立 UI Reference Replication Contract |
| 部署 | `rules/environment.md`、`rules/port-management.md`、`rules/release.md`、`docs/02-deployment.md` |
| 产品手册 / Mintlify | `rules/document-governance.md`、`rules/release.md`、`docs/02-deployment.md`、`mintlify/README.md` |
| 对象存储 | `rules/data-management.md`、`rules/object-storage.md`、`docs/07-object-storage-strategy.md` |
| 安全 | `rules/security.md` |
| 数据采集 / 链路观测 | `docs/standards/product-data-collection-observability.md`、`docs/standards/task-trace-coverage.md` |
| 问题排查 / 根因 / 返修 | `rules/root-cause-evidence.md`、相关 `logs/`、截图、测试失败、Change/Issue trace 片段 |
| 命令顺序 / 工作流编排 | `docs/08-command-execution-order.md`、`.agents/skills/workflow-sync/SKILL.md` |

## Agent 技能入口

本项目只保留 `.agents/skills/`。不得新增或恢复 `.claude/`、`.codex/`、`.cursor/`、`.kiro/`、`.opencode/`。

仓库自有目录除根目录 `.agents/` 外，不得出现 `.agents/`、`.codex/` 工具路径；即使为空也须清理。目录校验覆盖全仓自有目录；非空残留、文件和符号链接先核对内容归属，不自动删除。

常用命令族：

| 域 | 命令 |
|---|---|
| 开发执行 | `/opsx-apply`（`openspec-apply-change` 共用连续执行契约） |
| 自动验收 | `/opsx-accept`（逐 AC 证据包与归档就绪） |
| 通用探索 | `/explore` |
| 治理优化 | `/spec-opt`、`/spec-study` |
| Git 安全与同步 | `/git-check`、`/git-sync` |
| 产品手册 | `/usage-docs-generate`、`/usage-docs-update`、`/usage-docs-validate` |
| 发布镜像 | `/release-propose`、`/release-prepare`、`/image-prepare`、`/image-build`、`/release-publish` |
| 部署升级 | `/upgrade-plan --from <fresh\|version> --to <version>`、`/upgrade-validate --plan <path>` |

## 流程红线

- 不允许绕过 OpenSpec Change 直接开发正式功能。
- 所有命令在需要用户选择、确认、补充信息或处理阻塞时，必须优先采用“原生交互卡片 + 结构化选项 + 推荐项 + 可补充说明”的引导式反馈；当客户端或工具层不支持原生交互卡片时，降级为文本结构化选项；每轮只聚焦 1-3 个关键决策，并根据用户答案动态收敛，不得用大段开放式追问替代。
- 未评审的 REQ/BUG 不得进入 Sprint 规划，不得转 OpenSpec，不得执行开发。
- `/capture`、`/req-capture`、`/bug-capture` 创建新 Issue 前必须读取对应 `CHANGELOG.md` 与 `_registry.yaml` 做重复/相似 Issue 检查；疑似重复时先输出候选、相似原因和处理选项，默认推荐关联/更新原 Issue，确认非重复后才新建。
- REQ/BUG 评审通过后必须先执行 `/sprint-propose` 纳入 Sprint 并同步为 `in_sprint`，再执行 `/req-opsx` 或 `/bug-opsx`；不得从 review 直接跳到 opsx。
- `openspec/specs/` 只保存已生效规格，除归档合并动作外不得直接修改。
- 新建业务代码必须放在 `src/` 约定边界内。
- `.env`、真实密钥、真实客户数据、运行时数据库文件和临时大文件不得提交。
- `/git-sync` 默认按明确交付范围选择性暂存，提交前运行 `/git-check`；正式版本标签必须基于发布事实，远程分叉先整合验证，禁止强制推送或覆盖远端标签。
- 跨项目学习使用 `/spec-study`；学习对象必须全程只读，学习报告统一放入 `docs/spec-logs/YYYYMMDDhhmmss-study-xxx.md`，本地学习对象持久化时必须脱敏为项目名或占位符。
- 规范优化使用 `/spec-opt`；规范、技能、脚本、目录边界或校验规则迭代日志统一放入 `docs/spec-logs/YYYYMMDDhhmmss-governance-xxx.md`，不得写入隐私、密钥、未脱敏日志、学习对象源码、本机绝对路径、系统用户名或用户主目录。
- Sprint ID 必须使用 `sprint-xxx` 三位数字递增格式；自动创建 Sprint 时扫描 `iterations/change/` 与 `iterations/archive/` 后取最大编号加一。
- `/sprint-propose` 选择或创建 Sprint 前必须运行 `bash scripts/project-python.sh scripts/validate-sprint-selection.py [--sprint <sprint-id>]`；无 active Sprint 默认下一个连续编号，一个 active Sprint 默认当前 Sprint，两个及以上 active Sprint 必须显式指定。
- 发布升级与回滚计划使用 `/upgrade-plan` 与 `/upgrade-validate`；命令只生成和校验计划，不自动执行生产升级、真实 env 修改、DB restore 或对象存储写入维护。
- 命令最终输出不得泄漏尖括号占位模板、通用示例或 `MUST/SHOULD` 规范语气；「下一步」与「待用户决策/处理」必须去重。
- 下一步可执行命令必须保留链路身份：REQ 链路的 `/req-*` 与后续 `/opsx-*` 使用完整 `REQ-xxxx-slug`，BUG 链路的 `/bug-*` 与后续 `/opsx-*` 使用完整 `BUG-xxxx-slug`，非 REQ/BUG Change 才使用 `<change-id>`。
- `/req-opsx` 与 `/bug-opsx` 新建 Change `trace.md` 时必须写入 `execution.schema_version: 1` schema v1 frontmatter，初始 `started_at` 与 `completed_at` 为 `null`；`/req-opsx` 的 `last_event` 为 `req.opsx`，`/bug-opsx` 的 `last_event` 为 `bug.opsx`；后续执行事实由 Workflow Sync 的 `opsx.start` 与 `opsx.apply` 维护。
- 所有 workflow 命令完成后必须输出「执行链路复盘」，包含链路状态、问题证据和规范优化建议；发现可优化点时默认只给建议命令或 capture 文案，不自动创建 follow-up Issue/Change，除非用户明确授权。
- API、DB、UI、部署或安全边界变化必须同步文档、规则和测试。
- API、DB、日志审计、行为埋点、Task Trace、Web/管理端请求封装、对象存储或 Agent Workflow 链路观测相关变更必须读取 `docs/standards/product-data-collection-observability.md`，并在 REQ、Change、Sprint 或验收材料中声明 `product_data_collection_observability`、`affected_layers`、具体 N/A 原因和 `validation` 摘要。
- 带 `prototype/` 的 UI 页面必须先完成原型拆解、UI Contract、UI Skeleton 首轮确认、1440px 与关键交互视觉验收、computed style 证据、Mock/API 边界声明和 REQ 文档最终一致性检查；不得缺少视觉证据、样式证据或文档回填即归档。
- UI 参考稿复刻必须先完成附件/HTML/截图反向工程、组件级视觉契约、selector 映射、computed style 采样清单和分批验收门禁；不得只用“更现代”“更贴近附件”等主观描述直接进入实现完成态。
- UI 参考稿复刻若包含动作按钮、FAB、卡片 footer、工具栏动作或阶段动作，必须先建立“动作按钮 → modal 类型 → selector → 状态 → 验收证据”矩阵，并按动作族一次性实现按钮与 modal 组件族；不得继续逐按钮问答返修。
- UI 型 `/opsx-modify` 若验收反馈包含附件截图、标注图、原型截图或实际截图，必须先建立“附件截图逐项视觉对照表”，逐项确认期望、实际、偏差、检查方式、处置结论和证据入口；对照表证据不足时先补证，不得直接返修。
- REQ 来源 `/opsx-modify` 完成前必须执行 REQ 子文档一致性扫尾检查，按实际存在的 `requirement.md`、业务流程、用户故事、`acceptance.md`、`trace.md` 和 `prototype/**` 判断是否需同步，避免只更新 PRD 而遗漏子文档。
- 问题排查、测试、BUG 完善、验收返修或效果不如预期时遵守 `rules/root-cause-evidence.md`：需要产品运行态证据时可直接通过浏览器自主取证，优先复用 Codex 侧边浏览器，无需人工二次确认；自主取证仍不足时才给出人工补证步骤，无证据不得确认根因。
- 浏览器取证失败时遵守 `rules/root-cause-evidence.md` §5.0：先查现有标签页，清单失败后直接连接浏览器窗口并尝试可行替代入口；终端连接失败或一次工具超时不能单独证明产品无法访问，旧页面展示与当前服务连通性须分别标注。
- `/bug-explore`、`/bug-generate`、`/bug-complete` 遇到尚未确认的根因时，按 `rules/root-cause-evidence.md` §2.1 在当前命令内继续自主补证；文档生成不构成停止条件，证据不足不得伪造 `confirmed`。
- `/explore` 与 `/req-explore` 的结论依赖当前产品表现且材料不足时，按 `rules/root-cause-evidence.md` 第 5 节主动浏览产品取证；只读探索默认不写仓库或持久业务数据。
- `/opsx-modify` 验收返修执行中展示为研发中；返修完成、验证、文档同步和 Workflow Sync 通过后回到验收中 / 待复验。该展示是返修投影语义，不得用普通 `in_progress` 覆盖 Change `applied` 事实或首次 apply 的 `execution.completed_at`。
- `/opsx-apply` 完成后进入 `/opsx-accept`；已有验收结果按输入指纹增量复验，证据归属 Change `evidence/acceptance/`。运行前先检查环境与证据，视觉 AC 明确映射阶段×视口组合及证据入口；预检未就绪只生成阻塞诊断，逐 AC 摘要须区分命令、视觉与产品轮次证据。有验收计划的 Change 归档前必须取得当前 ready 结论；验收不自动扩大归档授权。
- OpenSpec 文档变更后运行中文优先校验；Mintlify 变更后运行产品手册校验。
- `/req-opsx` 与 `/bug-opsx` 生成 Change 后运行当前 Change 聚焦中文校验和全仓残留分离报告，当前 Change 失败阻断当前链路，无关 active Change 残留只作 warning。
- `/req-opsx` 与 `/bug-opsx` 使用 OpenSpec CLI 模板生成 proposal、design、tasks 时必须将英文脚手架标题中文化，不得把 `Why`、`What Changes`、`Capabilities`、`Impact`、`Implementation`、`Testing`、`Documentation` 等模板标题原样落盘。
- 完成前运行相关验证；无法运行时在回复中说明原因。

- 两份 apply 技能共用 [Apply 连续执行契约](docs/08-command-execution-order.md#apply-连续执行契约)：分批仅汇报进度，自检修复在当前 apply 内闭环，按硬阻塞、完成门禁和中断续接规则执行。每次final前执行停止前决策；存在可执行任务不得等待“继续”，局部依赖只阻断相关任务；行为验收区分合成回归与真实观察。

## 工作流同步

治理命令及任何治理文档写入前，先运行 `bash scripts/project-python.sh --check`。Python 治理脚本统一经 `bash scripts/project-python.sh scripts/脚本名.py` 调用；解释器选择与依赖准备见 `scripts/README.md`。CI/容器显式配置 `PYTHON_BIN`，无有效环境时先修复环境，不回退系统 Python。Python 子命令使用 `sys.executable`，shell 子命令继承 `PYTHON_BIN`。

状态变化后运行：

```bash
bash scripts/project-python.sh scripts/sync-workflow-status.py --event <event> [--req REQ-xxxx] [--bug BUG-xxxx] [--change change-id] [--sprint sprint-xxx|auto]
```

归档涉及 Issue 阶段迁移时继续运行：

```bash
bash scripts/project-python.sh scripts/promote-issue-stage.py --to archive [--change change-id] [--sprint sprint-xxx] --reason "<event>"
```

## 回复要求

回复默认中文。涉及代码必须说明修改路径、影响面、验证结果，以及是否需要同步 API、数据库、UI、部署、安全或客户端生成。

- REQ priority / BUG severity 的 Frontmatter 归属和同步统一遵循 `rules/document-governance.md` 的“Issue 分级元数据”。

Sprint容量遵循 `rules/iterations-lifecycle.md`：默认30人天，已有有效显式值保留，覆盖需明确请求；容量工具为 `scripts/add-sprint-scope-item.py --capacity-person-days`，修改后重算门禁与派生文档。

Change 创建与归档遵循 [Change 身份唯一性](rules/document-governance.md#change-身份唯一性)，创建前检查活动与归档 ID 占用。

本地 `logs/` 取证目录须被 Git 忽略且不得跟踪，归属和证据转存规则见 `rules/directory-structure.md`；保留现有日志，不因目录存在删除数据。

自动验收与归档编排统一遵循 [连续执行与恢复契约](docs/standards/opsx-acceptance.md)：逐 AC 队列与检查点、局部阻塞隔离、待采集证据自主补齐、精确指纹、命令去重、环境样本契约和归档预演。存在可执行项不得仅输出 diagnostic 后停止；交付、证据与用量分别报告，wrapper 成功不重复收尾。

## 稳定验证编排

遵循 [稳定批次与增量复验契约](docs/standards/opsx-acceptance.md#稳定批次与增量复验契约)：完整入口前置检查、修改稳定后集中验证、受影响范围增量复验和里程碑进度反馈。保留现有正确性门禁；未完成入口验证不提前宣布最终完成。

阶段变化、新发现与阻塞优先反馈；无变化时合并日志与轮询，保留必要状态反馈。复用证据须有当前有效依据，输出精简不减少检查。

## 治理执行量化与授权优化

遵循 [分级闭环](docs/standards/governance-feedback-loop.md)：非只读命令入口使用 `scripts/governance_feedback.py start`，完成门禁后 `finish` 自动复盘；只有明确边界的实测用量参与收益。用户已授权本项目治理范围自动优化，策略见 `rules/governance-feedback-policy.json`，仍保留 Change、Sprint、验证、预算和防递归门禁。只读探索不落盘，优化任务自身计成本，未获授权或业务范围仍只给建议。

面向用户的输出遵循 `rules/language.md` 的“产品经理视角沟通”：先讲业务结果和用户影响，优先日常语言，必要技术术语随文解释；决策说明体验、成本、时间和风险。

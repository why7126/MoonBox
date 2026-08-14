---
title: Sprint-002 经验复盘
purpose: 总结 sprint-002 的流程、需求、开发质量、组件抽象与模型 Token 使用经验
content: Sprint 复盘、行动项、后续 capture 建议和知识库沉淀
source: /sprint-exps sprint-002
owner: MoonBox 产品团队
status: active
created_at: 2026-08-14 16:31:49
updated_at: 2026-08-14 16:31:49
sprint_id: sprint-002
---

# Sprint-002 经验复盘

## Sprint 概况

| 指标 | 结果 |
|---|---|
| Sprint | sprint-002 |
| 生命周期 | completed / archive |
| 时间 | 2026-08-09 07:26:26 至 2026-08-23 07:26:26 |
| 范围 | 9 个 REQ，10 个 BUG，26 个 OpenSpec Change |
| 任务完成 | 498/498 |
| 容量 | 36 人天 / 30 人天，容量占用 120% |
| 归档状态 | 26/26 Change archived，readiness/stale scan PASS |

Sprint-002 是一个高密度交付 Sprint：一方面承接 sprint-001 的治理行动项，补齐 `/git-check`、引导式反馈、Mintlify 轻量治理、Issue CHANGELOG 和 prototype UI Gate；另一方面集中交付前台需求中心、真实数据接入、统一账号认证、前后台用户菜单、后台空间管理以及登录/上传/用户管理等缺陷闭环。最终 26 个 Change 全部归档，Fact Sheet warnings 为 0，Sprint 四件套已迁入 `iterations/archive/sprint-002/`。

## 流程复盘

### 做得好的地方

- Sprint archive 前置 Fact Sheet、readiness、stale scan 和 AI Usage gate，避免在 26 个 Change、498 个 tasks 的规模下人工逐项翻找事实。
- sprint-001 行动项被正式承接：`S1-A001` 与 `S1-A004` 进入 sprint-002，`S1-A002`、`S1-A003` 明确 deferred，说明知识库已经开始影响 Sprint 规划。
- UI 类 Change 形成了更完整的 prototype-driven 链路：UI Contract、UI Skeleton、1440px 视觉验收、computed style 证据、Mock/API 边界和 REQ 最终一致性逐步闭环。
- 归档阶段清理了已归档 Issue 子文档里的中间态文案和 active Change 路径，最终 `archived_path_residuals=0`，减少后续复盘和发布读取噪音。
- Workflow Sync 在最终 `sprint.archive` 后完成 133 个 Issue 子文档扫描，19 个验收结果均回填为 passed，说明派生状态同步已经能覆盖较复杂的 REQ/BUG 组合。

### 需要修正的地方

- 范围达到容量上限：36 人天正好是 30 人天容量的 120%，且实际包含 26 个 Change，说明 sprint-002 更像“交付 + 治理 + 返修”混合迭代，后续应拆分产品 Sprint 与治理 Sprint。
- REQ-0017 的后台空间管理累积 120/120 tasks，是单 Change 超大范围信号；空间列表、审批、回收站、空间详情、成员、配额、审计和视觉返修应在需求阶段拆成更小的垂直切片。
- 登录、会话、头像上传、前后台用户菜单与权限边界在多个 REQ/BUG 中重复出现，说明账号域缺少统一 cross-cutting checklist，导致修复在多个 Change 间反复补齐。
- Docker/media-upload 验收和端口/测试身份策略仍容易被本地环境影响；BUG-0007 已治理脚本口径，但后续所有 Docker 验收需要默认使用脚本准备身份与动态端口。

## 模型 Token 使用分析

### Token Usage Fact Sheet

| 指标 | 值 | 证据/说明 |
|---|---:|---|
| 精确 token 统计 | 有 | Fact Sheet: `ai_usage_snapshot.snapshot_status=present` 且 `ai_usage_mode=actual` |
| AI usage mode | actual | 来源：`data/ai-usage/sprints/sprint-002.json` |
| Snapshot status | present | generated_at: 2026-08-14T08:29:42.274461Z |
| Snapshot warning_count | 0 | Fact Sheet 无 AI usage warning |
| command_run_count | 219 | Sprint 级真实快照 |
| model_call_count | 3611 | Sprint 级真实快照 |
| tool_call_count | 6036 | Sprint 级真实快照 |
| input_tokens | 494317568 | 其中 cached_input_tokens 为 476126720 |
| output_tokens | 1610596 | reasoning_output_tokens 为 93554 |
| total_tokens | 496484530 | Sprint 级真实快照 |
| retry_count | 0 | Fact Sheet 统计 |
| 主要输入消耗 | 高 | 26 个 Change、498 个 tasks、Sprint 四件套、规则/技能、Issue/Change trace |
| 主要输出消耗 | 中 | Workflow Sync、Fact Sheet JSON、测试/构建/Docker 验收摘要、视觉证据记录 |
| 已采用节省策略 | 有 | Fact Sheet 优先、readiness 摘要、stale scan 定点清理、warnings=0 后不再回读原文 |

本 Sprint 的 token 统计可以按真实快照分析。最大特征是 input 与 cached input 占绝对大头，说明大量消耗来自长上下文复用、规则/技能/四件套和多 Change 文档读取，而不是最终输出本身。`token_risks` 也明确指出：Sprint 四件套中 2 个文件超过 200 行、OpenSpec Change 数量达到 26、archive lookup 应避免扫全量历史归档。

### 高消耗来源

| 来源 | 影响 | 证据 | 优化方案 |
|---|---|---|---|
| Sprint 四件套 | high | `sprint.md` 369 行，`sprint.yaml` 253 行 | `/sprint-exps`、`/sprint-archive` 默认读 Fact Sheet；只有 warnings 或 focus 时分段读取 |
| OpenSpec Change 数量 | high | 26 个 Change、498/498 tasks | 下一 Sprint 限制单 Sprint Change 数；超 10 个 Change 自动分批复核并只读 batch summary |
| 超大 UI Change | high | `add-admin-space-management` 单 Change 120 tasks | 后续后台复杂模块拆为列表/详情/审批/审计/视觉返修多个垂直 Change |
| 规则与技能重复读取 | medium | 跨 req/bug/opsx/sprint/release/usage-docs 多命令链路 | 同一会话复用已读摘要；高风险阶段只补读变更过的规则或目标 Skill |
| Fact Sheet / Workflow Sync 输出 | medium | 完整 JSON 可包含 usage matrices 和大量 evidence hints | 默认 summary；需要矩阵时使用字段过滤，不把完整 JSON 贴入复盘 |
| 测试、构建和 Docker 日志 | medium | 多个 Web test/build、pytest、Docker media upload 验收贯穿 Sprint | 成功路径只记录命令、退出码和证据路径；失败只截取失败用例、关键堆栈和相关文件片段 |

### 优化行动项

| ID | 优先级 | 描述 | 建议下一步 | 状态 |
|---|---|---|---|---|
| T2-001 | P1 | 为 Sprint Fact Sheet 增加稳定 `--summary-json` 或字段过滤，默认隐藏 usage matrices 和 evidence hints 明细 | `/opsx-propose optimize-sprint-fact-sheet-summary-json` | open |
| T2-002 | P1 | 下一 Sprint 规划增加 Change 数量与单 Change task 数门禁，超过阈值必须拆分或说明原因 | `/sprint-propose --from-retrospective sprint-002` | open |
| T2-003 | P2 | 为账号/会话/头像上传能力建立 cross-cutting checklist，减少前后台 session、头像读取和改密边界反复返修 | `/req-capture` | open |
| T2-004 | P2 | Docker 验收统一脚本化测试身份、动态端口和隔离栈证据记录 | `/opsx-propose standardize-docker-acceptance-fixtures` | open |

## 需求与设计复盘

- 前台需求中心与真实数据接入的拆分方向正确：先交付 9 阶段看板和空间上下文，再接入治理事实源、状态映射、权限态和 Mock/API 边界，降低一次性变更风险。
- 统一账号认证是 sprint-002 的关键底座，但它与多个前后台用户菜单 BUG/REQ 交织，后续账号域需求应先统一认证路径、session key、头像 URL、权限态和改密后会话清理规则。
- 后台空间管理的业务边界过宽，验收从列表、审批、回收站一路延伸到详情、成员、审计、配额、视觉和弹窗交互，需求阶段应把“空间全生命周期”拆成清晰的 capability slices。
- prototype-driven UI Gate 显著降低了最终归档风险：REQ-0012、REQ-0014、REQ-0017 都通过 UI Skeleton、视觉证据和最终一致性闭环，但成本较高，应该在 `/req-complete` 阶段提前确认证据清单。

## 开发质量复盘

- API、认证、媒体上传、后台空间管理和需求中心 BFF 都补了后端或前端回归测试，并同步了 OpenAPI/API/DB/部署/对象存储文档，质量闭环较完整。
- 前后台共享组件开始成型：统一头像、用户菜单、后台侧边栏、AdminList/AdminModal、日期时间选择器、分页、固定浮层和 lightweight tags 都有后续复用价值。
- 质量风险主要来自交互细节返修：更多菜单浮层、亮/暗主题按钮可读性、成员/审计表格密度、弹窗下拉裁剪、状态标签与中文枚举格式等，说明视觉验收应更早进入 apply 阶段。
- `/git-check`、env ignore、directory structure、stale scan、archive evidence 和 workflow sync check 组成了较强的归档前质量网，后续应继续让脚本输出可执行修复建议。

## 可复用抽象

| 抽象 | 来源 | 后续复用建议 |
|---|---|---|
| 需求中心 BFF 事实源读取 | REQ-0013 | 后续治理看板优先复用 registry/OpenSpec/Sprint 解析与安全脱敏策略 |
| 统一账号认证 `/api/v1/auth/*` | REQ-0016 / BUG-0006 | 所有前后台自助资料、头像、改密、退出登录走统一 Auth API，后台管理接口只保留二次授权 |
| 前后台用户菜单 | REQ-0010 / REQ-0014 / BUG-0004 / BUG-0005 | 菜单展示、头像、昵称、退出、进入后台、修改密码与主题偏好应作为共享 UX checklist |
| 头像上传与受保护读取 | REQ-0011 / REQ-0014 / REQ-0016 | 统一 `/api/v1/auth/avatar/{filename}`，禁止恢复旧 admin avatar 路径 |
| Admin 空间管理页面模式 | REQ-0017 | 列表、详情页、审批、回收站、成员、审计、配额操作可沉淀为后台复杂实体页面模板 |
| 原型驱动 UI Gate | REQ-0012 / REQ-0017 | 继续要求 UI Skeleton、1440px、computed style 和 Mock/API 边界声明 |
| Docker 验收 fixture | BUG-0007 | 媒体上传和部署验收默认动态端口、脚本化身份、隔离栈和证据路径 |

## 行动项

| ID | 优先级 | 类型倾向 | 标题 | 背景 | 影响范围 | 建议验收要点 | 建议命令 | 状态 |
|---|---|---|---|---|---|---|---|---|
| S2-A001 | P1 | Change | 优化 Sprint Fact Sheet summary JSON 输出 | sprint-002 真实 token 快照显示 Fact Sheet/矩阵输出可能很大，复盘只需要状态、计数、warnings 和 usage totals | `scripts/generate-sprint-fact-sheet.py`、`sprint-exps` | 默认 summary-json 不展开 usage matrices；支持按字段读取；复盘仍能拿到 AI usage totals | `/opsx-propose optimize-sprint-fact-sheet-summary-json` | open |
| S2-A002 | P1 | REQ | 下一 Sprint 增加范围拆分门禁 | sprint-002 达到 26 Change、498 tasks、容量 120%，单 Change 最高 120 tasks | Sprint 规划、容量评估、Change 拆分 | 超过 10 个 Change 或单 Change 超 40 tasks 时必须拆分或写明豁免；sprint.md 记录风险 | `/sprint-propose --from-retrospective sprint-002` | open |
| S2-A003 | P2 | REQ | 建立账号域 cross-cutting checklist | 登录、会话、头像、改密、前后台菜单在多个 REQ/BUG 中重复返修 | 认证 API、前后台 session、头像上传、用户菜单 | checklist 覆盖 session key、退出登录、改密清理、头像 URL、权限态、普通用户/管理员边界 | `/req-capture` | open |
| S2-A004 | P2 | Change | 标准化 Docker 验收 fixture | BUG-0007 暴露固定端口和默认管理员密码依赖，后续 Docker 验收仍可能复发 | Docker 验收脚本、media upload、部署文档 | 验收脚本准备测试身份；动态端口；不依赖默认密码；输出脱敏证据摘要 | `/opsx-propose standardize-docker-acceptance-fixtures` | open |
| S2-A005 | P2 | REQ | 沉淀后台复杂实体页面模板 | REQ-0017 的列表/详情/审批/回收站/成员/审计/配额模式可复用 | 后台管理复杂实体页面、AdminList/AdminModal、详情页 Tab | 新实体页面复用列表/详情/审计/操作弹窗模式；包含 1440px 和 computed style 验收 | `/req-capture` | open |

## 标准 Capture 文案

以下事项仅作为后续 capture 建议，当前命令未自动创建 Issue。

1. 建议命令：`/opsx-propose`
   类型倾向：Change
   标题：优化 Sprint Fact Sheet summary JSON 输出
   背景：sprint-002 复盘依赖 Fact Sheet，但完整 JSON 容易包含 usage matrices、evidence hints 和大量归因矩阵，增加 token 消耗。
   影响范围：`scripts/generate-sprint-fact-sheet.py`、`sprint-exps`、AI usage 复盘。
   建议验收要点：默认 `--summary-json` 只输出 sprint、scope counts、warnings、token_risks、AI usage status/totals；支持按字段读取矩阵；现有 `--json` 兼容。
   来源 Change/Sprint/命令：sprint-002 / `/sprint-exps sprint-002`。

2. 建议命令：`/req-capture`
   类型倾向：REQ
   标题：下一 Sprint 增加范围拆分门禁
   背景：sprint-002 范围达到 26 Change、498 tasks、容量 120%，单个后台空间管理 Change 达到 120 tasks。
   影响范围：Sprint 规划、容量评估、OpenSpec Change 拆分。
   建议验收要点：超过 10 个 Change、容量超过 100% 或单 Change 超 40 tasks 时必须拆分、延期或写明豁免；Sprint 四件套记录决策。
   来源 Change/Sprint/命令：sprint-002 / `/sprint-exps sprint-002`。

3. 建议命令：`/req-capture`
   类型倾向：REQ
   标题：建立账号域 cross-cutting checklist
   背景：登录、会话、头像、修改密码、前后台用户菜单和权限边界在多个 REQ/BUG 中重复返修。
   影响范围：认证 API、前台 session、后台 session、头像上传、用户菜单、权限态。
   建议验收要点：checklist 覆盖 session key、退出登录、改密后会话清理、头像 URL、普通用户/管理员权限边界、前后台菜单同步。
   来源 Change/Sprint/命令：sprint-002 / `/sprint-exps sprint-002`。

4. 建议命令：`/opsx-propose`
   类型倾向：Change
   标题：标准化 Docker 验收 fixture
   背景：BUG-0007 暴露 Docker media upload 验收依赖固定端口和默认管理员密码，后续部署验收应默认脚本化。
   影响范围：Docker 验收脚本、对象存储上传、部署文档、测试身份策略。
   建议验收要点：脚本准备测试身份；动态端口；不依赖默认密码；输出脱敏摘要；本地真实 env 不进入文档或日志。
   来源 Change/Sprint/命令：sprint-002 / `/sprint-exps sprint-002`。

5. 建议命令：`/req-capture`
   类型倾向：REQ
   标题：沉淀后台复杂实体页面模板
   背景：REQ-0017 的空间管理已形成列表、详情、审批、回收站、成员、审计、配额和弹窗操作组合模式。
   影响范围：Web 管理后台复杂实体页面、AdminList/AdminModal、详情页 Tab、审计抽屉。
   建议验收要点：新实体页面可复用列表/详情/审计/操作弹窗模式；包含 1440px 视觉验收、computed style 验收和 Mock/API 边界声明。
   来源 Change/Sprint/命令：sprint-002 / `/sprint-exps sprint-002`。

## 后续复用要求

- `/sprint-propose` 下一轮必须读取本复盘的 open 行动项，并在 Sprint 四件套中记录承接、延期或拒绝原因。
- `/req-complete` 处理账号、上传、后台复杂实体、prototype UI 时，应优先读取本复盘的可复用抽象。
- `/opsx-apply` 处理 Docker、media upload、认证或后台空间类 Change 时，必须提前声明测试身份、动态端口和验收证据边界。

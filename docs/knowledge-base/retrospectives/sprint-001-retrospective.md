---
title: Sprint-001 经验复盘
purpose: 总结 sprint-001 的流程、需求、开发质量、组件抽象与模型 Token 使用经验
content: Sprint 复盘、行动项、后续 capture 建议和知识库沉淀
source: /sprint-exps sprint-001
owner: MoonBox 产品团队
status: active
created_at: 2026-08-08 23:35:30
updated_at: 2026-08-08 23:35:30
sprint_id: sprint-001
---

# Sprint-001 经验复盘

## Sprint 概况

| 指标 | 结果 |
|---|---|
| Sprint | sprint-001 |
| 生命周期 | completed / archive |
| 时间 | 2026-07-30 08:51:51 至 2026-08-08 23:23:52 |
| 范围 | 8 个 REQ，0 个 BUG，17 个 OpenSpec Change |
| 任务完成 | 195/195 |
| 容量 | 27 人天 / 30 人天，容量占用 90% |
| 归档状态 | 17/17 Change archived，readiness/stale scan PASS |

Sprint-001 从官网首页、登录页、数据库兼容开始，扩展到管理后台用户管理、后台认证、CRUD 列表模板、首次登录激活，并穿插多项治理 Change。范围很密，但整体闭环成功：所有 Change 已归档，Issue 已迁入 archive，Sprint 四件套已关闭。

## 流程复盘

### 做得好的地方

- `sprint.yaml` 成为机器事实源后，Sprint 归档可以通过 Fact Sheet、readiness 和 stale scan 聚合判断，避免逐个 Change 全量翻阅。
- 后半段建立了更强的顺序门禁：REQ 评审后必须先纳入 Sprint，再创建 OpenSpec Change，再 apply/archive；这避免了 Issue、Sprint 和 Change 三套状态各走各的。
- 归档阶段新增 stale scan，及时发现四件套和 Issue trace 里的旧状态文案，防止 Sprint close 后仍残留“待 req-opsx / proposed / applied”。
- 原型驱动 UI 门禁被固化为治理能力，后续带 prototype 的页面必须有 UI Skeleton、1440px 视觉验收和 REQ 最终一致性回填。

### 需要修正的地方

- Sprint 范围在中途持续追加，治理类 Change 和产品类 Change 混在同一 Sprint 中，导致归档队列达到 17 个 Change，复核成本明显上升。
- 部分早期文档以人读说明记录“当前状态”，在 Change 归档后没有同步改为闭环语义，最终被 stale scan 阻断。
- REQ-0004、REQ-0005、REQ-0006、REQ-0007 之间复用了用户管理、认证、弹窗、toast、分页、上传等横切能力，但抽象是在迭代中逐步形成，不是 Sprint 开始前统一约束。

## 模型 Token 使用分析

### Token Usage Fact Sheet

| 指标 | 值 | 证据/说明 |
|---|---:|---|
| 精确 token 统计 | 无完整可信口径 | Fact Sheet 暴露 snapshot，但状态为 stale 且 coverage 有 warning |
| AI usage mode | estimated_fallback | Fact Sheet: `ai_usage_snapshot.ai_usage_mode` |
| Snapshot status | stale | Fact Sheet: `ai_usage_snapshot.snapshot_status` |
| Snapshot warning_count | 3 | `changes-coverage-missing`、`requirements-coverage-missing`、`snapshot-stale` |
| command_run_count | 85 | 仅作为估算快照字段，不作为完整真实统计结论 |
| model_call_count | 1248 | 仅作为估算快照字段，不作为完整真实统计结论 |
| tool_call_count | 2153 | 仅作为估算快照字段，不作为完整真实统计结论 |
| total_tokens | 171453217 | estimated_fallback 下仅用于量级参考 |
| 主要输入消耗 | 高 | 17 个 Change、195 个 tasks、Sprint 四件套、Issue trace、规则与技能文件 |
| 主要输出消耗 | 中 | 测试日志、Workflow Sync 报告、readiness/fact sheet 大 JSON、diff 输出 |
| 已采用节省策略 | 有 | Fact Sheet 优先、`sed -n` 分段读取、readiness 摘要、stale scan 定点修复 |

**原因与影响**：`ai_usage_snapshot` 存在但 stale，且有 Change/Requirement coverage warning。因此本复盘保留 `estimated_fallback`，不把 token 数字当作完整真实统计。影响是只能判断高消耗来源和优化方向，不能精确归因每个命令的实际成本。推荐动作：在需要精确复盘时运行 `python scripts/extract-ai-usage.py --session-jsonl <local-session.jsonl> --sprint sprint-001` 后重新生成 Fact Sheet。

### 高消耗来源

| 来源 | 影响 | 证据 | 优化方案 |
|---|---|---|---|
| Sprint 四件套 | high | Fact Sheet 标记 `sprint.md` 超过 200 行 | 后续命令先读 Fact Sheet，再按 warning/evidence hints 定点读取 |
| OpenSpec archive 查找 | high | 17 个 Change、195/195 tasks | 按 `sprint.yaml changes[]` 分批处理，避免扫全量 `openspec/archive/**` |
| 规则和技能重复读取 | medium | Sprint 内多次跨 req/opsx/sprint 技能切换 | 同一会话复用已读摘要，仅在 mtime/updated_at 改变时补读 |
| 测试与构建输出 | medium | Web test/build、pytest、Docker/环境校验贯穿多个 Change | 成功路径只记录命令和摘要；失败时只截取失败用例与关键堆栈 |
| Workflow Sync 与 Fact Sheet JSON | medium | JSON 输出可超过常规阅读预算 | 默认使用 summary；需要矩阵时再用字段过滤 |

### 优化行动项

| ID | 优先级 | 描述 | 建议下一步 | 状态 |
|---|---|---|---|---|
| T-001 | P1 | 为 `/sprint-exps` 增加 Fact Sheet 字段过滤或 summary 模式，避免默认输出完整 usage matrices | `/opsx-propose optimize-sprint-fact-sheet-output` | open |
| T-002 | P1 | 下一 Sprint 规划时强制读取最近复盘和 open 行动项，并限制单 Sprint Change 数量或拆分治理 Sprint | `/sprint-propose --from-retrospective sprint-001` | open |
| T-003 | P2 | 为归档后人读文档增加旧状态扫描自动修复建议，减少手工 stale 文案修补 | `/req-capture` 或 `/opsx-propose add-stale-close-fact-reconcile` | open |
| T-004 | P2 | 对成功测试/构建命令统一沉淀“摘要优先”记录格式，减少后续 trace 和验收文档噪音 | `/opsx-propose standardize-validation-summary-format` | open |

## 需求与设计复盘

- 首页、登录页、数据库兼容是基础能力，后续管理后台能力直接依赖它们；这种“先底座、再后台”的顺序是对的。
- 管理后台用户管理、后台认证、CRUD 列表模板、首次登录激活存在强耦合，最好在 Sprint 规划阶段就明确共享对象：用户状态机、会话撤销策略、列表页模板、弹窗与 toast 规范。
- 带 prototype 的 REQ 在 Sprint 后半段治理才逐步成熟。后续进入 Sprint 前，REQ 文档应先完成 prototype_refs、UI Skeleton 输入、AC-PROTOTYPE 和 1440px 验收口径。
- 数据库兼容和对象存储路径是非 UI 但高风险的验收点，需要在需求阶段把本地/生产差异、CI 条件和跳过条件写清楚，避免“本地跳过”被误解为未验证。

## 开发质量复盘

- 后端 API、数据库兼容、后台认证和用户管理都补了集成测试，形成了可回归的质量底座。
- Web 端从页面级实现逐步收敛到模板化列表页、统一弹窗、fixed toast 和分页 DOM 验收，减少了后续后台页面重复返工风险。
- 上传链路、认证会话撤销、冻结/解冻状态恢复都属于容易漏掉的跨层问题；本 Sprint 已沉淀为 best-practices，下一轮应前置读取。
- 归档时 readiness、directory structure、env ignore、stale scan 和 workflow sync check 全部通过，说明治理脚本已经能覆盖主要闭环风险。

## 可复用抽象

| 抽象 | 来源 | 后续复用建议 |
|---|---|---|
| AdminListPage / CRUD 列表模板 | REQ-0006 | 新后台实体页面必须优先复用列表模板、分页 DOM、筛选栏和操作槽位 |
| 设计系统确认弹窗 | REQ-0004 / REQ-0006 / REQ-0007 | 禁止回退到 `window.confirm`；敏感操作统一弹窗宽度、按钮尺寸和滚动策略 |
| fixed toast | REQ-0004 / REQ-0006 / REQ-0007 | 作为后台反馈的默认模式，避免被表格滚动容器裁剪 |
| 用户状态机 | REQ-0004 / REQ-0007 | 明确待激活、正常、冻结、已删除以及冻结前状态恢复规则 |
| 后台会话校验 | REQ-0005 | 后台 API 每次请求校验服务端会话，冻结、退出、重置密码后旧 token 不应继续有效 |
| 原型驱动 UI Gate | REQ-0008 | prototype 页面必须先拆解为 UI Skeleton，再做 1440px 视觉验收与最终一致性回填 |

## 行动项

| ID | 优先级 | 类型倾向 | 标题 | 背景 | 影响范围 | 建议验收要点 | 建议命令 | 状态 |
|---|---|---|---|---|---|---|---|---|
| S1-A001 | P1 | REQ | 下一 Sprint 规划承接 sprint-001 复盘行动项 | sprint-001 产生多项 open 经验，需要在 sprint-002 规划前显式承接 | Sprint 规划、知识库读取、容量控制 | sprint.md 写入知识库承接项；sprint.yaml 记录 action id；未承接项明确 deferred/rejected | `/sprint-propose --from-retrospective sprint-001` | open |
| S1-A002 | P1 | Change | 优化 Sprint Fact Sheet 输出字段过滤 | `/sprint-exps` 默认 JSON 过大，usage matrices 容易造成复盘阶段 token 浪费 | `scripts/generate-sprint-fact-sheet.py`、sprint-exps | 默认 summary 不展开矩阵；需要时可按字段读取；现有脚本兼容 | `/opsx-propose optimize-sprint-fact-sheet-output` | open |
| S1-A003 | P2 | Change | 增加 Sprint close 陈旧事实自动修复建议 | 归档关闭被历史“待 req-opsx/proposed/in_sprint”文案阻断，需要更清晰的 reconcile 路径 | stale scan、workflow sync、Issue 子文档 | stale scan 输出可执行 reconcile 建议；不修改 workflow-sync marker 块 | `/opsx-propose add-stale-close-fact-reconcile` | open |
| S1-A004 | P2 | REQ | 后台页面新增能力统一套用 CRUD 模板与 UI Gate | 用户管理、CRUD 模板和首次登录激活证明后台页面需要统一前置验收 | 后台列表页、弹窗、toast、分页、prototype | 新后台页面必须有 AdminListPage 复用说明、1440px 视觉证据和弹窗/toast 验收 | `/req-capture` | open |

## 标准 Capture 文案

以下事项仅作为后续 capture 建议，当前命令未自动创建 Issue。

1. 建议命令：`/req-capture`
   类型倾向：REQ
   标题：后台页面新增能力统一套用 CRUD 模板与 UI Gate
   背景：Sprint-001 中用户管理、CRUD 列表模板、弹窗、toast 和 prototype 视觉验收反复出现，说明后台页面需要前置统一门禁。
   影响范围：Web 管理后台页面、列表模板、弹窗、toast、分页、prototype 验收。
   建议验收要点：新后台页面必须声明 AdminListPage 复用方式；必须有 1440px 视觉证据；敏感操作不得使用 `window.confirm`；toast 为 fixed。
   来源 Change/Sprint/命令：sprint-001 / `/sprint-exps sprint-001`。

2. 建议命令：`/opsx-propose`
   类型倾向：Change
   标题：优化 Sprint Fact Sheet 输出字段过滤
   背景：`/sprint-exps` 需要 Fact Sheet，但完整 JSON 含 usage matrices 时输出过大。
   影响范围：`scripts/generate-sprint-fact-sheet.py`、`sprint-exps`、AI usage 复盘。
   建议验收要点：默认 summary 不展开矩阵；支持按字段读取；复盘 Token 章节仍可获得 status/mode/warnings/recommended_action。
   来源 Change/Sprint/命令：sprint-001 / `/sprint-exps sprint-001`。

3. 建议命令：`/opsx-propose`
   类型倾向：Change
   标题：增加 Sprint close 陈旧事实自动修复建议
   背景：Sprint-001 close 前 stale scan 发现多处历史状态文案，需要人工逐行修补。
   影响范围：`check-sprint-close-stale-scan.py`、Workflow Sync reconcile、Issue 子文档。
   建议验收要点：报告输出可执行修复建议；保留 workflow-sync marker 块边界；修复后 readiness 和 stale scan 均 PASS。
   来源 Change/Sprint/命令：sprint-001 / `/sprint-exps sprint-001`。

## 后续复用要求

- `/sprint-propose` 下一轮必须读取本复盘的 open 行动项，并在 Sprint 四件套中记录承接、延期或拒绝原因。
- `/req-complete` 处理后台 UI、上传、认证、用户状态时，应优先读取相关 best-practices。
- `/opsx-apply` 处理带 prototype 的 UI Change 时，必须先完成 UI Skeleton 和 1440px 验收计划，不得到 archive 阶段再补。

---
title: Sprint-004 经验复盘
purpose: 复盘工作台视觉、文档编辑权限、Chat 执行与治理交付经验
content: 流程、模型 Token、需求设计、开发质量、可复用抽象和行动项
source: sprint-004 Fact Sheet 与归档验收证据
owner: MoonBox 产品团队
status: active
sprint_id: sprint-004
created_at: 2026-09-14 00:12:29
updated_at: 2026-09-14 00:12:29
ai_usage_mode: estimated_fallback
---

# Sprint-004 经验复盘

本迭代完成工作台 Ops 视觉系统、Markdown 人工编辑权限矩阵与 Chat 工作台，并完成相关治理变更。交付已闭环，复盘重点是减少逐项 UI 返修、历史状态误判和重复读取成本。任务完成率不等于生产质量、工时或模型成本的完整测量。

## Sprint 概况与证据范围

| 维度 | 事实 | 解释 |
|---|---|---|
| 状态 | completed / archive | 关闭于2026-09-14，本地时区 Asia/Shanghai |
| 范围 | 3个 REQ、0个纳入范围的 BUG、11个 Change | 0个 BUG 不代表没有返修或缺陷；不把其他 Sprint 的 BUG 计入本迭代 |
| 任务 | 142/142，11个 Change 全部归档 | 来自 Fact Sheet；本次复盘不重新执行实现或归档 |
| 组成 | 3个产品 Change、8个治理 Change | 按当前 scope 与内容分类，不据此分摊实际工时 |
| 规划容量 | 30人天容量、32人天估算，106.67% | 超出2人天、无剩余缓冲；无实际工时，不能判断实际超支或速度 |
| 计划窗口 | 2026-08-31至2026-09-14 | sprint.yaml 的日期是规划字段，不推断实际逐项开工时间 |
| 归档检查 | readiness、陈旧扫描、目录、语言、环境忽略及 Workflow Sync 通过 | 本次归档2个、其余9个此前已归档 |
| 复盘读取风险 | 四件套共619行，其中2份超过200行；106条 evidence hints | 使用结构化摘要和定向片段，避免全文拼接 |
| 剩余信号 | 91条 archived-path-residual；AI 快照 stale | 与关闭扫描0阻断并不矛盾：扫描范围和判断目标不同 |

主要事实源：[Sprint 索引](../../../iterations/archive/sprint-004/sprint.yaml)、[关闭验收](../../../iterations/archive/sprint-004/acceptance-report.md)、[交付说明](../../../iterations/archive/sprint-004/release-note.md)。Fact Sheet 通过 `python scripts/generate-sprint-fact-sheet.py --sprint sprint-004 --json` 生成；本报告只保存脱敏聚合结果，不复制完整输出。

## 流程复盘

**有效做法。** Change、Issue、Sprint 的串行归档与校验使状态变化可追溯。权限矩阵与 Chat 的 artifact 和任务均完成后才合并规格，Issue 子文档同步后再迁移，最后关闭 Sprint。遇到问题先读命中文档与脚本片段，再修复，不用强制关闭掩盖问题。

**归档成本来自状态表达。** 首次 readiness 有7项阻断：5处旧路径和2处“待开发列”误报；后者由 `待.*(?:开发|实现)` 匹配 UI 列名产生。两个新归档 REQ 又触发27处正文状态/历史记录命中，结构化 reconcile 无待改字段，说明正文状态块、历史执行记录和机器状态并非同一覆盖面。收尾已更新当前态、澄清历史语义并保留当时验证事实；通用扫描行为尚未修复。

**日期与恢复。** 归档包装脚本按本地日期预期9月14日目录，CLI 实际产出9月13日目录。规格合并与目录迁移已经发生，后续按实际路径补验并同步，而非重放归档。下一个 Change 显式对齐 CLI 日期后成功。可确认的是日期预期不一致；CLI 内部采用何种时区仍需专门验证，不把 UTC 假设当作已证明根因。

**历史引用仍需分类。** Fact Sheet 的91条残留分布为视觉 Change 89条、动作矩阵与 CSS 治理各1条。抽样确认视觉 acceptance 的证据入口仍保留旧目录；不能把91条全部判为失效链接，也不能把它们全部忽略。迁移后的当前入口应可解析，历史命令与原路径应明确其历史语义。

证据：[归档验收中的文档复核与关闭摘要](../../../iterations/archive/sprint-004/acceptance-report.md)、[陈旧扫描实现](../../../scripts/sprint_close_stale_scan.py)、[视觉 Change 验收](../../../openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/acceptance.md)。

## 模型 Token 使用分析

### Token Usage Fact Sheet

| 指标 | 本次结论 | 依据与限制 |
|---|---|---|
| ai_usage_mode | estimated_fallback | 不将旧 snapshot 数值作为本 Sprint 真实统计 |
| snapshot_status | stale | generated_at 为2026-09-02T11:17:41.571336Z，早于最终范围与验收更新 |
| 覆盖 | 缺2个范围内 REQ、9个范围内 Change | 旧快照还含范围外对象，无法可靠分摊 |
| 自动发现复核 | warning / unavailable；command_run_count=0 | 本次 sprint.exps hook dry-run 未得到可归因记录；0是提取结果，不代表模型未调用 |
| Token 与调用指标 | 无可信 Sprint 总量 | input、cached input、output、reasoning output、total、模型/工具调用、失败重跑及工具输出字符数均不据旧值报数 |
| warnings | Fact Sheet 路径告警91条；快照告警3条；本次 hook 告警1条 | 属于不同检查口径，不相加为唯一问题数 |

reason：快照过期、覆盖不足，自动发现未得到可归因 command run。impact：不能计算本迭代真实成本、缓存命中率、单位任务 Token 或节省比例；下面仅分析上下文消耗风险，不编造数值。recommended_action：刷新 snapshot；若用于历史审计，提供显式 session，必要时补 manual-map，再检查范围覆盖、归因和时间。只保存脱敏派生事实，原会话不进入仓库。

矩阵中的 `-` 表示未观测到该对象在该阶段的 command run；它与已观测且数值为0不同。快照与提取语义见 [AI Usage 数据](../../../data/ai-usage/sprints/sprint-004.json) 和 [提取工具](../../../scripts/extract-ai-usage.py)。

### 高消耗来源与优化方案

| 来源 | 风险与证据 | 优化方案 |
|---|---|---|
| 规则与技能重复全文读取 | 本会话归档阶段出现多份规则/技能拼接和截断；当前复盘已复用摘要 | 保留已读路径、版本线索及门禁摘要，变更或阶段升级时只补必要片段 |
| Sprint/Issue/Change 全量读取 | 11个 Change、142任务、四件套619行；Fact Sheet 标记 needs_detail | 先筛选状态、计数、告警分组；按3个批次/每批最多5个 Change 展开，不复制整个 trace |
| 宽泛搜索与历史归档 | 91条路径告警，89条集中于一个 Change | 限定 scope ID；排除 node_modules、dist、coverage、generated、Harness/assets；仅对命中目标开放 archive 搜索 |
| Fact Sheet 与 Workflow Sync 输出 | 归档时 `--summary` 仍返回较大内容；21个子文档同步细节也可重复出现 | 显式字段筛选、按目标/类型聚合，成功只报计数；失败展示必要上下文，截断不作为完整检查证据 |
| OpenAPI/Orval 与 diff | 范围涉及契约与客户端生成；无证据量化其本 Sprint Token 占比 | 先看 diff --stat/name-only，再读相关 schema 或手写变更，生成物全文不入上下文 |
| 测试、Docker/build 日志 | Chat trace 有多轮构建和测试证据；无完整调用计量 | 成功保留命令、退出码、用例数；失败只取错误类型、首个相关堆栈和环境差异，完整日志留本地 |
| Harness/模板资产注入 | 属于预算规则要求防范的风险，本轮没有量化证据证明其占比 | 不因技能存在而加载模板资产；按具体任务路径定位，避免全目录注入 |

当前复盘遵守“Fact Sheet → 告警聚类 → 必要片段”的读取顺序；归档阶段的大输出拼接需要改进。动作见 S4-A001、S4-A002、S4-A003、S4-A005，不估计节省百分比。

## 需求与设计复盘

**UI 需求应以组件族收口。** REQ-0023 的卡片基础高度、空列、footer、按钮、弹窗等多轮修改说明：单一元素看似正确，仍可能破坏列表压缩、滚动和状态组合。REQ-0025 延用共享侧边栏与动作族、selector、1440/390深浅主题及 computed style，减少只凭“更接近参考”的验收歧义。后续应在实现前列出按钮→modal→状态→selector→证据矩阵，并标注原型与当前基线差异。

**能力矩阵优于前端阶段分支。** REQ-0024 将 readable、human_editable、ai_mutable、task_toggle_only 与 reason 作为统一能力返回；人工只读不等于系统治理不可写。demo/fallback 曾未遵循矩阵，提示生产与演示分支需要共享规则及契约断言，而不是单独维护权限推断。

**Chat 的运营决策是实施输入。** 实际接入经历受控验证、隔离执行、认证、备份和策略确认，最终采用单机 Compose、SQLite、独立本地备份、本机认证与 unlimited 策略。不能将最初的“统一额度/容量上限”规划直接写成最终上线事实。变更决策应同步 PRD、验收、trace 和交付说明，历史阶段记录明确时间与适用范围。

**返修不能用 BUG 数量替代衡量。** Sprint 范围无 BUG，但多个 Change 内含连续返修；不据此计算零缺陷率。当前材料不足以证明“缺原型导致 fix-* 增多”的因果关系，视觉参考存在但合同颗粒度、分批状态组合与证据更新仍有改进空间。

证据：[视觉 trace](../../../openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/trace.md)、[编辑权限 trace](../../../openspec/archive/2026-09-13-update-markdown-editor-human-edit-permission-matrix/trace.md)、[Chat trace](../../../openspec/archive/2026-09-13-add-chat-workbench-codex/trace.md)。

## 开发质量复盘

测试与真实观察的分层值得保留。Chat 的合成 API 视觉验证用于布局、状态、交互与样式；真实账号/隔离执行用于发送、恢复、停止、计量与删除。模拟 App Server 入库测试、默认跳过的真实探针和真实运行记录分别说明，避免把合成回归当成真实执行通过。

权限矩阵 trace 记录后端16项及前端59项通过；Chat 后续批次记录不同聚焦测试、SQLite/MySQL矩阵和真实部署证据。这些计数跨批次可能重复，不累加为唯一测试总量。本次复盘复核证据入口，不重新测试业务，不扩大到未验收的部署组合。

未知用量不按零结算、未知运行不伪造终态，说明状态与观测质量应优先于“看似完成”。文档操作的单次同步差异校验不接入长任务 Trace，其 N/A 原因保留；API/DB/请求日志/真实执行的适用层级与脱敏验证见各 Change 声明。

容量超配与持续返修同时存在，但没有实际工时证明二者因果关系。下一迭代应在加入晚到范围时重算容量、缓冲和依赖，不在关闭时倒改规划数值。

## 可复用抽象

| 已有模式 | 复用价值 | 边界 |
|---|---|---|
| 共享侧边栏与账号/空间操作 | 跨需求中心和 Chat 保持导航、主题与权限反馈一致 | 业务页面仍保留各自数据和权限来源 |
| Markdown capability 对象 | 统一全文编辑、只读、仅任务勾选及拒绝理由 | 最终授权在后端；demo/fallback也需验证 |
| 动作弹窗组件族与视觉矩阵 | 覆盖加载、取消、失败、禁用和窄屏 | 不以共享外观替代业务动作权限 |
| 运行互斥、可信 receipt 与幂等结算 | 支持重启、迟到用量和故障恢复 | 目前是 Chat 的已验收模式，不宣称通用执行平台已抽离 |
| 分层验收证据 | 区分合成、契约、真实运行与部署观察 | 不把缺失记录或跳过用例当通过 |

复用 [原型驱动 UI Gate](../best-practices/prototype-driven-ui-gate.md)、[列表页面一致性](../best-practices/admin-list-page-consistency.md)、[弹窗宽度与 CSS 层叠](../best-practices/admin-modal-width-css-cascade.md)。本次不新建内容重复的 best-practice，不修改既有规范。

## 上轮行动项承接

Sprint 机器源明确仅在 Chat 中承接 S3-A004 的动作族/视觉验收方法、S3-A005 的执行环境写入边界验证，未承诺通用模板完成。S3-A001 虽有相关会话归因治理 Change，本次提取仍不可用，不能据 Change 已归档宣称真实用量覆盖修复。S3-A002、S3-A003、S3-A006 在本轮未新增治理范围。

下表是上轮相关问题的本轮证据更新及新增事项，不自动创建重复需求；后续承接时合并原行动项。上轮复盘状态不在本命令中擅自关闭。

## 行动项

| ID | 优先级 | 类型倾向/承接 | 建议与验收目标 | 建议下一命令 | 状态 |
|---|---|---|---|---|---|
| S4-A001 | P1 | BUG候选，承接 S3-A001 | 排查 session 归因与快照覆盖；可归因样本能生成 command run，不匹配时返回具体原因；覆盖校验拒绝范围外污染，区分未观测与0 | `/bug-capture 排查 sprint-004 AI Usage 自动归因不可用与快照覆盖不足` | open |
| S4-A002 | P2 | 治理，承接 S3-A002 | 默认仅输出 scope、状态、分组告警与用量门禁；完整矩阵/证据按 fields 读取；大量告警有稳定摘要与明细入口 | `/spec-opt 优化 Sprint Fact Sheet 与 Workflow Sync 的默认摘要和字段筛选` | open |
| S4-A003 | P1 | 治理，承接 S3-A003 | 区分当前字段、历史记录与 UI 术语；真实未完成事项仍阻断，“待开发列”不误报；归档后正文状态块/索引/结论同步且可幂等复验 | `/spec-opt 区分 Sprint 关闭扫描的当前态与历史记录并完善正文同步` | open |
| S4-A004 | P2 | 治理，新发现 | 验证 CLI 日期语义；包装脚本根据实际归档结果校验，跨日及已移动后恢复不重复合并、不覆盖目录 | `/spec-opt 对齐 OpenSpec 归档日期与跨日恢复校验` | open |
| S4-A005 | P2 | 治理，承接 S3-A006 | 对91条告警按历史命令/当前证据引用分类；当前链接可解析，修复先 dry-run，不盲目替换历史文本 | `/spec-opt 分类处理 sprint-004 归档路径残留并聚合告警` | open |
| S4-A006 | P2 | REQ候选，承接 S3-A004/005 | 将动作族、权限矩阵、demo/fallback与环境写入边界纳入可复用验收材料；明确当前基线与历史截图，不强制重复已有 Gate 正文 | `/req-capture 沉淀复杂工作台动作族与权限环境验收材料` | open |
| S4-A007 | P2 | 规划改进 | 下次纳入范围前复核 open 项、依赖和容量；30人天容量下明确32人天范围的取舍，不把零缓冲当正常 | `/sprint-explore 评估下一迭代对 sprint-004 复盘行动项的承接与容量` | open |

这些是待承接建议，不是已评审 Issue、已纳入 Sprint 的承诺或本轮开发任务；未自动创建 Issue/Change。既有 Sprint-005 是否接纳由其范围与容量门禁决定，本复盘不调整任何 Sprint scope。

## 执行链路复盘

链路状态：warning。复盘基于已关闭的 Sprint，交付不因知识库分析而重新打开。问题证据：路径告警91条、快照过期且范围缺失、本次自动发现 unavailable；归档期间状态误报与日期差异见关闭验收摘要。规范优化建议：优先 S4-A003，再处理日期恢复、归因与摘要输出；仅建议，未自动创建 Issue/Change。

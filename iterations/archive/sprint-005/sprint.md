---
note: workflow-sync — workflow-sync 自动同步 — 8/8 Change archived；0 applied；Sprint `completed`
sprint_id: sprint-005
status: completed
lifecycle_stage: archive
created_at: 2026-09-11 08:59:42
updated_at: 2026-09-14 09:25:00
---

# sprint-005 本地项目迭代闭环

## 1. Sprint 目标

用一个 MoonBox 本地验证项目贯通需求中心、Chat 和治理成果受控应用；保留正式仓库与会话副本边界。

### Sprint 目标编号列表

- REQ-0022-local-project-import-product-iteration
- REQ-0026-requirement-center-standalone-change-cards
- BUG-0014-requirement-center-capture-not-persisted
- BUG-0015-requirement-center-apply-start-stage-not-synced
- BUG-0016-capture
- unify-issue-classification-metadata
- standardize-sprint-default-capacity
- refresh-issue-index-after-archive-promotion

### REQ-0022-local-project-import-product-iteration 要点

REQ `REQ-0022-local-project-import-product-iteration`：本地项目绑定与 Chat、需求中心迭代闭环。当前状态 done，估算 8 人天；archived `add-local-project-governance-loop`（2026-09-14 08:59:54）。

### REQ-0026-requirement-center-standalone-change-cards 要点

REQ `REQ-0026-requirement-center-standalone-change-cards`：需求中心 Change 可见性与关联追溯。当前状态 done，估算 8 人天；archived `add-requirement-center-change-visibility`（2026-09-12 22:42:37）。

### BUG-0014-requirement-center-capture-not-persisted 要点

BUG `BUG-0014-requirement-center-capture-not-persisted`：需求中心新建 Capture 仅创建前端临时卡片，未持久化 REQ/BUG 目录、文档、注册表与索引。当前状态 done，估算 5 人天；archived `fix-requirement-center-capture-persistence`（2026-09-12 16:40:10）。

### BUG-0015-requirement-center-apply-start-stage-not-synced 要点

BUG `BUG-0015-requirement-center-apply-start-stage-not-synced`：研发启动后需求中心卡片仍停留准备开发态，缺少 apply 启动状态同步。当前状态 done，估算 3 人天；archived `fix-requirement-center-apply-lifecycle-sync`（2026-09-14 08:59:42）。

### BUG-0016-capture 要点

BUG `BUG-0016-capture`：需求中心刷新缓慢，MD 文档右侧抽屉加载缓慢或无法加载。当前状态 done，估算 5 人天；archived `fix-requirement-center-loading-and-errors`（2026-09-14 08:58:53）。

### unify-issue-classification-metadata 要点

Change `unify-issue-classification-metadata`：unify issue classification metadata。当前状态 archived，估算 1 人天；archived `unify-issue-classification-metadata`（2026-09-12 17:48:54）。

### standardize-sprint-default-capacity 要点

Change `standardize-sprint-default-capacity`：standardize sprint default capacity。当前状态 archived，估算 1 人天；archived `standardize-sprint-default-capacity`（2026-09-14 23:59:59）。

### refresh-issue-index-after-archive-promotion 要点

Change `refresh-issue-index-after-archive-promotion`：refresh issue index after archive promotion。当前状态 archived，估算 1 人天；archived `refresh-issue-index-after-archive-promotion`（2026-09-14 09:11:30）。

## 2. Scope

| 类型 | 编号 | 标题 | 状态 | 估算 | 说明 |
|---|---|---|---|---:|---|
| REQ | REQ-0022-local-project-import-product-iteration | 本地项目绑定与 Chat、需求中心迭代闭环 | done | 8 人天 | archived `add-local-project-governance-loop`（2026-09-14 08:59:54） |
| REQ | REQ-0026-requirement-center-standalone-change-cards | 需求中心 Change 可见性与关联追溯 | done | 8 人天 | archived `add-requirement-center-change-visibility`（2026-09-12 22:42:37） |
| BUG | BUG-0014-requirement-center-capture-not-persisted | 需求中心新建 Capture 仅创建前端临时卡片，未持久化 REQ/BUG 目录、文档、注册表与索引 | done | 5 人天 | archived `fix-requirement-center-capture-persistence`（2026-09-12 16:40:10） |
| BUG | BUG-0015-requirement-center-apply-start-stage-not-synced | 研发启动后需求中心卡片仍停留准备开发态，缺少 apply 启动状态同步 | done | 3 人天 | archived `fix-requirement-center-apply-lifecycle-sync`（2026-09-14 08:59:42） |
| BUG | BUG-0016-capture | 需求中心刷新缓慢，MD 文档右侧抽屉加载缓慢或无法加载 | done | 5 人天 | archived `fix-requirement-center-loading-and-errors`（2026-09-14 08:58:53） |
| Change | unify-issue-classification-metadata | unify issue classification metadata | archived | 1 人天 | archived `unify-issue-classification-metadata`（2026-09-12 17:48:54） |
| Change | standardize-sprint-default-capacity | standardize sprint default capacity | archived | 1 人天 | archived `standardize-sprint-default-capacity`（2026-09-14 23:59:59） |
| Change | refresh-issue-index-after-archive-promotion | refresh issue index after archive promotion | archived | 1 人天 | archived `refresh-issue-index-after-archive-promotion`（2026-09-14 09:11:30） |

<!-- workflow-sync:scope-requirements:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
| REQ-0022 | 本地项目绑定与 Chat、需求中心迭代闭环 | P1 | done | archived `add-local-project-governance-loop`（2026-09-14 08:59:54） |
| REQ-0026 | 需求中心 Change 可见性与关联追溯 | P1 | done | archived `add-requirement-center-change-visibility`（2026-09-12 22:42:37） |
<!-- workflow-sync:scope-requirements:end -->

<!-- workflow-sync:scope-bugs:start -->
| 编号 | 名称 | 严重度 | 状态 | 说明 |
|---|---|---|---|---|
| BUG-0014 | 需求中心新建 Capture 仅创建前端临时卡片，未持久化 REQ/BUG 目录、文档、注册表与索引 | high | done | archived `fix-requirement-center-capture-persistence`（2026-09-12 16:40:10） |
| BUG-0015 | 研发启动后需求中心卡片仍停留准备开发态，缺少 apply 启动状态同步 | medium | done | archived `fix-requirement-center-apply-lifecycle-sync`（2026-09-14 08:59:42） |
| BUG-0016 | 需求中心刷新缓慢，MD 文档右侧抽屉加载缓慢或无法加载 | medium | done | archived `fix-requirement-center-loading-and-errors`（2026-09-14 08:58:53） |
<!-- workflow-sync:scope-bugs:end -->

<!-- workflow-sync:scope-changes:start -->
| Change ID | 关联需求 | 状态 | Sprint 目标 |
|---|---|---|---|
| `add-local-project-governance-loop` | REQ-0022-local-project-import-product-iteration | archived | archived `add-local-project-governance-loop`（2026-09-14 08:59:54） |
| `fix-requirement-center-capture-persistence` | BUG-0014-requirement-center-capture-not-persisted | archived | archived `fix-requirement-center-capture-persistence`（2026-09-12 16:40:10） |
| `unify-issue-classification-metadata` | — | archived | archived `unify-issue-classification-metadata`（2026-09-12 17:48:54） |
| `fix-requirement-center-apply-lifecycle-sync` | BUG-0015-requirement-center-apply-start-stage-not-synced | archived | archived `fix-requirement-center-apply-lifecycle-sync`（2026-09-14 08:59:42） |
| `add-requirement-center-change-visibility` | REQ-0026-requirement-center-standalone-change-cards | archived | archived `add-requirement-center-change-visibility`（2026-09-12 22:42:37） |
| `standardize-sprint-default-capacity` | — | archived | archived `standardize-sprint-default-capacity`（2026-09-14 23:59:59） |
| `fix-requirement-center-loading-and-errors` | BUG-0016-capture | archived | archived `fix-requirement-center-loading-and-errors`（2026-09-14 08:58:53） |
| `refresh-issue-index-after-archive-promotion` | — | archived | archived `refresh-issue-index-after-archive-promotion`（2026-09-14 09:11:30） |
<!-- workflow-sync:scope-changes:end -->

REQ：`REQ-0022`、`REQ-0026` 已纳入正式范围；BUG：`BUG-0014`、`BUG-0015`、`BUG-0016` 已纳入正式范围，优先级高于新增体验能力；当前完成度与验收风险以 Scope 表状态、关联 Change 和 acceptance-report 为准。

Change：已回填 5 个范围项关联 Change，另有 3 个纯 Change；8 archived，0 applied，0 in_progress，0 proposed。所有已纳入范围项均已关联 Change；执行开发与归档时以 Scope 表逐项状态为准。

## 3. 工作量与容量

<!-- workflow-sync:sprint-capacity-section:start -->
| 指标 | 数值 | 说明 |
|---|---:|---|
| Sprint 容量 | 30 人天 | 来自 `sprint.yaml:capacity_person_days` |
| 估算人天 | 32 人天 | 汇总 `scope_estimates[].estimated_person_days` |
| Story Points | 32 SP | 汇总 `scope_estimates[].story_points` |
| 容量占用率 | 106.67% | `estimated_person_days / capacity_person_days` |
| Fix 缓冲 | 0 人天 | 剩余可用容量，低于 0 时按 0 展示 |
| Fix 缓冲率 | 0.00% | `fix_buffer_person_days / capacity_person_days` |
| 容量门禁 | soft-pass：超过 100%，但未超过 120%，需记录容量风险 | Workflow Sync 派生判断 |
<!-- workflow-sync:sprint-capacity-section:end -->
## 4. 里程碑

<!-- workflow-sync:sprint-milestones-section:start -->
| 节点 | 目标日期 | 完成口径 | 当前状态 |
|---|---|---|---|
| Sprint 启动 | 2026-09-14 09:00:00 | 四件套创建并纳入正式范围 | completed |
| 范围实现完成 | 2026-09-28 09:00:00 | `changes[]` 全部 apply 完成 | 8/8 已 apply 或 archive |
| 归档收口 | 2026-09-28 09:00:00 | `changes[]` 全部 archive，验收报告完成 sign-off | 8/8 已 archive，0 待归档 |
<!-- workflow-sync:sprint-milestones-section:end -->
## 5. 风险与缓冲

<!-- workflow-sync:sprint-risks-section:start -->
| 风险 | 等级 | 证据 | 处理建议 |
|---|---|---|---|
| 容量超出计划值 | medium | 容量占用 106.67% | 后续不宜继续追加范围，除非替换或拆分 |
| Fix 缓冲不足 | medium | fix_buffer_person_days=0 人天 | 保留返修优先级，避免新增非必要治理范围 |
<!-- workflow-sync:sprint-risks-section:end -->
## 6. 知识库承接

<!-- workflow-sync:sprint-knowledge-section:start -->
| 承接项 | 触发条件 | 建议事实源 | 当前状态 |
|---|---|---|---|
| Sprint 复盘 | Sprint close 或集中归档前 | `docs/knowledge-base/retrospectives/sprint-005-retrospective.md` | 8/8 Change archived |
| 最佳实践 | 验收中出现可复用规则、脚本或 UI/API/DB 经验 | `docs/knowledge-base/best-practices/` | 由 `/sprint-exps` 基于证据生成或更新 |
| 事故与缺陷经验 | BUG 根因、返修或发布风险具备复用价值 | `docs/knowledge-base/incidents/` | 由 `/sprint-exps` 或后续治理命令按证据沉淀 |
<!-- workflow-sync:sprint-knowledge-section:end -->

## 7. 验收重点

REQ-0022 的 16 条功能、3 条横切、6 条原型 AC，及 review RC-001 至004为交付门禁。先确定可信基准和写入恢复设计，再完成 Skeleton 首轮确认，最后验证真实 req-generate → 审阅 → 应用 → 看板更新。模拟原型不作真实闭环证据。

知识库承接摘要：S3-A004 的动作族与视觉证据、S3-A005 的写入边界与失败反馈由 REQ-0022 验收承接；其他 open 行动项不新增范围。

BUG-0014 的 AC-001 至 AC-010 为新增修复验收门禁；REQ/BUG 两类真实落盘与刷新恢复均需证据，合成提交函数复现不等于修复通过。

## 8. 横切预防清单

- 复用 docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md：宽度类不冲突，computed width 与低视口正文滚动；对应 AC-XCUT-001、002。
- 承接 Sprint-003：写入失败保留成果与草稿，反馈不推动布局；对应 AC-XCUT-003。
- product_data_collection_observability 为 applicable；覆盖 Web、API、请求日志、行为事件、Task Trace、Agent Workflow 与部署。依据 docs/standards/product-data-collection-observability.md；AC-016 验证尚未开始。后台轮询不伪造行为，记录脱敏版本与真实结果。

- BUG-0014 承接 S3-A005：验证目标项目可写边界、部分失败恢复、输入保留及脱敏日志；AC-006至009。现有 Capture 弹窗重点验证错误反馈与操作可达性，不新增视觉改版范围。

- BUG-0015：复用最近复盘的需求中心卡片状态矩阵，核对启动0/N、门禁失败、幂等恢复、完成门禁、阶段与动作一致性；AC-001至011。admin-list/admin-form/admin-modal/media-upload模式不适用，本次不改版UI。

## 9. 依赖与执行顺序

```text
REQ-0025 会话与隔离执行 + REQ-0024 文档权限
  -> REQ-0022 OpenSpec设计（基准、受控写通道、恢复）
  -> UI Contract / Skeleton确认
  -> 项目绑定与读取刷新
  -> Chat关联与成果应用
  -> 冲突/幂等/重启回归 + 真实本地闭环
  -> 文档一致性及验收归档
```

复用依赖的实际能力在实施前核验，不把已有 验收态 等同于全部发布归档。sprint-004 保留原范围并收尾，sprint-005 计划从9月14日开始以减少人员重叠。日期为规划基线，不是发布承诺。

BUG-0014 执行依赖：

```text
现有项目授权与文件写通道能力核验
  -> BUG-0014 OpenSpec修复设计
  -> 服务端持久化与正式编号 + 前端成功/失败处理
  -> REQ/BUG真实落盘、并发恢复、权限与刷新验收
  -> 文档同步与归档
```

与 REQ-0022 共用需求中心及文件写通道，修改重叠处按顺序集成；不将其全部归档设为本 BUG 的前置门禁。

BUG-0015 执行依赖：

```text
BUG-0015 已评审并纳入 Sprint
└─ 创建修复 Change（bug-opsx）
   ├─ 核验现有 Workflow Sync 与分级元数据治理兼容性
   ├─ 统一启动、进度、完成事实源与入口契约
   └─ REQ/BUG 状态矩阵回归 → 真实 API/浏览器刷新验收
```

BUG-0014 仅为复现案例，不把其验收结果作为本条通过证据；本BUG严重度 medium。追加估算3人天后总量17/20人天，剩余机动3人天低于建议缓冲，新增范围重新核算。

## 10. 发布计划

先本地验证，不自动升级生产或提交推送。通过全部验收、收口条件项后再进入独立发布流程；本 Sprint 未绑定发布版本。

## 11. 关联文档

- issues/requirements/archive/REQ-0022-local-project-import-product-iteration/requirement.md
- issues/requirements/archive/REQ-0022-local-project-import-product-iteration/review.md
- issues/requirements/archive/REQ-0022-local-project-import-product-iteration/acceptance.md
- docs/knowledge-base/retrospectives/sprint-003-retrospective.md
- docs/knowledge-base/retrospectives/sprint-005-retrospective.md

## 12. 规划说明

容量20人天，REQ-0022估算8人天、BUG-0014估算5人天，合计13人天、占用65%；剩余7人天（35%）作为修复与不确定性缓冲。不得未经容量重算把剩余空间自动填入其他需求。

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-09-11 08:59:42 | sprint.propose | 用户指定新建连续 sprint-005，拆入 REQ-0022；不改变 sprint-004。 |
| 2026-09-12 12:24:58 | sprint.propose | 用户指定追加 BUG-0014，估算5人天，容量13/20人天；承接S3-A005与10项回归门禁。 |
| 2026-09-14 09:24:31 | sprint.archive | 8/8 Change 已归档；readiness、env ignore、stale scan 通过；AI Usage 自动发现不可用，保留 estimated_fallback 警告。 |

- 2026-09-12 20:54:39：追加 BUG-0015-requirement-center-apply-start-stage-not-synced，M=3人天；统一启动状态与看板投影，真实验收未执行。

## REQ-0026 补充执行约束

依赖：REQ-0022 项目快照与授权 → REQ-0026 聚合/去重 → 原卡片两项调整 → 真实权限、归档与视觉回归。横切预防承接 S3-A004 和 prototype-driven-ui-gate：既有组件族复用、同字号 computed style、1440px/390px及文档最终一致性；对应 AC-XCUT-001/002。Web/API 观测验证以 AC-009/010 为准，无新增数据库、部署、存储或异步任务链路。当前容量以工作量与容量章节为准；新增范围需重算缓冲，不能压缩验收。

## BUG-0016 规划承接

依赖：现有项目快照与授权 → 解析错误恢复及性能方案 → 页内/抽屉错误与详情弹窗 → AC-001至019回归和真实部署观察。先核对实际数据源，不将用户所有等待都归因于本地已确认错误。

横切预防：承接 S3-A004、S3-A005；参考 admin-modal-width-css-cascade 的宽度级联、低视口滚动与遮罩检查。附件只作现状证据；复用 prototype-driven-ui-gate 的视觉取证方法，不强行新增原型复刻。保留权限失效清理、草稿保护、上层弹窗Esc及焦点恢复，失败重试不反复打断用户。

发布与验收：修复Change待 /bug-opsx 创建；未执行19项验收，不形成发布承诺。product_data_collection_observability适用web/api/request_logs；无已确定DB、对象存储或部署配置变更，验证摘要见sprint.yaml及BUG验收文档。

## REQ-0026 阶段按钮增补规划

本轮已评审范围纳入：准备开发态“开始开发”、研发中“查看进度”、验收中按门禁“完成 / 归档”；已完成无阶段主按钮。复用现有REQ/BUG组件、权限和真实能力，不新增执行服务。新增3人天，REQ总计8人天；Sprint总计31/30人天，103.33%，剩余机动0，未触及120%硬门禁。建议后续低优先体验优化延后，不压缩权限与视觉验收。

交付状态：增补待req-opsx同步与实施，当前派生表的apply 21/21和待archive仅代表旧Change任务，不覆盖新增动作，不能据此归档。验收覆盖AC-ACTION-001至006、AC-XCUT-003及新范围原型门禁。承接Sprint-003的S3-A004动作矩阵经验，不宣称通用治理行动项完成。

product_data_collection_observability: applicable；affected_layers: web、api。验证行为关联、请求日志、拒绝路径和现有Task Trace；DB、部署、对象存储、保留周期无新增变化。真实执行能力缺失时禁用并说明，Demo不替代真实验收。

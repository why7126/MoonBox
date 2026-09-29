---
title: Capture 图文候选与可靠确认设计
created_at: '2026-09-15 00:14:40'
updated_at: '2026-09-16 19:58:00'
---
# Capture 图文候选与可靠确认设计

## 背景与目标

承接 REQ-0029 的 FR-001 至 FR-011、8 条故事和 36 条 AC。Readiness 为 Partially Ready：评审和 Sprint 门禁已满足，原型拆解已完成，真实 UI Skeleton、视觉及模型证据属于实施任务。实现目标是图文到正式采集记录的完整闭环；不生成正式 PRD、缺陷报告、Sprint 或 Change，不修改 Codex 直接 `/capture` 的用户流程。

现状依据：`src/backend/app/governance/capture.py:plan` 在注册表和目录中找最大号，`writer.py:process` 在项目锁内规划、保存前后镜像并恢复；其契约是单条 object_id，不能把循环提交单条当作批次原子性。`candidates.py` 处理已有 REQ 的生成结果，不用于未编号草稿。实施扩展独立 Capture 批次服务并复用授权、项目锁、持久化操作与读取屏障。

## 技术决策

### D1 — UI 策略采用现有设计系统

沿用用户此前按推荐建议收敛的方向，选 DS：复用 `Button.tsx`、现有浮层模式和 `tokens.generated.css`，按原型移植结构、密度与语义。CSS Port 容易复制演示脚本和全局样式；Asset 方案不能满足候选交互，均不采用。新样式限定 Capture 工作区，既有导航与需求中心其他阶段不变。

### D2 — 受限整理执行

从 `.agents/skills/capture/SKILL.md` 提取分类、独立交付单元拆分和内容保真规则，记录规则版本摘要；不直接运行该技能的落盘链路。模型只获得授权项目的只读必要规格与材料副本，工具白名单禁止命令执行、写入 API、正式仓库写挂载与通用网络取数。执行副本为临时目录，图片从授权 media_id 解析并以模型原生图片输入传递；不能把路径文本或上传成功当作图片已理解。复用 REQ-0028 适配前验证当前多模态能力和容器可读性。

模型输出结构为候选数组：type、title、priority 或 severity、description、source_refs、classification_reason、clarifications。服务端分配 candidate_id，校验类型、上限、来源归属、无正式身份字段与事实边界；文本/图片中的指令视为材料。失败保留材料，不预占编号。AI 运行绑定 base_revision，迟到结果只能成为独立建议，不能覆盖人工版本。重新整理须显式确认替换并保留旧版本与来源。

### D3 — 服务端业务数据与版本

建议新增 `capture_drafts`、`capture_revisions`、`capture_materials`、`capture_confirmations`、`capture_issue_links` 表；候选正文及来源边保存在不可变 revision payload，避免复用 PRD candidates 表的生命周期。字段和索引如下，实施用现有 SQLAlchemy/迁移体系：

| 数据 | 关键字段与约束 |
|---|---|
| 草稿 | UUID id、space_id、repository_id、binding_revision、actor_id、revision、state、confirmed_task_id、created_at/updated_at/deleted_at；按用户/项目/状态查询 |
| 版本 | draft_id + revision 唯一；完整原文引用、材料引用、候选集合、父子/合并来源边、AI 初判与人工变更；正文为业务数据，不进观测 |
| 材料 | UUID media_id、项目/用户、MIME、size、width/height、校验状态、私有对象映射、引用和 deletion tombstone；对象 key 不作为公开身份 |
| 确认 | UUID task_id，project + draft_id + revision 唯一，另对 draft_id 唯一锁定确认任务；immutable snapshot_hash、binding_revision、actor_id、state、operation_id、请求键摘要 |
| 正式映射 | task_id + candidate_id 唯一，项目 + issue_full_id 唯一；最终类型、来源引用与确认版本 |

保存以 expected_revision 做条件更新，成功递增版本；旧版本返回 409，不用最后写入覆盖。改类型沿用候选 ID，移除异类分级，展示目标类型建议并要求审阅；合并/拆分产生新 ID 并标记原条目 superseded，保留全部来源边和可编辑的图片分配。删除只改变确认集合，不删除共享来源。

用户输入停止 1 秒或持续 5 秒触发保存；确认先等待最新保存。服务端草稿同用户同项目恢复。未确认草稿保留至主动删除；最多 50 个/用户/项目、材料 1 GiB，配额用事务计数防并发突破。删除与确认在同一草稿锁/条件状态门禁下竞争，已删除批次返回 410，任务占用返回 409。未关联上传 24 小时清理，正式引用及非终态恢复材料不清理。删除标记重放到备份恢复和执行副本清理，不能宣称即时删除所有副本。

### D4 — API 契约

复用 `/api/v1/requirement-center`、ApiResponse 与现有身份/项目绑定依赖。以下为新增相对路径，路径 ID 均视为不可信并重新授权：

| 方法/路径 | 输入与结果 |
|---|---|
| GET /capture-capabilities | 返回文字/图片/候选/配额限制、模型图片可用性和写入就绪摘要 |
| POST /capture-drafts | 创建原始草稿，返回 draft_id、revision、state |
| GET /capture-drafts | 仅本人当前项目未删除草稿分页 |
| GET/PATCH/DELETE /capture-drafts/{draft_id} | 获取/以 expected_revision 保存完整编辑/主动删除；返回服务端版本和保存时间 |
| POST /capture-drafts/{draft_id}/materials | multipart 图片上传，返回 media_id、受控 preview_url、类型/尺寸/状态；不返回私有 key |
| GET /capture-materials/{media_id}/content | 每次鉴权的私有内容代理，撤权后不能读取；不缓存为公开资源 |
| POST /capture-drafts/{draft_id}/organize | base_revision、整理请求身份；202 返回 task_id，轮询返回结构化建议 |
| GET /capture-drafts/{draft_id}/organize-tasks/{task_id} | 状态、脱敏错误和经校验候选；不暴露任意模型全文 |
| POST /capture-drafts/{draft_id}/confirmations | expected_revision、idempotency_key；202 返回原或新确认任务，无客户端编号参数 |
| GET /capture-confirmations/{task_id} | 状态/阶段/可重试性，完成才返回完整 issue_links |
| POST /capture-confirmations/{task_id}/retries | 只续作原不可变任务，不接受候选内容 |
| GET /capture-sources/{issue_id} | 授权读取正式关联的原文、图片、初判、变更与确认版本 |

图片限制：10 张静态 PNG/JPEG/WebP、单张 10 MiB、总量 50 MiB、2000 万像素；文本 20000 码点，候选最多 50，标题 60、描述 10000。服务端验证 MIME/签名/解码/像素/动画，超限不截断。前端按 Unicode 码点计数，与服务端一致。

错误按现有业务错误码注册表分配不冲突的代码；稳定原因包含 revision_conflict、binding_changed、material_unreadable、quota_exceeded、invalid_candidates、recovery_blocked。HTTP 403 授权、404 不可枚举对象、409 冲突、410 已删草稿、413 体积、422 结构、503 依赖不可用；界面保留可安全展示输入。OpenAPI 必须使用具体 DTO，Orval 生成请求/响应类型并接入观测 header helper，不能只用 dict 绕开契约。

### D5 — 确认、编号与恢复

确认事务先授权和校验 binding_revision、草稿当前状态与期望版本、全部候选/材料有效性；若已有同一快照确认，无论请求键是否变化都返回原任务。同键异内容返回 409；不同版本不能绕过已确认草稿冻结。对过期未确认请求拒绝，不静默改用最新版。DB 唯一约束及 CAS 实现 SQLite/MySQL 一致竞争结果。

确认事务固定快照和 task_id，提交后才交给 writer。worker 重新授权并获得现有项目 OS 锁和 fencing token；在锁内读取注册表与所有 plan/review/archive 目录占用，按候选最终类型分别计算序列。一次构造整个批次 before/after，包括两种 registry 和 CHANGELOG 聚合结果，禁止每条从同一个旧 next_id 单独规划。

先把编号映射、所有目标路径/内容/摘要和 binding_revision 持久化为原任务 write plan，再执行第一份正式文件。计划持久化失败不得写正式文件；重启若发现已持久化计划必须复用，不能重新编号。操作记录与 DB 状态跨存储不承诺事务：恢复按 task_id 发现既有计划并校验哈希，DB 进度落后时从计划修复；计划损坏或丢失且有写入可能时转 recovery_blocked，不能重建新号。

状态：accepted → preparing → applying → verifying → completed；失败分 retryable_failed / recovering / recovery_blocked。每份文件只接受 before 或预期 after 哈希，遇第三种内容停止并保留证据；逐次检查权限与绑定。注册表/索引和所有 capture/trace 校验成功、正式映射持久化完成后才完成任务并释放读取屏障。ProjectReader 在非终态返回上一个完整快照或明确恢复提示；文档 API 也不得绕过屏障读半成品。外部直接文件读取不保证原子可见性。

不通过删锁、覆盖外部修改、重新分配编号或提交新任务“修复”失败。保留既有 continuous controller 就绪约束，新批次不得穿过其他未恢复操作。两个批次和兼容单条创建共享同一编号协调入口。

### D6 — 采集产物与来源

最终每条仅写 plan/ID 下 capture.md 和 trace.md，status captured、iteration null、openspec_changes 空；trace/capture 使用同类型分级并同步 registry。写 captured_via: capture、classification_rationale、来源标识、AI 初判、人工调整摘要和确认快照引用。来源以不含主机地址的业务 ID 引用保存在两份采集文档，由授权来源 API 解析；图片原件存既有项目 Bucket 的 images/original，草稿上传即使用随机对象key，由DB状态区分未关联材料和正式引用，避免确认时搬移对象破坏稳定关联。正式来源引用转长期保护，删除原草稿不级联释放。不得把签名 URL、本机路径或对象 key 当永久来源。

## Conflict Resolution — 冲突处理

视觉事实源排序：HTML > PNG > context.md > acceptance.md > ui-design.md > 已生效 spec；用户确定的产品边界不因演示细节而降级。以下显式裁决写入最终设计并由 delta spec 消化：

| 冲突 | 裁决 |
|---|---|
| 既有 spec 的预填标题/类型与 840px 短表单 vs 宽幅图文流程 | 替换对应完整 Requirement，原始输入不预填，Capture 弹窗只提供一个 MD 编辑器作为可编辑材料流；审阅编辑时才校验标题/分级；输入态按附件使用 900px 左右居中单列，审阅/结果态不超过 900px |
| context 给出另一套优先级 | 视觉采用上方治理顺序；结构参照 HTML，业务约束按 PRD/AC；不重新解释为附件一对一复刻 |
| HTML 默认审阅、localStorage、固定 AI、演示编号、图片不跨刷新 | 全部是原型演示。产品新建默认输入，服务端恢复/真实模型/真实任务替代，不复制演示行为 |
| HTML 自动流式页面高度 vs context 固定头脚 | 实现限定工作区高度、内容独立滚动、头脚固定可达，并在 Skeleton 证据中确认 |
| 原型只演示两个拆分标题且未覆盖 50 条/草稿管理 | 完整编辑候选正文、类型和来源；文本文件导入为 MD 编辑器内来源块，图片作为同一材料流的私有材料卡并由候选引用；补齐草稿恢复/删除和批量状态，不删减 AC |

## UI Contract — 界面契约

入口为既有需求中心新建 Capture，不新增导航。默认材料步骤，弹窗只有一个 MD 编辑器作为原始材料输入面；用户可直接输入文字，也可加入多张图片或多个 `.txt`/`.md` 文本文件。文本文件内容以内嵌来源块写入 MD 编辑器，图片以同一材料流中的私有材料卡展示和保存，候选通过稳定材料标识引用来源。恢复草稿跳转服务端状态；只读/未就绪禁用相关写操作并给原因，授权失败不得展示他人草稿。系统分材料、审阅、结果三步，“条目 1”仅显示顺序；主动作分别“AI 整理候选”“确认创建 N 条”“重试原任务/开始新一批”。不展示内部 ID/版本作为必填项。

字体 Inter/Noto Sans SC，正文 14px/1.45，候选正文 13px，标题 25/18/15px；金色深 #D8AC55、浅 #B9832E，面板/输入/边框/文字使用现有语义 token；卡片与按钮圆角 2px，边框 1px。候选 padding 17px 18px、间距 12px；操作图标统一现有图标库 16px，文字标签始终保留。主次动作共享 Button，不用新增品牌插画。

1440px 输入态工作区按附件保持居中单列，宽度约 900px；材料抽屉、MD 编辑器、草稿状态和删除草稿属于同一张输入 card。来源材料以紧凑 pill chip 展示，文本文件以内嵌来源块进入 MD 编辑器，图片保留私有材料引用与即时预览。`AI 整理候选` 位于输入 card 外并撑满内容宽度；关闭动作为轻量文字按钮。审阅态和结果态继续复用 900px 单列工作台。内容 min-width:0、独立滚动；900px 以下单列，390px 不横溢。编辑浮层宽≤610px、高≤85vh，内部滚动，焦点进入/约束/返回触发器。hover/focus/disabled/loading/open/invalid 全覆盖；保存失败阻止确认，项目切换使旧请求失效。

前后台一致性 checklist：复用页面壳的品牌/Logo、导航密度和 active、折叠、用户菜单、字体/图标/危险色/浮层层级与 toast；管理后台不新增页面，检查共享 token 无回归。预览允许 Esc/关闭/捕获阶段外部点击，即使内部 stopPropagation；数据编辑只能显式保存/取消，脏数据退出先提示。删除和确认保留明确取消路径，不用 window.confirm。

Mock/API 边界：Skeleton 仅用显式合成 fixture 建立布局且不可连接正式写入；进入联调后图文、草稿、候选、确认和结果全部来自真实 API，产品构建无演示成功回退。原型截图、合成测试和真实模型/浏览器证据分开记录。

## UI Skeleton — 先行骨架

组件目录为 `src/web/src/components/requirement-center/capture/`，由 RequirementCenterPage 引入。组件层级：CaptureDialog → CaptureWorkspace → 单一 `capture-md-editor` / `capture-materials-summary` / CaptureCandidateList → CaptureCandidateCard；底部 CaptureActions；统一 CaptureModal 管理编辑、合并、拆分、来源、删除、确认、草稿删除与退出提示；CaptureResult 只展示服务端终态。

| 区域 | 目标 data-testid | 数据/状态容器 | 1440px 焦点 |
|---|---|---|---|
| 工作区/布局 | capture-workspace / capture-layout | project + draft + step | 壳复用、输入态附件单列、审阅/结果切换 |
| 单一 MD 编辑器 | capture-md-editor / capture-file-input | text、导入文本块、media_ids | 唯一文本输入框、长材料滚动、文件加入可见 |
| 材料摘要 | capture-materials-summary / capture-image-card | uploading/ready/failed、图片移除 | 图片溢出与来源可读，不提供第二个文本编辑框 |
| 候选卡 | capture-candidate，data-candidate-id | revision、selected/edited/empty | 密度、长正文、50条滚动 |
| 操作栏 | capture-actions / capture-save-state | saving/saved/failed/conflict | 不遮正文、唯一主动作 |
| 浮层/结果 | capture-modal / capture-result | modal kind、task state | 焦点、层级、失败与恢复 |

结构和状态占位已按“单一 MD 编辑器 + 材料卡”方向完成；1440px 深浅主题和 390px 首轮 Skeleton 截图、尺寸与样式采样已写入 `evidence/skeleton-*.png` 与 `evidence/skeleton-styles.json`。细节交互仍以真实 API 和浏览器证据为完成门禁。

## UI Reference Replication Contract — 局部一致

本需求无用户附件复刻目标，保真模式为局部一致。反向工程范围是上述 HTML 的工作区/来源/卡片/底栏/浮层与现有页面壳；原型无指标、筛选、看板列头、空列、FAB，均不新增。业务语义按冲突裁决保留。

下表目标 selector 均为 data-testid，组件均归属上述目录；卡片动作额外以 data-candidate-id 选定对象，不能以序号当业务身份。

| 动作/参考 selector | 目标 selector → modal 类型 | 组件族与状态 | 验收证据 |
|---|---|---|---|
| 新建入口/.workspace | capture-workspace → 工作区 | Workspace：输入/审阅/结果/关闭 | Skeleton 1440px |
| #files / [data-image] | capture-file-input / capture-image-card → inline | Materials：文本文件导入 MD 来源块，图片上传/预览/失败/移除 | AC-XCUT-001 至 006 |
| #back-input | capture-back-input → 步骤 | Workspace：可用/任务冻结 | AC-008/010 |
| [data-edit] | capture-edit → capture-edit-dialog | Dialogs：编辑/改类型/非法/保存/取消 | AC-004/005、交互截图 |
| #merge | capture-merge → capture-merge-dialog | Dialogs：少于2条禁用/编辑/保存 | AC-006、双来源 |
| [data-split] | capture-split → capture-split-dialog | Dialogs：子条目/来源分配/保存 | AC-006、子来源 |
| [data-remove] | capture-delete → capture-delete-dialog | Confirm：取消/删除/空 | AC-007 |
| [data-source] | capture-source → capture-source-dialog | Preview：开/外部关/内部不关/撤权 | AC-016/018/PROTOTYPE-005 |
| #confirm | capture-confirm → capture-confirm-dialog | Confirm：保存中禁用/汇总/受理/冲突 | AC-010/011 |
| #retry | capture-retry → inline | Result：失败/恢复/成功/受阻 | AC-014/015 |
| #close | capture-close → capture-exit-dialog | Dialogs：保存成功直接退出/失败提示 | AC-008/009 |
| 原型未覆盖恢复/删除草稿 | capture-restore / capture-draft-delete → capture-drafts-dialog / capture-draft-delete-dialog | Dialogs：列表/空/恢复/删除/被占用 | AC-017/019 |

动作族一次性实现，编辑共享草稿表单和焦点状态，Confirm 共享确认/取消与 pending 状态，Preview 单独支持轻量退出；例外是 retry 不修改内容，只请求原任务续作。

Computed style 采样：每项记录页面、视口、主题、状态、selector、期望值、实际值、容差、证据路径。工作区 width≤1200、材料 width320、列布局；候选 padding17/18、间隔12；正文14/20.3px、候选13px；主按钮金色/2px圆角/1px边框；浮层 width≤610、max-height85vh/overflow；操作栏定位和 z-index 使用项目层级。尺寸容差1px、颜色 token精确一致，字体系统回退明确记录；实际值在实施采样前为 pending，不编造。

分批：A 壳与 Skeleton；B 材料/候选/全部动作与 modal 族；C 真实任务/错误/恢复、响应式和主题。每批留截图与样式摘要、非目标页面回归说明，存本 Change evidence/；原型中的 PNG 仅作设计输入。最终以 design、REQ acceptance、真实视觉/样式、Mock/API 声明和 REQ 最终一致性共同验收。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers: [usage_events, request_logs, task_traces, task_trace_spans]
  reason: 上传、AI 整理、版本确认和批量写入跨越 Web 行为、API、业务 DB、对象存储和 Agent Workflow，四层均适用。
  validation: 实施覆盖 AC-OBS-001 至 004 的可信 request_id、行为透传、直接 API、任务节点、重试关联、脱敏、降级、保留周期及 OpenAPI/Orval 和 SQLite/MySQL 测试；当前只完成设计声明。
```

稳定事件建议 capture.upload、capture.organize、capture.review_save、capture.confirm、capture.retry；统一登记字典。Web 产生 behavior_trace_id/event_id，服务端生成可信 request_id；整理及确认各有 task_trace_id，节点含授权/材料读取/模型/校验/保存/编号/写文件/最终核对。每次重试保留请求身份并关联原业务 task_id。后台清理也有任务摘要；普通 GET 仅请求日志，无多步骤执行，故不新建 Task Trace；直接 API 不伪造 usage_events。

metadata 只白名单保存 opaque ID、数量、状态、阶段与受控原因码，不保存原文、图片、Prompt、完整模型输出、凭证、对象 key 或本机路径。观测失败不阻断业务但保存降级摘要。request/task 明细90天、行为180天、聚合1年，业务草稿/正式来源遵守独立保留规则。

## 迁移、验证与风险

采用增量建表与索引，先迁移数据库、部署兼容后端/worker，再切 Web 入口；旧单条 API 保留授权兼容且与新批次共用项目写锁，不把历史 Issue 伪装成新草稿。回退先停止新确认并处理非终态任务，保留新表、材料和恢复计划；不能降级删除来源或让旧 worker 处理不认识的批次计划。

SQLite/MySQL 都验证 CAS、事务唯一约束、字符/JSON/时间、并发确认、迁移重复执行与重启恢复；不可仅凭 SQLite 宣称 MySQL 已验证。同步 docs/03-api-index.md、04-database-design.md、07-object-storage-strategy.md、02-deployment.md、观测映射、compatibility/database 与必要媒体/部署 README；沿用规范约束，若实现产生新长期策略再更新对应规则。客户端生成必需，新增公开产品手册不在本次生成命令范围。

RC-001 图片权限/保留由上传撤权、配额与删除重放验证；RC-002 固定版本/幂等/恢复以每个持久化边界故障注入验证；RC-003 原型不替代真实效果，12组样例对照 `/capture` 基线并分别记录合成和真实观察。模型实际耗时单列；本地异步受理 p95≤2秒，完成后前台≤5秒刷新。

风险：多文件不可事务回滚，采用前后镜像与读取屏障；外部写冲突保持受阻；模型权限隔离必须用执行配置测试证明；私有图代理增加服务开销但支持撤权立即生效。无新增用户决策，实施中的证据不足不能标记完成。

## 实施检查点

骨架实际入口为 `src/web/src/components/requirement-center/capture/CaptureWorkspace.tsx` 与 `capture.css`，通过 materials/children/actions 插槽及 step/saveState 承载区域状态。隔离测试入口为 `src/web/tests/fixtures/capture-skeleton.html`；当前未连接生产入口，候选为明确标注的合成数据。首轮截图与样式在 evidence/skeleton-*，1440px 深浅主题、390px 布局检查通过；首轮人工确认仍待答复。详细候选及浮层组件沿用上述动作矩阵，尚未完成。


## 验收返修 UI 契约：附件原型复刻

用户在验收中提供 `layout-4-console-workbench.html`，确认 Capture 弹窗采用“单一 MD 编辑器 + 内嵌图片/文本文件材料块”的正式方向，并要求布局按附件复刻且保持当前 UI 设计系统。返修后的 UI Contract 更新如下：

- 弹窗从 1200px 双栏治理工作台收敛为居中 Capture flow：输入态和审阅/结果态均按附件控制在约 900px 内。
- 顶部使用轻量 topbar、标题说明和三点式进度，不再使用横向 ol 步骤条。
- 原始材料区在主卡片内使用 `details.capture-material-drawer`，展示额外上传的图片、上传文本文件和“添加图片或文本文件” chip；上传后的 `media_id`、文本来源块和候选来源边仍由服务端草稿版本保存。
- 候选区使用 `.capture-board` 单列列表，`.capture-candidate` 为 `52px + 1fr` grid，左侧编号仅作为用户审阅序号，不是 REQ/BUG 编号。
- 编辑/改类型从 modal 改为候选卡片内联 field panel；保存时沿用候选内部稳定 ID，类型变化只重算分级字段，不丢失 `source_refs`、父子关系或图片关联。
- 最新验收反馈已覆盖上一轮 modal 承载方式：来源依据在候选卡内以 label 加具体依据文本展示；拆分和删除在候选卡内展开面板完成；确认创建直接提交确认流程。候选 ID、来源追溯、确认幂等、编号分配和服务端数据流程不变。
- 附件颜色和字体不直接复制；所有视觉值映射到 `--mb-*`、`--ops-*` 和 `--mb-accent`，满足“UI设计系统保持与当前一致”。


### 字体层级收敛补充

验收截图显示 Capture 审阅态整体字号偏大。UI Contract 追加 typography 约束：基础字号使用 13px，主标题约 26px，审阅区标题约 18px，候选标题约 15px，候选正文约 12.5px，按钮约 13px，候选编号约 15px。该约束只调整视觉密度，不改变三阶段布局、材料抽屉、候选审阅动作或确认编号契约。


### 附件字体比例回调补充

用户确认 typography 方向为“更像附件”。UI Contract 将字体比例更新为：主标题 26px/800，副标题 14.5px/1.6，审阅标题 19px/800，候选标题 16px/800，候选正文 13.5px/1.7，候选列表 12.5px/1.9，候选编号 18px/800，Badge 12px 且 `5px 12px`，主按钮 14px 且 `11px 20px`。实现保留 MoonBox 当前字体族和颜色 token，不引入附件 Manrope 字体。


### 输入态附件结构复刻补充

本轮验收反馈确认输入态以附件为准：来源材料从大卡片网格收敛为紧凑 pill chip；材料抽屉、MD 编辑器、草稿状态和删除草稿放回同一张 `.capture-editor-panel` card；`AI 整理候选 →` 作为 card 外全宽主按钮；关闭按钮为轻量文字按钮。该调整只改变 Web 输入态布局和取样脚本，不改变草稿保存、图片上传、文本文件导入、候选稳定 ID、确认幂等、编号延后和正式采集记录生成契约。


### Markdown 抽屉字体密度对齐补充

本轮验收反馈确认 Capture 字体密度应向需求中心 Markdown 右侧抽屉靠齐。UI Contract 更新为：主标题约 24px，保留高于抽屉标题的入口层级；顶部副标题约 13px；来源材料 header 约 12.5px；材料 pill 约 11.5px；MD 输入区使用右侧抽屉同款 `12.5px/1.85` monospace；草稿状态约 11.5px；普通按钮约 12.5px；主按钮约 13px/650；候选正文约 12.5px/1.68；Badge 约 11.5px/650。该调整只改变 typography，不改变输入态单 card 布局、材料流、保存、候选审阅、确认幂等或编号延后契约。


### Markdown 抽屉标题与审阅标签对齐补充

本轮验收反馈以需求中心 Markdown 右侧抽屉为产品内视觉基线，取代上一轮“主标题保留略高入口层级”的临时约束。Capture 弹窗全局字体族优先使用抽屉同源 token：`--rc-font-body`、`--rc-font-heading`、`--rc-font-mono`，并回落到现有 MoonBox 字体栈。弹窗主标题采用抽屉标题样式，固定为 19px / 650；顶部“新建 CAPTURE”采用抽屉 crumb 样式，使用 11.5px monospace 与 accent 色；MD 输入区继续使用抽屉编辑密度 `12.5px/1.85` monospace。

审阅态信息结构也按抽屉密度收敛：不再展示“AI 审阅结果”主标题；审阅头部仅保留实时统计 `{候选数} 条候选 · {需求数} 条需求 / {缺陷数} 条缺陷` 与合并所选操作，不再展示操作说明。候选卡片顶部不再可见展示“条目 n”，只保留选择框的可访问名称用于键盘/读屏定位；可见信息改为两个标签：最终类型建议（需求或 BUG）与对应分级（priority 或 severity）。删除候选动作使用危险色按钮文本。候选说明 notice 模块移除，确认前不占号、最终按类型分配编号的规则继续由确认提交、测试和服务端契约保障。


### 顶部标题与副标题精简补充

本轮验收反馈确认顶部主标题和副标题在当前弹窗结构中是冗余信息层级。最终 UI Contract 更新为：Capture 弹窗顶部只保留 `新建 CAPTURE` crumb、关闭动作和三点式步骤条；不再渲染独立主标题“写下需求或问题”和说明副标题。输入态的解释性文案迁移到 MD 编辑器 placeholder，内容区仍通过来源材料抽屉、`原始材料` label、保存状态和 `AI 整理候选` 主按钮表达当前任务。

该调整只改变顶部信息架构和文字承载位置，不改变三阶段流程、单一 MD 编辑器、材料抽屉、候选审阅、最终确认、编号延后、来源追溯或幂等写入契约。视觉采样不再使用 `.capture-workspace h1`，改为采样 `.capture-kicker`、`.capture-progress strong` 和 MD textarea 密度。


### 候选标题行、材料精简与二次弹窗可读性补充

本轮验收反馈基于实际深色主题截图。该阶段曾要求审阅候选卡顶部必须把选择复选框与候选标题放在同一行，类型与分级标签保留在右侧；标题与 checkbox 作为同一 label 绑定，视觉和可访问语义一致。来源依据、拆分、删除、确认等二次弹窗的高层级 modal 方案已被后续 `layout-5-split-delete.html` 反馈覆盖，当前生效契约见“附件拆分删除与来源依据行内化补充”。

输入态来源材料继续保留单一材料流，但文案进一步收敛：summary 只显示“来源材料 · x 项”；来源材料列表只展示额外上传的图片和文本文件；默认 Markdown 编辑器正文不显示为 `MD 文本` 或 `编辑器正文` chip，也不计入来源材料数量。图片 chip 不显示“图片材料”等副文案；“原始材料”不作为可见 label 展示，只保留 textarea 的可访问名称。输入 card 和来源材料外部边框移除，主要视觉边界由 textarea、材料 chip 和主按钮承担。该调整不改变草稿保存、材料上传、来源引用、候选稳定 ID、确认幂等或编号分配契约。


### 附件拆分删除与来源依据行内化补充

本轮验收反馈以 `layout-5-split-delete.html` 为参考，并明确覆盖上一轮“来源依据、拆分、删除和确认创建使用二次弹窗”的临时实现。最终审阅态契约如下：第 2 步不展示 `AI 审阅结果` 标题，只保留候选统计与合并所选；来源依据在候选卡正文后以 `来源依据` label 加具体依据文本展示，文本优先取模型 `classification_reason`，无理由时再回退来源引用摘要；拆分在候选卡内展开编辑面板，允许分别编辑两个子条目的标题和描述后确认；删除在候选卡内展开危险确认面板；确认创建按钮直接提交服务端确认流程，不再出现二次确认弹窗。

该补充只改变 Web 审阅态交互承载方式。候选内部稳定 ID、合并/拆分父子来源边、图片和文本来源追溯、确认版本绑定、服务端幂等、编号延后与按最终类型分配编号的流程保持不变。


### 拆分删除面板向下展开补充

本轮验收反馈进一步明确第 2 步卡内展开方向与拆分面板结构。最终 UI Contract 更新为：拆分和删除面板必须渲染在候选卡操作按钮行之后，视觉上向下展开，避免按钮被面板顶到下方造成“向上展开”的感知。拆分面板使用左右两栏，每栏都是完整子条目，包含类目、标题和描述；两个子条目的类目可分别选择需求或 BUG，确认拆分后按各自类目使用默认分级并保留父候选来源边。删除面板同样位于删除按钮下方展开。

该补充只改变 Web 审阅态卡内交互布局。候选 ID 生成、父来源保留、来源追溯、确认幂等、编号延后和服务端数据流程保持不变。


### 上传文本文件删除补充

本轮验收反馈确认第 1 步来源材料中的上传文本文件需要与图片一样具备可删除入口。最终 UI Contract 更新为：`.txt` / `.md` 文件导入后仍写入唯一 MD 编辑器中的来源文件块，同时来源材料区域必须显示独立文本文件 chip，chip 展示文件名和删除按钮；用户删除该 chip 时，同步从 MD 编辑器正文中移除对应 `### 来源文件：<filename>` fenced block。图片材料继续沿用现有 `media_id` 和 `removeImage` 删除逻辑。

该补充不新增服务端字段，不改变草稿保存、AI 整理、候选 ID、来源追溯、确认幂等、编号分配或服务端数据流程。文本文件 chip 由当前 MD 正文中的来源文件块派生，保持“单一 MD 编辑器”为唯一文本材料事实源。


### 候选卡操作按钮与编辑面板向下展开补充

本轮验收反馈确认第 2 步候选卡操作区需要与已调整的拆分/删除面板保持一致。最终 UI Contract 更新为：`编辑 / 改类型` 按钮文案收敛为 `编辑`，并显示编辑图标；删除按钮显示删除图标；编辑面板必须渲染在候选卡操作按钮行之后，视觉上向下展开，与拆分和删除面板方向一致。编辑面板内容和行为保持不变，仍支持类型、分级、标题和描述编辑；改类型不丢失候选 ID、来源和图片关联。

该补充只改变 Web 审阅态操作区文案、图标和面板承载位置。候选 ID、来源追溯、确认幂等、编号分配和服务端数据流程保持不变。



### 项目内相似 REQ/BUG 提示补充

本轮验收反馈确认 Capture 候选审阅应在确认创建前提示项目内可能已有的 REQ/BUG，帮助用户避免重复创建。最终设计约束如下：审阅态从当前需求中心上下文读取已有 Issue 的标题、状态、来源和文档摘要；仅当候选存在相似匹配时，才在候选卡内展示最多 3 条可能相关项。未发现相关项时不展示 `可能相关` 模块，也不展示“未发现高相似……”空态。用户可对相似项选择合并到已有记录或作为已有记录补充材料；默认创建状态不展示 `继续创建新记录` 文案。选择合并或补充材料的候选保留在审阅界面作为用户处置结果，但不进入确认创建批次，因此不会分配新的 REQ/BUG 编号；需要恢复时使用简洁 `恢复创建` 入口。

该能力当前位于 Web 审阅层，不新增后端 API、DB 字段或正式补充材料写入契约。确认创建仍按保存后的最终候选集合调用既有服务端确认流程，由服务端负责版本绑定、幂等任务、编号延后和按最终类型分配编号。若后续需要把“补充材料”真实追加到已有 Issue 的 capture.md/trace.md，应另立独立 REQ/Change 定义写入、权限、冲突和审计规则。



### 默认 Markdown 编辑器不显示来源 chip 补充

本轮验收反馈进一步确认：下方 Markdown 编辑器是默认输入区，手写或粘贴正文隐含存在，不应在来源材料区额外展示为 `MD 文本` 或 `编辑器正文` chip，避免用户误以为它是可移除附件。最终 UI Contract 更新为：来源材料区域只统计并展示额外上传的图片和 `.txt` / `.md` 文本文件；上传文本文件仍以独立 chip 展示文件名并支持删除，删除时同步移除唯一 MD 编辑器中的对应 `### 来源文件：<filename>` fenced block；图片材料继续沿用既有删除逻辑。

默认 Markdown 编辑器正文继续作为草稿文本事实源参与自动保存、AI 整理、候选来源追溯和确认创建。清空这部分正文由用户直接编辑 textarea 或删除草稿完成，不提供单独材料 chip。该补充只改变 Web 输入态材料 chip 的可见性和计数，不新增服务端字段，不改变草稿保存、AI 整理、候选稳定 ID、来源追溯、确认幂等或编号分配流程。


### 创建结果态图标移除补充

本轮验收反馈确认第 3 步创建结果态不需要顶部圆形结果图标。最终 UI Contract 更新为：confirming 状态可保留 loading 图标表示进行中；成功、失败或中断结果态均不显示圆形勾选或其他结果图标，只保留标题、副标题、结果卡片、错误提示、重试入口、完成入口和幂等/产物边界说明。该补充只改变 Web 结果态视觉呈现，不改变创建结果、确认幂等、编号分配、来源追溯或服务端数据流程。

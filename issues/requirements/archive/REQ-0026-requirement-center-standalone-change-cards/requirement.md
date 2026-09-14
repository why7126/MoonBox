---
requirement_id: REQ-0026-requirement-center-standalone-change-cards
title: 需求中心 Change 可见性与关联追溯
terminal: web-catalog
version: v1
status: done
owner: product
source: capture.md
parent_requirement: null
created_at: 2026-09-12 21:11:07
updated_at: 2026-09-14 08:44:37
priority: P1
---

# 需求中心 Change 可见性与关联追溯

## 1. 背景与价值

需求中心当前从 REQ/BUG 注册表生成卡片，Change 文档读取依赖关联 Issue 授权。独立 OpenSpec Change 即使已纳入 Sprint，也缺少卡片入口；REQ/BUG 已生成 Change 后，卡片缺少明确的关联 Change ID 信息，用户难以辨认方案、任务和进度的归属。

本需求整合“独立 Change 卡片”和“Change 生成后在所属卡片展示 Change ID”，形成一个交付单元。沿用 REQ-0026 完整身份和目录，不另建需求。优先级保持 P1：补齐研发看板覆盖与追溯能力，不属于当前线上阻断。

现状依据：`src/backend/app/services/requirement_center.py` 的卡片聚合、`src/backend/app/governance/reader.py` 的对象授权和 `src/web/src/pages/catalog/RequirementCenterPage.tsx` 的卡片模型。探索时示例 `unify-issue-classification-metadata` 位于活动 Change 目录，trace 为 验收态，关联 sprint-005；该样例状态随事实源变化，不作为固定生产数据。

## 2. 目标用户与目标

面向在 MoonBox 中管理需求、缺陷和技术治理变更的产品负责人、研发成员及验收人员。用户进入已授权项目后，可以找到有权访问的 Change，辨认其所属 Issue、生命周期阶段、文档和任务进度，并追溯归档结果。

成功标准：独立 Change 可见，关联 Change 不重复生成卡片；从 Change 实际生成并建立关联开始，所属 REQ/BUG 卡片保留 Change ID 直至归档；卡片、文档和统计遵守相同身份与授权规则。

## 3. 范围

### 3.1 首版包含

- 未关联 REQ/BUG 的活动、归档 Change 独立卡片。
- 独立 Change 阶段按钮，复用 REQ/BUG 的交互、权限和执行能力门禁。
- REQ/BUG 卡片的单个或多个关联 Change ID、状态、文档和进度归属。
- 统一关联识别、去重、阶段映射、授权读取、异常提示、搜索筛选与统计。
- 在现有项目绑定、稳定快照和刷新机制中更新结果，保留既有 REQ/BUG 行为。

### 3.2 首版不包含

本轮纳入独立 Change 阶段按钮与现有动作能力的受控复用；完整行为见文末补充契约。

- 新增 Change 创建、任意编辑、任务勾选或独立的开发/归档执行服务。
- 为独立 Change 新增 Chat 会话入口或自动发送命令。
- 自动补建虚构 REQ/BUG、自动修复关联、自动修改状态、自动清理重复归档。
- 重做需求中心布局、改造 REQ/BUG 生命周期、引入跨项目合并看板。

既有 REQ/BUG 编辑及治理动作继续遵守原权限与门禁；独立 Change 阶段按钮按本轮契约接入，文档读取不自动获得写权限。

## 4. 功能要求

### FR-001 Change 身份与关联识别

在同一授权项目的完整稳定快照中，结合 REQ/BUG registry 的 related_change/related_changes、Issue trace 的 openspec_changes，以及 Change trace 的 requirement、bug、source_requirement、source_bug 等结构化来源识别关联。采用完整 ID 精确匹配；兼容历史短 Issue ID 时仅在唯一解析后建立关联，不使用 slug 子串或正文提及推断归属。

存在任一明确关联证据的 Change 不作为独立 Change。来源对象不存在、关联字段冲突或无法唯一解析时标记关联异常，不静默解除关联、不借异常创建独立卡片。异常摘要仅向具有相应对象权限的用户呈现，不能公开隐藏对象身份。

先在完整项目快照构建关联关系，再进行对象可见性过滤。不能因某个 Issue 对当前用户不可见而将其 Change 识别为独立。REQ/BUG 注册表缺失或解析失败时不能把全部 Change 当作独立；沿用已有待同步/不可用反馈。

### FR-002 独立 Change 卡片

遍历 openspec/changes 下合法活动目录与 openspec/archive 下合法归档目录，排除非 Change 目录。独立卡片使用 Change 类型标识、真实完整 Change ID、标题、状态、文档入口、任务进度及可解析的 Sprint 信息。

标题优先使用 Change trace 的显式标题，再使用文档中的有效业务标题，缺失时以完整 ID 回退；不把“背景与动机”等通用章节名当标题。不强制要求 capture.md、requirement.md、bug.md 或 Issue trace。无责任人、分级或时间证据时显示未配置或未知，不套用默认 REQ 优先级制造事实。

### FR-003 所属卡片的 Change ID 与中文标题

当前卡片只做两项视觉调整：第一，在 REQ/BUG ID 正下方、中文标题上方新增一行当前 Change ID，字体大小与原 ID 完全一致；第二，将原中文标题替换为当前 Change 的中文标题。卡片的 Sprint 标签、优先级、责任人、文档分组、进度、更新时间、底部按钮与原有交互保持当前实现，不新增卡片内关联面板或独立文档抽屉。

基准为 RequirementCenterPage.tsx 的 renderIssueCard：新增行紧跟 .rc-card-top，其字号复用 .rc-card-top strong 当前的 10.5px，字体、字重、颜色与行高也保持一致。中文标题仍使用 .rc-card-title 的 13.5px 及原有点击行为，仅替换显示文字。新增行默认是文本，不增加按钮、徽标或动作。长 ID 可受控换行并选择复制，不缩小字号；新增行所需高度是唯一允许的卡片布局增量。

有唯一可确定的当前 Change 时，ID 与中文标题、当前文档及任务进度指向同一 Change。标题优先读取 Change trace 的中文业务标题，再读 Change 文档有效中文业务标题；不把“背景与动机”等通用章节名当标题。没有中文标题时保留原 Issue 标题并在既有详情中提示，不编造翻译。

无关联 Change 时完全保留原卡片。多个关联继续保留完整关联数据，沿用既有上下文可确定的当前 Change；不能唯一确定时保留原 Issue 标题，在新增行显示“多个 Change，当前项待核实”，通过既有详情查看关联，不任意选择首项或混用标题与进度。该异常策略不新增选项弹窗。

独立 Change 卡片保留自身 ID 和 Change 中文标题，不伪造 REQ/BUG ID，不重复增加相同 ID 行；此前独立识别、授权、去重和归档范围保持。

### FR-004 活动与归档解析

按项目与规范化完整 Change ID 去重；归档日期前缀不属于 Change ID。活动与归档同 ID 时活动目录优先，并显示冲突提示；活动目录缺文档时不读取归档旧副本冒充当前文档。

只有唯一归档候选时才读取归档内容；同 ID 多份归档不任意选取，保留一个异常摘要并禁用含糊文档入口。新鲜度遵循项目稳定快照；归档迁移期间不闪现重复卡片或把半写入内容当完整成功。

### FR-005 阶段与进度

| 事实证据 | 展示阶段 |
|---|---|
| 唯一合法归档来源 | 已完成 |
| 活动 Change trace.status 为 提议态 | 准备开发态 |
| 活动 Change trace.status 为 进行态 | 开发中 |
| 活动 Change trace.status 为 验收态 | 验收中 |
| 状态缺失、不支持或事实源冲突 | 状态待核实 |

活动 trace 为状态主依据，Sprint 成员状态仅作交叉核对和漂移提示，不覆盖 trace；不以加入 Sprint、文档齐备或任务勾选全部完成推断验收通过。活动目录声明 archived 等矛盾情况提示待核实。归档中的旧 trace 状态保留为漂移提示，不将唯一合法归档重新显示为开发中。

状态未知项保留接口事实，通过工具栏下默认收起的数据异常入口展示只读ID与说明；不渲染卡片、不计入页面业务总数，不塞入采集池，不新造业务生命周期。tasks 仅提供任务完成数/总数；缺失或无法解析时显示进度未知。

多个关联 Change 各自呈现阶段与进度；任何汇总进度明确标注统计范围，不将多个 Change 的任务进度标注为单个 Change。REQ/BUG 卡片主阶段继续沿用原规则，本期不重定义多 Change 驱动的 Issue 生命周期。

### FR-006 文档与 Sprint 追溯

Change 文档按 proposal、specs、design、tasks、Change trace、关联 Sprint 的顺序组织。specs 可沿用已有聚合阅读入口，但保留规格来源。独立 Change 主文档为 proposal；缺失时提示缺失并允许读取其他真实存在的文档，不自动生成文件。

所属 REQ/BUG 的主文档和 Issue trace 入口保留；既有文档阅读入口明确标识 Change trace，避免两个 trace.md 混淆。Sprint 文档依据 Change iteration 与 Sprint changes 成员关系交叉验证，支持活动及归档解析；未纳入 Sprint 不阻止只读展示，缺失或冲突不猜测归属。

页面阅读与直接文档 API 使用同一解析、授权和路径约束；刷新后文档仍需属于当前项目、当前对象，不能混用其他 Change 的文件。

### FR-007 搜索、筛选与统计

卡片类型筛选包含全部、需求、缺陷、独立 Change。搜索同时覆盖卡片标题、自身 ID 和有权访问的关联 Change ID；搜到关联 Change 时返回所属卡片，不额外生成独立卡片。已关联但无权访问的 Change 不参与搜索提示。

同一项目、同一筛选条件下，总数等于 REQ 卡片数、BUG 卡片数与独立 Change 卡片数之和。Change 类型数量仅指独立卡片数量，避免误解为所有关联 Change 数量。页面各阶段卡片数量之和等于页面结果总数；状态未知项仅计入数据异常数量（接口原始统计保持兼容）；归档可见性选项同时作用于结果与计数。

### FR-008 权限与安全

复用空间成员、项目绑定、对象读取授权和稳定快照边界。独立 Change 以自身完整 ID 校验对象授权；已有对象授权默认策略保持一致，不新增默认公开策略。关联 Change 保留既有 Issue 授权约束，多来源时不因为另一个来源可见而放宽限制。

无权用户不能通过卡片、搜索、计数差异、文档 URL 或异常详情获得受限对象内容。跨项目同 ID、路径越界、符号链接越界和伪造 ID 均不能绕过授权；错误返回遵循脱敏策略。只读用户和冻结空间可以读取授权内容；文档入口维持只读；阶段动作按独立 Change 补充契约核对写权限与真实执行能力。

### FR-009 刷新与兼容

复用 REQ-0022 的项目切换、稳定快照、新鲜度和失败恢复机制。稳定写入的新增关联、Change 状态及归档变更在既有刷新目标内可见；保留用户筛选与既有阅读状态，项目切换后迟到响应不能覆盖新项目。

没有独立 Change 的项目仍正常显示 REQ/BUG。解析异常不能静默显示为零数据成功；权限异常不暴露内部路径。新字段兼容既有卡片数据，后端、前端类型及 API 文档统一更新。

## 5. UI 约束

沿用现有需求中心布局、设计 token、卡片和文档抽屉，采用局部一致模式。卡片视觉以当前实现为事实源，仅新增同字号 Change ID 行并替换中文标题；关联异常、归档与权限仍按功能要求验收，不以新布局扩展卡片。原型及拆解见 prototype/web/prototype.html 与 context.md，仅呈现当前卡片的两项改动。

req-complete 已补齐局部一致契约种子与交互原型；后续 Change 完善组件级 UI Contract，覆盖 1440px、窄屏、深浅主题、长 ID、空态、权限差异和键盘可达性。后续 Change 明确 selector 与 computed style 采样，包括字体、间距、宽度、溢出和层级；原有文档与动作入口按当前组件族回归验收。浮层内部点击不误关闭，外部关闭不受 stopPropagation 影响；复制反馈不改变卡片阶段。

## 6. 验收要点

- AC-001：真实独立活动 Change 显示一张卡片，阶段、ID、任务及文档与快照一致；示例状态为 验收态 时显示验收中。
- AC-002：REQ/BUG 从无 Change 到关联一个/多个 Change 后，在原 ID 下方以同字号显示当前 Change ID，中文标题为同一 Change 的中文标题；无 Change 保持原卡片，多关联歧义按 FR-003 降级；归档后关联保留且不出现额外独立卡片。
- AC-003：唯一归档正常读取；活动/归档同 ID 活动优先；多归档、缺失状态、缺文档和关联冲突有明确反馈，不读取错误副本。
- AC-004：隐藏 Issue 的关联 Change 不变成独立卡片；验证跨项目同 ID、独立对象限制、冻结空间、只读用户及直接文档 API。
- AC-005：按关联 ID 搜索返回所属卡片；全部/需求/缺陷/独立 Change 筛选、阶段及异常数量一致，无重复统计。
- AC-006：任务全勾选不自动变成已完成；多个 Change 进度和两类 trace 入口不混淆。
- AC-007：项目切换、外部生成/关联/归档和刷新保持身份一致；不回退全局目录或演示数据。
- AC-008：1440px 与窄屏、深浅主题、长 ID、文本选择复制、文档读取和权限差异具有真实视觉与交互证据；自动化合成回归不替代真实观察。

## 7. 影响层与数据采集观测

依据 `docs/standards/product-data-collection-observability.md`：

```yaml
product_data_collection_observability: applicable
affected_layers: [web, api]
reason: 新增卡片聚合、Change 身份展示、筛选与文档读取授权，需要保持客户端行为与请求日志关联。
validation: 验证卡片/文档读取和筛选行为的关联字段、请求日志成功及拒绝结果、采集失败降级和敏感内容不入日志；实施验证已通过，证据见关联Change verification.md。
```

- Web/API：复用请求封装与行为采集；行为字段仅作观测，不参与身份授权。日志只保留安全摘要，不记录 Markdown 全文或本机路径。
- Task Trace：聚合与文档读取保持同步；阶段动作复用已有执行链路及其Task Trace，不新增执行器，后续按实际接入能力验证链路。
- DB：预期复用现有对象授权存储，不新增表、索引或保留周期，因此无迁移需求；若设计证明需扩展，评审前补齐范围。
- 部署、对象存储、管理端：复用既有项目快照和前台入口，不改变部署拓扑、挂载或对象存储读写路径。
- API、安全、客户端：实现时同步 API 索引、响应契约、OpenAPI/客户端类型及授权回归；本次仅生成需求文档，不修改上述实现。

## 8. 关联需求与交付边界

- REQ-0022-local-project-import-product-iteration：复用项目绑定、稳定快照、授权与刷新；本需求补充 Change 对象覆盖与展示，不扩展其受控写入范围。
- REQ-0020-requirement-center-card-document-actions-ai-chat：复用已有卡片文档阅读体验，复用已有动作交互和能力门禁，不新增独立 AI 执行服务。
- REQ-0013-requirement-center-real-data-integration：沿用真实数据聚合原则，新增独立 Change 来源与统计口径。

保持单条 REQ；两个展示分支共享身份解析、去重、授权及文档追溯验收。后续按 req-complete、req-review、sprint-propose、req-opsx 顺序推进，不从本草稿直接开发。

## 9. 当前状态

```yaml
status: done
lifecycle_stage: review
iteration: sprint-005
openspec_changes:
  - change_id: add-requirement-center-change-visibility
    status: 提议态
```

旧范围评审已通过；本轮阶段按钮增补已评审通过。首版只读范围和两项卡片调整已纳入历史评审结论；已纳入 sprint-005，并关联 add-requirement-center-change-visibility（实施自验完成）。真实浏览器与API观察已执行，人工业务验收待确认，不存在已授权的自动写入或阶段流转承诺。

## 实施一致性核对

2026-09-12：与add-requirement-center-change-visibility实现核对一致。所属卡片仅增加ID行与替换标题，独立对象只读；多Change进度和来源在原阅读器追溯属性查看，歧义不选首项。类型/归档筛选、状态、权限及刷新已验证。证据见openspec/archive/2026-09-14-add-requirement-center-change-visibility/verification.md，人工验收由acceptance.md承接。

## 2026-09-13 验收返修约定

独立Change使用主题info蓝色左边框，REQ金色、BUG红色保持。移除九阶段之外的“状态待核实”卡片区；unknown对象仅通过默认收起的数据异常入口查看只读ID/说明，不计入页面业务统计，接口原始unknown和授权保持兼容。搜索/类型过滤同时约束诊断集合，零正常对象时业务总数为0而诊断仍可达。重复归档已核对为不同内容复用ID，保留冲突事实，不按日期任取版本、不删除历史。

验收覆盖1440/390深浅主题、九阶段DOM、三类边框颜色、收起/展开键盘操作、仅异常筛选及正常文档入口；证据见Change返修记录和logs/req0026-modify/。

## 已完成独立变更的迭代归属补充

独立 Change 的 Sprint 标签优先使用合法 iteration 并核对 Sprint changes 成员关系；iteration 缺失、null 或空串时反查活动及归档 Sprint，仅唯一 Sprint ID 可关联。多个成员关系不猜测并提示待核实；显式错误不被反查覆盖。同 ID 活动 Sprint 优先，不从归档补活动缺口。标签不依赖 sprint.md 存在，文档入口仍要求文件可读。

## 独立 Change 阶段按钮补充契约

本次范围增补已实施并通过自验，人工业务验收待确认；原已应用 Change 和 sprint-005 关联保留，历史只读版本验收不覆盖新增动作。复用 REQ/BUG 的 footer 位置、按钮样式、弹窗族、权限和执行能力门禁，不另建执行系统。

| 阶段 | 主按钮 | 交互与门禁 | 命令身份 |
|---|---|---|---|
| 准备开发态 | 开始开发 | 复用 apply 动作弹窗；有写权限、有效 Sprint 纳入及真实能力才可执行；未接入显示禁用原因 | /opsx-apply 加完整 Change ID |
| 研发中 | 查看进度 | 复用 tasks 阅读入口；无 tasks 提示缺失，不生成虚假进度；只读用户可按读取权限查看 | 当前 Change tasks |
| 验收中 | 完成 / 归档 | 复用验收与归档确认交互；测试、人工验收、权限及执行能力全部通过才开放；缺证据不视作通过 | /opsx-archive 加完整 Change ID |
| 已完成 | 无阶段主按钮 | 与当前 REQ/BUG 一致，标题和文档仍可读取 | 无 |
| 状态未知 | 无 | 保留数据异常诊断，不提供流转入口 | 无 |

纯独立 Change 使用自身完整 ID；关联 REQ/BUG 仍使用完整 Issue ID，不伪造来源。只读成员、冻结空间不得执行写动作；无读取权限不显示对象或动作。能力不足明确提示具体原因，不静默无响应。按钮显示不等于具有执行能力；Demo 仅模拟弹窗状态，不调用真实写入、创建会话或修改阶段。真实模式沿用已有执行入口，未接入能力不得伪装成功。提交期间防重入，失败保留上下文，成功后读取稳定快照，不仅靠前端移动卡片。

不新增独立 Change 创建/任意编辑/任务勾选能力，不新增自动发送 Chat 命令或新的后端执行服务。若复用需扩大接口或授权边界，后续评审明确范围后再进入 OpenSpec。

## 阶段按钮实施与证据

阶段按钮已接入：准备开发态开始开发、研发中查看进度、验收中完成/归档，已完成与未知无阶段主按钮。后端沿用action字段提供完整Change命令和禁用原因；前端同样保守禁用未接入执行能力，不能由响应中伪造action解除门禁。冻结空间返回只读原因；进度按读取权限打开当前tasks，只读文档不允许编辑。无tasks保留现有缺失反馈。

当前独立Change没有真实开发/归档执行服务，因此相关按钮禁用；不开放Demo模拟写入或伪造成功。矩阵中开发/归档modal、提交防重入/成功刷新在本轮不可执行分支为N/A，原因是已批准的能力门禁禁止进入执行分支；不以禁用按钮宣称真实开发或归档已实现。既有REQ/BUG弹窗族与执行交互保持，78项前端回归覆盖其行为。进度复用.rc-drawer、关闭按钮和Escape退出。

用户已确认1440px Skeleton布局；openspec/archive/2026-09-14-add-requirement-center-change-visibility/evidence/actions/skeleton-dark-1440.png与skeleton-light-1440.png为首轮证据。最终1440/390深浅主题4组截图、进度抽屉截图及computed style见openspec/archive/2026-09-14-add-requirement-center-change-visibility/evidence/actions/，真实浏览器组件+合成API夹具，非部署观察。仓库实际索引只读核验48个独立对象、2个有阶段动作、0个写动作开放。

验证：后端93项（含HTTP权限、冻结只读、日志拒绝与采集失败）、前端78项、TypeScript、浏览器4组通过。未部署、未进行真实开发/归档执行。接口schema未变，无需重新生成OpenAPI/Orval；API行为说明已同步。DB、部署、对象存储、安全策略不变。

## 固定禁用提示返修结论

本节替代上一轮独立Change一律禁用的结论。后端复用REQ/BUG阶段必需文档与非空门禁，并核对唯一Sprint；缺失/空文档/只读才返回相应原因，不再固定生成测试核对或能力未接入提示。文档存在不代表测试执行通过；前端复用已有testProgress/manualAcceptanceCount判断，数据不存在不伪造检查结论。

独立Change与REQ/BUG进入同一动作处理器：研发中读取tasks；真实模式中当前未支持的开发/归档动作点击后显示现有统一能力提示，不执行写入；Demo沿用现有弹窗和模拟流转，不接入真实执行。取消、提交防重入和刷新行为复用当前组件，未新增服务或权限。

验证：后端94项、前端79项、TypeScript通过；1440/390深浅主题4组真实组件合成API浏览器验收通过，截图和computed style位于evidence/action-gates/。非部署观察，未执行真实开发/归档。保留现有权限和真实能力限制；新证据替代旧固定禁用截图。

## 独立交付验收来源返修（当前结论）

验收中不再固定要求acceptance.md：优先校验trace.acceptance_refs声明的Change内相对Markdown路径；显式引用无效、缺失或为空返回具体待核实原因，不回退。未声明时查现有acceptance.md、verification.md，再识别trace中非空“验证记录/验收记录/验证结果/验收结果”章节。不得跨Change或通过绝对路径、父路径、符号链接越界读取。没有证据来源提示待核实，不补建文件；本机制定位证据，不自动判断验收通过，验收态和tasks全勾均不代替验收。

真实仓库样本standardize-sprint-default-capacity以trace验证记录作为来源；unify-issue-classification-metadata使用acceptance.md，两者当前源码均无来源阻塞。后端95项回归通过，包含显式引用、缺失、空源、越界与历史trace来源；浏览器复用真实组件+合成API在1440/390深浅主题验收，证据evidence/action-gates，非部署验收。

运行页面核对：用户地址localhost:18102对应moonbox-web，加载index-y8JI4bjc.js，其中无旧能力提示；moonbox-backend镜像动作函数也无旧提示，但仍采用上一版固定acceptance.md清单，尚未部署本次解析。未对运行容器做重建或重启，截图旧提示的实际响应来源仍未取得，不断言缓存根因。

REQ主文档、故事、流程、验收、trace、原型context及HTML已核对同步；capture/review保留历史，不需改写。API既有action字段形状不变，无需OpenAPI/Orval生成；product_data_collection_observability为applicable，affected_layers为api，复用请求日志/授权，验证无越界；无新增DB、部署配置、存储、保留周期或Task Trace。

## 中文标题来源返修

标题来源保留既有优先级：trace显式中文标题或标题字段、proposal/design有效业务标题，最后回退trace正文一级业务标题；过滤追溯、背景与动机、验证记录、验收结果等通用章节名，全部缺失才显示完整Change ID。

证据：change_index.py 与 test_change_visibility.py；浏览器 title-fallback 四组1440/390深浅主题截图及styles.json。使用合成API验证组件，未部署18102，人工验收仍待确认。

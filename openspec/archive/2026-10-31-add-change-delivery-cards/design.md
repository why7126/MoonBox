---
title: 需求中心独立交付卡片设计
---
# 需求中心独立交付卡片设计

## 背景与现状
现有 change_index 聚合将有关联 Issue 的 Change 收拢至 Issue，当前 Change 在唯一关联时可确定；RequirementCenterPage 的任务入口因此遇到多 Change 歧义。保持现有治理事实源和命令链，仅调整投影与明确目标传递。

## 目标与非目标
覆盖 REQ FR-001～010 和全部 AC；保留前期 Issue，交付按 Change 去重。无需数据迁移，不修补归档历史，不新增执行器，不扩大权限、不改变 Sprint 容量口径。

## 设计决策
D1：CSS Port，复用现有设计 token、卡片和抽屉组件。用户已明确尽量少调整，不引入新设计系统。
D2：后端先在完整稳定项目快照建立 Issue↔Change、Change↔Sprint 索引，再授权、投影、筛选和计数。键为 project_id + 完整 change_id；前期键为项目+Issue。保留有权 Issue 的异常诊断，但有效交付不再重复出现聚合卡。多个来源显示受控集合，不拿第一个作默认执行来源。无来源沿用独立 Change。
D3：阶段、任务、版本、文档、验收、Sprint 都从目标 Change 的有效版本解析。活动优先及多归档冲突继续遵循现有规则，不回退兄弟或旧副本。已归档 Change 保持旧 Sprint；父 Issue partial 与剩余范围独立。未知状态进入诊断，不算完成。
D4：估算只认明确 Change 分项，缺失待估算；Issue 总量不能复制或平均。来源统计按 Issue 去重，交付统计按 Change 去重，两者不能直接相加。Sprint 指标仍来自原有 scope 事实。

## 数据与 API
扩展现有 DTO，明确 card_kind、稳定 card_key、target_change_id、授权 source_issues、sprint 来源、版本和能力/禁用原因；具体字段命名在实施前与当前 schema 对齐。保留原 Issue ID 用于来源详情，不把 Change ID 塞进 Issue 字段。任务与文档请求携带项目、完整 Change、来源类型/ID、版本；任务提交保持乐观锁与既有幂等契约。响应只有项目+卡片+请求代次一致才更新当前抽屉。
动作确认、预填、提交、重试、会话复用与恢复共用不可变目标上下文。来源型命令保留完整 REQ/BUG 身份，通过已存在的结构化执行上下文携带 Change；若现有后端/执行器不能验证并消费明确目标，先补全同一契约及测试，不能虚构 CLI 参数或仅在提示词里选目标。多来源需要唯一来源时显式选择，选择变化清除旧预填；服务端验证关系、权限、版本和当前动作准入。历史书签不明确时要求选择而非猜测。
同步 OpenAPI、Orval 生成客户端、API 索引及接口回归；不预计 DB schema、SQLite/MySQL 迁移、存储或部署变更，若实施发现需要则先更新设计和范围。不增加原始文档/Prompt 采集。

## 冲突处理（Conflict Resolution）
事实源优先级 HTML > PNG > context > acceptance > UI 规则 > 旧规格。HTML 仅是三张卡的局部参考，不能删除 PRD 的前期、独立及多来源场景；其“全部迭代”演示不替换产品默认当前 Sprint。旧“关联 Change 继续归属 Issue 卡”及搜索返回 Issue、标题多关联回退规则由本 Change 的 MODIFIED delta 替换。保留 Issue/Change/Sprint 三组链接，每张交付卡只含自身 Change 文档；Issue 验收入口不是交付验收结论。原型 PNG 是设计输入，不是运行截图。

## 界面契约（UI Contract）
参考源：关联REQ的prototype.html、context.md与cards-minimal-change-v2.png，具体入口见trace.md的prototype_refs。保留灰底、淡蓝灰卡、11px 圆角、REQ 金/BUG 红左边框、右上 Sprint、紧凑标签、金色文件链接与 footer 文本箭头；只增完整 Change ID 行。颜色按对象类型而非阶段，长 ID 换行并可复制，未知值不填零。多来源冲突元数据显示待核实，不选首项。前后台共同检查身份、排序、权限、阶段、文档来源、统计、估算和禁用原因。
Mock/API：HTML 是无网络合成演示；产品读取授权 API，不持久化模拟数据。管理员、可写、只读、受限四类权限分别验收；归档无新增写权限。文本/链接聚焦清晰，390px 宽仍可读。

## 界面骨架（UI Skeleton）
先确认现有页面壳与筛选不变，再建立 board→column→delivery card→身份/标题/标签/文档/进度/footer，以及共享 detail drawer 和 action modal 容器。骨架包含 loading、empty、error、unknown、readonly、conflict、多来源状态，所有数据绑定稳定 card_key。1440×900 先核对列宽、密度、完整 ID 和边界；取得首轮用户确认后细化动作族与样式。

## 参考稿复刻契约（UI Reference Replication Contract）
模式：局部一致，保留业务语义。页面壳/品牌/筛选/指标沿用产品；列头、空列、卡片、标签、动作、浮层逐项核对；保留现有滚动/sticky策略，不新增吸顶。窄屏复用看板横向滚动，抽屉宽不超视口。

| 原型 selector | 目标/测试 selector（实施新增稳定 data-testid） | 组件与状态 | 批次 |
|---|---|---|---|
| .board/.column | rc-board/rc-column | RequirementCenterPage，空列/loading | 1 |
| .card/.issue-id/.change-id/.sprint | rc-delivery-card/rc-source/rc-change-id/rc-sprint | RequirementCenterPage，正常/冲突/多来源 | 1 |
| `.tags`、`.docs`、`.doc-group` | `rc-tags`、`rc-docs`、`rc-doc-group` | 卡片子组件，只读/缺失 | 2 |
| .progress/.footer | rc-progress/rc-footer | 卡片子组件，未知/进行/完成 | 2 |
| #detail/#close | rc-detail/rc-detail-close | 共享抽屉，loading/error/ready | 3 |

### 动作与浮层矩阵
以下 selector 均为目标 data-testid，实施须映射实际组件；同族共享状态机，避免逐按钮返修。

| 动作 | 浮层类型/组件族 | selector | 状态与目标规则 | 验收证据 |
|---|---|---|---|---|
| Issue/Change/Sprint 文档 | 共享文档抽屉；HTML 新页 | rc-document/rc-detail | loading/disabled/error/ready，来源明确；Sprint只读 | 请求目标+截图 |
| 查看进度/任务勾选 | 任务抽屉 | rc-tasks/rc-task-submit | readonly/loading/saving/conflict/error，锁版本防重入 | A/B迟到+并发证据 |
| 交付验收/来源验收 | 验收抽屉/来源详情 | rc-acceptance/rc-source-detail | 各自计数、缺失待核实 | 两层证据截图 |
| 开发/返修/验收/归档 | 共用阶段动作 modal/AI 面板 | rc-stage-action/rc-action-confirm | preparing/ready/submitting/disabled/error，多来源先选；目标变更失效 | 确认/请求/执行同目标 |
| 重试/恢复/复用会话 | 同动作族 | rc-retry/rc-resume | 重验关系、权限、版本、阶段 | 真实中断恢复观察 |
| 关闭/Esc/外部点击 | 抽屉及 modal 共用关闭策略 | rc-detail-close/rc-action-close | 提交中禁止重复关闭导致重入；其余恢复焦点，脏内容确认 | 键盘/焦点/窄屏录像或截图 |

### 样式采样清单
所有行均在需求中心，1440×900与390×844，浅/深主题、正常/多来源/错误状态采样。当前值均“待运行态采样”，源码值仅作期望基线；证据归属 evidence/acceptance/，不得用源码替代 computed style。

| selector | 属性与期望 | 容差/检查 | 证据入口 |
|---|---|---|---|
| rc-delivery-card | radius11px，padding15px 16px 18px，左border3px，灰阶按token | 尺寸±1px，颜色等于解析token | styles-card.json |
| rc-source/rc-change-id | mono10.5px，italic，line-height1.2，完整换行 | 字体±0.5px，无截断 | styles-identity.json |
| 卡片标题 | 13.5px/600/1.5，margin8px | ±1px，长标题不遮挡 | styles-title.json |
| rc-sprint/rc-docs | mono10px / 链接10px金色line-height1.25 | ±0.5px，可聚焦 | styles-docs.json |
| rc-detail/rc-action-confirm | 抽屉参考560px且不超视口；z-index高于看板 | 无横向溢出/遮挡，焦点可见 | styles-overlay.json |

批次1结构与数据骨架用户确认；批次2卡片与来源/状态；批次3动作与所有浮层整体实现；批次4权限、主题、窄屏及全链验证。每批截图+样式证据，对非目标页面不改动；骨架确认不是后续完整验收。

## 产品数据采集与链路观测
product_data_collection_observability:
- status: applicable
- affected_layers: web, api, web_request_wrapper, usage_events, request_logs, task_traces
- reason: 明确来源 Issue 与 Change 的目标上下文贯穿点击、请求及执行恢复。
- validation: AC-017/021；行为事件仅真实 UI 触发，直接 API 不伪造点击；请求/Task Trace 关联目标，拒绝和遥测降级可检验；不采集凭据、Prompt、正文或本机路径。
遵循 docs/standards/product-data-collection-observability.md；数据库结构 N/A：仅使用现有观测字段/受控 metadata，无新增表索引或保留期。

## 风险与回滚
多来源授权泄漏→先解析关系再过滤，UI/API同测；旧客户端字段误用→契约及生成客户端同时更新；拆卡重复容量→固定样本对账；动作仍只认Issue→端到端验证前禁止启用。回滚同版本前后端投影与API客户端，不重写治理事实和归档文件。提案阶段尚缺的运行环境与视觉证据已在实施中补齐；最终验收与归档仍按当前有效证据判定。

## 实施补充：交付命令的持久目标通道

完整来源命令保留在用户可见的 Chat 草稿和消息中；交付卡的会话主对象使用 Change ID。服务端解析阶段命令时读取已授权会话主对象，联合校验项目、完整来源、Change 关系与阶段，不使用前端提示词作为授权。命令日志、事务锁和工作区基线以 Change 为目标，基线另保存 source_issue_id；同一请求的重放不能覆盖目标或来源。工作区初始化和执行提示生成重新验证绑定，内部调用既有显式 Change 命令形式，不新增 CLI 参数；原始来源链路仍保留。旧 Issue 主对象会话遇到多 Change 仍拒绝猜测目标。

开始开发与完成/归档共用交付目标确认组件；多来源必须显式选择，无默认首项。弹窗关闭恢复焦点，Escape及外部点击统一关闭；确认只进入 Chat 预填，未自动发送。当前产品尚未接入的自动验收动作不以普通聊天冒充支持；其能力门禁与真实恢复观察已完成，覆盖和限制见verification.md。上述服务端通道替代最初临时禁用受支持阶段动作的防护方案。

## 实际组件映射与验证口径

| 原设计动作族 | 实际入口与浮层 selector | 核验结果 |
|---|---|---|
| 卡片/来源/Change | `[data-testid=rc-delivery-card]`、`[data-change-id]`、`[data-testid=rc-source]`、`[data-testid=rc-change-id]` | 身份全文与来源文档分离；卡片样式见 role-theme-styles.json |
| 文档/任务/两层验收 | `.rc-doc-group`、`.rc-drawer[role=dialog]`、`[data-testid=markdown-drawer]`、`[data-task-navigation]` | 同抽屉族；关闭按钮聚焦、任务章节定位、Esc及焦点回退 |
| 开发/返修/归档 | 卡片动作按钮、`.rc-delivery-confirmation[role=dialog]`、`select[aria-label=选择来源事项]` | 多来源选择后预填；焦点循环与关闭；不直接发送 |
| 自动验收 | 名称为自动验收的禁用按钮 | 明示当前执行能力限制；不伪造参数 |
| 历史筛选 | `[data-testid=requirement-filter-trigger-sprint]`、`[data-testid=requirement-filter-clear-sprint]` | 当前默认范围与清除后历史交付分开 |

抽屉复用产品已有760px桌面宽度（原提案560px为参考值），390px时满视口；确认弹窗桌面560px、窄屏342px。该差异保留既有抽屉体验，已目视核对。长来源文档标签允许换行；390px列286px、卡片266px，保留横向滚动。截图与实际 computed style 见 evidence/acceptance/ui/overlay-styles.json、role-theme-styles.json。权限视觉为合成授权响应，服务端授权由真实数据库回归验证；不把角色预览当真实账号写操作。

执行权限判定使用经授权并持久化的所选来源与目标 Change；还需当前有效 Sprint 同时包含两者。固定镜像中的真实隔离观察验证 alpha 启动、主动停止及改绑 beta 后重试拒绝；同目标待核对时仍拒绝重试，不宣称成功续接已观察。

## 本轮布局契约修订
2026-10-31用户反馈优先于原PNG顶部顺序：来源编号/Sprint → 中文标题 → 完整Change ID → 元信息标签。人力待估算与P1/产品团队同一标签行；窄屏自然换行。selector及样式采样、附件逐项对照和批次门禁见acceptance-fixes.md。动作按钮与浮层矩阵、Mock/API边界均不变。

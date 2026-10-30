---
title: 继承迭代操作权限的工作区成果确认合入技术设计
created_at: '2026-10-29 06:50:53'
updated_at: '2026-10-29 06:50:53'
---

# 继承迭代操作权限的工作区成果确认合入技术设计

## 背景与现状

来源需求和评审已纳入sprint-015；现有执行/治理/内容存储在FastAPI与React架构内演进。既有实现入口在src/backend/app/chat与governance，当前Change仅设计，不宣称已完成改造。

## 目标与非目标

覆盖需求全部FR与AC；保留Web、现有鉴权与双库路径。无新增TUI、语言重写、远端推送或生产发布。每REQ/BUG链路最多一个活动开发树，子Change串行；正式事实源为主工作区，执行进度为数据库投影。

## 设计决策

### D1 UI 策略

采用既有Design System组件与token适配，原型仅作为信息结构和状态输入。相较直接复制静态HTML，可复用已有主题、请求封装和权限能力；不引入新的UI框架或图片资产依赖。

### D2 授权与候选身份

复用 governance/scope.py 的空间写权限与对象访问、sprint_object.py 的唯一Sprint解析，增加共用 sprint_operation_capability(actor,repository,sprint,action)；合入权限继承此能力，不能直接套用某次Chat write_allowed。检查Sprint、链路、Change和工作区对象限制，planning/active/in_progress允许门禁通过后确认，completed/closed/archived及未知拒绝。发起者满足同权限可自确认，无第二人审批或独立名单。

merge_candidate 固定 source_commit、target_ref/commit、candidate_commit/tree、scope_hash、validation_fingerprint、binding_revision；未提交内容不自动暂存。保留原提交历史，临时purpose=integration树构建候选，执行组合验证，不自动rebase/squash。证据必须绑定组合版本和环境。确认写merge_confirmation(actor,capability_revision,candidate_id,confirmed_at)，同候选幂等；来源/目标/候选变化全部失效并要求复验重确认。

### D3 集成与持久恢复

merge_operation按仓库队列串行，阶段prepared/confirmed/queued/applying/git_applied/projecting/completed/recovery_required；每步记录预期和实际提交、执行代次及保护引用。执行重验权限、Sprint归属、ref和目录状态；确认期间撤权阻断未执行动作。主目录可能被覆盖的人工修改拒绝，不自动stash/reset。可信Git适配在目标ref仍等于预期时集成候选，并核查真实ref与工作目录结果；不把应用锁当作外部编辑锁。

Git与DB不可同事务：先保存操作意图，再Git，再对账记录；重启发现目标已为候选/可证明结果时只补记，无法证明则保留待恢复与pin，不重做合并。主线治理投影单独可续接，注册表/Sprint汇总不接受任务分支任意重写；正式规格只在归档生效。已合入不自动清理开发树、不自动推送/发布/归档。

### D4 数据与 API

提供候选创建/差异/验证查询、能力查询、确认、返修失效及操作状态接口。确认输入candidate_id、expected_fingerprint、idempotency_key，服务端解析真实Sprint，不接受客户端指定授权归属。返回可确认能力与稳定拒绝原因；403权限、409候选失效或主线冲突。审计依据持久化失败时禁止Git写入，遥测失败仅降级。验收服务以 prepare/validate/result 适配复用既有能力；REQ-0048尚未交付的部分只阻断相关集成开放，不伪造验证通过或另建环境供应系统。

## 冲突解决（Conflict Resolution）

通用输入优先级为HTML、PNG、context、acceptance、UI规则、旧规格；本组原型context显式标注全部Mock且dialog统一演示，不是真实鉴权/交互契约。将此作为有记录的例外：业务语义以已评审PRD/AC及动作矩阵为准，HTML仅确定布局。禁止将原型“无权限禁所有按钮”当作完整对象可见性实现；只读差异入口仍按读取权限处理。popover/drawer按矩阵实施，演示统一dialog不成为强制形态。无PNG不阻断设计，但实现视觉门禁不省略。

旧spec中source/copy入口规则由0042的MODIFIED条款替换；0054修改可信快照授权范围语义；数据库两份自动备份保持原样。合入不取代旧治理candidate校验/归档流程。

## UI Contract

沿用现有空间/Chat/工作区详情路由壳和导航，不新建独立产品。14px正文、24px标题、1px细边、6px圆角；1440px下216px侧栏、32px内容边距，390px下16px边距与按钮换行。颜色来自src/shared/design-system/tokens/colors.ts，字体沿用项目资源。相同动作复用图标和文案，反馈使用既有Toast/状态组件，不展示物理私有路径。

所有生产数据来自受鉴权API，静态原型Mock不进入生产；能力结果决定写动作，后端仍再次鉴权。加载、空态、错误、权限拒绝、版本过期、执行中与部分成功分别展示；切换对象使迟到响应失效。

### 动作按钮与浮层矩阵


| 动作 | 浮层 | selector 种子（data-testid） | 状态及行为 |
|---|---|---|---|
| 查看候选差异 | drawer | merge-diff | 来源 / 目标 / 候选 / 证据；只读 |
| 确认合入 | confirm | merge-confirm | 待确认 / 无操作权限 / 证据过期 / 提交中 / 已接受 |
| 返回返修 | dialog | merge-repair | 保留来源树 / 旧候选失效；不改写已合入结果 |
| 查看恢复状态 | drawer | merge-recovery | 核对中 / 待补记 / 结果未知 / 已完成 |

每个浮层有关闭按钮和 Esc 路径；关闭只退出查看，不取消服务端已接受操作。提交中禁重复提交；提交错误保留上下文。确认类动作因文件写入/合入副作用需要明确确认；轻量工作区选择不额外确认。实现采用共享按钮/弹窗族，错误信息与主操作不重叠。


### 样式采样与证据

summary、status、actions、每个动作按钮与浮层根均有data-testid；浮层根使用动作名加-dialog。沿用Button/Modal/Drawer/Popover组件族，实施时在设计回填组件实际路径与selector映射。截图覆盖1440×900、1024×600、390×844深浅主题和关键动作；computed style采样font-family/font-size/line-height/width/height/gap/padding/border/background/color/z-index/overflow/position。预期弹窗宽min(880px, viewport-32px)，body可滚动，footer可达。证据存本Change evidence/acceptance，真实截图和样式记录已位于本Change evidence/ui；逐项映射见acceptance-plan.json。

## UI Skeleton

先复用页面壳 -> 标题/身份 -> 状态容器 -> summary -> actions -> 浮层插槽；接口适配在统一客户端，状态使用真实业务标识。先完成静态结构和可测选择器，在1440px做首轮截图确认再细化。分批为壳/摘要、状态/API、动作浮层族、响应式/权限；每批留截图和样式证据，外部关闭声明包含capture与stopPropagation验证。

## 迁移、风险与回滚方案

新增结构先兼容读取、回填和逐项核验，再切换新入口；中断依操作身份重入，不自动销毁旧数据。回滚先关闭新入口与停止新写任务，再核对未完成操作；保留新增数据和历史引用，不做破坏性数据库降级。镜像/存储/权限协议不兼容时拒绝续接并保留现场。跨库唯一性、外部编辑、未知Git结果、保护引用竞争均需故障注入。S15仅1人天缓冲，实施估算变化应重新规划，不裁剪验收。

## 依赖与阶段开放

0042身份/主目录接口 -> 0054恢复保护 -> 0055验证确认合入 -> 联合开放。0042本身可先验证主目录；独立worktree对外开放需三者共同门禁。复用0053分块、0047恢复；0048供应能力先检查可用接口，缺失时仅阻断依赖部分并记录，不擅自扩大本Change。

## 产品数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: web、api、db、agent_workflow、usage_events、request_logs、task_traces、task_trace_spans；reason:工作区和异步操作涉及持久化与权限；validation:成功/拒绝/版本失效/重复请求/中断续接/脱敏场景已按AC-DATA执行，证据见implementation-verification.md。引用docs/standards/product-data-collection-observability.md。OpenAPI/Orval/API索引、SQLite/MySQL迁移和数据库设计、部署挂载、安全规则、观测字典及测试随实现更新。移动端/桌面端未启用，首期无新对象存储后端。授权审计与恢复依据不可由通用遥测替代。

## 知识库与待实施确认

承接admin-modal-width-css-cascade.md和sprint-013-retrospective.md：恢复证据分层、状态不可伪造、双库与原子持久化边界、有限缓冲。当前无产品决策阻断；具体API路由注册、迁移编号、组件路径和测试环境样本在实施首任务对齐并回填，不使用未经验证的性能承诺。

## 合入后治理同步恢复协议

Git 结果与主线治理记录分别持久化。Git 完成后，以相同权限依据、主工作区占用及治理文件锁更新对应注册表的 workspace_integration 和 Sprint 合入记录区；不修改正式阶段或已生效规格。先保存逐文件前后内容，再比较当前内容并原子替换，最后读回确认。已完成文件不重复写，人工修改或撤权阻断后续写入。Web 区分“已合入，记录待同步”和全部同步完成。治理修改保持未提交，下一次基线准备仍要求主目录干净，避免自动提交无关人工修改。

## 最终组件与交付落位

工作区界面使用 src/web/src/components/workspaces/WorkspacePanel.tsx，浮层统一采用既有 ChatDialog。旧表中 drawer/confirm/dialog 是交互用途，落地为同一可滚动浮层族；选择器为 workspace-create-dialog、workspace-diff-dialog、workspace-restore-dialog、workspace-protect-dialog、workspace-recover-directory-dialog、workspace-confirm-dialog、workspace-repair-dialog、workspace-merge-status-dialog。原生select保留键盘和系统选择行为，不新造门户。已验证实际组件与原型业务矩阵一致，截图与样式、样本边界见implementation-verification.md。

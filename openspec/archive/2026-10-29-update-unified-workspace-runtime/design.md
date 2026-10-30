---
title: 统一主源码目录与交付链路工作区及模块化执行架构技术设计
created_at: '2026-10-29 06:50:53'
updated_at: '2026-10-29 06:50:53'
---

# 统一主源码目录与交付链路工作区及模块化执行架构技术设计

## 背景与现状

来源需求和评审已纳入sprint-015；现有执行/治理/内容存储在FastAPI与React架构内演进。既有实现入口在src/backend/app/chat与governance，当前Change仅设计，不宣称已完成改造。

## 目标与非目标

覆盖需求全部FR与AC；保留Web、现有鉴权与双库路径。无新增TUI、语言重写、远端推送或生产发布。每REQ/BUG链路最多一个活动开发树，子Change串行；正式事实源为主工作区，执行进度为数据库投影。

## 设计决策

### D1 UI 策略

采用既有Design System组件与token适配，原型仅作为信息结构和状态输入。相较直接复制静态HTML，可复用已有主题、请求封装和权限能力；不引入新的UI框架或图片资产依赖。

### D2 工作区身份与并发

新增 repository_workspace 与 workspace_binding 持久对象：workspace_id、repository_id、space_id、purpose(main/development/integration/recovery/legacy)、canonical_git_identity、root_locator、base_commit、branch、lifecycle、revision。物理路径仅服务端保存，API只返回安全标识。主目录唯一约束以物理仓库身份为键；linked worktree 通过 common Git dir 归一，远程URL不能替代本地身份。

开发链路占用单独使用 delivery_workspace_claim(repository_id, delivery_root_id) 唯一键映射 workspace_id；活跃结束后受控释放，历史工作区保留。该方式兼容SQLite/MySQL，避免依赖部分唯一索引。创建状态先预留claim，再受控Git创建，完成持久登记；失败根据操作ID核对现场补记或释放空预留，不删除归属未知目录。REQ/BUG子Change归一同一root，独立Change用自身；恢复与集成树没有开发claim且禁止开发执行。

conversation持有workspace_id，turn固定workspace_revision、base/input版本和runtime_digest。主目录也执行相同写锁与恢复协议。锁顺序为仓库管理操作锁 -> 交付链路claim -> 工作区写锁；普通独立工作区写任务不长期持有仓库锁。租约失效不等于进程终止，使用代次/进程身份核对后释放；撤权与外部编辑执行前复核。外部Git写者无法由应用锁排除，集成采用固定ref条件更新并验证目录状态。

### D3 模块落位与迁移适配

moonbox-ui 对应现有 src/web；moonbox-app-server 保留FastAPI API适配；moonbox-core集中执行上下文、策略和调度；moonbox-exec是非交互入口；moonbox-exec-server封装worker/沙箱；moonbox-rollout封装内容历史及证据引用；moonbox-worktree封装可信Git与目录生命周期；moonbox-tui仅预留。Python内部包使用合法下划线名称，逻辑/发布名称仍为moonbox-，不新增七个常驻服务。

先从 src/backend/app/chat/workspace.py、execution.py、policy.py、app_server.py、local_worker.py 和 governance/scope.py 提取端口接口，现有调用方经适配层保持兼容；代码全部在src边界。禁止UI/执行器绕过可信Git接口写共享元数据。执行配置固定镜像digest，热升级只影响新任务，旧任务兼容失败明确拒绝。

### D4 数据与 API

在现有认证路由约定下提供工作区列表/登记、链路创建或复用、会话绑定、能力查询和受控清理接口；写请求包含 expected_revision 与 idempotency_key。返回 operation_id、workspace_id、lifecycle、capabilities、reason_code。版本冲突返回409，权限403，不可恢复目录返回明确不可用结果。具体URL由现有API索引统一注册，不能另建匿名执行入口。SQLite/MySQL迁移采用新增列/表、回填和校验、切读，保留source/copy适配读取窗口。

## 冲突解决（Conflict Resolution）

通用输入优先级为HTML、PNG、context、acceptance、UI规则、旧规格；本组原型context显式标注全部Mock且dialog统一演示，不是真实鉴权/交互契约。将此作为有记录的例外：业务语义以已评审PRD/AC及动作矩阵为准，HTML仅确定布局。禁止将原型“无权限禁所有按钮”当作完整对象可见性实现；只读差异入口仍按读取权限处理。popover/drawer按矩阵实施，演示统一dialog不成为强制形态。无PNG不阻断设计，但实现视觉门禁不省略。

旧spec中source/copy入口规则由0042的MODIFIED条款替换；0054修改可信快照授权范围语义；数据库两份自动备份保持原样。合入不取代旧治理candidate校验/归档流程。

## UI Contract

沿用现有空间/Chat/工作区详情路由壳和导航，不新建独立产品。14px正文、24px标题、1px细边、6px圆角；1440px下216px侧栏、32px内容边距，390px下16px边距与按钮换行。颜色来自src/shared/design-system/tokens/colors.ts，字体沿用项目资源。相同动作复用图标和文案，反馈使用既有Toast/状态组件，不展示物理私有路径。

所有生产数据来自受鉴权API，静态原型Mock不进入生产；能力结果决定写动作，后端仍再次鉴权。加载、空态、错误、权限拒绝、版本过期、执行中与部分成功分别展示；切换对象使迟到响应失效。

### 动作按钮与浮层矩阵


| 动作 | 浮层 | selector 种子（data-testid） | 状态及行为 |
|---|---|---|---|
| 选择工作区 | popover | workspace-picker | 主目录 / 已有开发树；选择即生效，活动轮次禁止切换 |
| 创建独立工作区 | dialog | workspace-create | 输入链路；准备中 / 已存在复用 / 基线缺失 / 权限拒绝 |
| 清理工作区 | confirm | workspace-clean | 预检 / 被占用 / 未合入 / 可清理；明确确认 |

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

## 最终组件与交付落位

工作区界面使用 src/web/src/components/workspaces/WorkspacePanel.tsx，浮层统一采用既有 ChatDialog。旧表中 drawer/confirm/dialog 是交互用途，落地为同一可滚动浮层族；选择器为 workspace-create-dialog、workspace-diff-dialog、workspace-restore-dialog、workspace-protect-dialog、workspace-recover-directory-dialog、workspace-confirm-dialog、workspace-repair-dialog、workspace-merge-status-dialog。原生select保留键盘和系统选择行为，不新造门户。已验证实际组件与原型业务矩阵一致，截图与样式、样本边界见implementation-verification.md。

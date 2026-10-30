---
title: 工作区恢复点复用保留与冲突恢复技术设计
created_at: '2026-10-29 06:50:53'
updated_at: '2026-10-29 06:50:53'
---

# 工作区恢复点复用保留与冲突恢复技术设计

## 背景与现状

来源需求和评审已纳入sprint-015；现有执行/治理/内容存储在FastAPI与React架构内演进。既有实现入口在src/backend/app/chat与governance，当前Change仅设计，不宣称已完成改造。

## 目标与非目标

覆盖需求全部FR与AC；保留Web、现有鉴权与双库路径。无新增TUI、语言重写、远端推送或生产发布。每REQ/BUG链路最多一个活动开发树，子Change串行；正式事实源为主工作区，执行进度为数据库投影。

## 设计决策

### D1 UI 策略

采用既有Design System组件与token适配，原型仅作为信息结构和状态输入。相较直接复制静态HTML，可复用已有主题、请求封装和权限能力；不引入新的UI框架或图片资产依赖。

### D2 恢复点与内容引用

复用 src/backend/app/chat/snapshot_store.py、content_store.py、content_schema.py、block_diff.py 与恢复协调服务，不新建会话历史引擎。新增 workspace_recovery_point(id,workspace_id,manifest_hash,head_commit,policy_version,state,created_at)；清单保存规范相对路径、类型、模式、内容hash及删除事实。turn关联before/after点，可多轮指同一点。内容去重键至少含授权仓库域；读取仍核对引用ACL。

recovery_reference(point_id,owner_type,owner_id,protection_reason)唯一引用；操作中使用pin保护，GC标记候选后再核引用版本并删除，引用创建与删除同事务/版本协议串行化。数据库块写入完成并校验后才发布完整点；不完整点不占十版本配额也不可作为基线。最近10个未保护变更点按单调序列轮转，人工/初始/验收/合入/恢复pin另计。不改变MOONBOX_CHAT_LOCAL_SNAPSHOT_LIMIT=2的数据库备份策略，也不沿用其0禁用语义。

### D3 写前写后与恢复算法

写前鉴权、锁定写入范围、检查当前清单与可信结束点；监听/mtime只提供候选提示，不确定即内容复核。写前失败禁止启动写命令。写后只在变更时发布新点，异常采集标中断现场。范围清单与沙箱可写集合一致，明确凭证、Git内部、运行库、缓存排除；不跟随越界链接。磁盘预检结合预估字节与可配置安全余量，运行中ENOSPC停止新写入并保全已存内容。

恢复操作持久记录begin/end/current清单、选定路径、expected_revision、完成项和幂等键。只对current等于该轮结束内容的路径撤销；后续修改、新增后改写、删除后重建均冲突保留。执行前再次核版，逐项写临时文件并替换/校验，不能宣称跨文件原子；中断后逐项对账。冲突默认创建purpose=recovery的独立目标，通过moonbox-worktree固定基线，不允许直接转成第二个开发树。已合入主线撤销走新变更，不能用恢复点反写主线历史。

### D4 数据与 API

提供工作区恢复点列表、差异、恢复预检、恢复操作、保护/解除人工保护及操作查询；写接口含幂等键、固定版本及选定范围，分页读差异不一次加载所有正文。响应区分complete/incomplete/unavailable与冲突文件列表、恢复覆盖和保护原因；权限403、过期409。系统引用只能由所属流程终结释放。旧数据逐版本迁移，缺正文标legacy_unavailable，删除意图继续生效，备份演练同时校验元数据和内容。

## 冲突解决（Conflict Resolution）

通用输入优先级为HTML、PNG、context、acceptance、UI规则、旧规格；本组原型context显式标注全部Mock且dialog统一演示，不是真实鉴权/交互契约。将此作为有记录的例外：业务语义以已评审PRD/AC及动作矩阵为准，HTML仅确定布局。禁止将原型“无权限禁所有按钮”当作完整对象可见性实现；只读差异入口仍按读取权限处理。popover/drawer按矩阵实施，演示统一dialog不成为强制形态。无PNG不阻断设计，但实现视觉门禁不省略。

旧spec中source/copy入口规则由0042的MODIFIED条款替换；0054修改可信快照授权范围语义；数据库两份自动备份保持原样。合入不取代旧治理candidate校验/归档流程。

## UI Contract

沿用现有空间/Chat/工作区详情路由壳和导航，不新建独立产品。14px正文、24px标题、1px细边、6px圆角；1440px下216px侧栏、32px内容边距，390px下16px边距与按钮换行。颜色来自src/shared/design-system/tokens/colors.ts，字体沿用项目资源。相同动作复用图标和文案，反馈使用既有Toast/状态组件，不展示物理私有路径。

所有生产数据来自受鉴权API，静态原型Mock不进入生产；能力结果决定写动作，后端仍再次鉴权。加载、空态、错误、权限拒绝、版本过期、执行中与部分成功分别展示；切换对象使迟到响应失效。

### 动作按钮与浮层矩阵


| 动作 | 浮层 | selector 种子（data-testid） | 状态及行为 |
|---|---|---|---|
| 查看差异 | drawer | recovery-diff | 可恢复 / 冲突 / 排除；显示前后当前版本 |
| 撤销选定修改 | confirm | recovery-restore | 预检 / 版本过期 / 恢复中 / 部分成功 / 失败 |
| 创建恢复工作区 | dialog | recovery-create | 用途说明 / 准备中 / 成功 / 权限拒绝 |
| 保护恢复点 | confirm | recovery-protect | 保护 / 解除人工保护；存在系统引用不能解除 |

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

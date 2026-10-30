---
requirement_id: REQ-0042-agent-runtime-version-space-isolation
owner: 产品团队
created_at: '2026-10-29 00:02:50'
updated_at: 2026-10-29 16:33:01
title: 统一主源码目录与交付链路工作区及模块化执行架构验收标准
acceptance_status: passed
---
# 统一主源码目录与交付链路工作区及模块化执行架构验收标准

## 验收说明

所有清单初始未执行；文档检查不构成产品验收。FR、US 与 AC 按编号一一对应。实现阶段逐项附输入版本、脱敏环境、操作与观察结果；失败项保留证据，不以 wrapper 成功代替真实结果。

## 功能验收

- [x] AC-001 **登记唯一主目录**（FR-001 / US-001）：同一实际仓库以原路径、符号路径别名或其 linked worktree 重复登记，均解析到同一仓库身份并拒绝重复主目录；远程 URL 相同的不同本地实例不误合并。

- [x] AC-002 **交付链路复用**（FR-002 / US-002）：同一 REQ 的两个子 Change 并发申请，仅创建一个活动开发树；第二个 Change 排队，验收返修仍使用原树；另一 REQ 可获独立树。

- [x] AC-003 **基线完整**（FR-003 / US-003）：主目录有未提交的任务必要治理材料时创建被阻断，显示缺失材料且不自动提交；材料进入指定提交后创建真实 Git worktree，记录正确基线且不带无关脏文件。

- [x] AC-004 **会话绑定**（FR-004 / US-004）：同工作区两会话历史均指向原身份；活动轮次切换被拒绝；删除或替换底层目录后恢复失败且不回落主目录。

- [x] AC-005 **并行互斥**（FR-005 / US-005）：同一工作区两个写任务只能一个执行；不同链路可按容量并行；外部编辑后旧版本写入被拒绝或重新预检，公共治理更新串行且不会丢失。

- [x] AC-006 **治理写入分工**（FR-006 / US-006）：任务树可修改本 Change 任务和实现；直接重写公共注册表、Sprint 汇总及已生效规格被拒绝；主线受控流程可更新对应正式事实。

- [x] AC-007 **看板事实**（FR-007 / US-007）：任务树完成而尚未合入时主看板不显示正式交付；主目录治理读取失败保留上次完整快照并显示未更新；其他工作区证据不能混用。

- [x] AC-008 **模块复用**（FR-008 / US-008）：Web 与非交互入口对同一身份和输入执行相同鉴权与核心策略；依赖检查证明 Git/内容存储通过受控接口访问；所有模块名使用 moonbox-，无 TUI 交付要求。

- [x] AC-009 **镜像及资源隔离**（FR-009 / US-009）：启动时保存镜像 digest 和工具版本；更新默认镜像不改变活动轮次；不兼容恢复拒绝；两个空间的凭证、缓存、端口、数据库和容器资源不交叉。

- [x] AC-010 **Git 与路径权限**（FR-010 / US-010）：构造越界链接、伪造 .git 指针、跨空间工作区标识与非法绑定，读取/执行均拒绝；正常 Git 工作树操作可通过受控管理接口完成。

- [x] AC-011 **生命周期与清理**（FR-011 / US-011）：模拟创建/移除中断，重复请求核对现场后续接；主目录、正在写入、存在未提交/未合入成果或恢复引用的目录不得普通删除；错误提示不泄漏路径。

- [x] AC-012 **旧数据迁移**（FR-012 / US-012）：source 登记后旧会话和轮次可追溯；copy 标为历史副本并保留未应用成果；迁移中断重试不重复登记、不丢正文；0042/0054/0055 集成门禁未齐时不开放独立树正式交付。

## 横切 AC（knowledge-base）

来源：`docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md`。本需求是 Web 工作台而非 Admin CRUD；复用弹窗横切约束，标签记为 admin-modal（规则复用）。无管理端列表/独立表单或上传，不引入对应无关 AC。

- [x] AC-XCUT-001 检查实现模板，通用 modal-card 与专属宽度类不并存；在 1440px 与 390px 采集弹窗 computed width，符合原型约束且无横向溢出。
- [x] AC-XCUT-002 在 1024×600 低视口验证弹窗 body 独立滚动、主操作/取消始终可达，遮罩不吞内部滚动，背景不误滚动。
- [x] AC-XCUT-003 必填项、行内错误与 footer 不重叠；键盘 focus 可见；Esc/关闭可退出；声明 click-outside 的轻量浮层验证内部 stopPropagation 不误关且外部点击仍关闭。

## 原型驱动 UI AC

- [x] AC-PROTOTYPE-001 逐项核对 prototype/web/context.md 的区域、状态、数据依赖和动作矩阵，完整映射到 UI Contract；所有原型 Mock 数据明确隔离。
- [x] AC-PROTOTYPE-002 实现先完成页面壳、区域插槽和状态容器，在 1440px 形成 Skeleton 截图与首轮确认记录，再细化组件。
- [x] AC-PROTOTYPE-003 1440×900、1024×600、390×844 的深浅主题与正常/无权限/错误/浮层状态分别采截图及关键 computed style；与原型对照记录差异和结论。
- [x] AC-PROTOTYPE-004 归档前核对 requirement、用户故事、流程、AC、原型意图与实际行为一致；真实 API、Mock 及未交付边界清楚，不用静态原型充当实现证据。

## 数据、安全与观测验收

- [x] AC-DATA-001 SQLite 与 MySQL 分别验证迁移、约束、并发与失败续接；升级失败保留旧数据和恢复路径；OpenAPI、Orval、数据库设计及部署挂载说明同步。
- [x] AC-DATA-002 跨空间、跨仓库、对象拒绝、撤权及伪造关联标识均服务端拒绝；日志/埋点/Task Trace 无密钥、Prompt 正文、文件正文或本机私有路径。
- [x] AC-DATA-003 Web 行为、请求、任务和步骤可关联；后台入口不伪造行为，客户端追踪字段不可用于鉴权；遥测失败可降级，业务恢复/授权依据写失败依其门禁阻断。
- [x] AC-DATA-004 至少覆盖一个真实成功、权限拒绝、版本失效与中断续接样本；静态检查、合成回归和真实行为证据分别标记。性能报告列扫描/持久化/恢复及样本条件，不编造 SLA。

## 验收证据归属

实现与真实视觉证据放后续关联 Change 的 evidence/acceptance/，本文件只定义要求。当前无 Change，不创建虚构证据链接；PNG 暂不要求，静态 HTML 可供需求评审，真实视觉验证在实现阶段补齐。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-29 16:33:01
accepted_by: workflow-sync
source_change: update-unified-workspace-runtime
source_sprint: sprint-015
evidence: [openspec/archive/2026-10-29-update-unified-workspace-runtime/evidence/acceptance/20261029124936930594-377f0a36/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```


---
title: 继承迭代操作权限的工作区成果确认合入变更验收计划
created_at: '2026-10-29 06:51:35'
updated_at: '2026-10-29 06:51:35'
acceptance_status: passed
requirement_id: REQ-0055-sprint-authorized-worktree-merge
---

# 继承迭代操作权限的工作区成果确认合入变更验收计划

来源：`issues/requirements/review/REQ-0055-sprint-authorized-worktree-merge/acceptance.md`。本Change承担全部AC；所有项目已完成逐项验收，证据存本目录evidence/acceptance。


## 验收说明

所有清单已按当前有效证据完成；文档检查不构成产品验收。FR、US 与 AC 按编号一一对应。实现阶段逐项附输入版本、脱敏环境、操作与观察结果；失败项保留证据，不以 wrapper 成功代替真实结果。

## 功能验收

- [x] AC-001 **唯一迭代归属**（FR-001 / US-001）：服务端解析工作树至链路、Change、Sprint；缺失、重复、跨迭代混合或未正式纳入均阻断；客户端伪造 Sprint 无法改变授权依据。

- [x] AC-002 **继承操作权限**（FR-002 / US-002）：空间所有者/管理员/编辑者且能访问 Sprint、链路与工作区者在有效迭代可确认；只读成员、其他空间成员、被对象 ACL 排除者拒绝；同等权限的发起者可自确认。

- [x] AC-003 **固定提交范围**（FR-003 / US-003）：未提交成果不自动加入候选；固定来源、目标、候选版本与文件范围；保留原提交历史，不自动 squash/rebase；无配置主线时阻断。

- [x] AC-004 **候选组合验证**（FR-004 / US-004）：源分支单独通过但与最新主线组合失败时不得确认；候选冲突保留原树并返回返修；通过证据包含准确候选、目标、来源及环境身份。

- [x] AC-005 **确认失效**（FR-005 / US-005）：待确认候选提交时保存确认人和版本；确认后来源/目标/候选或迭代关联变化，需要重新验证及确认；确认后撤权在执行前阻断。

- [x] AC-006 **队列与主目录保护**（FR-006 / US-006）：两条链路同仓库确认后串行集成；第二条因主线变化回到待验证/确认；主目录受影响脏文件阻断且不 stash/reset；无合法确认不自动合入。

- [x] AC-007 **持久恢复**（FR-007 / US-007）：注入 Git 已成功、DB 回写失败，重启核对实际提交后仅补记；重复确认/回调只有一次结果；无法证明 Git 结果时进入待恢复，不重置主线。

- [x] AC-008 **治理与归档分开**（FR-008 / US-008）：合入后主线受控更新注册表/Sprint 汇总，任务树恶意篡改共享状态不生效；投影写入失败可续接且不再合并；未归档的正式规格不提前生效。

- [x] AC-009 **证据与清理**（FR-009 / US-009）：已合入记录关联实际提交、授权和验证；工作树清理不删除仍引用恢复点；有未合入返修成果不能删除；撤销已合入成果使用新受控变更。

- [x] AC-010 **状态能力展示**（FR-010 / US-010）：待验证、冲突、待确认、排队、合入中、已合入和待恢复均有真实依据；无权限与验证失败分别解释；刷新/断线/重复点击不创建重复合入。

- [x] AC-011 **审计与模块**（FR-011 / US-011）：缺授权审计持久化时不开始合入；通用遥测失败可降级而不伪造失败回滚；Web 不直接执行 Git，moonbox-core/worktree/rollout 的结果相互可追溯。

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
accepted_at: null
accepted_by: null
source_change: null
source_sprint: null
evidence: []
failed_items: []
source_event: req.review
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 最终验收结论

本Change 22/22 项通过，当前证据 ready，规格归档预演与共享归档准入均通过。正式报告：[20261029125257135740-c09d44cf](evidence/acceptance/20261029125257135740-c09d44cf/summary.md)。未执行正式归档。

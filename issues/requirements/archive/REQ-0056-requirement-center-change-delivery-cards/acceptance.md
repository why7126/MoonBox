---
requirement_id: REQ-0056-requirement-center-change-delivery-cards
title: 需求中心交付阶段按 Change 独立成卡验收标准
created_at: '2026-10-29 18:38:41'
updated_at: 2026-10-31 19:42:19
acceptance_status: passed
---

# 需求中心交付阶段按 Change 独立成卡验收标准

## 执行口径

所有勾选默认未通过。原型检查、合成回归、真实产品行为与用户验收分别留证，不能互相代替。实施验收至少包含管理员/可写成员/只读成员/受限成员，矩阵与部署环境在 Change 中固定。

## 功能验收

- [x] AC-001（FR-001）未生成有效 Change 的 captured/draft/pending_review Issue 保留前期卡；已评审无 Change 显示待生成方案，不制造空交付。
- [x] AC-002（FR-002）一个 Issue 的两个有效 Change 各一张卡；一个 Change 多个 Issue 仍一张；无来源 Change 仍可见。
- [x] AC-003（FR-001/010）仅缺失/冲突关系时有权限的 Issue 仍有待核实入口；受限来源不被重分类为独立 Change。
- [x] AC-004（FR-004）固定样本的旧交付归 sprint-015 已完成，新交付归 sprint-016 研发中；筛选当前迭代仅显示新交付。
- [x] AC-005（FR-004）两个活动 Change 可分别在研发/验收；返修投影不覆盖首次 apply 完成事实；未知状态不冒充完成。
- [x] AC-006（FR-003/005）每张卡完整 Change ID 位于中文标题下方；标题、完整 Change ID、文档 URL、tasks 章节及读写目标一致，不出现 Change 1/2 或兄弟任务回退。
- [x] AC-007（FR-005）任务提交携带自身版本；并发冲突不覆盖；重复提交沿用幂等语义；归档无新增写权。
- [x] AC-008（FR-005）打开 A 后迅速打开 B，A 迟到响应不覆盖 B；刷新及返回仍定位正确对象。
- [x] AC-009（FR-006）交付卡显示自身验收，需求验收从来源入口查看；不同计数不可复制；缺证据不显示通过。
- [x] AC-010（FR-001/006）子交付全完成而需求剩余范围未交付时，来源详情仍显示 partial/未完成及后续入口，不自动完成或归档 Issue。
- [x] AC-011（FR-007）按来源 ID/标题搜索或 REQ/BUG 类型筛选，多个匹配关系不重复计卡；隐藏来源不参与可见搜索结果泄漏。
- [x] AC-012（FR-007）列头按交付数计，需求/缺陷指标分别去重；独立 Change 不虚增 Issue 数，Sprint 完成数不由卡片数量推断。
- [x] AC-013（FR-008）缺少独立估算显示“人力待估算”，与P1、产品团队位于同一标签行，窄屏不足时自然换行；共享估算不重复累计、不平均分摊；拆卡前后同一事实源的 Sprint 容量一致。
- [x] AC-014（FR-009）开发/返修/验收/归档的确认与预填均显示同一项目、完整来源及 Change；不能只传 Issue 后任取 Change。
- [x] AC-015（FR-009）多来源执行需要唯一来源时先选择；变更选择使旧预填失效；无明确目标传递能力时阻止执行并给出原因。
- [x] AC-016（FR-009）重试、会话复用与中断恢复重验目标上下文；恢复 A 不执行 B，原阶段或权限失效时拒绝。
- [x] AC-017（FR-010）直接 API 与 UI 同样校验项目、来源关系、对象权限和目标；受限来源身份不泄漏，越权任务写入与执行拒绝。
- [x] AC-018（FR-002/010）同 ID 活动/归档按既有规则唯一展示并诊断冲突；快照失败与旧数据分开，不自动修复事实源。
- [x] AC-019（FR-003/010）1440×900 与390×844下完整身份可读、复制，按钮可聚焦、键盘打开关闭；浮层关闭后焦点回触发器。
- [x] AC-020（FR-009/010）文档/任务/验收/阶段动作具备loading、disabled、error及防重入；关闭、Esc、外部点击策略统一，反馈不造成布局跳动。
- [x] AC-021（FR-009/010）行为、请求和任务可关联目标 Change/来源 Issue；直接 API 不伪造行为事件，凭据/Prompt/文档原文不进入metadata，遥测失败不阻断业务。

## 原型驱动 UI AC

- [x] AC-PROTOTYPE-001 核对 prototype/web/context.md 的页面、组件、状态、数据依赖与 HTML；拆解与本需求一致。
- [x] AC-PROTOTYPE-002 实施前完成 UI Skeleton 首轮用户确认，记录选择结果；本轮静态原型不是实现 Skeleton 通过。
- [x] AC-PROTOTYPE-003 实施后对1440×900与390×844的当前/历史筛选、多来源、任务抽屉、验收及阶段动作留截图、computed style 与目标请求证据。
- [x] AC-PROTOTYPE-004 归档前核对 PRD、故事、流程、验收、trace、原型与实际行为，消除剩余范围、统计及动作身份冲突。
- [x] AC-PROTOTYPE-005 为所有动作族补全 selector 与浮层状态矩阵，采样字体、间距、宽度、溢出、层级及低视口滚动，深浅主题均可读。

## 横切 AC（knowledge-base）

管理端列表、表单、弹窗及上传四标签均 N/A：本需求是 Web 端交付看板，不新增管理端 CRUD 或媒体上传。以下为同域知识承接，非四类标签强行套用。

- [x] AC-XCUT-001 来源 docs/knowledge-base/best-practices/partial-delivery-sprint-handoff.md：旧 Change 的 Sprint、估算与历史证据不因父需求转入新迭代被覆写，父需求保持剩余范围与 partial。
- [x] AC-XCUT-002 同上：只读看板刷新不重放旧归档事件；复查历史附件哈希不变，不把既有同步器重放缺口宣称已修复。
- [x] AC-XCUT-003 来源 docs/knowledge-base/retrospectives/sprint-015-retrospective.md：任务数、AC数、估算和实耗分别表达，未知不填零，共享证据不重复计数。
- [x] AC-XCUT-004 来源 docs/knowledge-base/best-practices/prototype-driven-ui-gate.md：Skeleton先于细节；返修重采受影响视觉证据，归档核对REQ最终一致性。

## 证据计划

身份/去重/统计使用固定数据合成测试；读写/执行用服务端权限和版本回归；会话恢复另留真实执行观察；视觉按context矩阵取证。AC-021覆盖请求与任务关联、拒绝及降级。已完成实现回归、真实产品只读观察、固定镜像隔离中断拒绝观察及视觉自检，细节见对应Change的verification.md；逐AC机器验收结果由acceptance-plan.json运行后回填。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-31 19:42:19
accepted_by: workflow-sync
source_change: add-change-delivery-cards
source_sprint: sprint-018
evidence: [openspec/archive/2026-10-31-add-change-delivery-cards/evidence/acceptance/20261031194008387075-bde1ccdd/summary.md]
failed_items: []
source_event: opsx.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```


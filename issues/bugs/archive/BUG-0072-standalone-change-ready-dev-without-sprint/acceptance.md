---
title: 独立变更排期阶段与动作验收条件
created_at: '2026-10-31 08:17:50'
updated_at: 2026-10-31 15:59:53
acceptance_status: passed
---
# 独立变更排期阶段与动作验收条件

## 展示规则与交互范围
默认细化方案供评审：只处理尚未开始的proposed独立Change。无归属、冲突或失效均留在“迭代规划”；无归属标“待纳入迭代”，冲突/失效保留明确阻塞原因，不显示为可开发。唯一有效Sprint归属成立才显示“待开发”。研发中、验收中和已完成对象保持既有执行事实与保护。

“加入迭代”复用既有治理命令入口，携带完整Change ID进入sprint-propose上下文，不因点击直接改写Sprint或启动开发。“核对归属”打开只读诊断，列出声明归属、实际匹配Sprint及冲突/失效原因和文档入口；不自动选取、覆盖或修复归属。诊断受现有可见性与空间只读权限限制。

## 验收清单
- [x] AC-001：完整提案无Sprint时在迭代规划，标待纳入迭代，主动作为加入迭代；待开发统计不包含它。
- [x] AC-002：唯一有效Sprint时进入待开发，显示归属及开始开发；其他权限/执行阻断仍生效。
- [x] AC-003：多重归属与声明失效分别显示明确原因和核对归属入口，不能作为普通未排期自动加入；拒绝开发。
- [x] AC-004：加入迭代只打开带正确Change身份的治理入口；最终范围写入仍经过容量、权限、同步门禁。
- [x] AC-005：核对归属为只读，展示足够定位信息；不可见Sprint/文档不泄漏，关闭诊断不产生状态写入。
- [x] AC-006：正式纳入并刷新后从迭代规划进入待开发；归属失效后重新阻断；筛选、列计数与总数一致。
- [x] AC-007：REQ/BUG关联卡、研发/验收/归档阶段、非法trace的unknown保护及只读空间均无退化；不改变canonical status或执行时间。
- [x] AC-008：修复后在1440px需求中心验证无归属、有效归属、冲突、失效及主动作交互，保存脱敏截图和状态证据；合成回归与真实观察分别报告。

## 数据采集与链路观测
product_data_collection_observability: applicable
affected_layers: 需求中心API投影、Web主动作、Agent Workflow。
validation: 检查动作身份透传、现有权限和请求链路复用；无新增DB、日志存储或采集模型需求。若实现改变API字段或请求契约，补OpenAPI/Orval回归；不存在契约变化则记录N/A及理由。

## 验收状态
实施与回归已完成。AC-001至AC-007由后端/API和Web组件回归覆盖；AC-008由1440×1000真实浏览器隔离样本观察及样式证据覆盖。API为替身，未在真实项目执行模型轮次或改写Sprint。证据见 openspec/archive/2026-10-31-fix-standalone-change-sprint-stage/verification.md 与 evidence/browser/；自动验收8/8通过，最终完整清单：openspec/archive/2026-10-31-fix-standalone-change-sprint-stage/evidence/acceptance/20261031103721069403-bcb85314/summary.md。归档预演与共享归档准入均通过；未部署、未归档。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-31 15:59:53
accepted_by: workflow-sync
source_change: fix-standalone-change-sprint-stage
source_sprint: sprint-017
evidence: [openspec/archive/2026-10-31-fix-standalone-change-sprint-stage/evidence/acceptance/20261031103721069403-bcb85314/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```


---
bug_id: BUG-0028-requirement-center-card-owner-raw-user-id
title: 需求中心 Capture 卡片负责人名称验收方案
acceptance_status: not_started
created_at: 2026-10-08 17:53:55
updated_at: 2026-10-11 07:11:13
owner: 产品团队
---

# 需求中心 Capture 卡片负责人名称验收方案

## 验收前提

本文件为正式保存的修复验收草稿，尚未执行修复后验收。当前本机页面的显示根因已确认；评审仍需明确昵称、用户名及缺失名称回退契约，其他部署版本与影响范围待验证。所有测试使用授权测试数据。具体文案未定不影响保存场景，但阻止宣称验收通过。

## 回归场景

以下 AC 复选框供需求中心在进入验收阶段后计数；当前修复后验收尚未开始，均保持未勾选。表格继续记录详细操作和预期，不作为已签认状态。

- [ ] AC-001：有可读名称账号的 REQ Capture 卡片显示约定名称。
- [ ] AC-002：仅有用户名的账号显示约定可读名称。
- [ ] AC-003：名称缺失、身份无法解析与空 owner 均使用安全回退。
- [ ] AC-004：产品、中文团队及历史导入条目保留可读归属语义。
- [ ] AC-005：BUG 与 REQ Capture 首次显示及刷新保持一致。
- [ ] AC-006：卡片、详情、负责人筛选及同名用户的名称与身份规则一致。
- [ ] AC-007：长名称在 1440px 和原反馈视口可读且布局稳定。
- [ ] AC-008：不同授权角色的可见性、权限与项目隔离保持不变。

| 编号 | 场景与操作 | 预期结果 | 状态 |
|---|---|---|---|
| AC-001 | 有可读名称账号生成 REQ Capture 卡片，比较列表响应与标签 | 按评审后的名称契约显示，文本及 title 不以原始内部标识替代名称 | 待执行 |
| AC-002 | 仅用户名、无昵称账号走相同链路 | 使用约定可读名称，显示稳定 | 待执行 |
| AC-003 | 名称缺失、身份无法解析、空 owner 分别查看卡片 | 使用约定明确回退，不泄露原始身份标识，不导致页面异常 | 待执行 |
| AC-004 | 查看 product、中文团队 owner 及历史导入条目 | 既有可读团队语义保留，各来源归属正确 | 待执行 |
| AC-005 | 在授权环境检查 BUG Capture、REQ Capture 首次显示及刷新 | 两类共用路径一致，刷新不回退为内部标识 | 待执行 |
| AC-006 | 同一条目切换卡片、详情和负责人筛选；检查同名用户 | 名称规则一致，筛选与归属仍按稳定身份区分 | 待执行 |
| AC-007 | 长名称、1440px 及原反馈视口下检查 .rc-owner-tag | 布局可用；截断时可读名称可通过 title 辨识，记录样式与截图证据 | 待执行 |
| AC-008 | 用不同授权角色查看各自可见条目并执行原有允许操作 | 身份解析不改变可见性、权限及归属，无跨项目名称泄露 | 待执行 |

## 证据与通过标准

每项记录部署版本、测试角色、合成输入、步骤、预期/实际及证据入口。跨层场景对齐同一条目的脱敏 owner 与名称字段、标签文本及 title；UI 场景记录 selector、视口和 overflow、text-overflow、white-space、宽度的 computed style。合成函数断言不替代真实浏览器观察。全部适用场景通过且缺失场景有明确处置后，方可记录验收通过。

## 数据采集与链路观测

product_data_collection_observability: not_applicable

affected_layers: []

reason: 本轮仅维护缺陷治理草稿并只读检查，不调整 API、DB、日志、行为事件、Task Trace、对象存储或端请求封装。后续修复涉及这些层级时重新声明适用范围，遵循 docs/standards/product-data-collection-observability.md。

validation: 修复前 Firefox 页面复现与同条目映射断言 3/3 通过；修复后运行态、权限与视觉验收全部待执行，不宣称已完成回归。

## 验收结果回填

```yaml
acceptance_status: not_started
accepted_at: null
accepted_by: null
source_change: null
source_sprint: null
evidence: []
failed_items: []
source_event: bug.review
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

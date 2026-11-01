---
title: 独立 Change 创建时自动分级与卡片只读展示验收计划
requirement_id: REQ-0059-standalone-change-auto-classification
created_at: '2026-11-01 00:25:42'
updated_at: 2026-11-01 01:06:07
acceptance_status: passed
---

# 独立 Change 创建时自动分级与卡片只读展示验收计划

## 功能 AC

- [x] AC-001 创建 fix：无来源、change_type=fix 且材料充分时生成合法 severity、非空理由及证据引用，不生成用于展示的 priority。
- [x] AC-002 创建其他类型：无来源 non_fix 生成合法 P0–P3 priority 和依据；相同输入重试不重复写入。
- [x] AC-003 不足与冲突：信息不足返回待补充及缺口，类型冲突或非法值待核实，不假成功、不统一默认 P2/medium。
- [x] AC-004 卡片只读：各交付阶段不存在 change-priority-edit/editor/save 及替代菜单入口，键盘导航无编辑入口，Network 无卡片 PUT priority 调用。
- [x] AC-005 正确展示：fix 显示严重性，其他显示优先级；缺失和非法分别待评估/待核实，负责人及工作量独立。
- [x] AC-006 筛选一致：刷新、搜索、阶段切换与分级筛选后维度和值一致，不将 severity 映射 P 值、不改变默认排序。
- [x] AC-007 来源保护：REQ/BUG 来源值保持继承，来源不可见不按独立评估；多来源保持原处理策略。
- [x] AC-008 历史保护：旧 fix priority 不当 severity，旧非 fix priority 保留；归档文件无新增写入，旧缺字段不新增执行门禁。
- [x] AC-009 幂等与失败：重试无重复审计及更新时间变化；写入失败不显示成功，冲突不覆盖，旧历史不丢失。
- [x] AC-010 接口与权限：旧 priority API 对 fix 拒绝且不入队；non_fix 继续检查权限、版本、维护窗口，归档/来源转换拒绝；排队操作执行前复核。
- [x] AC-011 审计与观测：治理重评保存理由、主体、时间及旧新值，直接治理操作不伪造点击事件；日志脱敏，必要审计失败不静默成功。

## 原型驱动 UI AC
- [x] AC-PROTOTYPE-001 原型拆解覆盖页面、区域、状态、交互、数据和响应式，见 prototype/web/context.md；仅文档拆解完成。
- [x] AC-PROTOTYPE-002 实施前 UI Skeleton 与本原型对齐并取得首轮确认，保存确认记录。
- [x] AC-PROTOTYPE-003 对实际产品在 1440×900、390×844、深浅主题采集截图和 computed style；各阶段验证标签、间距、溢出、焦点以及无编辑入口。
- [x] AC-PROTOTYPE-004 归档前核对 requirement、user-stories、business-flow、acceptance、trace、prototype 与实际实现及证据一致。

## 横切 AC（knowledge-base）
无 admin-list、admin-form、admin-modal、media-upload 标签：本需求为 Web 看板标签与入口删除，不是管理端表单或上传，无对应横切 AC。引用 docs/knowledge-base/best-practices/prototype-driven-ui-gate.md 的要求已写入上述四项原型 AC；最新 sprint-017 复盘提醒区分状态与名称、保留历史证据，落实 AC-003、008。

## 取证矩阵与边界
阶段：待开发、研发中、验收中、已归档；每阶段覆盖 1440×900 与 390×844，深浅主题。每组合检查 fix/非 fix 的有效、缺失、非法状态及来源 Issue。截图按阶段、视口和主题命名；Change 建立后统一存于 evidence/acceptance/，证据边界及逐项实现核对见 Change evidence/acceptance/implementation-review.md；真实API样本与隔离完整状态矩阵分别标注。

优先级/严重性标签采集 font-size、line-height、padding、gap、border、background、color；卡片补充 overflow、宽度与焦点顺序。对照现有组件 token，保留区同视口无非预期样式差异；删除编辑区允许卡片自然缩短。自动 DOM 断言不代替实际视觉取证。新建评估验收需真实创建链路观察，合成回归另列。

## 数据声明
product_data_collection_observability: applicable；affected_layers: web、api、governance。验证见 AC-010、011。DB 无新增表或迁移需求；对象存储无读写；部署不新增服务；若实现方案改变这些边界，先同步设计与测试。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-11-01 01:06:07
accepted_by: workflow-sync
source_change: update-standalone-change-auto-classification
source_sprint: sprint-018
evidence: [openspec/archive/2026-10-31-update-standalone-change-auto-classification/evidence/acceptance/20261101010255336395-3fcce99f/summary.md]
failed_items: []
source_event: opsx.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 实施验收证据

逐项回归与视觉签认见 `openspec/changes/update-standalone-change-auto-classification/evidence/acceptance/implementation-review.md`。勾选代表当前实施核对；最终 acceptance_status 由完整 opsx-accept 门禁回填。全部状态的浏览器矩阵使用实际组件+隔离Mock，真实产品仅覆盖当前库已有历史样本；真实创建观察为OpenSpec CLI，不是产品对话模型轮次。

---
title: 独立 Change 优先级验收清单
created_at: '2026-10-30 09:48:10'
updated_at: 2026-10-30 09:49:11
acceptance_status: not_started
---

# 独立 Change 优先级验收清单

## 功能验收

全部条目为待执行；本轮仅文档结构校验，不勾选产品行为通过。

- [ ] AC-001 四档值 P0/P1/P2/P3 从 trace.priority 投影，卡片标签包含“优先级”；不映射 severity。
- [ ] AC-002 缺失显示“优先级未设置”，非法显示“优先级待核实”；缺负责人显示“负责人未分配”，两者独立。
- [ ] AC-003 活动且授权对象出现设置入口，卡片内编辑区选择后只在保存成功时更新显示。
- [ ] AC-004 有效修改保存旧值、新值、服务端操作者和时间；同值保存不刷新业务更新时间。
- [ ] AC-005 失败保留选择和旧标签，重试成功后刷新结果；保存中避免重复提交。
- [ ] AC-006 版本冲突提示重载，重载后重新选择；迟到响应不覆盖其他项目或 Change。
- [ ] AC-007 独立 Change 分级筛选覆盖四档、未设置、待核实；刷新后值一致，不新增默认排序。
- [ ] AC-008 REQ/BUG 原分级不回归；建立关联后保留旧 Change 字段但停止本入口编辑，不覆盖来源 Issue。
- [ ] AC-009 无写权限不可保存，直接请求也被拒绝；不可见来源不被误判为独立 Change。
- [ ] AC-010 归档只读；旧缺值对象不新增开发或归档门禁，不批量改写历史记录。
- [ ] AC-011 行为、请求关联可追溯且不记录凭证或文档全文；遥测失败不阻断主要操作。
- [ ] AC-012 字段读取和保存保持同一契约，API 差异同步文档与客户端；不引入首屏全量重检查。

## 原型驱动 UI AC

- [ ] AC-PROTOTYPE-001 原型拆解、页面/组件/状态/数据/断点与动作矩阵完整，和 PRD 一致。
- [ ] AC-PROTOTYPE-002 实施先完成 UI Skeleton，1440px 首轮证据确认后再完成细节。
- [ ] AC-PROTOTYPE-003 1440×900 与390×844，深浅主题覆盖卡片、编辑、错误、只读，记录截图及 computed style；低高度可滚动且按钮可达。
- [ ] AC-PROTOTYPE-004 归档前核对 PRD、故事、流程、原型、AC 与最终实现/Mock 边界一致，返修截图重采。

## 横切 AC（knowledge-base）

标签判定：本需求为 web-catalog 看板卡片内编辑，不属于 admin-list/admin-form/admin-modal，无媒体上传；四个专用标签 N/A。按通用原型实践承接以下四条，不能将无标签解释为免除 UI 验收。

- [ ] AC-XCUT-001 按 prototype-driven-ui-gate.md 保留稳定 selector 和状态容器，Skeleton 先于细节。
- [ ] AC-XCUT-002 按同文档记录视口、主题、字号/间距/边框/颜色/overflow 实测证据，不以文件存在代替视觉验收。
- [ ] AC-XCUT-003 按同文档返修后旧视觉证据失效，重新采集并回填 REQ。
- [ ] AC-XCUT-004 按 sprint-015-retrospective.md 区分历史通过与当前准入，聚焦核对主文档/trace/注册表/看板，保留历史证据。

## 证据计划

功能：字段投影/权限/版本冲突合成回归，加真实产品保存回读观察。视觉：prototype/web/context.md 的状态×视口矩阵。数据：只用测试对象及脱敏字段。UI Skeleton、产品截图与样式采样待后续实现阶段；原型全部为 Mock，不触发 API。


## 验收结果回填

```yaml
acceptance_status: not_started
accepted_at: null
accepted_by: null
source_change: null
source_sprint: null
evidence: []
failed_items: []
source_event: req.complete
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

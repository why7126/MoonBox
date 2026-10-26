---
requirement_id: REQ-0051-card-persistent-info-tags
title: 卡片常驻信息标签验收标准
acceptance_status: passed
created_at: "2026-10-22 13:44:14"
updated_at: 2026-10-26 11:12:29
---

# 卡片常驻信息标签验收标准

## 验收口径

以下均为待实施验收清单，未勾选不代表文档不完整。每项记录命令/接口证据与产品观察证据，纯合成回归不替代真实交互。

## 功能 AC

- [ ] AC-001 四种数据组合及顺序：REQ、BUG、独立 Change 分别验证无值/仅人天；BUG 另测仅根因/两者都有，顺序等级、负责人、根因、人天，无占位或互相隐藏。
- [ ] AC-002 人天数值及分档：验证0、1、3、5、10及上界之后小数的S/M/L/XL/XXL映射，显示“M·3人天”且按档位着色；0、0.5、3、3.25 显示正确；null、空字符串、数字字符串、负数、布尔值、非有限数不显示，不把未知填零。
- [ ] AC-003 根因字段兼容：对 root_cause_status、status、正文声明分别验证四种枚举；confirmed 为已确认，其余为待确认；声明冲突或专用字段非法不显示已确认。
- [ ] AC-004 有效根因内容：空文件、仅标题、仅 Frontmatter/状态、纯待填写模板和空证据表不显示；有真实分析/证据正文才显示，合法根因文档不会因生命周期 status 被误判。
- [ ] AC-005 估算身份与去重：完整 Issue/Change 身份匹配；一行同时引用 Issue/Change 仅计一次；唯一总估算优先，重复相同记录去重，冲突不取任意值。
- [ ] AC-006 分项与归档源：仅完整唯一 Change 分项可求和，缺项不输出；归档 Sprint 的已完成对象仍展示，不跨 Sprint 累加或借用顶层容量。
- [ ] AC-007 文档交互：点击、Enter、Space 打开对应 BUG 文档；关闭、Esc、外部点击可退出，内部操作不误关闭，焦点返回；无权限、删除和读取失败展示既有错误态且不泄漏正文。
- [x] AC-008 全阶段保留：对采集、规划、待评审、已评审、迭代规划、待开发、研发、验收、已完成建立有数据样本，标签一致；至少真实观察研发到验收到已完成及刷新。
- [x] AC-009 更新与隔离：源值更新、根因确认变更、源数据删除及项目切换后正确刷新；请求失败不伪造零值或最新确认状态，权限撤销不展示越权正文。
- [ ] AC-010 布局与可访问性：新旧标签字体、字号、行高、padding、radius一致且border为0；1440px 和 390px、深浅主题检查长负责人和换行；标签不溢出、不遮挡主动作，状态有文字，根因按钮焦点可见，人天不伪装可点击。
- [ ] AC-011 观测与接口：聚合响应给出真实人天、根因状态及缺失/冲突原因；点击沿用文档事件与请求关联，采集失败不阻断读取，日志不含根因正文；API/OpenAPI/客户端类型及手册同步。

## 横切 AC（knowledge-base）

来源：`docs/knowledge-base/incidents/20260912-requirement-center-read-performance.md`、`docs/knowledge-base/retrospectives/sprint-011-retrospective.md`。

- [x] AC-XCUT-001 卡片元数据在同一权限约束快照聚合，页面加载不逐卡下载完整根因正文；固定样本记录前后请求数与耗时，分别标明隔离基准和真实部署观察。
- [x] AC-XCUT-002 同尺寸内容变更、增删、绑定变化及权限撤销后不复用失效标签/正文；稳定解析错误不无限自动重试，可手动恢复。
- [x] AC-XCUT-003 已完成阶段标签事实与最新源文件一致；保留历史证据但不把历史状态当当前状态，不以自动化摘要替代当前产品观察。

管理列表/表单/弹窗和上传四类标签均不适用：本需求是前台看板只读标签与既有抽屉，没有 CRUD 表单、分页、管理弹窗或上传。未机械套用其 AC。

## 原型驱动 UI AC

来源：`docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`。

- [ ] AC-PROTOTYPE-001 实现前核对 prototype/web/context.md 的页面、组件、状态矩阵、动作映射及 Mock/API 边界，确认拆解与 PRD 一致。
- [ ] AC-PROTOTYPE-002 Change 建立 UI Skeleton，先验证现有卡片标签插槽和根因抽屉，完成首轮 1440px 证据确认后再细化。
- [ ] AC-PROTOTYPE-003 在 1440×900 和 390×844、深浅主题记录默认/换行/抽屉打开与错误状态截图及 computed style（字号、行高、padding、gap、border、color、overflow、z-index）；九阶段默认卡片均覆盖，根因交互覆盖待确认、已确认及已完成。
- [ ] AC-PROTOTYPE-004 归档前核对 PRD、用户故事、业务流程、验收、trace、原型与最终 UI/数据口径一致；返修后重采相关证据。

## 证据组织与退出条件

后续 Change 的 evidence/acceptance 保存脱敏证据，使用 AC、对象类型、阶段、视口、主题和交互状态索引；无真实数据时可使用明确标识的隔离样本，不能冒充真实业务结果。所有必需 AC 通过且有当前有效证据后方可交付；本次仅完成评审材料准备。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-26 11:12:29
accepted_by: workflow-sync
source_change: add-card-persistent-info-tags
source_sprint: sprint-013
evidence: [openspec/archive/2026-10-22-add-card-persistent-info-tags/evidence/acceptance/20261022191809580956-9179f514/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```


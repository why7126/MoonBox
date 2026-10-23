---
bug_id: BUG-0043-requirement-center-card-width-sprint-tag-wrap
title: 需求中心九阶段卡片扩宽与迭代标签验收标准
created_at: "2026-10-19 09:26:49"
updated_at: 2026-10-20 08:19:18
acceptance_status: passed
---

# 需求中心九阶段卡片扩宽与迭代标签验收标准

## 验收范围

页面 `/requirements`；九阶段共用列、卡片顶部 ID 与 Sprint 标签、横向滚动和既有文档及动作入口。以本缺陷截图为问题事实源，按已确认的 380px 目标做局部调整，不复刻截图中的旧列宽。

## 验收矩阵

| AC | 条件与操作 | 通过标准 | 证据 |
|---|---|---|---|
| AC-001 | 1440×900 视口逐列检查全部九阶段，包括空列和有卡片列 | 九列 computed width 均为 380px，允许 1px 测量误差；列头和列体对齐，卡片宽度随列一致变化 | 九阶段截图与 `.rc-board`、`.rc-column`、`.rc-column-head`、`.rc-card` 边界采样 |
| AC-002 | 长 Change ID 与 sprint-010 同排，含已知复现样本 | 标签文本完整单行，white-space 为 nowrap、flex-shrink 为 0；ID 与标签边界不重叠且均在卡片内 | 顶部截图、标签文本 Range 行数与边界、计算样式 |
| AC-003 | 短 ID、长带连字符 ID、80 字符无空格 ID，分别组合有无 Sprint 标签 | 长 ID 在剩余空间合理换行，不撑破卡片；无标签卡片不留额外固定占位；需求、BUG、Change 共用布局一致 | 测试样本及截图、边界断言；合成样本与真实产品样本分别标注 |
| AC-004 | 1440×900 与 768×900 视口横向滚动到首列与末列 | 九列保持 380px；可访问全部阶段；列头对应正确；滚动不裁切卡片内容与末列 | 首尾滚动截图与 scrollWidth/clientWidth 采样 |
| AC-005 | 检查需求、BUG、Change 卡片文档入口和阶段动作，兼顾空列 | 字体、颜色、文档入口和动作可见性不因扩宽改变；代表性文档入口可打开并关闭；动作只验证可见及弹层开启/关闭，不执行真实状态迁移 | 操作记录及截图；阶段动作与弹层内容保持原有行为 |

## 组件与样式检查

- 列宽映射：`.rc-board` → `.rc-column-head` / `.rc-column` → `.rc-column-body` → `.rc-card`。
- 顶部映射：`.rc-card-top strong` 为 ID；`.rc-sprint-tag` 为迭代标签。
- 采样：width、min-width、grid-template-columns、gap、padding、white-space、flex-shrink、overflow-wrap、overflow 和元素边界。
- 阶段×视口：九阶段均覆盖 1440×900 和 768×900；真实数据空缺的卡片组合使用隔离夹具，不写生产业务记录。
- 本次不新增动作或 modal 组件；仅对既有入口做回归，不改变按钮与弹层交互契约。

## 当前结果

修复与五项 AC 验收均已通过，证据见下方逐项签认。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-20 08:19:18
accepted_by: workflow-sync
source_change: fix-requirement-center-card-width-sprint-tag-wrap
source_sprint: sprint-010
evidence: [openspec/archive/2026-10-19-fix-requirement-center-card-width-sprint-tag-wrap/evidence/acceptance/20261019093942187340-583d39b0/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 本次逐项验收签认

AI 辅助验收：当前工作区组件与 CSS 的隔离 Chromium 环境，使用合成 API，不写业务数据。以下签认基于隔离回归；后续用户授权的本地部署更新已完成，真实页面列宽 380px、标签单行的复核见 Change verification.md 与 evidence/acceptance/deployed-web.jpg。

| AC | 结果 | 证据入口 |
|---|---|---|
| AC-001 | passed | Change evidence/acceptance/layout/ 的九阶段双视口截图与 styles.json |
| AC-002 | passed | done-1440.png、done-768.png 与文字行数、边界断言 |
| AC-003 | passed | 三类对象、长/短/80字符 ID、有无标签及 empty 双视口截图 |
| AC-004 | passed | 首列 capture 与末列 done 双视口截图；逐列滚动与宽度断言 |
| AC-005 | passed | document 与 progress 双视口抽屉截图、关闭断言 |

完整证据位于 `openspec/archive/2026-10-19-fix-requirement-center-card-width-sprint-tag-wrap/evidence/acceptance/`。已目视复核桌面与窄视口末列标签单行及长 ID 换行；其他阶段由逐列截图与计算样式、边界回归共同核验。

## 归档验收清单

- [x] AC-001：已通过，依据上方逐项验收结果及对应证据。
- [x] AC-002：已通过，依据上方逐项验收结果及对应证据。
- [x] AC-003：已通过，依据上方逐项验收结果及对应证据。
- [x] AC-004：已通过，依据上方逐项验收结果及对应证据。
- [x] AC-005：已通过，依据上方逐项验收结果及对应证据。

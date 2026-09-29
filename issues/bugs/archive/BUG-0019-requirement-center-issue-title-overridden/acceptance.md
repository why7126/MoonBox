---
bug_id: BUG-0019-requirement-center-issue-title-overridden
created_at: '2026-09-14 11:05:00'
updated_at: 2026-09-29 14:44:19
acceptance_status: passed
title: 需求中心阶段业务标题来源与文档中文标题校验验收清单
---

# 需求中心阶段业务标题来源与文档中文标题校验验收清单

本轮修复自验完成；自动回归和隔离真实页面观察见Change verification.md，等待用户验收及归档。

## 回归标准

- [x] AC-001：采集池使用注册表 title，即使主文档/Change 标题不同也不覆盖。
- [x] AC-002：规划中、待评审、已评审、迭代规划分别对 REQ/BUG 使用主文档中文业务标题，构造与注册表不同的标题验证来源。
- [x] AC-003：待开发、研发中、验收中、已完成优先唯一关联 Change proposal 中文业务标题，构造与 Issue 标题不同的有效标题验证。
- [x] AC-004：零/多个 Change、proposal 缺失或无效时回退主文档；主文档缺失或无效再回退注册表及 ID，并提示缺失。
- [x] AC-005：trace/design 标题即使有效也不参与 Change 主标题取值；修改这些文档不影响卡片标题。
- [x] AC-006：两个历史样本在 proposal 无有效标题时返回原期望业务主题；补入不同的有效 proposal 标题后按阶段正确切换。
- [x] AC-007：已完成从身份唯一的归档 proposal 取标题；身份歧义不猜测，独立 Change 使用 proposal 或 ID。
- [x] AC-008：关联数变化时按来源契约切换；卡片点击与详情保持对象身份正确，Issue 与 Change 标题区别明确。
- [x] AC-009：全部生成 Markdown 文档类型逐一验证 title 和一致中文一级标题，包括 capture、trace、user-stories、review、requirement、bug、business-flow、acceptance、root-cause、workaround、proposal、design、tasks、spec。
- [x] AC-010：注册表每条 title 非空中文；生成/更新主文档时正确同步业务 title，不被 Change 标题覆盖。
- [x] AC-011：缺失/空白/纯英文/纯 ID/纯类别/模板标题及 title 与一级标题冲突均被生成门禁拒绝；中文混合专名通过，业务语义由评审确认。
- [x] AC-012：CLI/技能及产品 Agent 生成入口覆盖；本次失败不宣称完成、不推进状态；聚焦报告分离无关历史残留，保留 OpenSpec 解析关键字。
- [x] AC-013：1440px 真实观察记录 .rc-card-title 文本、截图和 computed style，验证长中文标题布局及交互；合成九阶段回归与真实观察分别记录。

## 验证范围

读取单测、前端 DOM 回归、生成产物与门禁失败用例、真实页面观察共同覆盖。中文标题规范已落实共享校验、规则、12份技能与产品正式应用门禁。验证证据：`openspec/archive/2026-09-29-fix-requirement-center-stage-business-titles/verification.md`；后端162项、前端106项；1440px真实页面为隔离测试数据，不冒充生产观察。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-29 14:44:19
accepted_by: workflow-sync
source_change: fix-requirement-center-stage-business-titles
source_sprint: sprint-007
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```


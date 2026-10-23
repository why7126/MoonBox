---
bug_id: BUG-0063-compatible-requirement-successor-blocked
created_at: '2026-10-22 09:07:15'
updated_at: '2026-10-22 09:07:15'
title: 同条文兼容追加归档阻断根因分析
root_cause_status: confirmed
---

# 同条文兼容追加归档阻断根因分析

## 根因状态

status: confirmed

确认范围为当前三项条文的追加事实、共享判定代码与复现结果，不代表修复通过或所有运行行为无回归。复用同会话 2026-10-22 浏览器观察、条文比较及最近 bug-generate 只读重现；未重放归档命令。

## 现象

SPRINT 会话跳转和命令预填已成功。最终发送门禁及 CLI 预检对已归档 BUG-0060 返回 archive_requirement_conflict，指向后继 BUG-0061 三项同标题条文。

## 证据链

| ID | type | source | 摘要与支持判断 |
|---|---|---|---|
| E1 | reproduction | scripts/validate-sprint-archive-readiness.py --sprint sprint-012 --json | 2026-10-22 最近复验 blocked；四项 Change 均归档、62/62 任务完成，仅 fix-direct-command-completion-proof 深层检查报三项条文冲突 |
| E2 | code_path | src/backend/app/governance/archive_recovery.py：transition_chain | scope 与 protected 交集非空即跳过后继边并收集冲突，不比较追加性质 |
| E3 | data_sample | openspec/archive/2026-10-21-fix-direct-command-completion-proof/specs/governance-command-durable-recovery/spec.md | 三项原要求和原场景可逐条定位，作为受保护基线 |
| E4 | data_sample | openspec/archive/2026-10-21-fix-cross-entry-continuation-guard/specs/governance-command-durable-recovery/spec.md | 三项均保留基线全文，每项增加一场景；程序化比较 original_preserved 全为 true |
| E5 | data_sample | openspec/specs/governance-command-durable-recovery/spec.md | 三项当前条文与后继版本一致，current_equals_successor 全为 true |
| E6 | code_path | src/backend/app/governance/sprint_archive_admission.py；src/backend/app/governance/sprint_object.py：require_final | 深层验收/恢复判定传入 Sprint 最终门禁，转换为当前产品阻断 |
| E7 | reproduction | 同会话 Chat 只读观察及 capture.md | 主对象 sprint-012，命令预填保留，显示 Change 1 项和 sign-off 1 项；不是旧入口未跳转 |
| E8 | data_sample | issues/bugs/archive/BUG-0062-archive-requirement-scope-conflict/bug.md；acceptance.md AC-002 | 既定范围允许同模块不同条文，同条文修改继续拒绝，未覆盖兼容追加 |

三项标题为“直接命令动作级交付契约”“直接命令最终签认与版本围栏”“直接命令状态原因与跨入口验收”。BUG-0061 原验收 14/14 只作为既有背景，不替代本修复验收。

## 已排除假设

| 假设 | 排除依据与界限 |
|---|---|
| 旧前端缓存导致此次错误 | 当前 Chat 已有正确 SPRINT 身份及命令，CLI 独立重现同类阻断 |
| 任务或 Change 未归档 | 四项 Change 归档且任务 62/62，故障来自深层后继判定 |
| 当前三项原条文被删除或覆盖 | 原文保留、当前版本等于后继规格；不据此外推所有新增场景都可自动证明兼容 |
| 只缺人工签署 | CLI 有独立条文冲突；签署与冲突是两个门禁 |

未宣称已穷尽所有哈希、附件及并发风险；修复需完整验证，不能先放行再补证。

## 已确认根因

安全策略把“同一条文被触及”作为“无法承接”的充分条件。BUG-0062 缩小了范围到 Requirement，但仍没有受控兼容追加分类及对应证明，因此合法追加被保守拒绝。产品只显示数量使用户难以区分真实冲突、缺证和独立签署条件；这是用户可见诊断缺口，不是证明引擎拒绝的直接原因。

## 产品级防复发方向

1. 统一版本化后继分类与证据契约，区分未触及、可证明兼容追加、破坏性变化、证据不足和并发失效。所有入口消费相同结论，不按 BUG-ID、Sprint-ID 或本次三个标题白名单处理。
2. 可证明兼容追加保留原要求、原场景及身份，新增场景符合确定的受支持语法，并绑定有效交付/验收及完整后继链。自然语言相似、字符串包含或模型判定不能独立构成放行证明；无法判断语义时继续拒绝并说明缺口。
3. 后继 Change 的验收/归档预检提前评估其对历史受保护交付的影响，真实不可兼容变化在写入前阻断；避免直到 Sprint 关闭才暴露。预检不偷偷修改历史或创建业务对象。
4. 产品按项展示对象、阻断类别、条文、原因和可执行处理入口，保留输入及附件；签署缺失独立展示。入口仅在对象完成后允许准备，最终写入前仍复核，不倒退为提前要求签署才能进 Chat。
5. 提交与部署门禁覆盖独立对象、多跳后继、跨 Sprint、幂等、缓存失效及负向安全矩阵；形成可复用回归夹具，不依赖特定现场。

## 验证闭环

已完成故障侧证据闭环，修复尚未实施。见 acceptance.md 的逐项验收；正向证据、安全负例、产品观察和部署版本分别留证。不得编辑旧 manifest/journal、历史哈希或首次执行事实来消除阻断。

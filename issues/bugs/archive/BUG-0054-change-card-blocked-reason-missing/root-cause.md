---
bug_id: BUG-0054-change-card-blocked-reason-missing
title: 纯 Change 卡片验收阻塞缺少具体原因根因分析
created_at: '2026-10-20 18:56:49'
updated_at: '2026-10-20 18:56:49'
owner: 产品团队
severity: medium
root_cause_status: confirmed
---

# 纯 Change 卡片验收阻塞缺少具体原因根因分析

## 根因状态

status: confirmed

确认范围限本会话已取得的样本、代码分支与当时部署版本，不等于修复验收通过。

## 现象

纯 Change 卡片和禁用动作只显示 blocked，无法定位原因。

## 证据链

| ID | 类型 | 来源 | 观察与支持的判断 |
|---|---|---|---|
| E1 | reproduction | 本会话刷新后的需求中心 `/requirements`、用户截图，摘要见 capture.md | 卡片与禁用动作均只显示 blocked |
| E2 | data_sample | 同一样本的部署 readiness，摘要见关联 BUG-0053 capture.md | 已包含 AC-001、AC-002、AC-004 的 stale 信息，说明上游并非完全没有诊断 |
| E3 | code_path | `src/backend/app/governance/archive_admission.py` 的 change_acceptance 独立 Change 分支 | 返回 ready 与 reason=status，未保留 stale AC；本次文档生成时再次只读核对该代码 |
| E4 | code_path | `src/backend/app/governance/reader.py` 的归档准入卡片投影，前序探索记录见 capture.md | 将同一 reason 用于 acceptance_blocked_reason/action.disabled_reason，与页面表现吻合 |

运行态证据复用本会话前序取证；本次不宣称重新部署或完成修复验收。BUG-0053 解释为何此样本进入 blocked，本条解释为何任何进入该分支的诊断只剩状态词，两者可以独立修复和验证。


## 已排除假设

| 假设 | 排除依据 |
|---|---|
| 上游没有任何诊断信息 | readiness 已返回三个 stale AC，准入分支却仅返回状态词 |
| 仅为前端样式隐藏 | 后端 reason 已是 blocked，卡片投影复用该值，与页面及按钮提示一致 |
| 修好输入读取便不再需要错误原因 | 真实缺证和输入变化仍会触发阻塞，因此诊断投影是独立修复面 |

## 已确认根因

根因状态：confirmed（针对纯 Change 验收计划分支）。归档准入层将包含 stale AC 的 readiness 结果压缩为 `reason=evidence["status"]`，卡片投影继续复用这一字段，诊断信息在到达页面前丢失，因此只有 blocked 而无具体原因。


## 修复方向

覆盖未执行验收、缺失输入、输入变化、未知错误及 ready 状态，从准入投影到真实卡片检查中文摘要、AC 标识、相对路径及处理提示。维持禁用判定，不允许以优化文案替代验收。当前未修改接口或页面，修复效果尚未测量。


## 验证闭环

复用 capture.md、bug.md 的已取得证据完成现象—代码分支—原因对应；逐项修复验收见 acceptance.md，目前均未执行。没有额外人工补证阻塞，其他样本影响面在修复回归时核实。

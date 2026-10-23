---
bug_id: BUG-0063-compatible-requirement-successor-blocked
created_at: '2026-10-22 09:07:15'
updated_at: '2026-10-22 09:07:15'
title: 同条文兼容追加归档阻断临时处置
---

# 同条文兼容追加归档阻断临时处置

## 当前可用处置

没有能够安全绕过本门禁并完成 Sprint 关闭的临时方案。保留当前 SPRINT 会话和草稿，使用只读预检定位具体阻断，等待正式修复及验收。其他不依赖 Sprint 关闭的工作可继续。

`python scripts/validate-sprint-archive-readiness.py --sprint sprint-012 --json`

## 禁止作为绕过方式的操作

不使用 force 降低深层证明，不删除或改写历史 manifest、journal、哈希与执行事实，不移除 Sprint 范围成员，不重放模型或重复合并规格，不把已通过 AC 清零来制造重新验收理由。

## 独立关闭事项

人工 sign-off 和旧 active Change 链接仍需各自完成；本 BUG 修复不能自动签署或关闭 Sprint。旧证据本体保持不可变，当前导航引用通过正常文档收尾纠正。

## 解除条件

本 BUG 完成评审、迭代纳入、OpenSpec 实施及全部适用验收；部署版本一致并复验共享深层预检。其余关闭门禁通过且用户授权归档后，再执行标准 sprint-archive。

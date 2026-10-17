---
bug_id: BUG-0040-chat-archive-issue-promote-fixture
title: Chat 首次归档关联 Issue 迁移验收夹具证据缺口分析
status: confirmed
created_at: '2026-10-12 11:05:30'
updated_at: '2026-10-12 11:05:30'
---

# Chat 首次归档关联 Issue 迁移验收夹具证据缺口分析

## 根因状态

status: confirmed

本文件确认的是 **BUG-0026 验收证据缺口的成因**，不是新产品缺陷根因。该对象是用户授权的虚拟 Issue 夹具。

## 现象

首次产品归档成功样本 `verify-chat-archive-history-transition` 无关联 Issue；BUG-0027 有产品 Issue promote 证据，但属于半归档恢复。两者不能组成同一首次归档轮次的关联 Issue promote 证据。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | reproduction | BUG-0026 `acceptance.md` 首次产品归档记录 | 轮次 `d720688b-5667-43a7-a891-ed26e31197e3` 成功，但样本无关联 Issue | 当前首次归档证据不覆盖 promote |
| E2 | reproduction | BUG-0026 `acceptance-fixes.md` BUG-0027 恢复记录 | 产品轮次完成 Issue promote，但从唯一已归档目录恢复 | 该轮次不证明首次移动与 promote 同轮 |

## 已排除假设

已有纯治理样本不能凭空形成关联 Issue；既有恢复轮次不能重放为首次归档。

## 已确认根因

证据缺口由两个成功样本的前置事实不同造成。需要一个明确关联、状态就绪的全新测试 Issue/Change，在产品同一轮次中首次归档并 promote。

## 修复方向

只建立经授权的低影响测试夹具，按项目治理链路进入 Sprint 和 Change；不新增业务代码或发布能力。

## 验证闭环

以该夹具首次产品归档轮次的工具退出码、目录迁移、Sprint 与 Issue 阶段、产品终态共同判定 BUG-0026 AC-001。

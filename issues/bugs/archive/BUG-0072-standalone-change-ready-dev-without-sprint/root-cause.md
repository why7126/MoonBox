---
title: 独立变更未排期提前待开发根因分析
created_at: '2026-10-31 08:17:50'
updated_at: '2026-10-31 08:17:50'
---
# 独立变更未排期提前待开发根因分析

## 根因状态
status: confirmed

## 现象与确认范围
确认有效proposed独立Change不论Sprint是否成立都进入ready-dev的机制；不确认原提案创建来源，不宣称修复完成。无归属真实案例复用同会话截图和Firefox刷新观察，冲突/失效只做隔离合成验证。

## 证据链
| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | screenshot | 用户本会话卡片截图及capture.md | 原提案待开发并提示缺少唯一有效Sprint | 实际展示矛盾 |
| E2 | reproduction | 同会话Firefox需求中心刷新观察 | 原提案0/10，无Sprint，开始开发禁用 | 状态初始化后仍提前分列 |
| E3 | code_path | src/backend/app/governance/change_index.py:155 | proposed直接映射ready-dev | 分列未检查归属 |
| E4 | code_path | src/backend/app/governance/change_index.py:sprint_id/action | 归属解析返回None时只设置disabled_reason | 仅阻断动作，不提供规划入口 |
| E5 | reproduction | 本轮临时目录调用test_change_visibility.change/cards及test_governance_scope.fixture_tree | none、unique、conflict、invalid四种样本全部ready-dev；仅unique解析sprint-001且动作无阻断，其他三个均提示缺少唯一有效Sprint | 合成对照证实条件分支，非真实HTTP或产品验收 |

## 已排除假设
- trace缺失：真实样本已补齐有效proposed与schema v1。
- 前端未刷新：既有真实刷新观察和当前后端合成投影一致。
- 开发准入已被绕过：无归属动作仍禁用，当前问题是分列及规划引导。

## 已确认根因
阶段投影只使用执行状态；Sprint归属只进入动作禁用条件。独立提案完成被当作开发就绪，缺少未排期与冲突诊断的展示分支。

## 修复方向
保留proposed事实，以归属判定结果派生待纳入、就绪、需核对三类展示；状态、统计、动作共享判定，不自动修复归属。不改归档历史、不放宽执行门禁。

## 验证闭环
修复前四类合成样本已执行；修复后按acceptance.md回归并真实浏览器确认。根因证据门禁仅校验证据结构，不能替代修复验收。

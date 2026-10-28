---
bug_id: BUG-0066-chat-auto-verification-status-stale
title: 自动核验状态未刷新根因分析
created_at: '2026-10-26 18:19:35'
updated_at: '2026-10-26 18:19:35'
root_cause_status: confirmed
---

# 自动核验状态未刷新根因分析

## 根因状态

status: confirmed

## 现象

详见 [正式缺陷说明](bug.md)。

## 证据链

| id | type | source | 摘要 |
|---|---|---|---|
| E1 | screenshot | 用户截图与同会话浏览器观察 | 先显示待核验，后来已核验；不等同于精确请求时间线 |
| E2 | data_sample | bug.md 队列与保护只读统计 | confirmed、attempt_count=1、无错误，保护validated |
| E3 | code_path | DirectCompletion.tsx::useEffect；TurnActivity.tsx::poll | 子组件首次读取，父组件终态停轮询 |
| E4 | reproduction | 本次 Vitest/jsdom 与真实 DirectCompletion 组件 | 首次needs_review，模拟后端validated，推进60000ms；请求仍1次，onState最后仍needs_review；1 passed |
| E5 | code_path | governance/controller.py 与 completion_handoff.py | 存在自动核验队列，不是必须人工批准流程 |

## 已确认根因

DirectCompletion 只在挂载或 read/url 变化时 GET；其后没有定时刷新或自动核验事件订阅。TurnActivity 在执行 completed/failed/stopped 且事件批次不足200时停止轮询，执行结束后的核验变化不重新触发子组件读取。首次查询为 needs_review、随后后端自动成功时，组件保持旧状态直到重新挂载或人工动作。确认该生命周期缺口；历史截图时刻后端是否已成功、用户是否点击过仍不可倒推。

## 已排除假设

每轮必须手动批准：后端自动核验队列已成功。后端永久未成功：该样本保护已validated。不能据此否定其他轮次可能存在真实核验失败。

## 修复方向

把执行终态和核验终态分开，建立有界自动跟进并保留失败人工入口。

## 验证闭环

1. Mock governanceRequest：首次返回 needs_review/version=1/can_verify=true。
2. 渲染真实 DirectCompletion，等待首次读取完成。
3. 将模拟服务端状态设为 validated；使用 Vitest fake timers 推进60000毫秒，保持组件挂载，不点击按钮。
4. 断言请求次数为1、onState最后仍为needs_review。

本次 Vitest 1 passed，20ms断言时间；这是合成组件复现，不是浏览器60秒真实等待或修复验收。临时测试配置加载错误已修正后完成执行，未改产品源码。当前真实页面已成功，不为补证重置业务状态。

## 剩余边界

机制已确认，历史原始时序缺口不伪造；修复后仍需合成回归及真实产品复验。

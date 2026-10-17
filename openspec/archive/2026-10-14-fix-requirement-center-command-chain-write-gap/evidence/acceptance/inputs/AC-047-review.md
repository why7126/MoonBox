---
title: AC-047 停止评审后同会话 Sprint 续接产品复验
created_at: 2026-10-14 08:08:00
updated_at: 2026-10-14 08:08:00
---

# AC-047 停止评审后同会话 Sprint 续接产品复验

## 隔离样本与前置状态

- 在 BUG-0025 专用隔离源、空间和 SQLite 中复用已评审的 `BUG-0998-ac051-review-retest` 原对象 Chat。原评审轮次 `367a7617-3706-43e2-8665-7d4c36c5a82e` 为 completed，候选 applied，评审成果为 approved/review。
- 为复现历史遗留状态，仅在隔离 SQLite 中插入一条测试夹具：同会话旧评审轮次 `ed973be7-0a08-48b7-863f-90581c162e05` 为 stopped；旧候选 `0d276b9f-3aa3-494e-bf84-6ceb8b094689` 为 running，并绑定该停止轮次。该旧轮次是受控构造，不宣称经产品按钮停止。旧候选未附不存在的结果 manifest。
- 隔离 backend 与 chat-worker 均运行更新后的当前代码；本轮仅操作隔离对象与数据，正式项目对象未写入。

## 真实产品轮次

- 从需求中心 BUG-0998 “加入迭代”进入原 Chat，在同一会话通过产品发送 `/sprint-propose --bug BUG-0998-ac051-review-retest --sprint sprint-009`。新轮次 `d5833d7f-d6e3-41fe-8411-d2bfaabcdb97` 经 connecting → running → completed，错误码为空；同轮 `execution.tool` 的 `validate-sprint-selection.py --sprint sprint-009` 命令退出码 0。
- 运行中产品显示评审门禁通过、Sprint 容量门禁独立核对；最终指出 sprint-009 现为 35.8/30 人天，样本最小估算 0.5 人天后达 36.3/30（121%），超过 120% 硬上限，因此未纳入。本次业务阻断属于合法容量门禁，不是旧候选的准备失败。见[执行中画面](AC-047-sprint-turn-running.png)与[终态画面](AC-047-sprint-capacity-gate.png)。
- 新轮次完成后，旧评审轮次仍为 stopped，旧候选仍为 running 且 `turn_id`/`prepared_turn_id` 均指向旧轮次；原已应用评审候选仍为 applied。新轮次没有复用或改写旧候选，会话 `active_turn_id` 已释放。
- 隔离源回读：BUG-0998 的 trace 仍为 `status: approved`、`lifecycle_stage: review`、`iteration: null`；registry 仍指向 review 目录；CHANGELOG 仍为 approved/review 且下一步 `/sprint-propose --bug BUG-0998-ac051-review-retest`；sprint-009/sprint.yaml 未包含该样本。既有评审成果得到保护。

## 验收边界

本轮证明了受控停止态夹具下，原产品会话的新 Sprint 命令可以独立准备、运行并完成，且旧候选和原成果未被覆盖。由于既有 sprint-009 容量已超硬上限，本轮没有执行正式纳入或验证 Sprint 写入成功；容量门禁的拒绝是预期结果。停止态由隔离夹具构造，非本轮通过产品停止按钮产生。未保存聊天原文、原始事件、凭证或数据库文件。

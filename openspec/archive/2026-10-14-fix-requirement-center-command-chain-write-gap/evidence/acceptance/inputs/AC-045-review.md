---
title: AC-045 同会话完善与评审自动应用复验
created_at: 2026-10-14 08:27:00
updated_at: 2026-10-14 08:27:00
---

# AC-045 同会话完善与评审自动应用复验

## 隔离样本与执行链

- 仅在 BUG-0025 专用隔离项目复制已具备文档与原型拆解的 REQ 样本，建立 `REQ-0996-ac045-chain-test` 的 draft/plan 夹具。其内容来自已评审隔离样本，复制状态及索引已改为 draft/plan；正式项目对象未写入。产品从需求中心“完善需求”进入该对象 Chat。
- 同会话首个 `/req-complete` 轮次 `dca1ee5f-110b-400c-ae1a-c1335410f592` completed，但候选 `612076df-2907-57d2-8541-864a070ef95b` 因越界修改只读 capture.md 被后端拒绝（`completion_scope`）；事实源未前进。
- 第二个 `/req-complete` 轮次 `1cb66335-40b6-4e5f-b2b9-cdab298a5947` completed，但候选 `2bd09df2-1fba-515d-8a8c-be65ce6eda90` 因夹具 registry 路径缺末尾 `/` 被拒绝（`completion_registry_scope`）。两个模型完成态均未被当作后端应用成功；拒绝后原文件保持 draft/plan。规范化隔离夹具路径后，在同一会话第三次发送 complete。
- 第三轮 `2c8896dd-8a2d-4871-b95c-3b67f7b8074a` completed；候选 `606b7fca-3bc3-5405-9a7e-2f099c096757` applied，application `8432991c-e7a6-4c7f-b8b3-e5e62706be25` applied/verified、无错误码。源 trace、registry 与索引变为 pending_review/plan。
- 从同一 Chat 发送 `/req-review REQ-0996-ac045-chain-test --approve`，新轮次 `b8feea49-a38f-4663-91dd-25b3b3daaadc` completed，独立当前轮候选 `14556479-5934-53c2-82e0-5b124f70364c` applied，application `7f4243a2-4da7-4c55-8df5-c109eb739da1` applied/verified，均无错误码。同轮 `execution.tool` 的评审状态同步检查命令退出码 0。complete 与 review 候选各绑定自身轮次，没有复用前轮候选。

## 事实源、删除记录与产品回读

- 评审后 `issues/requirements/plan/REQ-0996-ac045-chain-test/` 不存在，`issues/requirements/review/REQ-0996-ac045-chain-test/review.md` 存在；trace、registry 和 CHANGELOG 为 approved/review，索引下一步指向 `/sprint-propose --req REQ-0996-ac045-chain-test`。
- 评审候选持久化结果包含原 plan 目录 8 个文件的删除记录，均有 before 摘要、无 after 摘要；对应新 review 文件存在。无活动轮次时重启专用隔离 backend 和 chat-worker；重启后 8 条删除记录仍可读取，两个 application 仍为 applied/verified，原 plan 目录仍不存在。后端与 worker 服务恢复健康。
- 产品需求中心在评审应用后及服务重启刷新后，REQ-0996 均处“已评审”，提供 `review.md` 与“加入迭代 →”；点击 `review.md` 后右侧抽屉加载批准结论。见[已评审文档截图](AC-045-reviewed-document.png)。
- 冲突与成果保护由 `test_governance_review.py` 的结论冲突、重验冲突、重启 tombstone 用例及 `test_governance_candidates.py` 的工作区冲突保留用例验证；本次 65 项相关聚焦回归及 59 项评审模块完整回归均通过。前两次产品 complete 拒绝也实证了模型完成与 application 成功必须区分。

## 覆盖边界

同会话连续 complete→review、自动回写、目录迁移、删除记录重启持久化、看板与 review.md 入口有新产品证据。评审结论冲突和工作区冲突采用真实文件系统/SQLite 回归，未在产品 UI 对该已批准样本故意构造冲突。无代码修改；不将隔离样本视为正式需求。

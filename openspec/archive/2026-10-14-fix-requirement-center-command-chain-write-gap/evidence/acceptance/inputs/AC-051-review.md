---
title: AC-051 隔离产品评审投影收尾复验
created_at: 2026-10-14 00:18:00
updated_at: 2026-10-14 00:18:00
---

# AC-051 隔离产品评审投影收尾复验

## 样本与门禁

- 专用隔离源、SQLite 和空间中复制已确认根因的待评审 Bug 为 `BUG-0999-ac051-isolated-review` 与修复后新样本 `BUG-0998-ac051-review-retest`；正式 BUG-0037 未执行评审。样本仅存在于隔离源，不进入正式发布。
- 两个样本均从产品需求中心待评审卡片进入对象 Chat。发送 `/bug-review <完整样本 ID> --approve`，并明确让模型完成评审文档和迁移，但不主动编辑目标 registry/CHANGELOG 行，从而检验后端收尾。
- 运行容器仅为 `moonbox-bug0025-backend` 和 `moonbox-bug0025-chat-worker`。第二轮前，两容器的 `review.py` 哈希均为 `b84f51d31fffa3ccaa8c8acc47ca52ce852971dcbc0637ee0f3b58c0808d47b0`，`review_finalization.py` 哈希均为 `896d03d19c009cedb7ff8e2d2f407e99d5e9682ac52c758299af242194d1ade0`；重启后健康。

## 首轮发现

- 2026-10-14 00:04:09 产品轮次 `67825fa2-122c-4204-99ca-9a194f55885a` completed；候选 `691a355d-1958-50c2-9aab-fb85390b559b` applied，应用 `50cb2845-034a-423b-84d1-0bc2731e66d5` applied/verified，无错误码。
- 事实源的评审文档、trace、registry 和目标目录均为 approved/review；但 BUG CHANGELOG 目标行仍为 `plan` 且下一步仍为 `/bug-review`。这与 AC-051 的“索引同步”不符，故首轮判失败。根因是后端收尾只改索引行的状态与路径，完整评审校验也未检查阶段及下一步列。

## 返修后真实产品轮次

- 2026-10-14 00:14:12 从第二个专用卡片发送；轮次 `367a7617-3706-43e2-8665-7d4c36c5a82e` completed、无错误码。同轮 `execution.tool` 含已完成且退出码为 0 的 `/bug-review` 检查命令。
- 候选 `03479b15-636b-54a5-868b-e43353401b49` 为 applied；应用 `b7ab2327-f340-402a-b9b5-c235730fca8f` 为 applied/verified，均无错误码。模型执行后注册表和索引目标行保留旧值；产品后端收尾再应用结果。
- 隔离事实源回读：`issues/bugs/review/BUG-0998-ac051-review-retest/` 有七份 Markdown（含 review.md），旧 plan 目录不存在；trace 与 review 为 approved、root-cause 为 confirmed；registry 为 approved/review 且路径为 review 目录；CHANGELOG 目标行状态 `approved`、阶段 `review`、下一步 `/sprint-propose --bug BUG-0998-ac051-review-retest`、trace 路径为 review 目录。七份标题校验通过。
- 此轮使用 `workspace_mode: source`，会话的 `chat_workspace_baselines` 有最新 `content_hash` 与同值 payload hash，包含 4085 个文件条目，且 active_turn 已释放。copy 模式 Git checkpoint 和恢复由聚焦真实文件系统/SQLite 回归覆盖，不能把本轮 source 模式说成 copy 模式产品观察。

## REQ 产品轮次

- 专用隔离对象 `REQ-0997-ac051-isolated-review` 从看板待评审卡片进入 Chat。2026-10-14 00:19:46 发送 `/req-review`，模型只写评审文档、需求与追溯状态并迁移目录，保留目标 registry 和 CHANGELOG 旧值供后端收尾。
- 轮次 `de46903d-7c0b-43e4-9536-a34f1ff08d9a` completed、无错误码；候选 `64c6581c-ac5b-59b7-868a-dc398531d3be` applied，应用 `4e106901-e357-4656-a9ce-bbe1eecfcb78` applied/verified，均无错误码。
- 隔离事实源回读：review 目录包含八份 Markdown，旧 plan 目录不存在；registry 为 approved/review、路径指向 review；CHANGELOG 目标行为 approved/review、下一步 `/sprint-propose --req REQ-0997-ac051-isolated-review`、trace 路径指向 review。八份中文标题校验通过。会话 `workspace_mode: source`，active_turn 已释放，baseline content_hash 与 payload hash 一致，包含 4094 个文件条目。
- 需求中心重新读取后，REQ-0997 与 BUG-0998 均显示在“已评审”列，均出现 `review.md` 与“加入迭代 →”动作；[REQ 看板截图](AC-051-req-reviewed-board-1440x900.png)及[BUG 看板截图](AC-051-bug-reviewed-board-1440x900.png)已目视核对，该页面观察与 SQLite、文件回读相互印证。

## 回归与范围

- `PYTHONPATH=src/backend src/backend/.venv/bin/python -m pytest -q src/backend/tests/test_governance_review.py`：59 passed，1 条既有 Starlette/httpx 弃用 warning。新增完整 CHANGELOG 行断言覆盖 REQ 与 BUG 的阶段、下一步；原有用例覆盖 approved/rejected/deferred、结论冲突、越权、缺文件、根因未确认、source 原轮次恢复、copy 应用与 checkpoint。
- 本证据不包含原始 prompt、Chat 事件正文、数据库文件或凭证。两条产品轮次分别支持 BUG 与 REQ 评审遗漏投影后的自动补齐；copy checkpoint 及各类异常门禁由聚焦回归覆盖，仍缺 copy 模式独立产品轮次。

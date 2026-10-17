---
title: "治理候选自动应用与冲突恢复复验"
created_at: 2026-10-14 10:03:00
updated_at: 2026-10-14 10:40:00
---

# 治理候选自动应用与冲突恢复复验

结论：通过本项现行口径。异常时仅用轻量错误或轨迹提示，不恢复“待应用成果”面板。

正常路径：共享产品既有 REQ-0045 真实 turn `4770287b-fbbb-4b3d-ba66-29b39550c89a` completed，candidate `8291d21e-acf7-5d4f-941c-7c9ee40ce5ad` applied，application `cabd516b-16a3-485c-9c6a-a6615b3aba09` applied/verified，requirement.md、trace、注册表及 CHANGELOG 均为 draft。隔离 BUG-1001 的 turn `6a66a033-9e73-425b-9458-0f36f8318091`、candidate `6de047fa-0eb6-5278-8669-b41c7e5fd51c` 和 application `7695e2fd-c475-4ecd-adbe-f0fd8525b737` 同样达到 completed、applied、applied/verified；四份事实源均为 draft。

异常产品轮次：专用隔离 BUG-1002 在候选 `992f10ab-b92c-501f-8b2a-ac0d6b247b2c` prepared 后，仅对该夹具 capture.md 增加版本探针。产品发送 `/bug-generate BUG-1002-ac-015` 显示“项目文件已变化，请重新准备治理动作”的轻量 alert；1440×900 DOM 中治理成果面板数量为 0。该候选保持 prepared、没有 turn、没有 application，bug.md 未生成。截图：[版本冲突](AC-015-revision-conflict-1440x900.png)。

恢复产品轮次：从同一卡片重新准备候选 `005d0174-3cae-5245-abb2-ce4a9d391e73`，新 baseline 与旧 baseline 不同；turn `d2ab9252-bbf1-4597-a589-9e0b5900ccdb` completed，application `5d73ebed-ed3c-4711-a0fc-3a45ea3349d9` 为 applied/verified。bug.md、trace、注册表和 CHANGELOG 回读均为 draft，产品看板在规划中展示 bug.md 和“完善 Bug”。截图：[恢复后看板](AC-015-recovery-board-1440x900.png)。旧候选没有被复用或应用。

合成门禁：候选、写入器和不支持命令后端回归 63/63 通过，覆盖写集合 allowlist、manifest/revision、dry-run/冲突、幂等、同步失败、外部变更与锁竞争。产品轮次直接覆盖版本冲突及恢复；其他异常机制以受控回归验证，未将其写成逐分支真实产品轮次。隔离测试管理员原密码哈希已恢复。

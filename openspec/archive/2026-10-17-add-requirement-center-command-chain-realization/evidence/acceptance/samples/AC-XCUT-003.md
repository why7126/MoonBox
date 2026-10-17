---
title: AC-XCUT-003 归档治理与事实源回溯复验
created_at: 2026-10-13 20:05:00
updated_at: 2026-10-17 15:40:00
status: passed
---

# AC-XCUT-003 归档治理与事实源回溯复验

隔离项目：`moonbox-validation`，产品 API `127.0.0.1:39028`；仅核验隔离对象，不把其状态写回主产品 REQ-0027。以下分别引用真实产品轮次与合成回归，避免混称。

| 场景 | 真实产品证据 | 文件事实 |
|---|---|---|
| 缺验收时拒绝归档 | `REQ-9114-archive-multi-change` 的轮次 `7a1192dc-dfc2-4661-92e4-0aac96b38425`；归档 readiness 返回 blocked，Change 保持 applied，REQ 保持 in_sprint | [AC-008 逐项记录](AC-008.md)记载前后治理树一致 |
| 满足门禁后归档 | 同对象第二个 Change 的轮次 `6cc626c6-8a23-4f83-ab37-7fca627c4b4d` 为 completed；两个 Change 唯一归档、增量规格生效、Issue done | [AC-008 逐项记录](AC-008.md)与[重启后只读投影矩阵](AC-013-projection-matrix-readonly.json)核对注册表、CHANGELOG、trace、Sprint 与 Change |
| 界面入口和阶段反馈 | `REQ-9314-ac014-observability` 在归档前卡片显示“验收中”、研发 2/2、验收 1/1；首轮 `9d22dea8-4c95-4a96-b462-f7ab3596317b` 因交付证据门禁停下，补证后从同一界面发起的 `afa916b4-0011-44c0-8f67-3ad8e14d7326` 为 completed | [AC-014 观测记录](AC-014.md)及[脱敏矩阵](AC-014-observability-matrix.json)保留 Web 事件、服务端请求、轮次和节点关联；隔离注册表与 CHANGELOG 的完整 ID、标题、done、archive 和归档路径一致 |
| 文档入口与标题 | `REQ-9114` 归档后产品 context GET 显示唯一 done 卡片；完整 ID 的 `requirement.md` GET 为 200/0，内容非空且版本可读 | [AC-008 逐项记录](AC-008.md)与[重启后投影矩阵](AC-013-projection-matrix-readonly.json)核对文档 API 字节等于归档文件、卡片与索引一致 |

合成命令回归另见 AC-008 的 74 项测试、AC-013 的投影检查和 AC-014 的直接 API 负向对照；它们不充当上述真实轮次。2026-10-17 对隔离项目已归档的 `REQ-9314` 再次只读检查：`trace.status=done`、`lifecycle_stage=archive`，注册表及 CHANGELOG 标题与路径一致，唯一关联 Change 存在于规范归档目录。归档入口沿用同一后端证据和状态门禁；标题、进度及文档可从卡片回溯到治理事实源。

结论：**passed**。

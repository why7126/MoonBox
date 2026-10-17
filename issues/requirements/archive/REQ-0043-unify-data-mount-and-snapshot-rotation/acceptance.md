---
requirement_id: REQ-0043-unify-data-mount-and-snapshot-rotation
title: 统一 data 目录边界与本地数据挂载及快照轮转验收清单
acceptance_status: passed
created_at: '2026-10-08 14:19:59'
updated_at: 2026-10-17 17:01:21
owner: product
---

# 统一 data 目录边界与本地数据挂载及快照轮转验收清单

## 业务库与迁移

- [x] AC-001 根 Compose、本地 Compose、Chat/Governance overlay 和辅助脚本在本地 SQLite 模式下解析为同一宿主机 `data/sqlite/moonbox.db`；记录各入口的实际挂载结果。
- [x] AC-002 本地正常启动、重启和 Chat 执行后，`data/runtime/backend/sqlite/` 不再新建业务库；业务数据在目标库持续可读写。
- [x] AC-003 生产 MySQL 配置缺失或误用 SQLite 时仍按既有门禁启动失败，不能静默回退。
- [x] AC-004 迁移前停服并分别保全新旧业务库，提供库存、磁盘占用、`PRAGMA integrity_check`、schema 版本和关键表行数对比摘要。
- [x] AC-005 新旧库内容不同或完整性不通过时，自动切换停止且不覆盖任一原文件；差异报告列出待人工确认项和回滚入口。
- [x] AC-006 确认来源后完成挂载切换，API、Chat Worker、关键数据与重启回归通过；失败可按记录的步骤回滚。

## 快照配置与轮转

- [x] AC-007 未设置 `MOONBOX_CHAT_LOCAL_SNAPSHOT_LIMIT` 时默认值为 `2`；设置正整数 `N` 时，启动和周期轮转后的未受保护自动快照不超过 `N` 份。
- [x] AC-008 设置 `0` 后，控制器启动及后续周期均不创建自动快照；既有快照、手动备份入口和独立删除日志仍保留且可用。
- [x] AC-009 空字符串、负数、小数和非数字配置均产生明确配置错误，不静默取默认值；API/Worker 配置不一致可被就绪检查识别。
- [x] AC-010 新快照通过 SQLite 完整性、摘要和账本登记验证后才清理旧副本；验证失败时旧有效恢复点与账本不受损。
- [x] AC-011 自动轮转仅通过受控备份接口清理已登记的超额自动副本；手动副本和被治理成套备份引用的副本不被自动清理，并记录受保护例外。
- [x] AC-012 对备份创建、轮转中断、过期失败及磁盘不足进行故障注入，库存与账本保持一致，错误摘要可定位且不含敏感数据。
- [x] AC-013 历史快照清理前具备库存、摘要、引用与删除状态清单；迁移前恢复点被保全，清理后记录数量、占用和每次受控过期结果。

## 删除恢复与治理边界

- [x] AC-014 配置为 `0` 或自动轮转时，独立删除日志不被删除或回滚；从旧快照离线恢复会重放删除意图，已删除会话不复活。
- [x] AC-015 治理成套备份仍可通过其 manifest 找到所引用快照并完成离线恢复校验；受保护副本不计入未受保护自动快照上限。
- [x] AC-016 Chat 执行器状态、治理状态、备份和本地业务库仍按用途隔离；目录权限、Git ignore 和真实数据提交边界验证通过。
- [x] AC-017 `.env.example`、本地部署示例、数据目录说明、数据库设计、部署和回滚文档与实际配置、挂载及 `0` 的语义一致。
- [x] AC-018 快照创建、跳过、轮转及迁移的脱敏运维摘要可关联对应后台任务；验证 DB、Task Trace 与 span 的适用范围，不写入业务正文、凭据、完整连接串或本机绝对路径。
- [x] AC-019 若本次未新增 API、Web 行为入口或请求封装，Change 验收材料分别记录具体 N/A 原因；若设计新增这些入口，则补齐对应观测与文档验证。

## 横切 AC（knowledge-base）

无 UI 横切 AC。本需求没有管理端列表、表单、弹窗或媒体上传，也不包含产品页面原型；知识库的 UI 模式标签均不适用。Sprint-007 复盘关于 SQLite/MySQL、部署和文档证据分层的经验已体现在 AC-003、AC-006、AC-017 至 AC-019。

## 本次实施证据对照

| 验收项 | 证据层级与结论 |
|---|---|
| AC-001、AC-016、AC-017 | Compose 解析、真实 backend/chat-worker/governance-controller 挂载、目录权限与 Git ignore；通过。 |
| AC-002 | API/Worker 真实启动与重启、canonical 库可读；隔离测试库中的一条真实 Chat 消息完成且额度结算，测试仓库未变化。测试后 canonical 库完整、legacy 未再出现；通过。 |
| AC-003 至 AC-006 | 生产 MySQL 门禁及双库同/异内容、损坏、显式选源、保全、回滚由合成回归验证；本机 legacy 库不存在，无真实旧库切换。真实 API/Worker 重启通过。 |
| AC-007 至 AC-013 | 默认 2 份经真实 Worker 连续启动与重启观察到 1→2→2、过期旧副本且摘要有效；正整数、0、非法值、保护引用、来源不明、故障注入及周期调用由合成回归验证。约 24 小时自然周期未等待。 |
| AC-014、AC-015 | 合成回归验证独立删除日志与治理成套备份恢复；真实最新自动快照离线恢复完整性通过，本机无待重放删除意图。 |
| AC-018、AC-019 | 真实库有 3 条 local_snapshot Task Trace，started/rotated span 各 3 条；离线迁移用不透明 manifest 记录阶段。无新增 HTTP API、Web 行为、请求封装，故 OpenAPI、Orval、UI、request_logs、usage_events 不适用。 |

详细命令与限制见 `openspec/archive/2026-10-08-add-local-data-mount-and-snapshot-rotation/trace.md`。以上勾选表示实施验证证据已具备，不替代最终人工 sign-off。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-17 17:01:21
accepted_by: workflow-sync
source_change: add-local-data-mount-and-snapshot-rotation
source_sprint: sprint-009
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

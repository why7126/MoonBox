---
title: Chat 大规模工作区持续执行方案
created_at: 2026-10-25 22:27:00
updated_at: 2026-10-25 22:27:00
---

# Chat 大规模工作区持续执行方案

## 背景
大规模工作区在模型启动前被固定文件数／字节门槛拒绝，长结果受单轮内存聚合与预留量限制。来源 REQ-0053-chat-scalable-execution-storage，已评审并纳入 sprint-013；本次只生成设计，不实施业务代码。

## 变更内容
- 用户／空间月度 Token 和累计 Chat 存储缺省不限额，保留显式有限运营配置；取消单轮 Token 平台预算。
- 以分批索引、可验证增量快照、分块持久化和游标读取替换固定总量门槛。
- 保留部署级解析、队列、容器保护；准确呈现保存范围、资源原因与原轮次恢复。
- 增加版本化迁移、删除引用保护、可信计量及完整验收矩阵。

## 能力影响
### 新增能力
- chat-scalable-storage：可信快照、结果分块、迁移、按需读取与资源有界处理。
### 修改能力
- codex-session-execution：平台额度与结果空间、事件持久化与可信差异。
- web-catalog-chat-workbench：额度与容量反馈，追加持续保存与安全恢复展示。

## 影响范围
后端 chat/settings、admission、accounting、workspace、execution、worker、schema、service、api、cleanup 与备份集成；Web ExecutionPanel、消息／轨迹／Diff 阅读。同步 SQLite/MySQL、OpenAPI/Orval、API/DB/部署/安全/产品手册与测试。对象正文采用现有业务数据库分块，本期不新接对象存储；后台配额页面及其他客户端不纳入。
沿用既有13人天估算，不重复增加 Sprint 容量；Sprint 当前31/30人天的风险仍保留。


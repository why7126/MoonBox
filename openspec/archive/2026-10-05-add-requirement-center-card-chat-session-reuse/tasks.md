---
title: 需求中心卡片动作复用对象 Chat 会话任务清单
change_id: add-requirement-center-card-chat-session-reuse
source_requirement: REQ-0039-requirement-center-card-chat-session-reuse
created_at: 2026-09-30 08:37:58
updated_at: 2026-09-30 09:16:52
owner: MoonBox 产品团队
---

# 需求中心卡片动作复用对象 Chat 会话任务清单

## 1. 数据与接口契约

- [x] 1.1 梳理需求中心卡片动作触发 Chat 的现有前后端入口，确认对象类型、对象 ID、标题、阶段、动作类型和幂等键的传递边界。
- [x] 1.2 设计或扩展对象会话关联、turn、candidate、幂等记录和历史 candidate 引用的数据结构。
- [x] 1.3 如修改 REST API、错误码、请求头或响应字段，同步 OpenAPI、Orval 生成物和 `docs/03-api-index.md`。
- [x] 1.4 如新增或修改表、字段、索引或迁移，同步 SQLite/MySQL schema、迁移脚本、`docs/04-database-design.md` 和数据库测试。（未新增表字段或迁移，复用既有 `chat_relations` / `chat_turns` / `governance_candidates`。）

## 2. 后端会话选择与 candidate 生成

- [x] 2.1 实现按对象类型和对象 ID 查询未归档、未删除且当前用户有权访问的对象会话。
- [x] 2.2 实现最新会话排序降级：最近 turn 更新时间、最近消息更新时间、会话 `updated_at`、稳定创建事实。
- [x] 2.3 实现无可用会话时的新建对象会话逻辑，并写入来源、对象关联和触发动作摘要。
- [x] 2.4 实现生成类治理动作在目标对象会话中创建新 turn 和新 candidate，不默认复用旧 candidate。
- [x] 2.5 实现重复点击和网络重试幂等处理，返回同一轮结果或明确重复提交提示。
- [x] 2.6 覆盖对象不存在、对象无权、会话无权、会话已归档、会话已删除、candidate 创建失败和服务端异常的受控错误。

## 3. Web 交互与展示

- [x] 3.1 扩展需求中心卡片动作调用链，传递对象上下文、动作类型和幂等标识。
- [x] 3.2 在 Chat 顶部或上下文区展示当前对象类型、对象 ID、标题和最近动作摘要。
- [x] 3.3 区分本轮 candidate 与历史 candidate，禁止把历史 candidate 展示为本轮可提交结果。
- [x] 3.4 为动作执行中按钮提供 loading 和禁用态，失败时不移动卡片阶段。
- [x] 3.5 验证长标题、长对象 ID 和长 candidate 摘要在卡片、抽屉与 Chat 区域中不溢出。

## 4. 观测与安全

- [x] 4.1 为卡片动作触发、复用会话、新建会话、新建 turn、新建 candidate、重复提交拦截和失败分支记录脱敏 usage_events 摘要。
- [x] 4.2 为相关 API 写入 request_logs，保留服务端可信 request_id、路由、状态码、耗时、操作者和脱敏错误码。
- [x] 4.3 为生成类治理动作写入 task_traces 或等价链路节点，区分会话查找、新建会话、追加 turn、创建 candidate 和返回结果。
- [x] 4.4 校验观测 metadata 不保存完整 Prompt、完整回复、完整 candidate 正文、对象正文、密钥、Cookie、Authorization header、本机绝对路径或真实客户敏感数据。

## 5. 验证与文档同步

- [x] 5.1 增加后端测试覆盖会话复用过滤、多会话最新选择、新建会话、生成类动作新建 candidate、幂等和权限异常。
- [x] 5.2 增加前端测试覆盖卡片动作传参、按钮锁定、candidate 区分、失败不流转和文本溢出。
- [x] 5.3 增加或更新观测测试，覆盖 usage_events、request_logs 和 task_traces 的脱敏摘要。
- [x] 5.4 运行 OpenSpec、后端、前端和文档相关校验，并把验证结果回填到 Change trace。
- [x] 5.5 如实现改变 REQ 描述、验收口径或 Mock/API 边界，同步 linked REQ 的 `requirement.md`、`acceptance.md` 和 `trace.md`。（本次未改变 REQ 验收口径；API 边界已同步 `docs/03-api-index.md`、OpenAPI 与 Orval。）

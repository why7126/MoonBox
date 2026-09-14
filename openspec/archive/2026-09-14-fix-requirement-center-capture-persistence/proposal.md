---
change_id: fix-requirement-center-capture-persistence
bug_id: BUG-0014-requirement-center-capture-not-persisted
created_at: 2026-09-12 16:38:11
updated_at: 2026-09-12 16:38:11
---

## 修复背景

[BUG-0014](../../../issues/bugs/review/BUG-0014-requirement-center-capture-not-persisted/bug.md) 已确认新建 Capture 只插入前端临时卡片，未持久化文档与索引，描述也被丢弃。缺陷已评审并纳入 sprint-005，需让成功反馈对应真实创建结果。

## 变更内容

- 服务端在授权项目内创建 REQ/BUG Capture，分配完整唯一编号并保存目录、capture、trace、注册表与当前态索引。
- 复用受控写入的锁、幂等及恢复机制，保证部分失败不产生假成功或覆盖既有数据。
- 前端提交全部有效字段，等待服务端最终成功后插入卡片，错误保留输入，重新加载仍可读取。
- 添加两类创建、并发、重试、故障恢复、权限和刷新回归，并同步 API、客户端与观测契约。

## 能力范围

### 新增能力

无。

### 修改能力

- `web-catalog-requirement-center`：明确 Capture 创建成功以服务端持久化为前提，补充失败保留、编号和刷新语义；保留导入选择行为。

## 影响范围

影响需求中心页面、API与schema、项目授权和受控文件写通道、接口/前端测试及OpenAPI客户端生成。复用已有治理操作记录；不新增业务数据表、不修改正式生效spec、不自动提交推送或部署。若实现核验发现现有写通道不能覆盖创建，先同步本设计和数据库/部署影响再开发。

## 回滚计划

停止接收新的 Capture 创建操作，先让进行中的操作完成或按恢复日志收敛，再回退应用版本；保留已成功创建的REQ/BUG与注册表，不删除用户条目。不得回退到“临时卡片也提示成功”的旧入口，可临时禁用网页创建并提示使用项目治理capture命令。恢复失败时隔离目标项目写入并按受控日志人工核验，禁止覆盖较新的文件。

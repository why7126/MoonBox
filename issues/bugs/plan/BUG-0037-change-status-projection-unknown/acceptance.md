---
bug_id: BUG-0037-change-status-projection-unknown
title: 需求看板端口迁移 Change 状态异常验收标准
created_at: '2026-10-11 10:12:03'
updated_at: 2026-10-11 10:12:48
acceptance_status: not_started
---

# 需求看板端口迁移 Change 状态异常验收标准

## 验收场景

- [ ] AC-001：活动 Change 缺 `status` 与 `execution` 时，治理上下文返回可测试的“生命周期事实缺失”原因，不混同于归档身份冲突或非法 schema。
- [ ] AC-002：授权用户在需求看板可见异常对象的 ID、业务标题、可证实的 Sprint 归属、任务进度和具体原因，并能打开正确来源的只读治理文档；正常阶段统计与待核实数量分别表达。
- [ ] AC-003：缺完成事实时，任务 4/4、Sprint 摘要 `applied` 或文件存在均不能使 Change 自动进入验收中或已完成，也不能解锁归档动作。
- [ ] AC-004：非法执行 schema、活动与归档同 ID、无 Sprint 归属分别显示正确诊断；异常原因可追溯，不暴露本机路径、文档正文、凭证或无权对象身份。
- [ ] AC-005：产品受控恢复流程在可信执行事实、权限、版本和幂等校验通过后写入合法生命周期状态；缺证据、版本冲突和重复提交保持安全阻断并给出可理解反馈。
- [ ] AC-006：新建 Change、执行启动、首次 apply、验收返修、归档各事件持续写入可识别的生命周期事实；返修不覆盖首次 apply 完成时间或将已完成执行误写为普通 `in_progress`。
- [ ] AC-007：旧记录恢复状态后，同一对象从异常区进入正确阶段，卡片、统计、文档入口及 Sprint 关联一致；刷新后保持一致，不制造第二个 Change 身份。
- [ ] AC-008：后端聚焦测试与浏览器真实观察同时覆盖目标样本、正常独立 Change、REQ/BUG 来源 Change、异常记录和无权读取场景；明确区分合成回归与真实产品证据。
- [ ] AC-009：若修改治理上下文 API 字段，同步 OpenAPI、客户端生成、API 索引与数据采集观测声明；请求日志只存安全诊断摘要和服务端 request_id，不记录治理文档正文或凭证。
- [ ] AC-010：在目标运行环境核对治理根目录、目标 trace 和上下文响应是同一快照；若不一致，诊断明确显示数据源版本差异，修复验收不得仅凭当前仓库的合成投影通过。

## 验收证据要求

记录目标环境、浏览器和路由、触发动作、脱敏的上下文响应原因码与 request_id、修复前后页面截图、相关状态事实摘要及聚焦测试结果。真实页面与当前仓库样本分别标注来源；不保存 Token、Cookie、完整文档正文、本机绝对路径或客户数据。

## 验收结果回填

```yaml
acceptance_status: not_started
accepted_at: null
accepted_by: null
source_change: null
source_sprint: null
evidence: []
failed_items: []
source_event: bug.complete
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

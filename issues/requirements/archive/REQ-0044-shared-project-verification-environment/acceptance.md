---
requirement_id: REQ-0044-shared-project-verification-environment
title: 平台提供跨空间项目验证环境验收标准
acceptance_status: passed
created_at: '2026-10-08 22:43:10'
updated_at: 2026-10-17 17:01:21
owner: 产品团队
---

# 平台提供跨空间项目验证环境验收标准

## 验收矩阵

- [x] AC-001：项目声明与锁文件、包管理器及版本一致时预检返回 ready；缺失或冲突时返回可行动的 preparable/unavailable 与稳定错误类别。
- [x] AC-002：相同环境身份复用已校验只读制品；锁文件、Node、Playwright、OS 或架构变化后不复用旧制品，Darwin 依赖不进入 Linux ARM64 任务。
- [x] AC-003：Firefox 和 Chromium 的可执行文件、系统库及实际启动均在预检中确认；无网且制品缺失时任务保持未验收，不尝试无限网络安装。
- [x] AC-004：两个空间、两个项目和同仓库双空间绑定可并发验证；可写目录、凭证、会话、截图和结果互不串用，授权外访问被拒绝。
- [x] AC-005：验证任务覆盖排队、准备、运行、完成、失败、取消和超时；重复请求、任务重启及制品清理不产生跨项目复用或丢失活跃引用。
- [x] AC-006：真实浏览器分别在 1440px 和窄屏执行用例，结果关联浏览器/版本、视口、截图、断言、computed style 摘要及项目任务身份。
- [x] AC-007：BUG-0030 的刷新重进、对话/轨迹切换、部分内容和未知提示完成真实浏览器验收；另一个独立 Web 项目使用同能力运行并留证。
- [x] AC-008：合成 DOM、后端/API 集成与真实浏览器结果分项呈现；缺真实浏览器证据时 Change 不自动进入已验收。
- [x] AC-009：任务命令、路径、网络及资源边界经过拒绝测试；运行任务不能访问其他空间工作区、宿主 Docker socket或真实认证文件。
- [x] AC-010：请求日志与 Task Trace 仅保留脱敏标识、版本、耗时、计数和错误码；截图访问受权限与保留期控制，日志和公共文档不含页面正文或敏感路径。
- [x] AC-011：受控制品更新、旧版本回退、磁盘容量不足和缓存失效均可演练；部署矩阵、环境示例、运维与恢复文档同步。

## 知识库横切检查

本期无管理端列表、表单、弹窗或媒体上传，也无 prototype；上述 UI 横切标签不适用。承接 sprint-007 复盘中的证据分层经验：合成、API 和真实浏览器结果独立记录，不能仅汇总测试数。

## 产品数据采集与链路观测

product_data_collection_observability：applicable。affected_layers：API、request_logs、task_traces、task_trace_spans；若未来新增 Web 操作入口，则追加 usage_events 和客户端请求封装。validation：跨空间请求与任务标识不串联，预检及运行失败只保存脱敏类别；截图另按权限访问与保留期验证。首期不新增行为入口，usage_events 为 N/A；对象存储和 DB 结构是否变化由 Change 设计决定，验收时记录实际影响。

## 验收结论

AC-001 至 AC-011 已依据 Change `verification.md` 的分层证据复核：真实依赖制品准备与身份复用、双空间同仓库及独立 Web 项目任务、Firefox/Chromium 双视口与并发执行、授权拒绝、生命周期与脱敏、一次性 MySQL 迁移，以及本地镜像身份切换与回退检查均通过。BUG-0030 使用合成 API 的真实浏览器场景和现存登录会话只读观察分别取证；已删除的原故障轮次无法复验。生产部署、长期压力和生产回滚不属于本次隔离验收结果，部署时仍需单独验证。证据源：`openspec/archive/2026-10-09-add-shared-project-verification-environment/verification.md`。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-17 17:01:21
accepted_by: workflow-sync
source_change: add-shared-project-verification-environment
source_sprint: sprint-009
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

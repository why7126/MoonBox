---
title: 对象级归档查询与诊断展示追溯
change: add-object-archive-diagnostics
status: applied
sprint: sprint-016
iteration: sprint-016
created_at: 2026-10-30 09:40:00
updated_at: 2026-10-30 10:34:56
execution:
  schema_version: 1
  started_at: 2026-10-30 09:44:35
  completed_at: 2026-10-30 10:34:56
  last_event: opsx.apply
---

# 对象级归档查询与诊断展示追溯

## 来源与边界

来源为本会话对象级归档查询与诊断展示探索及用户明确提案请求；直接 Change，不虚构 REQ/BUG 来源。依赖 fix-archive-finalization-consistency 的共享收尾检查器。提案阶段只创建实施材料；随后用户明确授权四批实施与隔离验收，未授权正式 Change/Sprint 归档。

## 根因证据入口

- archive_finalization.py 生成检查报告后仅抛出错误码；archive_diagnostics.py 与 replacement_cli.py 尚缺专属映射。
- chat/api.py 公共错误过滤及 Web 请求封装未贯通原操作身份与结构化诊断。
- Composer 发送失败处理不能证明发送成功后的 Agent 归档失败已展示；工具事件不作为授权事实。
- replacement_schema.py 已保存操作身份、阶段、版本和绑定；archive_dispatch.py 已有对象解析规则，优先复用且不新增持久字段。

以上保留为提案时的代码定位；本次修复及真实隔离产品证据见 acceptance.md。

## 状态与后续

已纳入 sprint-016；现已完成四批实现，最终自动验收 8/8 通过。新增估算 5 人天，Sprint 合计 22/30 人天，缓冲 8 人天（26.67%）。前置检查器已有实现及自动验收证据，真实产品闭环单独验收。保留历史证据与部分交付策略；原操作恢复沿用当前有效权限和身份边界，不恢复已退出的独立签名或额外确认流程。

product_data_collection_observability: applicable；affected_layers: API、Web、请求封装、归档治理；reason: 新查询与诊断展示经过公开接口及现有审计链路；validation: 公开字段过滤、权限与原操作边界已回归；真实隔离请求头与 chat_request_logs 一次关联已核对。


## 实施与入口证据

| 入口 | 事实源与范围 | 实测与证据 |
|---|---|---|
| 在线 CLI | 真实部署 archive-commands，独立 Change | evidence/live-cli-first.json；首次执行与重放分别验证 |
| 产品恢复 | 真实登录会话、主对象查询、显式确认 | evidence/ui/product-recovery.json；同一 operation_id 到 completed |
| 查询与拒绝 | 原记录、当前文档与权限 | evidence/live-final-samples.json、live-recovery-and-denials.json |
| 移动后恢复 | 初始隔离部署缺少 titles 模块；真实 move_verified 中断 | evidence/live-matrix.json；会话中读取检查点，补齐环境后原操作完成 |
| 同步后阻断 | 独立样本的缺失导航目标；真实 synced | evidence/live-final-samples.json；补充目标后从产品侧栏恢复 |
| 正式对象 | 不执行写操作 | Sprint014/015 及正式历史归档未作为测试写入目标 |

隔离镜像使用项目标准 replacement Dockerfile、真实 OpenSpec 1.3.1 与 Node22.22；镜像版本 32a0fe49c918。未使用假归档驱动或绕过权限门禁。后端模块与镜像对应；Web 使用当前 Vite 实现。无模型轮次调用，因此不伪造 product_turn。首次工具缺模块及两种未触及目标检查点的只读文件实验均未作为通过证据；移动后恢复以实际 move_verified 检查点为准。

骨架确认：用户明确要求“改放到执行详情侧栏”。初次真实截图发现旧容器实际为中间轨迹视图，已纠正为右侧栏并重采 1440px/390px 证据。合成 API 截图保留为早期布局回归，product-* 为真实页面。浏览器使用 Playwright 后备入口，以获得固定视口与 computed style；不借用生产凭证。

## 本次完成证据

自动验收完整通过，入口 evidence/acceptance/20261030103534694575-eaf7eb8a/summary.md。归档临时副本预演通过；最终共享准入在验收同步后复核。保留已有历史，不改变部分交付状态策略。

临时环境收尾：登记运行 7c4b4e807955438dbed4c4289ce19c1d 已 cleanup/check，容器与专属网络均为 0；两个临时 Web 服务已停止，生成的账号凭证与运行数据库已从临时样本目录清理。用量 hook 为 actual、warning_count=0。

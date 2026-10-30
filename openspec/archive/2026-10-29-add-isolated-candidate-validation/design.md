---
title: 固定候选隔离验收设计
created_at: '2026-10-29 10:40:00'
updated_at: '2026-10-29 10:40:00'
---

# 固定候选隔离验收设计

## 背景与现状

已有 verification 具备受控浏览器执行与证据协议；新增供应器补齐候选绑定、独立数据库和应用生命周期，作为 moonbox-exec-server 端口的正式实现。

## 设计方案

服务端部署配置批准 moonbox-web-python-v1 模板，含不可变 Python/浏览器/MySQL 镜像、linux/arm64、依赖锁摘要、项目入口和验收计划摘要。仅受信部署配置能指定迁移、种子、测试命令；请求端仅传候选 ID。候选 Git 提交固定后导出普通文件到受控暂存，拒绝链接、凭据、嵌套工具目录和路径越界，不挂载原工作树或 .git。逐库独立执行 SQLite 与 MySQL 8.4；网络为 internal、数据库无宿主端口、无生产连接。应用与测试只持有该库临时账号，无 Docker socket、宿主凭据和公网。

持久环境行先于创建副作用，保存候选/模板/计划/版本/阶段/租约/归属及清理状态。每候选独占文件锁与持久记录；服务端全局容量两个、空间一个，未知现场先清理并记录 interrupted，不重跑未知检查。确认合入只消费 passed 且清理已确认的证据。证据摘要绑定精确提交、计划、依赖锁与环境镜像，不读取项目文件中的自报通过。

阶段：reserved → provisioning → database_ready → checking → cleaning → passed/failed/blocked。所有外部命令有限超时，总期限不滚动延长；失败保留可读原因和已取得证据。恢复先检查受管资源精确标签；仅清理本环境资源。

应用健康与版本检查、受控迁移、种子、适用测试及既有浏览器执行器结果分别记录；任一必需项失败不能形成 passed。不开放任意项目自动识别模板；不满足批准模板的项目明确不可用。

## 数据与 API

新增 verification_candidate_environments 双库表，环境记录不存密码。复用候选验证 API，响应继续仅公开状态、稳定原因、证据摘要及环境键；不暴露宿主路径、连接串和容器日志。OpenAPI/Orval 无新请求参数，需回归既有候选响应。

product_data_collection_observability：status=applicable；affected_layers=api,db,agent_workflow,task_traces；reason=供应动作和证据必须关联候选；validation=验证成功/失败、清理未知、观测失效不代替业务记录；Web 行为复用原候选验证操作，后台不伪造点击。

## 原型承接与冲突处理

已读取 REQ-0048 prototype/web/prototype.html 与 context.md；原型是全量 Chat 自主验收的结构输入。本次用户明确仅推进三个工作区需求的必要依赖，使用 REQ-0055 工作区详情展示供应结果，不新增 Chat 原型中的继续/停止入口。全量原型 AC 保留未完成，不借本次交付宣称整条 REQ-0048 完成。

## UI Contract

沿用 REQ-0055 的 WorkspacePanel 组件、14px 字号、6px 圆角、880px 最大宽度及深浅主题。候选结果仅来自真实 API；验证按钮、阻塞原因、确认按钮权限与证据按服务端投影。selector、动作族与样式证据复用该 Change 的契约，补齐真实供应通过/失败状态截图。

## UI Skeleton

复用已实现的工作区详情 → 候选列表 → 验证结果 → 确认合入浮层。供应阶段本期不新建门户；1440px 与390px复核错误长文案与键盘关闭。

## 风险与回滚

Sprint 015 34/30 人天为容量 warning，保留其余 REQ-0048 范围。关闭批准模板即关闭新开发树/候选供应，不删除工作区或恢复点。表为增量迁移；不自动回退 Git。镜像不可用、版本不符、空间不足或清理失败均保持阻断。


## 子交付签认范围

本计划声明 `issue_acceptance_scope: partial`。Change 自身所有 AC 通过可取得 ready，但 Workflow Sync 将 REQ-0048 的整体验收显示为 partial，保留未交付的完整 Chat 编排与原型 AC，不将单一依赖子交付误签为整条需求完成。省略此字段的既有完整交付语义不变。

## 最终组件与交付落位

工作区界面使用 src/web/src/components/workspaces/WorkspacePanel.tsx，浮层统一采用既有 ChatDialog。旧表中 drawer/confirm/dialog 是交互用途，落地为同一可滚动浮层族；选择器为 workspace-create-dialog、workspace-diff-dialog、workspace-restore-dialog、workspace-protect-dialog、workspace-recover-directory-dialog、workspace-confirm-dialog、workspace-repair-dialog、workspace-merge-status-dialog。原生select保留键盘和系统选择行为，不新造门户。已验证实际组件与原型业务矩阵一致，截图与样式、样本边界见implementation-verification.md。

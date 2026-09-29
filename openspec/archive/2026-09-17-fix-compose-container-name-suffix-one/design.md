---
created_at: 2026-09-15 00:18:00
updated_at: 2026-09-15 00:18:00
owner: MoonBox 产品团队
source_bug: BUG-0017-compose-container-name-suffix-one
---

# 设计说明

## 根因摘要

`chat-worker`、`governance-controller` 和 `chat-recovery` 所在 Compose 文件未声明 `container_name`。在项目名为 `moonbox` 的 Compose 环境中，Docker Compose 按默认规则生成 `moonbox-chat-worker-1`、`moonbox-governance-controller-1`、`moonbox-chat-recovery-1`。主服务已显式声明容器名，因此没有出现同类后缀。

## 修复方案

1. 在三个目标服务中加入显式 `container_name`。
2. 默认值使用项目稳定命名：`moonbox-chat-worker`、`moonbox-governance-controller`、`moonbox-chat-recovery`。
3. 使用环境变量包裹默认值，例如 `${CHAT_WORKER_CONTAINER_NAME:-moonbox-chat-worker}`，允许并行环境按需覆盖。
4. 文档说明显式 `container_name` 与多副本扩展冲突；如未来需要同服务多副本，应使用服务名、label 或 profile 化副本方案，而不是固定容器名。

## 测试策略

- 配置解析：运行目标 Compose 组合的 `docker compose config`，断言目标服务存在 `container_name` 且值为稳定默认值或指定覆盖值。
- 运行态检查：在可用 Docker 环境中启动目标服务，使用 `docker compose ps` 或等价查询确认容器名不包含 `-1` 后缀。
- 回归：确认主服务 `backend`、`web`、`minio`、`mysql` 的既有容器名不变化。
- 文档：部署说明不再指导用户引用 `moonbox-*-1`，并记录环境变量覆盖与多副本限制。

## 风险与约束

- 显式 `container_name` 会限制同一 Compose 项目内同服务多副本扩展；当前目标服务按单副本运维与验收约定处理。
- 本变更不调整网络、卷、端口、健康检查或业务环境变量，避免扩大部署面。
- 若本地存在旧 `moonbox-*-1` 容器残留，运行态验收前需先清理或重建，避免名称冲突误判。

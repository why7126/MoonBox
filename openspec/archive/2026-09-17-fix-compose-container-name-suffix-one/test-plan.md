---
created_at: 2026-09-15 00:18:00
updated_at: 2026-09-15 00:18:00
owner: MoonBox 产品团队
source_bug: BUG-0017-compose-container-name-suffix-one
---

# 测试计划

## 自动化验证

- 运行 Compose 配置解析测试，确认目标服务的 `container_name` 存在且默认值稳定。
- 运行覆盖变量解析测试，确认环境变量能替换默认容器名。
- 运行 OpenSpec 当前 Change 中文校验和 residual report。

## 手工或环境相关验证

- 在 Docker 可用环境启动 chat-platform、governance 和 chat-recovery 组合，使用 `docker compose ps` 核对运行态容器名。
- 若本地存在旧 `moonbox-*-1` 容器，先用正常 down/清理流程处理残留，再执行运行态验收。

## 不适用项

- API 测试不适用：本变更不新增或修改 API 路径、请求字段、响应字段或错误码。
- DB 测试不适用：本变更不修改 schema、迁移、持久化语义或数据保留策略。
- 前端 UI 测试不适用：本变更不修改 Web 或管理端视觉与交互。

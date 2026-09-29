---
created_at: 2026-09-15 00:18:00
updated_at: 2026-09-15 00:18:00
owner: MoonBox 产品团队
source_bug: BUG-0017-compose-container-name-suffix-one
source_sprint: sprint-007
---

## 背景与动机

BUG-0017 记录了 Docker/Compose 叠加服务容器名自动追加 `-1` 后缀的问题。根因证据显示，主编排中的 `backend`、`web`、`minio` 等服务已通过显式 `container_name` 获得稳定名称，而 `deploy/docker-compose.chat-platform.yml`、`deploy/docker-compose.governance.yml` 和 `deploy/local/compose.chat-recovery.yml` 中的 `chat-worker`、`governance-controller`、`chat-recovery` 未声明 `container_name`，运行态回退为 Compose 默认的 `moonbox-<service>-1` 命名。

该问题影响部署排查、验收脚本和长期文档中的容器定位稳定性。修复目标是在不改变业务服务行为的前提下，为用户可见或脚本会引用的 Compose 叠加服务补齐稳定容器名，并明确多副本扩展限制。

## 变更内容

- 为 `chat-worker`、`governance-controller`、`chat-recovery` 补齐显式 `container_name`，默认命名分别为 `moonbox-chat-worker`、`moonbox-governance-controller`、`moonbox-chat-recovery`。
- 容器名应支持通过环境变量覆盖，便于本地并行环境或特殊部署场景调整。
- 增加 Compose 配置解析回归，确认目标服务的 `container_name` 字段存在且不再回退到 `-1` 形式。
- 增加运行态或等价 Docker smoke 验收，确认实际容器名与配置解析一致。
- 同步部署文档、脚本说明或验收说明，避免长期资料继续引用 `moonbox-*-1` 运行态名称。

## 能力范围

### 新增能力

- 无。

### 修改能力

- `deployment-governance`: 明确 MoonBox 用户可见或脚本引用的 Compose 服务必须具备稳定容器名，叠加服务不得回退到 Compose 默认序号命名。

## 影响范围

- Docker/部署配置：`deploy/docker-compose.chat-platform.yml`、`deploy/docker-compose.governance.yml`、`deploy/local/compose.chat-recovery.yml`。
- 部署文档与验收说明：记录稳定容器名约定、环境变量覆盖方式和多副本限制。
- 测试：补充 Compose 配置解析或脚本级回归；运行态 Docker smoke 可按本地环境能力执行。
- API、数据库、Web UI、对象存储、OpenAPI/客户端生成：不变。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 本修复仅调整 Docker/Compose 容器命名配置与部署文档，不新增或修改 API 路径、请求头、响应字段、行为埋点、request_logs、usage_events、Task Trace、数据库或前端请求封装。
  validation: apply 阶段通过 Compose 配置解析、运行态容器名检查或等价 smoke 验证；无需 OpenAPI、Orval、DB migration 或链路字段同步。
```

## 回滚计划

- 若显式 `container_name` 阻碍同一 Compose 项目内多副本扩展，可回退对应服务的 `container_name` 字段，并在部署文档中标注临时回退原因。
- 回滚后必须保留 BUG-0017 未闭环状态或返修记录，避免把 `moonbox-*-1` 运行态误判为已修复。
- 若仅环境变量默认值导致命名冲突，应优先调整覆盖变量而非删除全部稳定命名约定。

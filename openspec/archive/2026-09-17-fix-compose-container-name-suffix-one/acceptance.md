---
created_at: 2026-09-15 00:18:00
updated_at: 2026-09-15 00:18:00
owner: MoonBox 产品团队
source_bug: BUG-0017-compose-container-name-suffix-one
acceptance_status: not_started
---

# 验收标准

## AC-001 稳定容器名

`chat-worker`、`governance-controller`、`chat-recovery` 在默认配置解析中必须分别具有稳定容器名，不得回退为 `moonbox-*-1`。

## AC-002 可覆盖

目标服务容器名必须可通过环境变量覆盖，便于本地并行环境或特殊部署环境避免名称冲突。

## AC-003 主服务不回归

`backend`、`web`、`minio`、`mysql` 等主服务既有容器名、网络、卷、端口和健康检查不发生非预期变化。

## AC-004 运行态一致

在可用 Docker 环境中启动目标组合后，`docker compose ps` 展示的目标容器名与配置解析结果一致，不出现 `-1` 后缀。

## AC-005 文档一致

部署文档、脚本说明和验收步骤使用稳定容器名或服务名查询方式，不再把 `moonbox-*-1` 作为期望名称。

## 验收结果回填

```yaml
acceptance_status: not_started
accepted_at: null
accepted_by: null
source_change: fix-compose-container-name-suffix-one
source_sprint: sprint-007
evidence: []
failed_items: []
source_event: bug.opsx
notes: apply 阶段根据 Compose 配置解析、运行态 smoke 和文档同步结果回填。
```

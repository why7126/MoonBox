# 临时规避方案

## 当前可用规避

在正式修复前，运维和验收步骤优先使用 Compose 服务名、label 或 `docker compose ps` 查询结果定位容器，不硬编码带 `-1` 的运行态名称。

推荐查询方式：

```bash
docker compose ps
docker compose ps chat-worker
docker compose ps governance-controller
```

## 本地临时覆盖

如必须在本地短期获得稳定容器名，可使用额外 Compose override 为目标服务声明 `container_name`。该方式仅适合单副本本地环境；若服务需要扩缩容或并行多环境运行，应等待正式修复方案统一处理。

示例方向：

```yaml
services:
  chat-worker:
    container_name: moonbox-chat-worker
  governance-controller:
    container_name: moonbox-governance-controller
```

## 风险与限制

- 显式 `container_name` 会限制同一 Compose 项目中同服务多副本扩展。
- 临时 override 容易与正式部署文件漂移，不应作为长期方案。
- 不应把运行态 `moonbox-*-1` 名称写入长期文档、测试断言或自动化脚本。

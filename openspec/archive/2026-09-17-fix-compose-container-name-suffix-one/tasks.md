---
created_at: 2026-09-15 00:18:00
updated_at: 2026-09-15 00:18:00
owner: MoonBox 产品团队
source_bug: BUG-0017-compose-container-name-suffix-one
---

# 实施任务

## 1. Compose 配置修复

- [x] 1.1 为 `deploy/docker-compose.chat-platform.yml` 的 `chat-worker` 增加可覆盖的稳定 `container_name`。
- [x] 1.2 为 `deploy/docker-compose.governance.yml` 的 `governance-controller` 增加可覆盖的稳定 `container_name`。
- [x] 1.3 为 `deploy/local/compose.chat-recovery.yml` 的 `chat-recovery` 增加可覆盖的稳定 `container_name`。
- [x] 1.4 确认主 Compose 服务既有容器名、网络、卷、端口和健康检查未被非预期改变。

## 2. 回归测试

- [x] 2.1 增加或更新 Compose 配置解析测试，覆盖 `chat-worker`、`governance-controller`、`chat-recovery` 的 `container_name`。
- [x] 2.2 覆盖环境变量覆盖场景，确认覆盖值可被 Compose 解析。
- [x] 2.3 在可用 Docker 环境中运行目标 Compose 组合，确认实际容器名不再出现 `-1` 后缀；若本地 Docker 不可用，记录等价解析证据和需人工补跑的 smoke 命令。
- [x] 2.4 回扣 BUG-0017 AC-001 至 AC-007，确认文档、脚本和验收说明不依赖旧 `moonbox-*-1` 名称。

## 3. 文档与验收

- [x] 3.1 更新 `docs/02-deployment.md` 或部署入口说明，记录稳定容器名、覆盖变量和多副本限制。
- [x] 3.2 如新增或修改环境变量，同步 `.env.example` 或相关 env 示例注释；若未新增全局 env，说明豁免原因。
- [x] 3.3 回填 Change trace、BUG acceptance 和 Sprint scope，记录验证命令与结果。
- [x] 3.4 判断是否需要沉淀 `docs/knowledge-base/incidents/`；若仅为局部 Compose 命名遗漏，可在归档 trace 中说明不沉淀原因。

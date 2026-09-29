---
change_id: fix-compose-container-name-suffix-one
source_bug: BUG-0017-compose-container-name-suffix-one
source_requirement: null
source_sprint: sprint-007
type: fix
status: applied
created_at: 2026-09-15 00:18:00
updated_at: 2026-09-15 00:28:22
owner: MoonBox 产品团队
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 本修复仅调整 Docker/Compose 容器命名配置与部署文档，不影响 API、DB、request_logs、usage_events、Task Trace 或前端请求封装。
  validation: apply 阶段通过 Compose 配置解析、运行态容器名检查或等价 smoke 证据验证。
execution:
  schema_version: 1
  started_at: 2026-09-15 00:20:11
  completed_at: 2026-09-15 00:28:22
  last_event: opsx.apply
---

# fix-compose-container-name-suffix-one Trace

## 缺陷就绪

| 项 | 结论 | 证据 |
|---|---|---|
| BUG 状态 | ready | `BUG-0017-compose-container-name-suffix-one` 为 `in_sprint`，迭代 `sprint-007`。 |
| 文档包 | ready | `bug.md`、`root-cause.md`、`workaround.md`、`acceptance.md`、`trace.md` 均存在。 |
| 根因证据 | pass | `python scripts/validate-root-cause-evidence.py --bug BUG-0017-compose-container-name-suffix-one` 通过，confirmed，证据 5 条。 |
| Change 身份 | pass | `python scripts/validate-change-identity.py --new-id fix-compose-container-name-suffix-one` 通过。 |

## 缺陷分析报告

| 维度 | 摘要 |
|---|---|
| 现象 | Docker/Compose 叠加服务容器名出现 `-1` 后缀。 |
| 复现 | 启用 chat-platform、governance 或 chat-recovery Compose 后查看运行态容器名。 |
| 影响 | 运维排查、脚本引用和验收步骤无法依赖稳定容器名。 |
| 根因分类 | 部署配置遗漏显式 `container_name`。 |
| 严重等级 | medium。 |

## 修复边界

- 补齐目标叠加服务稳定容器名。
- 保留环境变量覆盖能力。
- 不调整 API、DB、Web UI、对象存储、业务环境变量、端口、网络或卷语义。
- 不修改 `openspec/specs/` 正式规格；归档时由 OpenSpec 合并 delta spec。

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-09-15 00:18:00 | /bug-opsx | proposed | 由 BUG-0017 生成 OpenSpec Change，固化 execution schema v1。 |
| 2026-09-15 00:20:11 | /opsx-apply | in_progress | 启动实现，Workflow Sync 写入执行开始事实。 |

## 验证摘要

| 时间 | 命令 | 结果 | 覆盖 |
|---|---|---|---|
| 2026-09-15 00:18:00 | `python scripts/validate-root-cause-evidence.py --bug BUG-0017-compose-container-name-suffix-one` | pass | 根因证据 5 条，状态 confirmed。 |
| 2026-09-15 00:18:00 | `python scripts/validate-change-identity.py --new-id fix-compose-container-name-suffix-one` | pass | Change ID 未被 active 或 archive 占用。 |
| 2026-09-15 00:23:00 | `uv run pytest tests/unit/test_chat_platform_script.py tests/unit/test_docker_lifecycle_scripts.py -q` | 13 passed | YAML 解析回归覆盖三个叠加服务稳定 `container_name`；既有 Docker 脚本行为未回归。 |
| 2026-09-15 00:23:00 | `docker compose ... config --format json` | pass | 默认解析得到 `chat-worker=moonbox-chat-worker`、`governance-controller=moonbox-governance-controller`、`chat-recovery=moonbox-chat-recovery`，主服务 `backend/web/minio` 名称保持稳定。 |
| 2026-09-15 00:23:00 | `docker compose ... config --format json` with overrides | pass | 覆盖变量可解析为自定义容器名。 |
| 2026-09-15 00:24:00 | `CHAT_RECOVERY_CONTAINER_NAME=moonbox-chat-recovery-smoke docker compose ... up -d --no-deps --no-build chat-recovery` | pass | 临时运行态容器名为 `moonbox-chat-recovery-smoke`，随后已清理；未留下 smoke 容器。 |
| 2026-09-15 00:27:00 | `docker compose create --no-build ... chat-worker governance-controller chat-recovery` | warning | 本机存在同项目旧容器残留，create 会复用旧项目容器状态；不作为 chat-worker/governance 运行态通过证据，默认名以 config 与单测为准。 |

## 文档与生成物同步

- API、OpenAPI、Orval、DB schema、对象存储和前端 UI 不适用。
- 已同步 `.env.example`：`CHAT_WORKER_CONTAINER_NAME`、`GOVERNANCE_CONTROLLER_CONTAINER_NAME`、`CHAT_RECOVERY_CONTAINER_NAME`。
- 已同步 `docs/02-deployment.md`，记录稳定容器名约定、覆盖变量和多副本限制。

## 知识沉淀判断

BUG-0017 属于局部 Compose 命名配置遗漏。本次已补齐目标服务并增加测试，暂不新增 `docs/knowledge-base/incidents/`；若后续继续发现同类遗漏，建议通过 `/capture` 记录治理项，统一校验所有 Compose 服务命名约定。

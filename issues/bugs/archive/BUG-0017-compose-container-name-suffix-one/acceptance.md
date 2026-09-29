---
bug_id: BUG-0017-compose-container-name-suffix-one
title: 容器名不应自动追加 -1 后缀
acceptance_status: passed
created_at: 2026-09-14 23:55:58
updated_at: 2026-09-29 14:44:19
---

# 验收标准

## AC-001 主部署服务容器名保持稳定

执行常规 Docker Compose 部署后，`backend`、`web`、`minio`、`mysql` 等主服务继续使用既有稳定容器名，不出现命名回退或重复冲突。

## AC-002 Chat 平台服务不再出现 `-1` 后缀

启用 chat-platform 叠加部署后，`chat-worker` 的容器名使用项目约定的稳定名称，不再显示为 `moonbox-chat-worker-1`。

## AC-003 Governance 控制器不再出现 `-1` 后缀

启用 governance 叠加部署后，`governance-controller` 的容器名使用项目约定的稳定名称，不再显示为 `moonbox-governance-controller-1`。

## AC-004 Chat recovery 服务命名一致

启用 `deploy/local/compose.chat-recovery.yml` 恢复 worker 时，`chat-recovery` 使用稳定容器名，不再显示为 `moonbox-chat-recovery-1`。

## AC-005 配置解析可验证

运行 Compose 配置解析时，相关服务的 `container_name` 字段均存在且值符合项目命名约定；主服务、网络名和卷名不发生非预期变化。

## AC-006 运行态可验证

运行 `docker compose ps` 后，目标服务实际容器名与配置解析结果一致；无旧容器残留造成同名冲突。

## AC-007 文档与脚本同步

部署文档、Docker 启停脚本测试和任何引用容器名的验收步骤均使用修复后的稳定容器名或服务名查询方式，不再依赖 `-1` 后缀。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-29 14:44:19
accepted_by: workflow-sync
source_change: fix-compose-container-name-suffix-one
source_sprint: sprint-007
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```


---
change_id: apply-tilesfst-data-collection-governance
type: update
status: proposed
created_at: 2026-08-27 00:27:55
updated_at: 2026-08-27 00:27:55
---

# 应用 TilesFST 数据采集治理学习成果

## 背景

`/spec-study TilesFST --focus 数据采集` 已完成第一阶段只读学习。ProjectTilesFST（本地只读项目）在行为事件、请求日志、Task Trace、流程节点、脱敏、保留周期和 REQ/Change/Sprint 门禁上形成了可迁移治理模式。

MoonBox 当前启用 Web 端、管理后台、REST API、SQLite/MySQL、MinIO/S3、Agent Workflow、OpenSpec 和 Sprint 治理，但还没有专项的产品数据采集与链路观测事实源。本变更按 MoonBox 当前事实源转写学习成果，不复制学习对象的小程序/App、瓷砖业务、店主端或具体表结构。

## 目标

- 新增 MoonBox 产品数据采集与链路观测标准，定义 `usage_events -> request_logs -> task_traces -> task_trace_spans` 四层模型。
- 新增 Task Trace 覆盖清单，给出 MoonBox 首批候选场景、接入优先级和流程节点策略。
- 新增治理校验脚本，校验标准文档、规则入口、技能入口和目标 Change/Sprint 声明。
- 同步 `AGENTS.md`、`rules/`、`.agents/skills/` 和 `docs/README.md` 的轻量门禁引用。
- 生成单份 `/spec-study` 学习报告，并登记到 `docs/spec-logs/CHANGELOG.md`。

## 非目标

- 不修改 `src/` 业务运行时代码。
- 不新增真实 `usage_events`、`request_logs`、`task_traces` 或 `task_trace_spans` 表、迁移、API 或前端请求封装。
- 不启用微信小程序、移动端、桌面端或学习对象业务专属采集规则。
- 不修改 `openspec/specs/` 正式规格。
- 不复制学习对象长脚本或长规范原文。

## 影响范围

```yaml
impact:
  backend: false
  web: false
  admin: false
  database: false
  api: false
  docker_compose: false
  governance: true
  docs: true
  scripts: true
```

product_data_collection_observability:
  status: applicable
  affected_layers:
    - governance_rules
    - docs_standards
    - workflow_skills
    - validation_scripts
  reason: "本变更建立 MoonBox 数据采集与链路观测治理事实源和门禁，不落地业务数据表或运行时采集实现。"
  validation: "运行产品数据采集门禁脚本、OpenSpec 校验、目录结构校验、Sprint scope 校验和 Workflow Sync。"

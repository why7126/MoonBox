---
change_id: apply-tilesfst-data-collection-governance
status: proposed
created_at: 2026-08-27 00:27:55
updated_at: 2026-08-27 00:27:55
---

# 设计说明

## 1. 学习来源与适配原则

学习对象记为 `ProjectTilesFST（本地只读项目）`。本变更采纳其治理模式，不迁移业务实现：

- 标准事实源：将行为事件、请求日志、Task Trace、流程节点、保留周期和脱敏规则集中到 `docs/standards/product-data-collection-observability.md`。
- 覆盖清单：将任务型接口判定标准和首批候选场景集中到 `docs/standards/task-trace-coverage.md`。
- 门禁声明：REQ、Change、Sprint 和验收材料使用固定 `product_data_collection_observability` 声明，包含 `status`、`affected_layers`、`reason` 和 `validation`。
- 脚本校验：用 MoonBox 目录与技能边界重写校验脚本，只检查治理资产和目标文档，不扫描依赖、构建产物或运行时数据。

## 2. 标准文档设计

`docs/standards/product-data-collection-observability.md` 是唯一完整事实源，覆盖：

- 四层模型：`usage_events -> request_logs -> task_traces -> task_trace_spans`。
- 界面触发入口与直接 API/后台入口。
- 链路字段生成方、语义和可信边界。
- 最小数据结构、可空规则和产品扩展规则。
- Task Trace 分级覆盖、保留周期、安全与脱敏、验收清单。

规则、技能、Sprint 和 Change 文档只保留摘要与路径引用，不复制完整正文。

## 3. Task Trace 覆盖清单

`docs/standards/task-trace-coverage.md` 只维护 MoonBox 候选场景：

- 空间创建与加入申请。
- 文件与图片上传。
- 需求与 OpenSpec 工作流。
- 产品手册生成。
- 发布与镜像。
- 知识图谱同步。

本文不承诺这些场景已经完成运行时接入；任何真实 API、DB 或 Web 实现必须另走 REQ/OpenSpec。

## 4. 脚本校验设计

新增 `scripts/validate-product-data-observability.py`：

- 默认校验标准文档、入口规则和关键技能是否接入门禁。
- `--change <change-id>` 校验 active Change 命中触发范围时是否声明 `product_data_collection_observability`。
- `--sprint <sprint-id>` 校验 Sprint 文档是否存在触发范围缺失声明。
- `--diff` 可聚焦当前 working tree 中的文档和脚本触发项。

脚本只读取文件，不写入文件，不执行业务测试，不访问网络。

## 5. Workflow 接入

接入范围：

- `AGENTS.md` 追加读取路由和流程红线。
- `rules/api.md`、`rules/database.md`、`rules/testing.md`、`rules/requirement-management.md`、`rules/iterations-lifecycle.md` 追加门禁摘要。
- `.agents/skills/req-complete`、`req-review`、`req-opsx`、`opsx-propose`、`opsx-apply`、`opsx-archive`、`sprint-propose`、`sprint-apply`、`sprint-archive` 追加声明、验证和归档门禁。

## 6. 影响声明

product_data_collection_observability:
  status: applicable
  affected_layers:
    - governance_rules
    - docs_standards
    - workflow_skills
    - validation_scripts
  reason: "本变更治理层适用，用于建立后续 API、DB、请求日志、行为事件、Task Trace 和请求封装变更的声明门禁；本次不修改运行时代码或数据库。"
  validation: "校验标准文档完整性、规则/技能门禁接入、目标 Change 声明、OpenSpec 语言、目录结构、Sprint scope 和 Workflow Sync。"

## 7. 不采纳说明

- 不迁移小程序/App 字段和请求封装规则，因为 MoonBox 当前未启用这些端。
- 不迁移 ProjectTilesFST 的瓷砖、SKU、门店、媒体转码业务清单。
- 不创建真实数据表、迁移或 API，因为这属于业务实现范围，需要独立 REQ/OpenSpec。

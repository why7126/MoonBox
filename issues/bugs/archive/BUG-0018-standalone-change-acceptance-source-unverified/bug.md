---
bug_id: BUG-0018-standalone-change-acceptance-source-unverified
title: 独立 Change 卡片误报验收来源待核实
status: done
owner: 产品团队
discovered_at: '2026-09-14 09:16:42'
environment: web
related_requirement: REQ-0026-requirement-center-standalone-change-cards
related_change: null
created_at: 2026-09-14 10:21:19
updated_at: 2026-09-17 08:12:45
severity: medium
---

# 独立 Change 卡片误报验收来源待核实

## 现象

需求中心“验收中 / 测试与人工验收”分组内，独立 Change 卡片 `refresh-issue-index-after-archive-promotion` 展示红色提示；后续在 `enhance-workflow-sync-current-status-block` 卡片上复现同类提示：

- “验收来源待核实：未找到交付验证记录”

用户截图显示相关卡片归属 Sprint，并展示 `trace.md`、`sprint.md`、`proposal.md`、`spec.md`、`design.md`、`tasks.md` 等文档入口。

## 复现步骤

1. 打开需求中心或相关当前迭代看板。
2. 查看“验收中 / 测试与人工验收”分组。
3. 定位独立 Change 卡片 `refresh-issue-index-after-archive-promotion` 或 `enhance-workflow-sync-current-status-block`。
4. 观察卡片底部或动作区域是否出现“验收来源待核实：未找到交付验证记录”。

## 期望结果

- 独立 Change 卡片按自身交付证据定位验收来源。
- 当独立 Change 存在可追溯验证记录、验收记录、验证结果、验收结果、验证摘要、`Validation Log` 或 `verification.md` 等证据入口时，不展示“未找到交付验证记录”。
- 提示语应区分“没有证据入口”“证据文件为空”“引用路径无效”“运行态未读取到归档版本”等不同情况，便于定位。

## 实际结果

- 页面展示“验收来源待核实：未找到交付验证记录”。
- 用户会被误导为该独立 Change 没有交付验证记录。

## 影响范围

- 影响需求中心独立 Change 卡片的验收来源展示。
- 可能影响用户对独立 Change 交付完整性、验收状态和归档质量的判断。
- 已观察对象包括 `refresh-issue-index-after-archive-promotion` 与 `enhance-workflow-sync-current-status-block`；影响使用 `验证摘要`、`Validation Log`、`实施与验证记录` 等非白名单标题记录验证事实的独立 Change。

## 严重等级说明

严重等级初判为 `medium`：

- 该问题影响治理看板的可信度和验收判断，但当前未证明会破坏源文件、权限或真实归档流程。
- 缺陷位于已交付的独立 Change 卡片能力上，属于现有能力展示偏差。
- 若后续证明确实阻断 `/opsx-archive` 或导致用户误操作，可在评审时上调严重等级。

## 初步证据

| 证据 | 路径 | 说明 |
|---|---|---|
| 用户截图 | `issues/bugs/review/BUG-0018-standalone-change-acceptance-source-unverified/screenshots/user-evidence-acceptance-source-unverified.png` | 展示独立 Change 卡片出现“验收来源待核实：未找到交付验证记录”。 |
| 目标 Change trace | `openspec/archive/2026-09-14-refresh-issue-index-after-archive-promotion/trace.md` | 包含 `## 验证摘要` 章节及多条验证命令记录。 |
| 后续复现 Change trace | `openspec/archive/2026-09-14-enhance-workflow-sync-current-status-block/trace.md` | 包含 `## Validation Log` 章节及多条验证命令记录，但卡片仍提示未找到交付验证记录。 |
| 相关规格 | `openspec/specs/web-catalog-requirement-center-real-data/spec.md` | 独立 Change 应按自身交付证据定位验收来源，不套用 Issue 固定 `acceptance.md` 要求。 |
| 相关实现线索 | `src/backend/app/governance/change_index.py` | 验收来源识别当前只匹配部分标题和文件入口；`验证摘要` 与 `Validation Log` 均不在白名单内。 |

## 待确认线索

- 目标 Change 的 `## 验证摘要` 与 `## Validation Log` 是否应被验收来源识别逻辑接受。
- 运行态是否读取到了目标 Change 的当前活动目录或归档版本。
- 若运行态读取的是旧快照，需进一步确认是否为缓存、项目快照或 Change 目录解析问题。

## 建议验证方向

- 使用后端单元测试覆盖含 `## 验证摘要` 与 `## Validation Log` 的独立 Change trace。
- 使用真实或合成需求中心上下文确认该卡片不再展示“未找到交付验证记录”。
- 保留“证据存在不等于验收通过”的语义，避免把文件存在误判为归档可通过。

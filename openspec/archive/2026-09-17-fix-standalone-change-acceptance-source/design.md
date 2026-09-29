---
created_at: 2026-09-15 00:02:17
updated_at: 2026-09-15 00:02:17
owner: MoonBox 产品团队
source_bug: BUG-0018-standalone-change-acceptance-source-unverified
---

# 设计说明

## 根因摘要

独立 Change 验收来源识别逻辑对 trace 章节标题采用固定白名单，只接受 `验证记录`、`验收记录`、`验收结果`、`验证结果`。项目实际 Change trace 中存在非空 `验证摘要` 与 `Validation Log` 章节；当目标 Change 没有 `acceptance.md` 或 `verification.md` 时，后端仍返回“未找到交付验证记录”，导致需求中心卡片误报。

## 修复方案

1. 将 trace 验证章节识别抽象为稳定标题集合，覆盖：
   - 既有标题：`验证记录`、`验收记录`、`验证结果`、`验收结果`。
   - 新增标题：`验证摘要`、`Validation Log`。
   - 项目既有表达：`实施与验证记录`。
2. 标题匹配只对非空章节生效；空章节不得作为验收来源。
3. 保持来源优先级：
   - `trace.acceptance_refs` 显式声明优先，并严格校验 Change 内相对 Markdown 路径。
   - 显式引用失败时返回具体待核实原因，不回退到其他来源掩盖错误。
   - 无显式引用时，再检查非空 `acceptance.md`、`verification.md` 和 trace 验证章节。
4. 验收来源只证明“存在可追溯来源”，不得自动判定验收通过；tasks 全勾、`applied` 状态或文件存在不得单独推出可归档。

## 测试设计

- 后端单元测试：
  - trace 仅含非空 `## 验证摘要` 时，独立 Change 卡片不返回“未找到交付验证记录”。
  - trace 仅含非空 `## Validation Log` 时，独立 Change 卡片不返回“未找到交付验证记录”。
  - 既有标题、`acceptance.md`、`verification.md` 继续通过。
  - 空章节、无来源仍返回待核实提示。
  - 显式 `acceptance_refs` 缺失、空文件、越界或非 Markdown 仍返回具体错误，不回退。
- 真实或合成需求中心上下文测试：
  - 覆盖 `refresh-issue-index-after-archive-promotion`、`enhance-workflow-sync-current-status-block` 或等价合成样本。

## 文档与生成物同步

- 不新增 API 字段、DB schema、对象存储、部署配置或客户端生成物。
- OpenAPI/Orval 仅在实现阶段发现响应契约变化时同步；本设计预期不需要。
- 长期规格通过 delta spec 更新 `web-catalog-requirement-center-real-data` 的独立 Change 交付验收来源场景。

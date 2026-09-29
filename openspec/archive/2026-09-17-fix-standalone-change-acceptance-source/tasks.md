---
created_at: 2026-09-15 00:02:17
updated_at: 2026-09-15 00:11:09
owner: MoonBox 产品团队
source_bug: BUG-0018-standalone-change-acceptance-source-unverified
---

# 实施任务

## 1. 后端修复

- [x] 1.1 定位独立 Change 验收来源识别函数，补充 `验证摘要`、`Validation Log` 和 `实施与验证记录` 的非空章节识别。
- [x] 1.2 保持 `acceptance_refs` 显式引用优先和失败不回退的安全边界。
- [x] 1.3 保持无来源、空章节、空文件、缺失文件、越界路径和非 Markdown 引用的具体待核实原因。

## 2. 回归测试

- [x] 2.1 增加后端测试覆盖 `## 验证摘要`。
- [x] 2.2 增加后端测试覆盖 `## Validation Log`。
- [x] 2.3 增加或复核既有来源回归：`acceptance.md`、`verification.md`、`验证记录`、`验收记录`、`验证结果`、`验收结果`。
- [x] 2.4 增加或复核安全边界回归：显式引用缺失、空文件、越界、非 Markdown、无来源。
- [x] 2.5 用真实或等价合成需求中心上下文确认 BUG-0018 复现样本不再误报“未找到交付验证记录”。

## 3. 文档与验收

- [x] 3.1 回填 Change trace 的验证摘要，记录测试命令与结果。
- [x] 3.2 如实现阶段确认 API 契约未变化，在 trace 或验收中记录 OpenAPI/客户端生成不适用原因；若契约变化则同步 `docs/03-api-index.md`、OpenAPI 和客户端生成物。
- [x] 3.3 完成 BUG acceptance 回填，确认 AC-001 至 AC-006。
- [x] 3.4 判断是否需要将 BUG-0018 经验沉淀到 `docs/knowledge-base/incidents/`；若仅为局部标题漏判，可在归档 trace 中说明不沉淀原因。

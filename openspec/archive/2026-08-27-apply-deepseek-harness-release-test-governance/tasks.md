---
change_id: apply-deepseek-harness-release-test-governance
status: proposed
created_at: 2026-08-27 08:06:34
updated_at: 2026-08-27 08:06:34
---

# Tasks

## 1. OpenSpec 与 Sprint

- [x] 1.1 创建独立治理 Change，承载本次 deepseek-harness 发布与测试治理学习应用。
- [x] 1.2 将 Change 纳入 `sprint-003` scope。

## 2. 规则应用

- [x] 2.1 在发布规则中补充构建记录、产物 manifest 和发布写入边界。
- [x] 2.2 在测试规则中补充测试分区与慢测试调度。
- [x] 2.3 在命令执行顺序文档中补充发布构建与慢测试治理校验入口。

## 3. 学习报告与索引

- [x] 3.1 写入 `docs/spec-logs/YYYYMMDDhhmmss-study-deepseek-harness-release-test-governance.md`。
- [x] 3.2 在 `docs/spec-logs/CHANGELOG.md` 倒序登记本次 study。

## 4. 验证与同步

- [x] 4.1 复核聚焦 diff，记录当前 `src/web/openapi.json` generated diff 不属于本次学习应用编辑范围。
- [x] 4.2 运行上下文预算、OpenSpec 语言、目录结构、目标 Change validate 和 Sprint scope 校验。
- [x] 4.3 运行 Workflow Sync 与 AI Usage hook。
- [x] 4.4 复核学习对象只读状态。

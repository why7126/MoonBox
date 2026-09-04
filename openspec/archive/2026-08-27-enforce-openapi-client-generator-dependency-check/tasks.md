---
change_id: enforce-openapi-client-generator-dependency-check
created_at: 2026-08-27 08:06:17
updated_at: 2026-08-27 08:12:00
---

# 任务清单

- [x] 创建治理 Change 并纳入 Sprint。
- [x] 补强 `scripts/generate-openapi-client.sh` 的 pnpm 缺失、pnpm 版本错配、Orval、配置缺失提示和 fallback。
- [x] 保持 `src/web/openapi.json` 导出为可读格式，避免生成物整文件格式 churn。
- [x] 在 `scripts/validate-api-standard.py` 增加客户端生成脚本依赖提示检查。
- [x] 修正 API 标准校验对 router 级 tags 的误报，避免遮蔽新增检查项。
- [x] 同步 OpenAPI 治理文档和 delta spec。
- [x] 写入治理日志并同步 spec-logs 索引。
- [x] 运行脚本级测试与治理校验。
- [x] 运行 Workflow Sync 和 AI Usage hook。

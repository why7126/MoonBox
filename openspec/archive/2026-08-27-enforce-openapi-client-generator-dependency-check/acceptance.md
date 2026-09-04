---
change_id: enforce-openapi-client-generator-dependency-check
created_at: 2026-08-27 08:06:17
updated_at: 2026-08-27 08:12:00
---

# 验收标准

- `generate-openapi-client.sh` 在缺少 pnpm、pnpm 版本错配、缺少 Orval 或 Orval 配置时输出明确修复提示。
- 脚本在 OpenAPI 已导出但客户端未生成时说明 fallback 状态和后续命令。
- `validate-api-standard.py` 能检查脚本是否保留 pnpm/orval 依赖提示与 fallback 文案。
- OpenSpec、治理文档、治理日志和 Sprint scope 保持一致。

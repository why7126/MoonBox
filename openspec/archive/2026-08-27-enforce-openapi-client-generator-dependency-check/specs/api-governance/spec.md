## ADDED Requirements

### Requirement: OpenAPI 客户端生成脚本依赖提示
MoonBox SHALL 在 OpenAPI 客户端生成脚本中检查 pnpm 可用性、pnpm 项目版本匹配、Orval、生成配置和 fallback 状态，避免依赖缺失或版本错配时只暴露低层 shell 错误。

#### Scenario: 缺少客户端生成依赖时输出可执行提示
- **WHEN** 开发者运行 `scripts/generate-openapi-client.sh`
- **AND** pnpm 缺失、pnpm 版本错配、Orval 本地二进制缺失、Orval 依赖声明缺失或 Orval 配置缺失
- **THEN** 脚本 MUST 输出对应缺失项、建议修复命令和 `src/web/openapi.json` 是否已导出的状态
- **AND** 脚本 MUST NOT 隐式联网安装 Orval 或改写锁文件

#### Scenario: API 标准校验覆盖生成脚本依赖提示
- **WHEN** 运行 `python scripts/validate-api-standard.py`
- **THEN** 校验 MUST 检查 `scripts/generate-openapi-client.sh` 是否保留 pnpm 缺失提示、pnpm 版本错配提示、Orval 缺失提示和 OpenAPI 已导出但客户端生成未完成的 fallback 文案

---
purpose: Testing Governance 生效规格
content: pytest、Vitest、E2E 目录、覆盖率和映射基线
created_at: 2026-07-29 23:10:00
updated_at: 2026-07-29 23:10:00
owner: MoonBox 产品团队
---

## Purpose

MoonBox 测试治理定义 pytest、Vitest、E2E 目录、覆盖率和映射基线。
## Requirements
### Requirement: 后端测试基线

MoonBox SHALL 在 `tests/` 和 `src/backend/tests/` 提供 pytest 配置与后端基线测试。

#### Scenario: 后端测试可发现

- **GIVEN** 开发者在仓库根目录运行 pytest
- **WHEN** 测试发现开始
- **THEN** 单元测试、集成测试和后端服务测试均可被发现

### Requirement: 前端测试基线

MoonBox SHALL 为 React 组件测试提供 Vitest 配置。

#### Scenario: 前端测试已配置

- **GIVEN** 开发者在 `src/web` 工作
- **WHEN** `pnpm test` 可用
- **THEN** Vitest 可以执行 React 测试文件

### Requirement: 测试治理校验

MoonBox SHALL 提供 `scripts/validate-test-framework.py` 和 `openspec/testing-mapping.md`。

#### Scenario: 框架校验通过

- **GIVEN** 基线测试目录和治理文档存在
- **WHEN** 校验脚本运行
- **THEN** 交付前可发现缺失的测试框架资产

### Requirement: Docker media-upload 测试身份

MoonBox Docker media-upload 验收 SHALL 使用脚本准备的可控测试身份，不得依赖本地持久库中的默认管理员密码。

#### Scenario: 本地持久库默认密码漂移

- **GIVEN** Docker 后端数据挂载在 `data/runtime/backend`
- **AND** 管理员密码可能已被用户修改或由不同 `ADMIN_INITIAL_PASSWORD` seed
- **WHEN** 执行 Docker media-upload 验收
- **THEN** 验收脚本 MUST NOT 假设 `ADMIN_INITIAL_PASSWORD` 或项目示例密码等于当前管理员密码
- **AND** 验收脚本 MUST 创建或准备一次性测试用户、测试会话或可回收 fixture

#### Scenario: 使用测试身份完成上传链路

- **GIVEN** 验收脚本已准备测试身份
- **WHEN** 执行 media-upload 回归验证
- **THEN** 脚本 MUST 使用该身份完成 `/api/v1/auth/login`
- **AND** 脚本 MUST 使用该身份完成 `POST /api/v1/auth/avatar`
- **AND** 脚本 MUST 验证受保护头像读取和同会话回显
- **AND** 验收输出 MUST NOT 包含真实密码、Authorization header、Cookie 或真实 `.env` 原文


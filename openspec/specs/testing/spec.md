---
purpose: Testing Governance 生效规格
content: pytest、Vitest、E2E 目录、覆盖率和映射基线
created_at: 2026-07-29 23:10:00
updated_at: 2026-07-29 23:10:00
owner: MoonBox 产品团队
---

# 测试治理

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

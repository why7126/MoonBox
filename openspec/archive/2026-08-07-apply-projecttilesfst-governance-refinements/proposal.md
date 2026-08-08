---
purpose: OpenSpec Change Proposal
content: 应用 ProjectTilesFST A-E 治理学习候选
created_at: 2026-08-07 00:00:00
updated_at: 2026-08-07 00:00:00
owner: MoonBox 产品团队
---

# Proposal

## 背景

ProjectTilesFST 在 spec-logs、Mintlify 产品手册、usage-docs、deploy 矩阵和输出安全方面有更细的治理约束。MoonBox 已具备基础目录和命令，但仍可补齐日志命名、隐私边界、站点投影、旧版本修正授权、共享截图资产和部署脚本安全输出等规范。

## 目标

- 将 `docs/spec-logs/` 升级为 `/spec-study` 学习报告和 `/spec-opt` 治理迭代日志的统一目录。
- 强化 Mintlify 站点投影、manifest、截图资产、旧版本手册修正授权和公开安全校验。
- 固化部署 env 回退、docs-site 预览、Compose profile 和脚本输出安全边界。

## 非目标

- 不修改 `src/` 业务运行时代码。
- 不引入小程序、瓷砖业务脚本或 ProjectTilesFST 专有业务流程。
- 不直接修改 `openspec/specs/` 正式规格。

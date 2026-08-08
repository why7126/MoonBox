---
name: "usage-docs-validate"
description: "校验 MoonBox Mintlify 产品手册、导航、manifest 和公开安全"
---

# usage-docs-validate

Use this skill when the user asks `/usage-docs-validate <version>` or wants to validate MoonBox product manual readiness.

## Context Budget Guardrails（MUST）

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 默认只读取 `mintlify/README.md`、`mintlify/mint.json`、`mintlify/site-manifest.json` 和校验失败文件。

## Input

- `<version>`：可选，默认校验整个 `mintlify/` 站点。

## Steps

Run:

```bash
python scripts/validate-mintlify-docs.py
```

When validating release readiness and the matching release directory exists, also run:

```bash
python scripts/validate-release.py --release-dir releases/<version> --stage prepare
```

## Validation Scope

The validator checks:

- `mintlify/mint.json` 和 `site-manifest.json` 是合法 JSON。
- Mintlify 导航引用的 `.mdx` 页面真实存在。
- `mintlify/` 中没有 `.env`、构建产物目录或常见敏感配置模式。
- 公开页面不包含数据库连接串、密钥字段、Authorization header、Cookie 或对象存储密钥。
- `site-manifest.json` 中的 `latest_version`、`versions`、`projections`、共享截图资产和 manual overrides 格式一致。
- 页面内相对链接、站内 `.mdx` 链接和 `/assets/screenshots/` 图片引用有效。
- 共享截图资产存在且可公开；如记录 `sha256` 或 `content_hash`，校验实际文件 hash。

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Output

Report validation commands, pass/fail summary, failing files, and suggested fix command.

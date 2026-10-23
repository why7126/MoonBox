---
name: "usage-docs-validate"
updated_at: 2026-10-23 08:31:02
description: "校验 MoonBox Mintlify 产品手册、导航、manifest 和公开安全"
---

# usage-docs-validate

Use this skill when the user asks `/usage-docs-validate <version>` or wants to validate MoonBox product manual readiness.

## 浏览器自主取证（MUST）

浏览器清单超时、单个工具失败或终端 HTTP 探测失败时，先按 `rules/root-cause-evidence.md` §5.0 检查现有标签页、直接连接浏览器窗口并尝试可行替代入口；区分旧页面展示和当前服务连通性，完成这些检查后才判断是否无法访问。

测试、验收、BUG 补证或问题排查需要产品运行态证据时，Agent 可在已有权限与任务范围内直接通过浏览器访问产品并取证，优先复用 Codex 侧边浏览器中与任务相关的产品标签页，无需人工二次确认；该入口不可用或不能取得所需证据时，使用已提供的其他浏览器或等价自动化工具，Firefox 作为后备。只有无法访问、权限不足、操作超出已授权边界，或自主取证后关键证据仍不足时，才请用户补证，并说明已尝试路径与具体缺口。证据脱敏、不可逆操作和存放边界遵循 `rules/root-cause-evidence.md` 第 5 节。

## Context Budget Guardrails（MUST）

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 默认只读取 `mintlify/README.md`、`mintlify/mint.json`、`mintlify/site-manifest.json` 和校验失败文件。

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

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
- `mintlify/` 不包含 `.mintlify/`、`dist/`、`build/`、运行时数据库、真实 env 或大体积构建产物。
- 如验证发布或部署准备，docs-site Compose config 必须证明服务只读挂载 `mintlify/` 和静态预览脚本，不挂载真实 env、`data/`、数据库卷、对象存储数据或密钥文件。

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Output

Report validation commands, pass/fail summary, failing files, and suggested fix command.
## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。

## 面向用户的表达

面向用户的输出遵循 `rules/language.md` 的“产品经理视角沟通”：先讲业务结果和用户影响，优先日常语言，必要技术术语随文解释；决策说明体验、成本、时间和风险。

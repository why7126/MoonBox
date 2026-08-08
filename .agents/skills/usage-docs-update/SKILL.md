---
name: "usage-docs-update"
description: "更新 MoonBox Mintlify 产品手册页面并保持公开安全校验"
---

# usage-docs-update

Use this skill when the user asks `/usage-docs-update <version>` or wants to edit existing MoonBox product manual pages.

## Context Budget Guardrails（MUST）

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 只读取本次影响的 `mintlify/docs/<version>/**/*.mdx` 页面、`mintlify/mint.json` 和 `site-manifest.json` 片段。
- 不默认读取全部 `docs/**`、`releases/**` 或历史版本目录。

## Input

- `<version>`：可选，默认 `latest`。
- 修改内容：用户指定的页面、段落、发布公告投影或公开安全修复。

## Must Read

```text
AGENTS.md
rules/document-governance.md
rules/directory-structure.md
rules/release.md
rules/security.md
mintlify/README.md
```

Then read only impacted pages.

## Steps

1. 判断修改是内容更新、链接/格式修复、发布公告投影刷新还是敏感信息清理。
2. 更新对应 `mintlify/docs/<version>/**/*.mdx` 页面；新建 Markdown 必须有 `created_at` 和 `updated_at`，更新页面只刷新 `updated_at`。
3. 旧版本页面内容变更必须有明确授权，并在 `mintlify/site-manifest.json manual_overrides` 或对应 release manifest 中记录 `reason`、`confirmed_by`、`confirmed_at`、`files` 和 `summary`；未授权时只能做 broken link、frontmatter、格式、导航引用或敏感信息清理。
4. 新增或 materially 更新用户可见页面时，SHOULD 使用 `mintlify/assets/screenshots/` 下真实系统截图；不得使用原型图、设计稿、未脱敏截图或不可公开运维截图。
5. 运行：

```bash
python scripts/generate-mintlify-docs.py --version <version>
python scripts/validate-mintlify-docs.py
```

6. 若改动源自 release 公告，确认 `releases/vX.Y.Z/announcement.mdx` 仍是发布事实源，Mintlify 只是投影。

## Safety

- 发现敏感信息必须立即移除并报告影响文件。
- 不从产品手册技能修改运行时代码、API、数据库、OpenSpec 范围或 release scope。
- 旧版本页面内容变更必须说明原因；无明确授权时只做链接、格式、敏感信息清理等非语义维护。

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Output

Report changed pages, validation commands, remaining blockers, and preview command.

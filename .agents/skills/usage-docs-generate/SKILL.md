---
name: "usage-docs-generate"
description: "生成或刷新 MoonBox Mintlify 产品手册元数据与公开站点投影"
---

# usage-docs-generate

Use this skill when the user asks `/usage-docs-generate <version>` or wants to generate/update MoonBox public product manual pages for Mintlify.

## Context Budget Guardrails（MUST）

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 先读取 `mintlify/README.md`、目标页面和脚本摘要；不要全量读取 `docs/**`、`issues/**`、`iterations/**` 或历史归档。
- 失败时只展开相关页面、`mint.json`、`site-manifest.json` 或脚本报错片段。

## Input

- `<version>`：可选，默认 `latest`。当前 MoonBox 轻量站点以 `latest` 为默认公开入口；若已建立 `mintlify/docs/vX.Y.Z/`，可传入具体版本。

## Command Order（MUST）

- `/usage-docs-generate` 位于发布计划之后，用于生成或刷新 Mintlify 公开投影；不得替代 `docs/`、`releases/`、`deploy/` 或 OpenSpec 事实源。
- 发布链路中，产品手册命令通常位于 `/release-prepare` 之后、`/image-prepare` 之前；若只刷新 `latest` 手册，也必须运行公开安全校验。
- 页面、`mint.json`/`docs.json`、`site-manifest.json`、release announcement 投影和 AI Usage hook 写入 MUST 严格串行执行。
- 不得把真实 env、密钥、生产私有地址、客户数据或本机绝对路径写入 Mintlify 页面或站点 manifest。

## Must Read

```text
AGENTS.md
rules/document-governance.md
rules/directory-structure.md
rules/release.md
rules/security.md
mintlify/README.md
mintlify/docs/<version>/
scripts/generate-mintlify-docs.py
scripts/validate-mintlify-docs.py
```

## Steps

1. 确认 `mintlify/docs/<version>/` 存在；若不存在，先说明缺少产品手册源页面，不要生成空站点。
2. 运行：

```bash
python scripts/generate-mintlify-docs.py --version <version>
python scripts/validate-mintlify-docs.py
```

3. 若存在 `releases/vX.Y.Z/announcement.mdx`，生成脚本会投影到 `mintlify/releases/vX.Y.Z/announcement.mdx` 并刷新导航。
4. 产品手册页面 SHOULD 引用 `mintlify/assets/screenshots/` 下的真实系统截图；如页面需要截图但当前没有真实系统截图，MUST 记录 blocker，不得使用原型图、设计稿或未脱敏截图替代。
5. 生成或刷新站点投影时，MUST 更新 `mintlify/site-manifest.json` 的 `latest_version`、`versions`、`assets`、`projections` 或 `manual_overrides` 中的相关事实；不得只改 MDX 页面。
6. 如涉及发布准备，继续运行对应 release 门禁：

```bash
python scripts/validate-release.py --release-dir releases/<version> --stage prepare
```

仅当 `<version>` 对应真实 release 目录时运行 release 校验。

## Safety

- MUST NOT 写入真实密钥、真实 `.env`、数据库连接串、Authorization header、Cookie、对象存储凭据、生产私有地址或真实客户数据。
- MUST NOT 将 `mintlify/` 作为唯一事实源；长期产品/部署/发布事实仍分别在 `docs/`、`deploy/`、`releases/` 和 OpenSpec 中维护。
- MUST NOT 把构建产物、`.mintlify/`、`dist/`、`build/` 放入 Git。

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Output

Report version, generated metadata files, validation commands, blockers, and whether docs-site can be previewed through `deploy/scripts/up.sh`.

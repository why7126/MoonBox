---
purpose: ProjectTilesFST Mintlify 轻量治理学习应用报告
content: 记录轻量产品手册治理、Mintlify 站点投影和 docs-site 部署边界在 MoonBox 的适配结果
created_at: 2026-08-09 08:54:59
updated_at: 2026-08-09 08:54:59
owner: MoonBox 产品团队
---

# ProjectTilesFST Mintlify 轻量治理学习应用报告

## 基本信息

- 学习对象：ProjectTilesFST（本地只读项目）
- 学习模式：`/spec-study ProjectTilesFST --focus mintlify` 后确认应用 `mintlify-lightweight-governance`
- 执行时间：2026-08-09 08:54:59
- 承载 Change：`apply-mintlify-lightweight-governance`
- 承载 Sprint：`sprint-002`

## 学习到的治理能力

- 产品手册生成需要有 generated / skipped / pending_confirmation 决策，避免默认生成空文档。
- `mintlify/` 应作为公开站点投影，不替代 `docs/`、`releases/`、`deploy/` 或 OpenSpec 事实源。
- `site-manifest.json` 应记录 latest、版本投影、共享截图资产和人工修正记录。
- Mintlify 校验应覆盖导航、站内链接、图片引用、共享截图 hash、公开安全、构建产物和运行时文件。
- docs-site 服务部署应只读挂载公开产品手册源目录，并在本地预览、生产承载和 release 门禁中记录校验。

## 已采纳内容

- 采纳轻量 `usage_docs.status` 决策门禁，保留 MoonBox 当前 `latest` 优先的产品手册模式。
- 采纳 `site-manifest.json`、导航、链接、截图资产和公开安全校验增强。
- 采纳 docs-site 部署边界：只读挂载 `mintlify/` 和静态预览脚本，不挂载真实 env、运行时数据、数据库卷、对象存储数据或密钥。
- 采纳发布门禁：涉及 Mintlify 站点、docs-site、端口或生产承载方式时，必须运行 Mintlify 校验和 docs-site Compose config 校验。

## 未采纳内容

- 未采纳完整版本化 `releases/vX.Y.Z/usage-docs/` 快照体系；当前 MoonBox 尚未需要每版完整使用文档继承与冻结策略。
- 未采纳强制每个页面必须包含真实系统截图；MoonBox 当前采用 SHOULD 约束和 hash 校验，后续可在对外发布成熟后升级。
- 未切换到 `mintlify/docs.json` 唯一主配置；当前继续兼容 `mintlify/mint.json`。

## 更新文件

- `openspec/changes/apply-mintlify-lightweight-governance/`：新增 Change、设计、任务、追踪和 release/deployment delta spec。
- `rules/document-governance.md`：补充轻量 `usage_docs.status` 和 docs-site 只读部署边界。
- `rules/release.md`：补充产品手册决策和 Mintlify 服务部署发布门禁。
- `rules/directory-structure.md`：补充 docs-site profile 的禁止挂载范围。
- `.agents/skills/usage-docs-generate/SKILL.md`：补充 release 决策、docs-site Compose 校验和输出边界。
- `.agents/skills/usage-docs-update/SKILL.md`：补充 docs-site 影响时的 Compose 校验要求。
- `.agents/skills/usage-docs-validate/SKILL.md`：补充运行时文件、大文件和 docs-site 部署校验范围。
- `scripts/validate-mintlify-docs.py`：增强 env、运行时文件和大体积公开文件扫描。
- `docs/02-deployment.md`、`deploy/README.md`、`deploy/local/README.md`、`deploy/prod/README.md`：补充 docs-site 本地与生产部署边界。
- `mintlify/README.md`：补充产品手册决策和生产承载方案记录要求。
- `docs/spec-logs/CHANGELOG.md`：登记本次学习应用。

## 影响评估

- API：不涉及。
- 数据库：不涉及。
- Web：不涉及运行时代码。
- 客户端：不涉及。
- 管理端：不涉及。
- Orval：不涉及。
- Docker Compose：涉及 docs-site profile 的治理规则和校验要求，未修改 Compose 服务定义。
- 测试：运行治理脚本和 Mintlify 校验；业务测试不适用。

## 校验记录

- `python scripts/validate-sprint-scope.py sprint-002 --item apply-mintlify-lightweight-governance`：通过。
- `openspec validate apply-mintlify-lightweight-governance`：通过。
- `python scripts/validate-mintlify-docs.py`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change apply-mintlify-lightweight-governance --sprint auto`：通过，更新 2 处，错误 0。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change apply-mintlify-lightweight-governance --sprint sprint-002`：通过，warning 0。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `MOONBOX_DEPLOY_ENV_FILE=self-storage-sqlite.env.example docker compose --env-file deploy/local/self-storage-sqlite.env.example --profile self-hosted-storage --profile docs-site -f deploy/local/compose.yml config --quiet`：通过。
- `MOONBOX_DEPLOY_ENV_FILE=external-storage-external-mysql.env.example docker compose --project-name moonbox --env-file deploy/prod/external-storage-external-mysql.env.example --profile docs-site -f deploy/prod/compose.s3-mysql.yml config --quiet`：通过。
- `git diff --name-only -- src`：无输出，本次未修改 `src/`。

## 学习对象只读保护

本次仅对 ProjectTilesFST（本地只读项目）执行只读文件读取和 Git 状态查询，未对学习对象执行写入、格式化、安装、生成、迁移、测试修复、清理、提交或分支操作。

## 后续建议

- 若 MoonBox 后续进入正式公开文档运营，可通过新的 OpenSpec Change 升级到完整版本化 usage docs 快照体系。
- 若迁移到 Mintlify `docs.json`，需同步生成脚本、校验脚本、README 和发布门禁。

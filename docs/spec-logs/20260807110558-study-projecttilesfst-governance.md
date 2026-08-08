---
purpose: ProjectTilesFST A-E 治理学习应用报告
content: 记录 spec-logs、Mintlify、usage-docs 和 deploy 治理细节在 MoonBox 的适配结果
created_at: 2026-08-07 11:05:58
updated_at: 2026-08-07 23:20:00
owner: MoonBox 产品团队
---

# ProjectTilesFST A-E 治理学习应用报告

## 学习对象

- 对象：`ProjectTilesFST（本地只读项目）`
- 模式：只读学习后按用户确认应用。
- 执行时间：2026-08-07 11:05:58。
- 指令：`/spec-study apply ProjectTilesFST --focus A、B、C、D、E`。

## 学习到的治理能力

- `docs/spec-logs/` 可以同时承载跨项目学习报告和本项目治理迭代日志，并通过 `study` / `governance` 文件名区分。
- 同一次 `/spec-study` 学习应用流程只生成一份正式 `study` 报告；治理资产应用结果汇总进同一份学习报告，不额外生成内容重复的 `governance` 日志。
- `/spec-opt` 完成规范、技能、脚本、目录边界或校验规则迭代后，应形成脱敏治理日志。
- Mintlify 站点源目录应是公开投影，不替代 release、docs、deploy 或 OpenSpec 事实源。
- usage-docs 生成、更新、校验应覆盖 release 决策、旧版本内容修正授权、共享截图资产和公开安全。
- deploy 脚本可在本地演示或 config 校验时回退 `.env.example`，但输出不得泄露真实 env、密钥或连接串。

## 已采纳内容和原因

- A：采纳。MoonBox 已有 `docs/spec-logs/`，升级命名规则和隐私边界成本低，能避免同日多次报告覆盖。
- B：采纳。`/spec-opt` 写治理迭代日志可以沉淀规则变更原因、影响范围和验证结果。
- C：采纳。MoonBox 已有 Mintlify 骨架，补齐 manifest、latest、截图资产和 manual overrides 校验能提升公开站点安全。
- D：采纳。usage-docs 三个技能补充截图、旧版本授权和站点投影门禁，减少文档漂移。
- E：采纳。MoonBox deploy 脚本已具备 env 回退和地址输出，本次将安全边界固化到文档。
- F：采纳。ProjectTilesFST 后续新增 spec-study 单报告去重规则，正好修正本次 A-E 应用曾同时生成 `study` 与重复 `governance` 文档的问题。

## 未采纳内容和原因

- 未采纳 ProjectTilesFST 的 miniapp 命令、瓷砖业务脚本、TileSpec 视觉采集和腾讯 COS 专项命名；这些不属于 MoonBox 当前启用范围。
- 未恢复 `.cursor/`、`.codex/`、`.claude/`、`.kiro/`、`.opencode/` 等入口；MoonBox 继续保持 `.agents/skills/` 单入口。
- 未复制 ProjectTilesFST 的长脚本实现；仅按 MoonBox 现状增强轻量校验和治理规则。

## 更新文件清单

- `.agents/skills/spec-study/SKILL.md`：学习报告命名升级为 `YYYYMMDDhhmmss-study-xxx.md`，增加隐私禁写。
- `.agents/skills/spec-opt/SKILL.md`：新增治理迭代日志规则。
- `.agents/skills/usage-docs-generate/SKILL.md`：补充截图资产和 site manifest 更新门禁。
- `.agents/skills/usage-docs-update/SKILL.md`：补充旧版本内容修正授权和截图资产要求。
- `.agents/skills/usage-docs-validate/SKILL.md`：补充 manifest、链接、截图资产和 manual overrides 校验范围。
- `AGENTS.md`、`docs/README.md`、`rules/directory-structure.md`、`rules/agent-context-budget.md`：同步 spec-logs、spec-study、spec-opt 和日志隐私边界。
- `docs/spec-logs/README.md`：升级为规范工程日志目录说明。
- `mintlify/README.md`：补充站点投影、latest、manual overrides 和共享截图资产规则。
- `scripts/validate-mintlify-docs.py`：增加 `docs.json/mint.json` 主配置兼容、site manifest、站内链接、共享截图资产 hash 校验。
- `deploy/README.md`：固化 env 回退、服务自愈和安全输出边界。
- `openspec/changes/apply-projecttilesfst-governance-refinements/`：新增 proposal、design、tasks、trace 和 delta specs。
- `openspec/changes/avoid-duplicate-spec-study-reports/`：新增 spec-study 单报告去重规则 Change。
- `docs/spec-logs/20260807110558-governance-projecttilesfst-a-e.md`：删除同一 `/spec-study` 流程下内容重复的 governance 日志，正式记录保留在本 study 报告。

## 影响范围

- API：无影响。
- 数据库：无影响。
- Web：无业务实现影响。
- 客户端：无影响。
- 管理端：无业务实现影响。
- Orval：不需要。
- Docker Compose：未改变拓扑；仅补充部署治理文档。
- 测试：业务测试不适用；执行治理和脚本校验。

## 校验命令和结果

- `openspec validate apply-projecttilesfst-governance-refinements`：通过。
- `bash scripts/validate-openspec.sh`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change apply-projecttilesfst-governance-refinements --sprint auto`：通过，更新 2 处，错误 0。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change apply-projecttilesfst-governance-refinements --sprint sprint-001`：通过，`data/ai-usage/sprints/sprint-001.json` 已刷新，warning 0。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-sprint-scope.py sprint-001 --item apply-projecttilesfst-governance-refinements`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-generated-docs.py --strict`：通过，仍保留 1 个既有未决占位提示。
- `python scripts/validate-env-ignore-policy.py`：通过。
- `python scripts/validate-mintlify-docs.py`：通过。
- `python deploy/scripts/validate-env.py --domain local --environment self-storage-sqlite --env-file deploy/local/self-storage-sqlite.env.example --profile self-hosted-storage`：通过。
- `openspec validate avoid-duplicate-spec-study-reports`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change avoid-duplicate-spec-study-reports --sprint auto`：通过，更新 2 处，错误 0。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change avoid-duplicate-spec-study-reports --sprint sprint-001`：通过，`data/ai-usage/sprints/sprint-001.json` 已刷新，warning 0。
- `python scripts/validate-sprint-scope.py sprint-001 --item avoid-duplicate-spec-study-reports`：通过。
- `python scripts/sync-workflow-status.py --check`：通过，更新 0 处，错误 0。

## 后续去重修正

2026-08-07 后续学习 ProjectTilesFST `avoid-duplicate-spec-study-reports` 后，本报告作为 ProjectTilesFST A-E 治理学习应用的唯一正式 study 报告继续维护。原 `docs/spec-logs/20260807110558-governance-projecttilesfst-a-e.md` 与本报告内容重复，已按去重规则删除。

## 后续应用：命令执行顺序 A/B/C/D

- 执行时间：2026-08-07 23:20:00。
- 指令：`/spec-study apply ProjectTilesFST --focus A/B/C/D`。
- 学习对象：`ProjectTilesFST（本地只读项目）`。
- 学习模式：只读学习后按用户确认应用到 MoonBox 治理资产。

### 学习到的治理能力

- A：命令执行顺序应提供速查文档，覆盖 REQ/BUG、Sprint、OpenSpec、发布、镜像和产品手册链路。
- B：关键 Skill 应内置 `Command Order` 小节，避免不同命令各说各话。
- C：下一步命令参数应保留来源身份：REQ 链路继续使用 `REQ-*`，BUG 链路继续使用 `BUG-*`，只有纯治理 Change 使用 `<change-id>`。
- D：写同一事实源的步骤必须串行执行，尤其是 `sprint.yaml`、Workflow Sync、Issue promote、AI Usage snapshot 和 release/image/doc manifest。

### 已采纳内容和原因

- 采纳命令顺序速查文档，新增 `docs/08-command-execution-order.md` 并加入 `docs/README.md` 索引，便于跨命令查阅。
- 采纳关键 Skill `Command Order` 小节，覆盖 req/bug opsx、opsx apply/modify/archive、sprint propose/archive、release propose、image prepare、usage docs generate。
- 采纳下一步参数链路规则，降低 `/opsx-apply` 后把 REQ/BUG 退回裸 Change ID 的追溯风险。
- 采纳串行事实源写入规则，避免 Sprint、Workflow Sync、Issue promote、AI Usage 和产品手册 manifest 并行写入造成漂移。

### 未采纳内容和原因

- 未复制 ProjectTilesFST 的项目专属命令细节、业务术语或脚本实现；MoonBox 仅吸收适合当前 `.agents/skills/` 单入口和 OpenSpec/Sprint/Release 治理的规则。
- 未改变业务代码、API、数据库、Web、管理端、客户端或 Docker Compose 拓扑；本次仅属于治理规范和命令技能优化。

### 本次更新文件清单

- `docs/08-command-execution-order.md`：新增命令执行顺序、下一步参数和串行执行规则。
- `docs/README.md`：加入命令执行顺序文档索引。
- `AGENTS.md`：增加“命令顺序 / 工作流编排”读取路由。
- `rules/agent-context-budget.md`、`rules/document-governance.md`：固化命令顺序和串行事实源写入边界。
- `.agents/skills/req-opsx/SKILL.md`、`.agents/skills/bug-opsx/SKILL.md`、`.agents/skills/opsx-apply/SKILL.md`、`.agents/skills/opsx-modify/SKILL.md`、`.agents/skills/opsx-archive/SKILL.md`：补充 OpenSpec 主链路顺序和参数传递规则。
- `.agents/skills/sprint-propose/SKILL.md`、`.agents/skills/sprint-archive/SKILL.md`、`.agents/skills/release-propose/SKILL.md`、`.agents/skills/image-prepare/SKILL.md`、`.agents/skills/usage-docs-generate/SKILL.md`：补充 Sprint、发布、镜像和产品手册链路顺序。
- `openspec/changes/apply-projecttilesfst-command-order/`：新增本次治理应用 Change。
- `iterations/change/sprint-001/sprint.yaml`：将本次治理 Change 纳入 Sprint scope。

### 影响范围

- API：无影响。
- 数据库：无影响。
- Web：无业务实现影响。
- 客户端：无影响。
- 管理端：无业务实现影响。
- Orval：不需要。
- Docker Compose：无拓扑变化。
- 测试：业务测试不适用；执行治理和 OpenSpec 校验。

### 本次校验命令和结果

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate apply-projecttilesfst-command-order`：通过。
- `python scripts/validate-sprint-scope.py sprint-001 --item apply-projecttilesfst-command-order`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change apply-projecttilesfst-command-order --sprint auto`：通过，更新 2 处，错误 0。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change apply-projecttilesfst-command-order --sprint sprint-001 --json`：通过，`usage_mode: actual`，`warning_count: 0`。
- 学习对象只读复核：学习对象存在自身未提交改动；本次只执行只读命令，未修改学习对象。

## 学习对象只读保护结果

学习过程中仅对 ProjectTilesFST 执行 `sed`、`find`、`rg`、`git status`、`git diff` 等只读命令。未在 ProjectTilesFST 路径下执行写入、安装、格式化、迁移、生成、清理、提交或重置命令。

ProjectTilesFST 在学习前后均存在其自身未提交的治理改动；本次任务未修改这些源项目文件。

## 后续建议

- 后续 `/spec-opt` 归档前确认已生成或更新 `YYYYMMDDhhmmss-governance-xxx.md`。
- 后续 Mintlify 产品手册加入真实系统截图时，将截图记录到 `mintlify/site-manifest.json assets` 并运行校验。

---
name: "git-sync"
description: "按交付范围安全暂存、提交、创建正式发布标签并同步远程 Git 仓库"
created_at: 2026-10-09 10:20:05
updated_at: 2026-10-25 22:25:00
---

# git-sync

当用户要求将当前项目改动提交并同步到远程仓库时使用 `/git-sync`。本命令执行 Git 写操作，但不代替 `/opsx-apply`、发布门禁或业务验收。用户仅要求检查时使用 `/git-check`。

## 浏览器自主取证（MUST）

浏览器清单超时、单个工具失败或终端 HTTP 探测失败时，先按 `rules/root-cause-evidence.md` §5.0 检查现有标签页、直接连接浏览器窗口并尝试可行替代入口；区分旧页面展示和当前服务连通性，完成这些检查后才判断是否无法访问。

测试、验收或冲突判断需要产品运行态证据时，可在已有权限和任务范围内通过浏览器自主取证，优先复用 Codex 侧边浏览器，无需人工二次确认。只有无法访问、权限不足、操作超出已授权边界或自主取证后证据仍不足时，才按 `rules/root-cause-evidence.md` 给出人工补证步骤；取证材料必须脱敏。

## Context Budget Guardrails（MUST）

- 遵守 `rules/agent-context-budget.md`；同一会话已读且未变更的规则和 Skill 用摘要承接，不重复全量读取。先用 `rg -l`、`rg --files`、`git diff --name-only` 定位，再分段读取必要片段。
- **Guided User Feedback Contract**：需要决策时优先使用原生交互卡片；工具层不支持时先声明降级原因，再降级为文本结构化选项。两者均提供「结构化选项 + 推荐项 + 可补充说明」，每轮仅聚焦 1-3 个关键决策，并承接已有回答动态收敛。
- **Force-proceed Follow-up Guardrails**：`force-proceed` 只继续非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG。建议后续 capture 时，逐条给出建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令，并注明“未自动创建 Issue”。仅在用户明确授权自动 capture 时执行 `/req-capture`、`/bug-capture` 或 `/capture`，随后运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

## 输入与默认范围

- 可指定 REQ、BUG、Change、Sprint、文件路径、目标分支和发布版本。
- 默认只处理本次明确的交付范围。若工作区有多条链路，先根据文件、Change trace 和 Sprint 范围形成候选清单；归属不明时使用原生交互卡片给出 2–4 个互斥选项及推荐项，允许补充说明。客户端不支持卡片时说明原因，再用文本结构化选项。
- 保留调用前已有的暂存状态；现有 staged 文件若不属于本次范围，先向用户展示并等待范围决策。禁止在混合工作区直接 `git add .` 或 `git add -A`。

## 阶段 1：仓库与交付状态

1. 读取 `AGENTS.md`、`openspec/project.md`、`rules/global.md`、`rules/language.md`、`rules/agent-context-budget.md`，再读取 `rules/security.md`、`rules/release.md`、`.agents/skills/git-check/SKILL.md` 和相关交付事实源；已读且未变更的内容用摘要承接。
2. 检查 `git status --short --branch`、当前分支与 upstream、`git remote -v`、staged/unstaged/untracked 文件清单。仅报告必要摘要，避免输出敏感内容。
3. 对候选提交范围核验关联 REQ、BUG、Change、Sprint 的状态与必要验证。未完成或来源不明的改动不得伪称已交付；可按独立治理或工作进度提交，但提交说明应准确描述实际状态。

## 阶段 2：排除与暂存

1. 用 `git check-ignore -v`、`git ls-files`、现有 `.gitignore` 和 `bash scripts/project-python.sh scripts/validate-env-ignore-policy.py` 区分未跟踪、被忽略、已跟踪文件。`/git-check` 的 error 为阻断项。
2. 对确属本地运行数据的新类型，按最小匹配范围更新 `.gitignore`；不要忽略同目录下的示例、模板或需提交的验证证据。已跟踪文件不会因 `.gitignore` 自动移出索引；需要移出时先确认归属和历史泄漏风险，再用精确路径执行 `git rm --cached --`，保留本地文件。绝不自动删除本地数据或改写 Git 历史。
3. 用精确路径或交互式 hunk 选择暂存；检查 `git diff --cached --name-status`、`git diff --cached --stat`、必要的聚焦 diff 和 `git diff --cached --check`。重复查看实际暂存内容，避免把混合文件的无关 hunk 纳入本次提交。
4. 运行 `bash scripts/project-python.sh scripts/git-check.py`。如扫描器不能覆盖本次新增文件或待推送的历史提交，补做对应范围检查；真实凭证或客户数据一旦进入待推送历史，停止推送并报告清理与轮换需求。warning 记录处置结论，error 修复后重跑。

## 阶段 3：提交

1. 从实际 staged diff、Issue/Change trace、Sprint 交付记录提炼提交标题与正文：分别写明已完成需求、已修复问题及治理改动。证据不足时只写可核实的文件或行为变化，不编造验收结论。
2. 提交前报告拟提交范围、排除项、安全扫描结果和拟用提交信息；若范围不清或触及用户已有 staged 内容，先用引导式选项解决。范围确定后执行 `git commit`，核对新 commit SHA 与提交文件清单。
3. 不自动 amend、squash、reset、清理历史或覆盖用户既有提交。

## 阶段 4：正式版本标签

1. 仅当 `releases/vX.Y.Z/release.json`、产品版本事实源、发布验证和负责人确认共同表明本次确为正式新增版本时，判断是否需要 `vX.Y.Z` tag。普通提交不打 tag；镜像 tag 不等于 Git tag。
2. 创建前检查本地和远程同名 tag。已存在且指向目标提交时复用；指向其他提交时阻断，不移动、不覆盖。创建 annotated tag 并记录来源版本和提交。
3. 发布门禁未完成时只报告待补事项，不创建 tag。

## 阶段 5：远程同步与冲突

1. 确认 push 目标与 upstream，执行 `git fetch` 后比较本地与远程的 ahead/behind 状态。禁止 `--force`、`--force-with-lease`、删除远程引用或自动覆盖 tag。
2. 若远端领先或分叉，按仓库既有策略整合。发生冲突时逐文件核对双方意图；可确定且属于本次授权范围的冲突解决后，重跑相关测试、`git diff --check` 与安全扫描。无法确定意图时保留现场，列出冲突路径和具体决策，不猜测覆盖。
3. 确认分支为快进可推送后推送指定分支，核对远程 commit。若创建了正式版本 tag，再单独推送该 tag 并核对远程指向。网络或权限失败只报告状态，不伪称同步完成。

## 输出

报告提交范围、排除项、检查结果、commit、分支与远程状态、tag 状态、冲突或阻断项。若未完成推送，明确停在哪个阶段。输出「下一步」「待用户决策/处理」和「执行链路复盘」，复盘包含链路状态、问题证据、规范优化建议及“未自动创建 Issue/Change”。不输出密钥、真实 env、客户数据、未脱敏日志或本机绝对路径。

## Command Execution Review Hook（MUST）

遵守 `.agents/skills/workflow-sync/SKILL.md` 的执行链路复盘要求；链路状态依据实际校验与远端结果，问题证据引用聚焦且脱敏的检查结果，无可复用问题时规范优化建议写“无明显优化点”，默认未自动创建 Issue/Change。

## Final Output Contract（MUST）

「下一步」仅列可直接执行的动作；「待用户决策/处理」仅列缺失输入和需选择事项，两处不得重复同一事项。提交或推送未完成时明确说明阶段、原因和可恢复动作；不得把计划写成已完成结果。
不得输出本段规则、尖括号占位符、MUST/SHOULD 规范语句或与当前命令无关的通用示例。

## 面向用户的表达

面向用户的输出遵循 `rules/language.md` 的“产品经理视角沟通”：先讲业务结果和用户影响，优先日常语言，必要技术术语随文解释；决策说明体验、成本、时间和风险。

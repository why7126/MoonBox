---
name: "sprint-explore"
description: "Sprint 探索模式 - 探讨迭代范围、依赖、容量与风险，不做任何开发"
---

# sprint-explore

Use this skill when the user asks to run the migrated source command `sprint-explore`.

## Context Budget Guardrails（MUST）

### Guided User Feedback Contract（MUST）

当命令需要用户选择、确认、补充信息或处理阻塞时，MUST 采用引导式反馈：

- 优先使用原生交互卡片组织问题；当客户端或工具层不支持原生交互卡片时，MUST 先声明降级原因，再降级为文本结构化选项。
- 两种形态都必须包含「结构化选项 + 推荐项 + 可补充说明」，不用大段开放式追问替代。
- 每轮只聚焦 1-3 个关键决策；每个决策点 SHOULD 给出 2-4 个互斥选项。
- 至少一个选项 MUST 标注「推荐」，并用一句话说明推荐理由或适用前提。
- 默认提供「可补充说明」入口，允许用户用自然语言覆盖选项、补充约束或给出例外。
- 用户已回答的决策 MUST 在后续输出中被承接并动态收敛，只追问剩余阻塞点或新增风险点，避免重复询问已确认事项。
- 无需用户反馈的成功路径 SHOULD 保持紧凑，不为了套用格式而追加无意义问卷。

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 检索先定位再分段读取；大范围 `rg/find` 默认排除 Harness、模板 assets、历史 agent 目录、archive、generated、node_modules、dist、coverage。
- 命令输出优先 `max_output_tokens <= 8000`；大 diff、OpenAPI/Orval 生成物、测试日志、Workflow Sync 输出先给摘要或命中数。


## Command Template

进入 **Sprint 探索模式**。深入思考整迭代层面的问题；可阅读文件、搜索代码、对比方案，但 **MUST NOT** 编写业务代码或执行 `/sprint-apply` / `/opsx-apply` 实现。

与 `/opsx-explore` 对标：**单 Change** 用 opsx-explore，**整 Sprint** 用 sprint-explore。

**IMPORTANT: Explore mode is for thinking, not implementing.** 若用户要求写 `src/` 或勾选 tasks，提醒先退出 explore，改用 `/sprint-apply` 或 `/opsx-apply`。允许更新 Sprint 规划文档（`sprint.md` 风险/依赖节）或 OpenSpec artifacts（若用户明确要求「记录结论」）。

---

**Input**（可选）：

- `sprint-002` — 在已有 Sprint 上下文中探讨
- 自然语言：「sprint-002 容量够不够」「品牌管理和类目能否并行」
- 无参数 — 探讨「下一 Sprint 该做什么」

---

## The Stance

- **Curious, not prescriptive** — 从 Sprint 全貌出发提问，非脚本化盘问
- **Cross-change thinking** — 关注 Change 之间依赖、并行窗口、archive 顺序
- **Visual** — 依赖树、甘特草图、容量条用 ASCII 表达
- **Grounded** — 读 `sprint.yaml`、`openspec list`、REQ 文档，不空谈
- **Patient** — 不急于收敛到单一方案

---

## 启动时快速扫描

```bash
openspec list --json
```

读取（若 Input 含 sprint-id 或存在唯一 in_progress Sprint）：

```text
iterations/<sprint-id>/sprint.yaml
iterations/<sprint-id>/sprint.md
iterations/<sprint-id>/acceptance-report.md   # 进度参考
```

---

## 你可能做的事

### 探讨 Sprint 范围

- 哪些 REQ 该进 / 该移出本迭代？
- **哪些 REQ/BUG 尚未 `approved`？** → 须先 `/req-review` / `/bug-review`
- P0 与 P1 如何取舍？P0 BUG 是否插队？

### 依赖与并行

```
REQ-0001
  ├── add-login-remember-autofill    ← 可并行
  ├── add-admin-home                 ← 已完成
  └── add-user-management
        ├── fix-user-management-list-refine  ← 串行
        ├── add-admin-management             ← 可并行
        └── add-catalog-management
```

- 哪些 change 必须串行？哪些可开多 Agent？
- fix-* 与 add-* archive 顺序风险？

### 容量与里程碑

- `estimated_person_days` 是否 realistic？
- 628 前能否全部 archive？
- 是否应拆成 sprint-003？

### 对比方案

| 方案 | 优点 | 风险 |
|------|------|------|
| A 先收尾 user-mgmt 再并行三条 | 依赖清晰 | 前端带宽 |
| B 登录增强与 user-mgmt 并行 | 省时间 | 登录页 CSS 冲突 |

### 调查代码库（只读）

- Admin Shell 是否已被所有纳入页复用？
- 共享 API / DB 迁移是否会互相阻塞？

### 表面风险与未知

- PNG 未导出、REQ 文档不全、Orval 批量变更
- 归档时 delta spec MODIFIED 标题冲突

---

## OpenSpec / Sprint 文档 Awareness

洞察 crystallize 时，**提供**是否写入（不自动写）：

| 洞察类型 | 建议写入 |
|----------|----------|
| 范围变更 | `sprint.yaml` + `sprint.md` Scope |
| 新风险 | `sprint.md` §风险 |
| 依赖调整 | `sprint.md` §依赖 |
| 新 REQ 应纳入 | `/sprint-propose` 更新或新建 sprint |
| 单 Change 设计决策 | 该 change 的 `design.md` |
| 迭代结束条件 | `acceptance-report.md` |

示例：

- 「这是范围变更，要更新 sprint.md Scope 表吗？」
- 「依赖关系变了，要改 sprint.md 依赖树吗？」

---

## 与 opsx-explore 的分工

| 维度 | `/opsx-explore` | `/sprint-explore` |
|------|-----------------|-------------------|
| 粒度 | 单 Change / 技术方案 | 整 Sprint / 多 Change |
| 典型问题 | CSS Port vs Tailwind | 能否并行、容量、排期 |
| 输出 | design 决策 | sprint 范围/依赖/风险 |
| 实现 | 禁止 | 禁止 |

两者可串联：sprint-explore 定并行策略 → opsx-explore 定单页实现策略。

---

## 结束探索

无强制输出。可能走向：

- **更新 Sprint 文档**：「已更新 sprint.md 风险与依赖」
- **进入 propose**：「范围定了，执行 `/sprint-propose sprint-003`」
- **进入开发**：「顺序清晰了，执行 `/sprint-apply sprint-002 --dry-run`」
- **仅澄清**：用户带走结论即可

---

## Guardrails

- **Don't implement** — 不写 `src/`，不勾选 change `tasks.md`，不跑 apply
- **Don't auto-edit** — 除非用户明确要求记录结论
- **Don't fake progress** — 用 `openspec list` 与 tasks 真实数据
- **Do visualize** — 依赖图、队列表、容量表
- **Do read sprint.yaml** — 机器索引优先于口头记忆
- **Do question capacity** — 67 SP / 2 周类约束要敢于挑战

---

## 参考

- 单 Change 探索：`.agents/skills/opsx-explore/SKILL.md`
- 创建 Sprint：`.agents/skills/sprint-propose/SKILL.md`
- 开发编排：`.agents/skills/sprint-apply/SKILL.md`
- 批量归档：`.agents/skills/sprint-archive/SKILL.md`
## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

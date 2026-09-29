---
title: Capture 创建前去重门禁提案
created_at: 2026-09-16 22:42:16
updated_at: 2026-09-16 22:42:16
---

# Capture 创建前去重门禁提案

## 背景

`/capture`、`/req-capture` 和 `/bug-capture` 当前会读取 `_registry.yaml`，但主要用于分配编号、更新索引和保持状态同步。创建前缺少明确的重复/相似 Issue 检查门禁，导致同一需求、同一缺陷或对已有 Issue 的小幅补充可能被误建为新的 peer REQ/BUG。

本变更把“创建前重复/相似 Issue 检查”前置为 capture 类命令的固定步骤：先用 `CHANGELOG.md` 和 `_registry.yaml` 建立候选范围，再按需读取现有 `capture.md` / `trace.md` 的标题与摘要，发现疑似重复时先让用户选择关联、更新或确认新建。

## 变更内容

- `/capture` 在分类和拆分后，对 REQ/BUG 分别执行对应类型的重复/相似 Issue 检查。
- `/req-capture` 在分配新 REQ ID 前检查现有需求候选，优先识别已有 REQ refinement、同主题重复或父子关系。
- `/bug-capture` 在分配新 BUG ID 前检查现有缺陷候选，优先识别同页面/同现象/同根因/同修复面的重复记录。
- 三个命令发现疑似重复时，输出候选 Issue、相似原因和处理选项；默认推荐关联/更新原 Issue 或挂父子/关联关系，用户确认非重复后才新建。
- 同步需求/缺陷管理规则、上下文预算规则、AGENTS 入口红线、OpenSpec delta 和治理日志。

## 能力影响

### 新增能力

- `agent-workflow-tooling`: capture 类命令具备创建前重复/相似 Issue 检查门禁。

### 修改能力

- `agent-workflow-tooling`: REQ/BUG capture 从“读取 registry 后直接编号”调整为“先做候选去重，再决定新建、关联或更新”。

## 影响范围

- 技能：`.agents/skills/capture/SKILL.md`、`.agents/skills/req-capture/SKILL.md`、`.agents/skills/bug-capture/SKILL.md`。
- 规则：`AGENTS.md`、`rules/agent-context-budget.md`、`rules/requirement-management.md`、`rules/bug-management.md`。
- OpenSpec：`openspec/archive/2026-09-17-add-capture-dedup-gate/`。
- 治理日志：`docs/spec-logs/`。
- API/DB/Web/管理端/客户端/Orval/Docker Compose：不适用，本变更仅调整治理命令和治理文档，不触达业务运行时代码。

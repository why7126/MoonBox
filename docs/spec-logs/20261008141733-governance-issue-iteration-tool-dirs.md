---
purpose: 治理迭代日志
content: 清理 Issue 与迭代目录工具残留并补目录校验
created_at: 2026-10-08 14:17:33
updated_at: 2026-10-08 14:17:33
owner: MoonBox 产品团队
---

# Issue 与迭代目录工具残留治理

## 迭代目标

清理 `issues/`、`iterations/` 下的空工具目录，防止同类残留绕过项目目录结构校验。

## 变更摘要

- 核对并移除四个空目录；没有删除目录内文件或业务数据。
- 目录校验新增两个治理根的直属 `.agents/`、`.codex/` 检查，空目录和同名符号链接均报错；校验器不自动删除。
- 更新目录规则、Agent 入口与文档索引；纯治理 Change 纳入 sprint-008。

## 影响范围与更新文件

`AGENTS.md`、`rules/directory-structure.md`、`docs/README.md`、`scripts/validate-directory-structure.py`、`openspec/changes/prevent-issue-iteration-tool-dirs/` 和 sprint-008 规划事实源。

API、DB、Web、客户端、管理端、Orval、Docker Compose 均无变更；不需要客户端生成或业务迁移。

## 验证结果

目录结构正向校验通过，四种空目录反向校验均被阻断；Agent 上下文预算、当前 Change 中文优先、文档标题、OpenSpec validate、Sprint scope 和聚焦 diff whitespace 通过。执行证据摘要保存在 Change `trace.md`。

## 后续建议

若目录再次出现，按创建时间和启动命令追查实际写入入口；在无法定位创建者前，不将其归因于某个工具。非空残留先核对内容归属，不由校验器自动删除。

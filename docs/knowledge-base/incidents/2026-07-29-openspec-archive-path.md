---
purpose: OpenSpec 归档路径偏差复盘
content: initialize-project 执行中误用 openspec/changes/archive 的根因、影响和预防措施
created_at: 2026-07-29 23:20:00
updated_at: 2026-07-29 23:20:00
owner: MoonBox 产品团队
---

# OpenSpec 归档路径偏差复盘

## 现象

初始化过程中创建了 `openspec/changes/archive/2026-07-29-build-*` 目录，和项目事实源 `openspec/config.yaml` 中的 `archive_dir: openspec/archive` 不一致。

## 根因

迁移后的部分 Agent 技能文件仍保留旧路径 `openspec/changes/archive/`。执行初始化时优先参考了技能中的示例和归档步骤，没有把技能残留路径与 `openspec/config.yaml`、`rules/document-governance.md`、`rules/directory-structure.md` 的当前事实源做冲突校验。

## 影响

- 归档 Change 可能被放入错误目录，导致 Workflow Sync、发布追溯和目录校验出现分歧。
- `openspec/archive/` 与 `openspec/changes/` 的生命周期边界变模糊。

## 修复

- 将错误目录移动到 `openspec/archive/`。
- 更新 `opsx-archive`、`openspec-archive-change`、`req-opsx`、Sprint、BUG、发布相关技能中的旧路径。
- 在 `scripts/validate-directory-structure.py` 中增加 `openspec/changes/archive` 禁止路径校验。
- 在规则中明确 `openspec/archive/` 是唯一归档目录。

## 预防

后续涉及 OpenSpec 归档路径时，优先以 `openspec/config.yaml`、`rules/document-governance.md` 和 `scripts/validate-directory-structure.py` 为事实源；技能文件只能作为执行说明，发现冲突时必须先修技能或规则。

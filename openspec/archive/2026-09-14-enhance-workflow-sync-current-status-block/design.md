## 背景

Issue `trace.md` 同时存在机器事实源和人读快照。机器事实源包括 Frontmatter 与正文 fenced `yaml`，人读快照可能位于 `## 当前状态`。现有 `patch_issue_trace()` 已对 Frontmatter 与首个 fenced `yaml` 运行 `update_openspec_changes_in_block()`，并通过 `update_current_status_section()` 更新 bullet 状态和阶段。

缺口是 `## 当前状态` 章节内若存在独立 fenced `yaml`，其中的 `openspec_changes` 与 `next` 不会同步，导致当前态快照与 registry / CHANGELOG / trace Frontmatter 分歧。

## 目标

- 让 `## 当前状态` 章节内的 fenced `yaml` 快照跟随 Workflow Sync 派生态更新。
- 复用现有下一步推导 `_issue_next_step()`，保持 REQ/BUG 链路继续使用完整 Issue ID。
- 复用并扩展现有 `openspec_changes` 块更新逻辑，兼容旧 scalar 条目。
- 控制影响范围，避免修改 Readiness、验收、历史示例和其他语义代码块。

## 非目标

- 不重写所有历史 Issue 文档。
- 不引入标准 YAML round-trip 依赖。
- 不改变 CHANGELOG 当前态看板、registry 或 Sprint 派生表语义。
- 不触碰业务 `src/`、API、数据库或前端实现。

## 实现方案

1. 新增 `ensure_openspec_change_in_block()`：先调用既有 `update_openspec_changes_in_block()`，若目标 Change 不存在则在 `openspec_changes` 节点下补入 `{change_id, status}`。
2. 新增 `update_current_status_yaml_block()`：基于 `_issue_next_step()` 写回 `next`，并遍历 `change_status_map` 同步 `openspec_changes`。
3. 扩展 `update_current_status_section()`：继续保留 bullet 状态/阶段同步；仅在 `## 当前状态` 章节内匹配第一个 fenced `yaml` 代码块并替换其内容。
4. `patch_issue_trace()` 将当前 `change_status_map` 传入 `update_current_status_section()`。
5. 单元测试构造含旧 scalar `openspec_changes` 与旧 `next` 的 trace，验证同步后升级为结构化 Change 状态和正确下一步命令。

## product_data_collection_observability

```yaml
status: not_applicable
affected_layers: []
reason: 本变更仅增强 Agent Workflow 治理脚本对 Markdown trace 文档正文当前态块的派生同步，不新增或修改 API、数据库、请求日志、行为事件、Task Trace、请求封装、对象存储或运行时产品数据采集。
validation: 通过聚焦单元测试、Workflow Sync dry-run/check、OpenSpec 与目录治理校验确认；业务运行时测试不适用。
```

## 风险

- 如果历史文档在 `## 当前状态` 下存在非当前态用途的第一个 fenced `yaml`，可能被同步。当前实现通过章节名和首个代码块限定范围，避免跨章节误改。
- 轻量字符串更新无法保持复杂 YAML 注释或锚点；当前 trace 快照未依赖这些能力，后续若引入复杂 YAML 可评估标准 round-trip 库。

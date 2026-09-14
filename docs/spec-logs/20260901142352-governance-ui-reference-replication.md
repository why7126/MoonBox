---
purpose: UI 参考稿复刻治理流程
content: 建立附件反向工程、组件级视觉契约、selector 映射、computed style 采样、分批实现与验收门禁
created_at: 2026-09-01 14:23:52
updated_at: 2026-09-13 16:07:10
owner: MoonBox 产品团队
---

# UI 参考稿复刻治理流程

## 迭代目标

建立 UI 参考稿复刻治理流程，在 explore、req 和 opsx 阶段引入附件反向工程、组件级视觉契约、selector 映射、computed style 采样清单、分批实现与验收门禁，避免 UI 一对一复刻退化为逐元素问答返修。

## 变更摘要

- 新增 UI Reference Replication Contract，区分一对一复刻、风格迁移和局部一致。
- 将参考稿拆解从返修阶段前移到 `/explore`、`/req-complete` 和 `/req-opsx`。
- 要求 Change `design.md` 承接组件清单、selector 映射、computed style 采样和分批实现计划。
- 要求 `/opsx-apply` 和 `/opsx-modify` 按批次验证，不再只用整体观感关闭。
- 要求 `/opsx-archive` 复核最终截图、computed style、selector 映射和 REQ/Change 证据一致。

## 影响范围

- Agent 工作流：影响 UI 参考稿复刻类 explore、req、opsx 命令。
- 规则文档：补强 UI 设计规则和上下文预算规则。
- 标准文档：补强原型驱动 UI 验收标准。
- OpenSpec：新增纯治理 Change `add-ui-reference-replication-governance`。
- Sprint：纳入 `sprint-004`。

## 更新文件

- `AGENTS.md`
- `rules/ui-design.md`
- `rules/agent-context-budget.md`
- `docs/standards/prototype-ui-acceptance.md`
- `docs/spec-logs/CHANGELOG.md`
- `.agents/skills/explore/SKILL.md`
- `.agents/skills/req-complete/SKILL.md`
- `.agents/skills/req-opsx/SKILL.md`
- `.agents/skills/opsx-apply/SKILL.md`
- `.agents/skills/opsx-modify/SKILL.md`
- `.agents/skills/opsx-archive/SKILL.md`
- `openspec/archive/2026-09-01-add-ui-reference-replication-governance/`
- `iterations/change/sprint-004/sprint.yaml`

## 验证结果

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：未通过；根目录存在既有未登记目录 `.vite`，非本次治理变更新增。
- `openspec validate add-ui-reference-replication-governance`：通过。
- `python scripts/validate-sprint-scope.py sprint-004`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change add-ui-reference-replication-governance --sprint auto`：通过，解析到 `sprint-004`。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change add-ui-reference-replication-governance --sprint sprint-004 --json`：已运行，返回 `warning/unavailable`，原因是当前会话无可持久化 command-run token 事件。

## 分层影响声明

- API：不适用，未修改接口契约。
- DB：不适用，未修改数据结构。
- Web：不修改运行时代码；后续 Web UI Change 需执行参考稿复刻门禁。
- 客户端：不适用。
- 管理端：不修改运行时代码；后续后台 UI 对齐任务需执行参考稿复刻门禁。
- Orval：不适用。
- Docker Compose：不适用。

## 后续建议

后续可将 UI Reference Replication Contract 的字段完整性接入脚本校验，例如检查 Change `design.md` 是否包含 selector 映射、computed style 采样清单和分批验收记录；另需按项目策略处理既有未登记根目录 `.vite`。

## 历史定位纠正

2026-09-13 16:07:10：初建 ID 保持不变，当前入口指向 2026-09-01 归档；2026-09-02 动作矩阵强化独立为 enhance-ui-reference-replication-action-matrix。历史验证结论保持原样。

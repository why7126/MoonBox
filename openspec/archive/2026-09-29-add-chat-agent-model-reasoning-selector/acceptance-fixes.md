---
change_id: add-chat-agent-model-reasoning-selector
source_requirement: REQ-0035-chat-agent-model-reasoning-selector
sprint: sprint-006
created_at: 2026-09-15 09:33:51
updated_at: 2026-09-15 22:38:04
owner: product
---

# 验收返修台账

## 返修批次

| 时间 | 反馈来源 | 范围判断 | 处理状态 |
|---|---|---|---|
| 2026-09-15 09:33:51 | `/opsx-modify`：需求中心卡片仍提示“验收来源待核实：未找到交付验证记录” | 范围内；属于 Change 交付验证来源入口补齐，不改变 Chat 模型/推理配置业务行为、API、DB、Web UI、权限、部署或观测契约 | 已处理 |
| 2026-09-15 22:38:04 | `/opsx-modify`：模型列表需要与 Codex 实际可选项保持同步 | 范围内；属于服务端默认执行能力配置与验收口径修正，改变接口返回的默认模型候选集合，不改变 API schema、DB schema、权限、部署或前端取数方式 | 已处理 |

## 偏差证据

| 项 | 记录 |
|---|---|
| 期望 | applied Change 在需求中心验收中卡片可识别 Change 内交付验证来源，不展示“未找到交付验证记录”。 |
| 实际 | `trace.md` 已记录 UI 证据清单与变更记录，但缺少需求中心识别白名单内的验证类章节，也未声明 `acceptance_refs`。 |
| 证据链 | 需求中心 Change 索引返回 `验收来源待核实：未找到交付验证记录`；后端识别逻辑接受 `acceptance_refs` 或非空 `验证记录`、`验证摘要` 等章节。 |
| 根因状态 | confirmed。 |

### 2026-09-15 模型列表与 Codex 可选项同步

| 项 | 记录 |
|---|---|
| 期望 | Chat 模型菜单由服务端能力配置返回，并与 Codex 当前实际可选模型保持同步：`GPT-5.6 Sol`、`GPT-6 Astra`、`GPT-5.6 Terra`、`GPT-5.6 Luna`、`GPT-5.5`。 |
| 实际 | `execution_config()` 默认 `models` 仅包含 `gpt-6-astra`、`gpt-5.6-sol`、`gpt-5.6-terra` 三项，且 `display_name` 使用稳定值而非产品展示名。 |
| 证据链 | 用户验收反馈明确要求与 Codex 实际可选项同步；代码证据见 `src/backend/app/chat/settings.py` 默认配置。前端 `Composer` 消费 `capabilities.execution.models`，无独立模型常量。 |
| 根因状态 | confirmed。 |

## 调整内容

- 在 `trace.md` Frontmatter 增加 `acceptance_refs: [acceptance-fixes.md]`。
- 在 `trace.md` 增加非空 `## 验证记录`，汇总既有后端 Chat 回归、前端 Composer 测试、TypeScript、Vite build 与 Playwright UI 证据。
- 在 `tasks.md` 增加验收返修勾选摘要和本台账链接。
- 在 `src/backend/app/chat/settings.py` 将默认模型候选补齐为 Codex 当前 5 款，并将 `display_name` 改为产品展示名；默认模型仍为 `gpt-6-astra`。
- 在后端能力查询测试、前端 Composer 测试和 UI 证据脚本中同步 5 款模型夹具，验证前端继续按接口返回值渲染与发送稳定标识。
- 在 `docs/03-api-index.md`、REQ `requirement.md` 与 `acceptance.md` 回填本次模型清单同步事实。

## 验证证据

- 需求中心 Change 索引复核：本 Change 的归档动作阻断原因为 `None`。
- `openspec validate add-chat-agent-model-reasoning-selector --strict`：通过。
- `python scripts/validate-openspec-language.py --change add-chat-agent-model-reasoning-selector --residual-report`：通过。
- `uv run pytest src/backend/tests/test_chat.py -q`：35 passed, 1 skipped。
- `node_modules/.bin/vitest run src/chat-composer.test.tsx`：9 passed。
- `node_modules/.bin/tsc -b`：通过。
- `node_modules/.bin/vite build`：通过。

## REQ 子文档一致性扫尾检查

- 已检查现有 `requirement.md`、`acceptance.md`、`trace.md`、`business-flow.md`、`user-stories.md` 与 `prototype/**` 一致性。
- 第一批次只补齐 Change 内交付验证来源入口，不改变需求、验收标准、业务流程、用户故事、原型意图、API/DB/观测契约或 UI 行为，REQ 子文档无需手工更新。
- 第二批次改变默认模型候选集合，已同步 `requirement.md`、`acceptance.md` 与 API 文档；业务流程、用户故事、原型交互、DB 文档、部署文档和安全规则不变，因为取数方式、用户流程、数据结构、部署变量和权限边界均未变化。

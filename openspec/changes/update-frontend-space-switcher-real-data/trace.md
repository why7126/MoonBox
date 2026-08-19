---
change_id: update-frontend-space-switcher-real-data
change_type: update
status: applied
created_at: 2026-08-15 11:07:53
updated_at: 2026-08-15 11:42:00
source_requirement: REQ-0018-frontend-space-switcher-real-data
source_sprint: sprint-003
related_specs:
  - web-catalog-requirement-center-real-data
  - web-catalog-requirement-center
prototype_refs:
  - path: issues/requirements/review/REQ-0018-frontend-space-switcher-real-data/prototype/web/prototype.html
    role: html-structure
  - path: issues/requirements/review/REQ-0018-frontend-space-switcher-real-data/prototype/web/context.md
    role: prototype-context
prototype_gate:
  decomposition: done
  ui_contract: done
  ui_skeleton: done
  visual_acceptance_1440: done
  computed_style: done
  mock_api_boundary: done
  req_final_consistency: done
conflict_resolution:
  status: done
  notes: "REQ-0018 将既有项目治理元数据派生空间升级为后台真实空间事实源；prototype 仅作为结构输入，创建/加入流程继续归属 REQ-0019。"
---

# Change Trace

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-15 11:07:53 | req.opsx | 从 REQ-0018 创建 OpenSpec Change，状态 proposed；等待 /opsx-apply REQ-0018-frontend-space-switcher-real-data。 |
| 2026-08-15 11:42:00 | opsx.apply | 接入需求中心真实空间 BFF、前端空间浮层状态、测试与 1440px UI 证据；状态 applied。 |

## 实现证据

| 项 | 状态 | 证据 |
|---|---|---|
| 后端空间事实源 | done | `src/backend/app/services/requirement_center.py` 查询 `admin_spaces`、`admin_space_members`、`admin_space_products`，只返回当前用户作为负责人或成员加入且非回收空间 |
| 字段白名单 | done | `RequirementCenterWorkspace` 仅暴露前台需要字段，新增 `status`、`readonly`，不返回配额、审计、删除原因、allowed actions |
| 前端 SpaceSwitcher | done | `src/web/src/pages/catalog/RequirementCenterPage.tsx` 使用 context `workspaces`、校验本地最近选择、覆盖 loading/empty/error/frozen/current/create-or-join |
| 1440px 视觉证据 | done | `openspec/changes/update-frontend-space-switcher-real-data/evidence/space-switcher-1440.png`、`space-switcher-1440-empty.png`、`space-switcher-1440-error.png` |
| Computed style | done | `openspec/changes/update-frontend-space-switcher-real-data/evidence/space-switcher-1440-style.json`：`position=fixed`、`z-index=21`、`width=330px`、`overflow=auto`、行高/间距和冻结标记颜色已记录 |
| 关闭交互 | done | `space-switcher-1440-style.json` 记录 `closedByEscape=true`、`closedByOutside=true` |
| API 文档 / OpenAPI | done | `docs/03-api-index.md` 已同步真实空间来源和字段白名单；`src/web/openapi.json` 已刷新。`scripts/generate-openapi-client.sh` 的 Orval 步骤因本地 `src/web/node_modules/.bin/orval` 缺失未执行客户端生成，当前页面未使用生成客户端。 |

## 验证记录

| 命令 | 结果 |
|---|---|
| `pnpm --dir src/web test -- --run src/requirement-center.test.tsx` | pass，Vitest 6 files / 88 tests passed |
| `uv run pytest tests/integration/api/test_requirement_center.py` | pass，8 passed |
| `openspec validate update-frontend-space-switcher-real-data --strict` | pass |
| `python scripts/validate-openspec-language.py` | pass |
| `python scripts/sync-workflow-status.py --event opsx.apply --change update-frontend-space-switcher-real-data --sprint auto --dry-run` | pass，REQ-0018 acceptance pending |

## 需求就绪度

| 项 | 状态 | 证据 |
|---|---|---|
| requirement.md | ready | 已存在并评审通过 |
| user-stories.md | ready | 已补齐 |
| business-flow.md | ready | 已补齐 |
| acceptance.md | ready | 已补齐功能/API/UI/测试/原型 AC |
| trace.md | ready | `status: in_sprint`，`iteration: sprint-003` |
| prototype | ready | `prototype/web/context.md` 与 `prototype/web/prototype.html` 已存在 |

## 影响范围

```yaml
impact:
  backend: true
  web: true
  miniapp: false
  admin: false
  database: false
  storage: false
  api: true
capabilities:
  new: []
  modified:
    - web-catalog-requirement-center-real-data
    - web-catalog-requirement-center
```

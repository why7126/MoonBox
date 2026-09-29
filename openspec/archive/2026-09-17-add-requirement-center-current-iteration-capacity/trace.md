---
change_id: add-requirement-center-current-iteration-capacity
type: add
status: applied
created_at: 2026-09-14 15:12:00
updated_at: 2026-09-17 08:31:24
requirement: REQ-0031-requirement-center-current-iteration-capacity
bug: null
sprint: sprint-006
owner: product
acceptance_refs:
  - acceptance-fixes.md
source: issues/requirements/review/REQ-0031-requirement-center-current-iteration-capacity/
prototype_refs:
  - path: issues/requirements/review/REQ-0031-requirement-center-current-iteration-capacity/prototype/web/prototype.html
    role: html-structure
  - path: issues/requirements/review/REQ-0031-requirement-center-current-iteration-capacity/prototype/web/context.md
    role: prototype-decomposition
prototype_gate:
  decomposition: done
  ui_skeleton: done
  visual_acceptance_1440: done
  req_final_consistency: passed
ui_contract:
  status: drafted
  source: design.md
ui_skeleton:
  status: done
  evidence:
    - openspec/archive/2026-09-17-add-requirement-center-current-iteration-capacity/evidence/capacity-1440.png
visual_acceptance:
  desktop_1440: pass
  mobile_390: pass
  evidence:
    - openspec/archive/2026-09-17-add-requirement-center-current-iteration-capacity/evidence/capacity-1440.png
    - openspec/archive/2026-09-17-add-requirement-center-current-iteration-capacity/evidence/capacity-refresh-failed-1440.png
    - openspec/archive/2026-09-17-add-requirement-center-current-iteration-capacity/evidence/capacity-390-strip.png
    - openspec/archive/2026-09-17-add-requirement-center-current-iteration-capacity/evidence/capacity-modify-1440.png
computed_style:
  status: pass
  evidence:
    - openspec/archive/2026-09-17-add-requirement-center-current-iteration-capacity/evidence/capacity-computed-style.json
    - openspec/archive/2026-09-17-add-requirement-center-current-iteration-capacity/evidence/capacity-modify-computed-style.json
mock_api_boundary:
  status: declared
  source: design.md
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
  reason: 当前迭代容量展示涉及需求中心 Web 展示、刷新/筛选行为，以及后端上下文聚合响应字段和请求日志摘要。
  validation: 实现阶段需验证行为事件采集失败不阻断主流程、容量聚合请求写入脱敏请求日志、错误摘要不含敏感内容、OpenAPI/客户端类型同步；普通查询不新增 Task Trace，若改为异步或批量计算则重新评估。
execution:
  schema_version: 1
  started_at: 2026-09-14 15:36:00
  completed_at: 2026-09-14 15:37:45
  last_event: opsx.apply
---

# Change Trace

## 来源

- REQ：`REQ-0031-requirement-center-current-iteration-capacity`
- Sprint：`sprint-006`
- 需求状态：`in_sprint`
- Change 类型：`add`

## 影响分析

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

## Conflict Resolution

- 原型 HTML 和 context 作为结构与状态输入，最终实现以真实需求中心组件、design.md、acceptance.md、1440px/390px 视觉证据、computed style 和 Mock/API 边界共同验收。
- 当前迭代容量展示作为需求中心现有统计/筛选区域的局部扩展，不重做页面 Shell、侧边栏、9 阶段看板或卡片主动作。
- 容量事实源以 `sprint.yaml`、`scope_estimates[]` 和 `capacity_person_days` 为准，不由前端卡片数量或筛选结果推断。

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-17 08:31:24 | /opsx-archive | 归档前完成 REQ 最终一致性检查：`requirement.md`、`acceptance.md`、`trace.md` 与最终 Change 设计、实现证据、Mock/API 边界、容量口径及 UI 返修证据一致。 |
| 2026-09-14 18:24:52 | /opsx-modify | 根据用户验收反馈，将当前迭代容量条按附件 HTML `.capacity` 模块做局部一致返修：移除可见文案“当前迭代容量”，保留 `aria-label`，改为紧凑横向条、细进度轨和状态点；未调整其他模块。 |
| 2026-09-15 09:33:51 | /opsx-modify | 补齐需求中心可识别交付验证来源：`acceptance_refs` 指向 `acceptance-fixes.md`，并新增非空 `## 验证记录`。 |
| 2026-09-14 15:35:00 | /opsx-apply | 实现当前迭代容量上下文字段、前端容量条、OpenAPI/Orval 类型、API 文档、后端/前端测试和 1440px/390px 视觉证据；普通同步查询不新增 Task Trace。 |
| 2026-09-14 15:12:00 | /req-opsx | 创建 OpenSpec Change，补齐 proposal、design、delta specs、tasks 和 trace。 |

## 验证证据

| 类别 | 证据 | 结果 |
|---|---|---|
| 后端聚合/权限/脱敏 | `uv run pytest tests/integration/api/test_requirement_center.py -k "current_iteration_capacity or returns_real_governance_data or sanitizes_paths"` | 3 passed |
| 前端组件 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx -t "current iteration capacity\|Sprint metrics"` | 2 passed |
| TypeScript | `./node_modules/.bin/tsc -b --pretty false` | pass |
| OpenAPI/客户端 | `uv run python -c "import json; from app.main import app; print(json.dumps(app.openapi(), ensure_ascii=False, indent=2))" > ../web/openapi.json`；`./node_modules/.bin/orval --config orval.config.ts` | pass |
| 视觉 1440px | `capacity-1440.png`、`capacity-refresh-failed-1440.png` | pass；正常、双当前迭代、超量、待核实、刷新失败均可见 |
| 视觉 390px | `capacity-390-strip.png`、`capacity-computed-style.json` | pass；长 Sprint ID、容量比例和待核实提示可见，FAB 缩为 44px 图标按钮避免遮挡文字 |
| 验收返修 UI | `capacity-modify-1440.png`、`capacity-modify-computed-style.json` | pass；容量条不再出现可见“当前迭代容量”标题，保留 Sprint ID、容量比例、来源标签、进度轨和状态点 |
| 返修前端聚焦 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx -t "current iteration capacity"`；`./node_modules/.bin/tsc -b --pretty false` | 1 passed；TypeScript pass |

## 验证记录

| 时间 | 验证项 | 结果 |
|---|---|---|
| 2026-09-15 09:33:51 | 需求中心交付验证来源入口 | pass；`acceptance_refs` 指向 `acceptance-fixes.md`，本节作为非空验证来源章节，避免卡片误报“未找到交付验证记录”。 |
| 2026-09-17 08:31:24 | 归档前 REQ 最终一致性检查 | pass；REQ 文档包与最终 Change 设计、实现证据、Mock/API 边界、容量口径及 UI 返修证据一致。 |
| 2026-09-14 18:24:52 | 当前迭代容量实现与返修验证 | pass；详见 `## 验证证据`、容量视觉证据和 `acceptance-fixes.md`。 |

## Mock/API 边界与观测

- 生产数据来自 `GET /api/v1/requirement-center/context` 的 `current_iteration_capacity[]`，测试和视觉脚本中的容量项仅为 fixture。
- 容量事实源为授权项目内活动 Sprint 的 `sprint.yaml`、`scope_estimates[]` 与 `capacity_person_days`；不使用卡片数量或前端筛选结果推断。
- 本实现不新增 DB、对象存储、部署拓扑、后台异步任务、Task Trace 或流程节点；普通同步查询沿用 ChatRoute/request_logs，前端刷新失败保留上一次成功容量快照。

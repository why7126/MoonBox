---
change_id: add-requirement-center-real-data-integration
status: applied
source_requirement: REQ-0013-requirement-center-real-data-integration
source_sprint: sprint-002
created_at: 2026-08-10 22:12:00
updated_at: 2026-08-11 13:49:52
---

# Trace

## 来源

| 类型 | 路径 |
|---|---|
| REQ | `issues/requirements/archive/REQ-0013-requirement-center-real-data-integration/` |
| Sprint | `iterations/archive/sprint-002/` |
| Prototype context | `issues/requirements/archive/REQ-0013-requirement-center-real-data-integration/prototype/web/context.md` |
| Prototype HTML | `issues/requirements/archive/REQ-0013-requirement-center-real-data-integration/prototype/web/prototype.html` |

## Readiness

```yaml
requirement_status: in_sprint
iteration: sprint-002
readiness: ready
change_type: add
impact:
  backend: true
  web: true
  miniapp: false
  admin: false
  database: false
  storage: false
  api: true
capabilities:
  new:
    - web-catalog-requirement-center-real-data
  modified: []
```

## Prototype Gate

```yaml
prototype_refs:
  - path: issues/requirements/archive/REQ-0013-requirement-center-real-data-integration/prototype/web/context.md
    role: state-decomposition
  - path: issues/requirements/archive/REQ-0013-requirement-center-real-data-integration/prototype/web/prototype.html
    role: html-structure
prototype_gate:
  decomposition: done
  ui_contract: done
  ui_skeleton: done
  visual_acceptance_1440: done
  computed_style: done
  mock_api_boundary: done
  req_final_consistency: done
```

## Conflict Resolution

当前无阻断冲突。REQ-0013 的 prototype 是状态原型，负责真实数据状态容器和 Mock/API 边界；REQ-0012 的已实现页面仍是视觉骨架事实源。实现阶段不得用 REQ-0013 原型重做 REQ-0012 页面结构。

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-08-11 13:49:52 | opsx.modify | applied | 验收返修：空间列表不再由后端固定演示数组返回；在首版治理事实源边界内从 `MOONBOX_GOVERNANCE_ROOT/project.yaml` 派生当前项目空间，成员数由治理对象负责人和当前登录用户计算，空间角色由登录用户角色派生，避免生产 context 暴露 Mock 空间。验证：`uv run pytest tests/integration/api/test_requirement_center.py` 7 passed。 |
| 2026-08-10 23:40:00 | opsx.modify | applied | 验收返修：需求中心页面增加登录守卫，context BFF 增加 Bearer 鉴权；版本 badge 改为读取 `PRODUCT_VERSION`；Docker Compose 后端只读挂载治理事实源并通过 `MOONBOX_GOVERNANCE_ROOT` 指向 `/app/governance`；Web Dockerfile 复制 `src/shared` 以支持真实版本常量；context 请求携带登录 token，数据源缺失返回脱敏 503，避免显示 Mock 或“加载中 / 加载空间中”长期占位。验证：`uv run pytest tests/integration/api/test_requirement_center.py` 5 passed；`pnpm --dir src/web test -- requirement-center.test.tsx admin-auth.test.tsx --run` 5 files / 41 tests passed；`pnpm --dir src/web build` passed；`docker compose config --quiet` passed；`git diff --check -- <touched files>` passed。 |
| 2026-08-10 22:58:00 | opsx.apply | applied | 已新增 `/api/v1/requirement-center/context` BFF、Pydantic schema 与只读聚合服务；数据源限定 REQ/BUG registry、issue trace frontmatter、Sprint yaml、OpenSpec trace/tasks；响应使用字段白名单并脱敏错误。前端需求中心改为 fetch context，生产运行时不再定义 `initialIssues`、`workspaces`、`currentUser` 静态数据，保留测试 fixture。UI 状态覆盖 loading/error/forbidden/empty/retry，保留 `data-state`、`data-stage`、`data-issue-id`、`#themeSwitch` 等选择器。验证：`uv run pytest tests/integration/api/test_requirement_center.py` 3 passed；`pnpm --dir src/web test -- requirement-center.test.tsx --run` 5 files / 39 tests passed；`pnpm --dir src/web build` passed；`openspec validate add-requirement-center-real-data-integration --strict` passed；`python scripts/validate-openspec-language.py --root openspec/changes/add-requirement-center-real-data-integration` passed。1440px 视觉截图：`/private/tmp/req-center-real-1440-second.png`。 |
| 2026-08-10 22:12:00 | req.opsx | proposed | 创建 OpenSpec Change，生成 proposal、design、delta spec、tasks 和 trace；下一步执行 `/opsx-apply REQ-0013-requirement-center-real-data-integration`。 |

# Trace

## Governance Mapping

| 用户诉求 | 落点 |
|---|---|
| UI Contract | `rules/ui-design.md`、`docs/standards/prototype-ui-acceptance.md`、`req-opsx` / `opsx-apply` |
| 前后台一致性 checklist | `rules/ui-design.md`、`docs/standards/prototype-ui-acceptance.md` |
| Skeleton 首轮确认 | `rules/ui-design.md`、`docs/standards/prototype-ui-acceptance.md`、`opsx-apply` |
| 1440px/关键交互截图门禁 | `rules/ui-design.md`、`docs/standards/prototype-ui-acceptance.md`、`opsx-apply`、`opsx-modify` |
| computed style 验收 | `rules/ui-design.md`、`docs/standards/prototype-ui-acceptance.md`、`req-opsx` / `opsx-apply` / `opsx-modify` |
| Mock/API 边界声明 | `rules/ui-design.md`、`docs/standards/prototype-ui-acceptance.md`、`req-opsx` / `opsx-apply` / `opsx-modify` |
| 图标/文案一致性检查 | `rules/ui-design.md`、`docs/standards/prototype-ui-acceptance.md` |

## Boundaries

- API：无运行时 API 变更。
- DB：无数据库变更。
- Web：无 `src/` 前台或后台业务代码变更。
- 客户端：无客户端变更。
- Orval：无 OpenAPI 或客户端生成变更。
- Docker Compose：无部署编排变更。

## Evidence Status

- Governance docs：updated。
- Skill contract：updated。
- OpenSpec delta：validated。
- Workflow Sync：passed，resolved Sprint `sprint-002`。

---
change_id: fix-unified-frontend-login-auth
type: fix
status: applied
created_at: 2026-08-11 23:26:45
updated_at: 2026-08-11 23:38:04
source_bug: BUG-0006-frontend-login-needs-real-frontend-auth
sprint: sprint-002
---

# Trace

## 当前状态

- 状态：applied
- 来源 BUG：BUG-0006-frontend-login-needs-real-frontend-auth
- Sprint：sprint-002
- 下一步：`/opsx-archive fix-unified-frontend-login-auth`

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-11 23:26:45 | bug.opsx | 基于 BUG-0006 创建统一登录与前后台权限边界修复 Change。 |
| 2026-08-11 23:38:04 | opsx.apply | 完成统一登录实现：正常/待激活用户可登录，待激活首次登录自动激活；需求中心改用统一登录态，后台接口继续按当前后台管理员角色授权；前端前台 session 保存 token，普通前台用户不写入后台 session 且不展示“进入后台”。 |
| 2026-08-11 23:38:04 | verify | `uv run pytest tests/integration/api/test_admin_users.py tests/integration/api/test_requirement_center.py` 通过，23 passed。 |
| 2026-08-11 23:38:04 | verify | `pnpm --dir src/web test --run homepage.test.tsx admin-auth.test.tsx requirement-center.test.tsx` 通过，40 passed。 |

## 知识沉淀评估

- 不单独新增 `docs/knowledge-base/incidents/` 事故复盘：本次问题已通过 BUG-0006、OpenSpec Change、API/认证标准文档和测试回归完整留痕，影响边界集中在统一登录与后台授权判定，没有形成需要跨迭代复用的独立事故模板。

## 背景与原因

MoonBox already uses one backend token/session mechanism across the frontend requirement center and admin console, but the formal API is still named `/api/v1/admin/auth/*` and the web client keeps separate frontend/admin session stores. This creates a confusing boundary where shared account and personal-center behavior appears to belong only to admin.

## 变更内容

- **BREAKING** Replace `/api/v1/admin/auth/*` with `/api/v1/auth/*` as the only formal account authentication and personal-center API surface.
- Allow every logged-in user, not only admin users, to read `me`, update their own nickname/avatar URL, change their own password, and upload/read their own avatar through the unified auth domain.
- Keep `/api/v1/admin/**` resource authorization independent: unified auth creates identity, admin APIs still require backend admin permission.
- Replace `moonbox.frontend.session` and `moonbox.admin.session` runtime dependency with a single `moonbox.session` or equivalent unified session store.
- Sync API documentation, OpenAPI metadata, generated client code, backend integration tests, frontend tests, and release/acceptance evidence.

## 能力影响

### 新增能力

- None. This change redefines existing authentication, session, API governance, and personal-center boundaries.

### 修改能力

- `web-admin-auth-system`: Authentication, session validation, logout, current user, password change, personal profile, avatar upload, frontend session storage, and admin authorization boundary move from admin-auth naming to unified account-auth semantics.
- `api-governance`: API contract governance must treat `/api/v1/auth/*` as the canonical documented/generated route set and remove old `/api/v1/admin/auth/*` references.

## 影响范围

- Backend API routes, schemas, services, repositories, session revocation, and avatar upload/read proxy paths.
- Web frontend auth/session clients, route guards, login/logout flows, current user context, requirement center user menu, admin user menu, profile dialog, and password-change flow.
- OpenAPI source, Orval/generated client output, API index, authentication standard documentation, backend pytest coverage, frontend Vitest/Testing Library coverage, and Docker `:3000` avatar upload/readback verification.

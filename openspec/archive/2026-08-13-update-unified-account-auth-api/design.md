## 背景

REQ-0016 makes authentication and personal-center behavior a product-wide account capability instead of an admin-named capability. The change is intentionally breaking: old `/api/v1/admin/auth/*` paths must not remain as aliases, redirects, or hidden compatibility routes.

No `prototype/` exists for this REQ, and the requirement explicitly does not redesign login, user menus, or profile dialogs. UI work is limited to wiring existing views to the unified API/session model and preserving current visual systems.

## 目标

- Provide `/api/v1/auth/login`, `/api/v1/auth/logout`, `/api/v1/auth/me`, `PATCH /api/v1/auth/me`, `/api/v1/auth/change-password`, and unified avatar upload/read paths.
- Make all logged-in users able to edit their own nickname/avatar and change their own password.
- Remove runtime dependency on frontend/admin dual session storage.
- Preserve backend admin authorization for all `/api/v1/admin/**` resources.
- Produce verifiable contract, documentation, generated client, and test evidence for the breaking migration.

## 非目标

- No registration, forgot-password, OAuth, SSO, MFA, refresh token, device list, or multi-device management.
- No visual redesign of login, frontend user menu, admin user menu, or profile dialogs.
- No change to admin user-management resources such as resetting another user's password, freezing users, or deleting users.

## 决策

### D1 Unified Auth Route Boundary

Create a first-class `/api/v1/auth/*` router for account authentication and current-user personal-center behavior. Remove old `/api/v1/admin/auth/*` route registration instead of leaving compatibility aliases.

Backend handlers must derive the target user from Bearer token/session context. `PATCH /api/v1/auth/me` must ignore or reject request-body fields that attempt to set target user ID, username, role, status, permissions, password, or other management data.

### D2 Current User Summary

The current-user summary returned by login and `GET /api/v1/auth/me` should include user ID, username, nickname, avatar URL, role/status facts needed by the UI, `is_super_admin`, and a server-derived `can_access_admin` or equivalent field. The field may control frontend entry visibility, but admin API authorization remains server-side.

### D3 Password Change Revokes Sessions

`POST /api/v1/auth/change-password` must verify current password, validate new/confirmed password, update the password hash, and revoke all sessions for that user. The response must not include a new token, raw session ID, password, hash, or any reusable credential. Frontend must clear unified session and navigate to `/login`.

### D4 Avatar Upload And Read Proxy

Avatar upload belongs under `/api/v1/auth/*` and is available to every logged-in user. Upload accepts JPG, PNG, and WebP up to 2 MB, validates MIME/size/storage write, and returns a persistent URL. Avatar reads must use a protected backend proxy path rather than direct private MinIO URLs, credentials, signatures, or internal object paths.

Historical user rows may still store avatar URLs under `/api/v1/admin/users/avatar/{filename}` from the previous admin-user API. Read models that return current-user or user-list summaries should normalize those stored legacy URLs to `/api/v1/auth/avatar/{filename}` so existing avatars keep rendering after the breaking route migration. This does not re-register the old route as an alias, redirect, or hidden compatibility API.

Frontend avatar rendering must prefer the normalized current-user context returned by `/api/v1/auth/me` or feature context APIs over stale local session snapshots. If a unified session still contains a legacy admin avatar URL, the backend admin shell/profile should refresh the current-user summary via `/api/v1/auth/me` before rendering the protected avatar, while the frontend requirement center should ignore that legacy avatar URL until normalized context is available.

### D5 Single Web Session Store

Web runtime should converge on one session key, such as `moonbox.session`, containing token, expiry, and current-user summary. Login writes only that session. Logout, password change success, 401 auth failure, revoked session, and unusable account state clear that session for both frontend and admin flows.

User-menu and profile-dialog text avatar fallbacks should derive from the current display name using the same two-character initials rule across frontend and admin surfaces, keeping fallback length and background styling consistent when no image is available.

### D6 API Contract And Generated Client

OpenAPI metadata must expose only `/api/v1/auth/*` for authentication/current-user personal-center APIs. Orval/generated clients and handwritten frontend service wrappers must stop referencing `/api/v1/admin/auth/*`.

## 验证计划

- Backend pytest integration coverage for login, logout revocation, me, profile update, password change session revocation, avatar upload/read, removed old auth paths, and admin authorization preservation.
- Backend pytest integration coverage for normalizing stored legacy avatar URLs to the unified auth avatar path in login, `GET /api/v1/auth/me`, and admin user list responses.
- Frontend Vitest/Testing Library coverage for single session storage, login/logout, profile save, avatar upload state machine, password-change relogin flow, 401 cleanup, and admin-entry permission display.
- Static checks or grep evidence showing old `/api/v1/admin/auth/*`, `moonbox.frontend.session`, and `moonbox.admin.session` no longer appear in runtime calls or generated clients.
- Docker local `:3000` evidence for avatar upload, protected read, and frontend/admin current-user echo.

## 风险

- Breaking API migration can leave stale tests, docs, generated clients, or scripts on old admin-auth paths.
- Session-store migration can create one-sided logout if legacy keys are not cleaned during transition.
- Avatar upload can pass in direct backend tests but fail through Docker reverse proxy or browser-accessible protected read paths.
- `can_access_admin` can be mistaken for authorization if backend admin dependencies are weakened.

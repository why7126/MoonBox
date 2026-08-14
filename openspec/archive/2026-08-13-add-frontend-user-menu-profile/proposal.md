---
change_id: add-frontend-user-menu-profile
type: add
status: proposed
created_at: 2026-08-11 17:36:19
updated_at: 2026-08-11 17:36:19
owner: product
source_requirement: REQ-0014-frontend-user-menu-profile
sprint: sprint-002
---

# add-frontend-user-menu-profile

## 背景

MoonBox 前台需求中心已经具备左侧边栏、用户菜单、当前用户上下文、受保护头像读取、空间切换、主题切换、进入后台和退出登录能力。当前用户菜单中的“个人资料”入口仍缺少可用闭环，用户无法在前台需求中心内直接维护自己的头像和昵称。

REQ-0014 已评审并纳入 sprint-002。本 Change 将该需求转为 OpenSpec 变更，仅创建前台个人资料弹窗、头像上传和当前用户上下文刷新能力；实现阶段由 `/opsx-apply REQ-0014-frontend-user-menu-profile` 承接。

## 范围

### 包含

- 前台需求中心用户菜单“个人资料”入口打开 `rc-*` 个人资料弹窗。
- 弹窗仅支持当前登录用户修改头像和昵称。
- 头像上传复用现有对象存储链路和受保护头像读取链路。
- 昵称允许清空，清空后前台用户菜单回退显示用户名。
- 保存成功后直接使用接口返回的最新 user 更新前台当前用户上下文、用户菜单展示和本地会话缓存。
- 覆盖 media-upload 横切验收、原型驱动 UI Gate、1440px 视觉验收和 computed style 验收。

### 不包含

- 不实现密码修改；前台修改密码由 BUG-0004 承接。
- 不实现后台用户管理、角色权限、账号状态或他人资料编辑。
- 不实现头像裁剪、图库选择、批量上传、滤镜或图片处理。
- 不新增移动端、小程序或桌面端能力。

## 影响面

```yaml
impact:
  backend: true
  web: true
  miniapp: false
  admin: false
  database: false
  storage: true
  api: true
capabilities:
  new:
    - web-catalog-user-profile
  modified:
    - web-catalog-requirement-center
    - web-admin-auth-system
```

## 依赖

- REQ-0012-frontend-requirement-center：前台用户菜单、当前用户上下文和 `rc-*` 视觉基础。
- REQ-0011-admin-user-menu-profile：当前用户资料更新、头像上传和持久 URL 约束的复用参照。
- REQ-0004-admin-user-management：头像字段、昵称字段和对象存储头像上传基础。
- REQ-0005-admin-auth-system：认证态、当前用户身份和会话缓存基础。

## 成功标准

- 用户可从前台需求中心用户菜单打开个人资料弹窗。
- 弹窗仅展示头像、昵称和只读账号摘要，不包含密码或后台管理字段。
- 头像上传具备 `idle -> uploading -> done/failed` 状态机，同会话即时预览，保存持久 URL。
- 昵称清空后保存为空值或等价空状态，菜单回退用户名。
- 保存成功后无需刷新页面，前台 currentUser、用户菜单和会话缓存同步更新。
- 通过相关前后端测试、OpenSpec 严格校验、1440px 视觉验收和 Docker `:3000` 上传读取回显边界验收。

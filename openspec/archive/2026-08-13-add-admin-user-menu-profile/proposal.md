---
change_id: add-admin-user-menu-profile
status: proposed
type: add
source_requirement: REQ-0011-admin-user-menu-profile
source_sprint: sprint-002
created_at: 2026-08-10 09:30:11
updated_at: 2026-08-10 09:30:11
---

# 新增后台用户菜单栏个人资料功能

## 背景

管理后台已具备后台登录、当前用户摘要、用户管理、头像上传和用户菜单基础入口，但用户菜单中的“个人资料”仍是占位反馈。后台管理员无法从全局菜单快速维护自己的头像和昵称，只能依赖用户管理列表中面向他人的编辑能力。

本 Change 基于 REQ-0011，在用户菜单栏新增个人资料 Modal，仅允许当前登录管理员修改自己的头像和昵称，并在保存后刷新当前用户摘要、菜单头像和昵称展示。

## 目标

- 在管理后台用户菜单中提供“个人资料”入口，并以 Modal 承载资料修改流程。
- 后端提供当前用户专用资料更新接口，只允许更新当前登录用户自己的 `nickname` 与 `avatar_url`。
- 头像上传沿用现有后台头像上传和对象存储链路，保存资料时只写入后端返回的持久 URL。
- 前端复用创建用户表单的头像上传交互：单头像预览位、右侧格式提示、上传/更换按钮和隐藏 file input。
- 保存成功后刷新当前用户摘要、本地会话缓存和用户菜单展示。
- 补齐 API、前后端测试、admin-modal / media-upload 横切验收和 1440px 视觉验收。

## 非目标

- 不支持修改用户名、角色、状态、密码、空间数、最近登录时间或系统内置超级管理员保护字段。
- 不支持管理员在个人资料 Modal 中编辑他人资料。
- 不新增独立个人资料页、抽屉、头像裁剪、图库选择或批量上传。
- 不覆盖普通 Web 前台用户、小程序、移动端或桌面端个人资料。
- 不处理密码修改；该能力由 REQ-0010 / `add-admin-user-menu-password-change` 承接。

## 影响范围

```yaml
impact:
  backend: true
  web: true
  admin: true
  api: true
  storage: true
  database: false
  miniapp: false
capabilities:
  new:
    - 当前登录后台管理员自助修改头像和昵称
    - 用户菜单个人资料 Modal
    - 当前用户资料更新接口
    - 个人资料保存后当前用户摘要刷新
  modified:
    - web-admin-auth-system
    - web-admin-user-management
```

## 验收摘要

- 用户点击“个人资料”后打开 Modal，不再展示占位 toast。
- 当前用户资料读取和更新必须以后端认证上下文为准，不信任请求体目标用户 ID。
- 更新接口只接受 `nickname` 与 `avatar_url`，昵称非必填且最长 128 个字符。
- 头像上传支持 JPG、PNG、WEBP，单文件不超过 2MB；最终保存的 `avatar_url` 必须是持久 URL，不得是 `blob:` URL。
- Modal 内只出现一个头像图标，且只位于头像上传区；用户名和角色摘要用文本展示。
- 保存成功后刷新当前用户摘要、本地会话缓存和用户菜单展示。
- Change 实现阶段必须完成 UI Skeleton、admin-modal / media-upload 横切验收、Docker `:3000` 上传读取回显验收和 1440px 视觉验收。

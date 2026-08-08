---
change_id: add-admin-user-management
status: applied
type: add
created_at: 2026-08-07 22:29:45
updated_at: 2026-08-08 19:20:56
source_requirement: REQ-0004-admin-user-management
source_path: issues/requirements/review/REQ-0004-admin-user-management/
sprint: sprint-001
capabilities:
  new:
    - web-admin-user-management
  modified: []
impact:
  backend: true
  web: true
  miniapp: false
  admin: true
  database: true
  storage: true
  api: true
strategy: css-port
knowledge_base_refs:
  - docs/knowledge-base/best-practices/admin-list-page-consistency.md
  - docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md
  - docs/knowledge-base/best-practices/admin-media-upload-chain.md
prototype_refs:
  - issues/requirements/review/REQ-0004-admin-user-management/prototype/web/prototype.html
  - issues/requirements/review/REQ-0004-admin-user-management/prototype/web/prototype.png
---

# Change Trace

## Requirement Readiness Report

| 项 | 结果 |
|---|---|
| REQ status | approved |
| Readiness | Ready |
| Knowledge-base gate | Pass |
| UI prototype | HTML + PNG + context |
| Decision | 可以创建 OpenSpec Change |

## Impact Report

```yaml
impact:
  backend: true
  web: true
  miniapp: false
  admin: true
  database: true
  storage: true
  api: true
change_type: add
capabilities:
  new:
    - web-admin-user-management
  modified: []
```

## Conflict Report

| 来源 | 优先级 | 处理 |
|---|---:|---|
| prototype.html | 1 | 页面结构、筛选、分页、弹窗、超级管理员行以 HTML 为准 |
| prototype.png | 2 | 1440px 深色主题信息密度和布局验收 |
| context.md | 3 | 字段、接口预期和组件规范参考 |
| acceptance.md | 4 | 用户已确认的角色范围与冻结 10 秒规则优先 |
| ui-design.md | 5 | MoonBox 视觉风格边界 |
| openspec/specs | 6 | 当前无相关能力，新增 capability |

## PNG Checklist

- [ ] 1440px 用户列表布局与 `prototype.png` 信息密度一致。
- [ ] 筛选区搜索框自适应，角色/状态筛选宽度稳定。
- [ ] 分页左右分区，操作列在最右侧可访问。
- [ ] 新增/编辑弹窗在深色主题中可读且尺寸正确。
- [ ] 系统内置超级管理员行展示标识且不可操作。

## 验收返修记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-08 10:40:21 | opsx.modify | 按 REQ-0004 `prototype.html` v1.0.5 对齐用户管理页后台 Shell、侧边栏、用户菜单、主题入口、页头、筛选栏、表格、分页、弹窗、toast 和 1440px 信息密度。 |
| 2026-08-08 10:46:53 | opsx.modify | 将管理后台 Shell 左上角文字标记替换为现有 MoonBox 产品图标资产，并用前端测试锁定资源路径。 |
| 2026-08-08 10:54:11 | opsx.modify | 将侧边栏导航和底部用户菜单的文字/符号占位图标替换为当前菜单语义对应的 Lucide 图标，并补充前端测试锁定图标渲染数量。 |
| 2026-08-08 11:11:28 | opsx.modify | 参考 ProjectTilesFST 管理后台图标风格，收敛侧边栏图标映射、尺寸、stroke、透明度和 active/hover 表现；空间管理按“组织空间”语义使用 Network 图标，并补充不同菜单 SVG 差异测试。 |
| 2026-08-08 11:18:31 | opsx.modify | 保留主题入口在用户菜单内，修复主题行样式：避免主题开关继承用户菜单按钮通用样式，明确开关尺寸、圆角、对齐、hover 和 focus 表现，并补充 DOM 结构测试。 |
| 2026-08-08 11:26:53 | opsx.modify | 优化用户菜单主题切换交互：主题行改为整行 switch 按钮，右侧开关改为视觉状态，消除嵌套 button，并补充 aria-checked 与 toast 测试。 |
| 2026-08-08 12:42:59 | opsx.modify | 修复亮主题只局部生效：为后台 Shell 引入主题语义 CSS 变量，light 主题覆盖侧边栏、用户菜单、页头、筛选栏、表格、分页、弹窗、toast 和按钮颜色，并补充主题切换测试。 |
| 2026-08-08 12:54:07 | opsx.modify | 对齐 `prototype.html` v1.0.5 右侧用户管理内容：优化新增用户按钮、筛选栏自动查询提示、用户列表列顺序和操作列密度、分页结构、用户新增/编辑弹窗 form-row/form-hint/avatar-picker/drawer-actions 样式，并将用户菜单主题文案改为“界面主题”。 |
| 2026-08-08 13:00:06 | opsx.modify | 调整用户管理页头文案为“统一管理平台用户、角色生命周期”，并删除筛选栏“输入或筛选后自动查询”提示及对应测试断言。 |
| 2026-08-08 14:33:47 | opsx.modify | 对齐 `prototype.html` v1.0.5 新增用户按钮：新增 `admin-btn` 基础按钮样式，页头新增用户按钮使用 `admin-btn admin-primary`，固定 36px 高度、0 15px padding、2px 圆角和 600 字重，并补充测试。 |
| 2026-08-08 14:40:41 | opsx.modify | 对齐 `prototype.html` v1.0.5 新增用户按钮颜色：为后台 Shell 引入 `admin-gold`、`admin-gold-strong` 和 `admin-primary-text` 主题变量，light 主题金色使用 `#B8863E`，并将 `admin-primary` 从硬编码色值改为变量驱动。 |
| 2026-08-08 14:47:52 | opsx.modify | 修复新增用户按钮颜色仍不生效：提升 `.admin-primary` 在 `.admin-content`、用户弹窗和确认弹窗内的 CSS 优先级，避免被通用按钮选择器覆盖，并补充测试锁定覆盖选择器。 |
| 2026-08-08 14:56:02 | opsx.modify | 对齐 `prototype.html` v1.0.5 用户列表整体视觉：显式锁定表格列宽、正文 13px 轻量密度、日期不换行和操作列宽度，修复正文过暗、日期裁切与分页总数不一致问题，并补充密度与列顺序测试。 |
| 2026-08-08 15:07:02 | opsx.modify | 修复用户列表细节：缩小头像字体，优化表头字体比例，将“所属 Workspace”改为“空间数”，让系统内置标签与用户名同行，收紧列宽但保持日期/操作不换行，并将分页总数恢复为真实筛选结果。 |
| 2026-08-08 15:14:33 | opsx.modify | 对齐 `prototype.html` v1.0.5 用户新增/编辑弹窗：收敛 560px 表单弹窗内边距、字号、必填星号、输入控件、头像 picker、hint/error 和底部操作区样式；分页每页显示新增 50 条与 100 条。 |
| 2026-08-08 15:26:03 | opsx.modify | 修复用户表单头像上传体验：删除用户名错误文案，上传按钮按头像状态显示“上传/更换”，按钮与说明分两行且字号一致，并将前端假上传改为调用 `/api/v1/admin/users/avatar` 真实上传接口。 |
| 2026-08-08 15:39:09 | opsx.modify | 微调用户表单头像上传区：将“支持 JPG、PNG，建议 1:1”置于上传/更换按钮上方，并将上传按钮改为随文案自适应的紧凑宽度。 |
| 2026-08-08 15:49:08 | opsx.modify | 继续微调用户表单头像上传区：将上传/更换按钮高度从 36px 收敛为 28px，使其更接近辅助操作按钮层级。 |
| 2026-08-08 15:55:36 | opsx.modify | 修复头像上传失败排查闭环：前端上传失败时展示后端错误详情；上传成功后通过授权 fetch 读取头像 blob 并转为 object URL 回显，避免 `img` 直接访问需 Bearer 的头像接口失败。 |
| 2026-08-08 16:02:18 | opsx.modify | 统一用户表单校验提示：用户名、头像上传和操作原因异常均使用字段下方 `admin-form-error` 展示，hint 常驻不被错误替换，按钮禁用不再作为唯一反馈。 |
| 2026-08-08 16:13:03 | opsx.modify | 统一管理后台字体体系：为 `.admin-shell` 引入字体、字号、字重和行高语义 token，收敛侧边栏、用户菜单、页头、筛选栏、表格、分页、弹窗、toast 和按钮排版，同时保留 `Noto Serif SC` 标题与 `EB Garamond` 英文点缀。 |
| 2026-08-08 16:23:14 | opsx.modify | 头像上传接入 MinIO：上传接口写入单 Bucket `images/avatars/{uuid}.{ext}`，读取接口经后台授权从 MinIO 拉取并回显；同步 Docker/backend env、API/对象存储/上传标准、OpenSpec delta、REQ 验收和 Sprint 范围说明。 |
| 2026-08-08 16:46:09 | opsx.modify | 修复 `self-storage-sqlite` 头像上传 `NetworkError` 配置陷阱：`docker-up.sh` 启动前校验 `HOST_PORT_BACKEND` 与显式 `VITE_API_BASE_URL` localhost 端口一致，缺省时按后端宿主机端口自动导出浏览器 API 地址，并补充脚本测试和部署文档。 |
| 2026-08-08 17:08:42 | opsx.modify | 优化 MoonBox 本地环境变量：宿主机端口统一使用 `18101-18199`，容器内端口不再通过 env 配置，默认北京时区、bucket `moonbox` 和自建 MinIO `data/s3`，并同步 Compose、env、部署文档、端口规范和校验测试。 |
| 2026-08-08 18:27:58 | opsx.modify | 修复用户列表数据源不真实：移除前端 `initialUsers` mock，列表加载、筛选、分页和写操作全部改为授权调用后台用户 API，分页总数使用后端 `total`，并补充真实数据流测试。 |
| 2026-08-08 18:38:55 | opsx.modify | 修复用户创建和重置密码不可登录：创建用户与重置密码均生成一次性临时密码并写入 `password_hash`，前端仅展示一次临时密码，后端测试覆盖创建后登录与重置后新旧密码行为。 |
| 2026-08-08 18:45:56 | opsx.modify | 优化一次性临时密码展示：创建用户和重置密码成功后改用 `TemporaryPasswordModal` 展示密码、复制按钮和安全提示，复制成功反馈“已复制”，关闭后清空临时密码状态且不持久化。 |
| 2026-08-08 18:52:47 | opsx.modify | 优化临时密码弹窗关闭文案：底部按钮由“我已复制并关闭”改为“关闭”，安全提示改为关闭后不可再次查看并提醒妥善保存，复制状态保留在复制按钮上。 |
| 2026-08-08 19:04:31 | opsx.modify | 修复弹窗右下角按钮过窄：为用户表单、确认弹窗和临时密码弹窗 footer button 统一设置高度、最小宽度、padding 和圆角，避免短文案按钮过窄。 |
| 2026-08-08 19:15:43 | opsx.modify | 优化已删除用户列表展示：默认列表和“全部状态”排除 `status=已删除`，显式筛选“已删除”时展示逻辑删除用户，后端 `total` 同规则计算，已删除用户操作列显示不可操作。 |
| 2026-08-08 19:20:56 | opsx.modify | 删除状态筛选项“已删除”：前端状态下拉仅保留“全部状态/待激活/正常/已冻结”，默认列表继续隐藏逻辑删除用户，并更新测试与可归档规格描述。 |

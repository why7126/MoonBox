---
note: workflow-sync — 26/26 Change 已 archive；0 applied；待人工 sign-off
sprint_id: sprint-002
status: passed
created_at: 2026-08-09 07:26:26
updated_at: 2026-08-14 16:28:17
---

# sprint-002 验收报告

## 验收范围

| 类型 | 编号 | 标题 | 状态 |
|---|---|---|---|
| REQ | REQ-0009-git-check-pre-push-security-gate | git-check 推送前安全检测命令 | planned |
| REQ | REQ-0010-admin-user-menu-password-change | 后台管理用户菜单栏密码修改功能 | pending |
| REQ | REQ-0012-frontend-requirement-center | MoonBox 前台需求中心 | planned |
| REQ | REQ-0013-requirement-center-real-data-integration | 需求中心真实数据接入 | planned |
| REQ | REQ-0014-frontend-user-menu-profile | 前台用户菜单栏个人资料功能 | planned |
| REQ | REQ-0015-login-password-visibility-toggle | 登录页密码显示/隐藏切换功能 | planned |
| REQ | REQ-0016-unified-account-auth-api | 统一账号认证与个人中心 API | planned |
| REQ | REQ-0017-admin-space-management | 后台管理实现空间管理模块 | planned |
| BUG | BUG-0001-admin-web-login-api-proxy-and-spa-fallback | Docker Web 管理后台登录 API 误路由且缺少 SPA fallback | planned |
| BUG | BUG-0002-homepage-frontend-login-entry-routes-to-admin | 首页前台登录入口误跳后台登录页 | planned |
| BUG | BUG-0003-homepage-start-moonbox-should-open-login-route | 官网开启 MoonBox 应进入 /login 独立登录页 | passed |
| BUG | BUG-0004-frontend-user-menu-change-password-not-implemented | 前台用户菜单栏修改密码入口未实现 | passed |

## 验收标准

- REQ-0009 的 `acceptance.md` 中 AC-001 至 AC-015 全部通过。
- REQ-0010 的自助修改密码、会话撤销、modal 交互、显示/隐藏密码和 1440px 视觉验收通过。
- REQ-0012 的 9 阶段 Requirement/Bug 看板、空间切换 Hover 浮层、空间设置弹窗、主题切换、吸顶列头、UI Skeleton 和 1440px 视觉验收通过。
- REQ-0012 的 `acceptance.md` 中功能 AC、AC-PROTOTYPE 和 AC-XCUT 均完成或有明确验收证据。
- REQ-0013 的 BFF 聚合接口、治理文件事实源读取、状态映射、安全脱敏、前端 Mock 替换、加载/错误/空态、权限态和 1440px UI 状态验收通过。
- REQ-0014 的前台个人资料弹窗、头像上传状态机、昵称清空回退、保存后 currentUser/菜单/会话缓存刷新、受保护头像读取、前后台个人资料 Modal 交互结构一致性、摘要仅用户名、菜单头像 32px、弹窗头像 48px、前台保存后进入后台菜单同步、前后台主题偏好跨路由同步、前台昵称输入框可读对比、1440px 用户菜单/弹窗视觉验收，以及 Docker Web `:18102` 隔离栈头像上传、未授权读取 401、Bearer 读取 200 和前台菜单回显验收通过。本机 `:3000` 被 unrelated `tilesfst-web` 占用，本轮按用户选择 B 改用 `:18102` 记录证据。
- REQ-0015 的登录页密码输入框默认隐藏、显示/隐藏切换、值不丢失、不触发表单提交、键盘触发、无障碍状态、敏感信息不持久化、登录流程回归和 1440px 密码字段视觉验收通过。
- REQ-0016 的 `/api/v1/auth/login|logout|me|change-password|avatar` 统一接口、旧 `/api/v1/admin/auth/*` 删除、所有登录用户资料/头像/密码自助能力、单一前端 session、后台授权边界、OpenAPI/Orval/API 文档同步、头像上传状态机和同会话回显验收通过；Docker 固定 `:3000` 与默认管理员密码依赖问题由 BUG-0007 独立治理，本 Change 仅保留 Docker 默认端口 `18102` 尝试记录，不作为 REQ-0016 主体实现阻断。
- REQ-0017 的空间列表、申请审批、回收站、空间详情原型结构、空间与产品一对一绑定、配额与用量、有效期、冻结恢复、删除回收、永久删除、通知审计、admin-list/admin-modal 横切 AC、空间详情头与 5 个详情分区 Tab、详情页与空间列表页复用统一后台侧边栏且用户菜单一致、侧边栏视口高度稳定且底部用户触发区不随详情内容下沉、返回空间列表入口为无边框文字链接、详情页编辑/调整配额/续期/移交负责人/冻结/删除操作闭环且成功后重新拉取详情/审计并刷新概览最近操作或删除后返回列表、详情操作弹窗标题按具体动作展示、成员分区展示真实成员管理表格且支持添加成员、编辑角色和移除成员，负责人不进入成员列表且角色限定为管理员/编辑者/查看者并按角色和加入时间排序，成员用户列复用统一头像组件并支持真实头像，负责人/成员头像 URL 统一规范化为 `/api/v1/auth/avatar/{filename}` 且不恢复旧 `/api/v1/admin/users/avatar/{filename}` 读取接口、操作记录分区接入真实 `/api/v1/admin/spaces/{space_id}/audit-events`，展示操作人展示名、时间、来源、对象、变更摘要、原因和结果，操作/来源/结果/状态等枚举值使用轻量标签和中文文案，审批通过创建空间后新空间详情可追溯审批来源、产品分区顶部展示绑定关系 notice，下方按产品卡片列表展示且当前仅一个产品卡片，卡片不显示“绑定产品”标题，字段为产品名称、产品 ID、绑定状态、研发状态并复用统一字段网格，无产品数字段且无未实现操作、配额与用量分区调整配额入口可用、负责人头像复用统一头像组件并支持真实头像、负责人摘要删除多余“负责人”文案、无边框文本面包屑、标题状态同行、负责人摘要同组、右侧实体操作按钮、删除危险按钮、详情页字体/按钮/头像/卡片间距按原型紧凑尺度收敛且降低过度加粗、概览三卡片左宽右窄原型布局且不展示产品绑定提示、基础信息两列字段网格、空间列表成员数/产品数/AI 用量列按内容收敛且不挤压操作列、空间列表 AI 用量原型进度条两行展示且第二行仅百分比、语义状态图标、更多 fixed 浮层显示在当前行按钮下方、左对齐、保留间隙、菜单项靠左且暗色/浅色主题背景边框均可区分、hover/focus 高亮且紧凑可读、操作原因参照 BUG-0010 完成必填标记和无效原因可见反馈，移除成员原因标签单行紧凑显示、添加/编辑成员弹窗纵向布局且用户/角色下拉不被弹窗滚动容器裁剪或遮罩、prototype-driven UI AC、1440px 视觉验收、computed style 验收和 Mock/API 边界声明通过。
- REQ-0017 本轮继续补齐空间详情有效期和审计记录交互：固定日期支持时分秒输入/选择，默认当前季度最后一天 23:59:59 且必须晚于当前时间，长期有效不保存到期时间；概览基础信息字段顺序调整为空间名称、唯一标识、创建来源、创建时间、有效期，最近操作显示真实审计最新 6 条；操作记录 Tab 使用真实分页、统一分页组件、时间/操作人/操作动作/变更摘要/结果/操作列、差异化枚举标签和右侧详情抽屉。
- REQ-0017 本轮继续完成空间详情操作记录视觉返修：操作记录分页改为轻量无边框样式并保留 hover/focus/active 状态，操作详情抽屉中的变更前/变更后改为格式化 JSON code block，长内容在 code 区域内滚动；空间列表长期有效文案统一显示为“长期有效”。
- REQ-0017 本轮继续完成空间详情成员 Tab 与最近操作视觉返修：成员表格在不放大字号的前提下增加行高和上下间距，头像/用户信息/操作保持垂直居中；概览最近操作动作文本取消过度加粗，仅保留卡片标题强调。
- REQ-0017 本轮继续完成空间有效期到期时间控件返修：固定日期到期时间改用自研轻量 `AdminDateTimePicker`，输入框展示 `yyyy-mm-dd hh:mm:ss`，展开面板支持日期和时/分/秒选择、快捷项和手动输入格式化，长期有效仍隐藏到期时间。
- REQ-0017 本轮继续完成操作记录详情抽屉空值展示返修：变更前/变更后为空、null、空字符串或“无”时改为轻量空态文本，不再使用大块 JSON code block 或撑高抽屉。
- REQ-0017 本轮继续完成后台亮主题主按钮文字颜色返修：以空间详情成员 Tab“添加成员”为验收点，亮主题金色主按钮文字改为主题适配深棕文本并降为中等字重，hover/focus-visible 保持可见；暗主题保持可读。
- REQ-0017 本轮继续完成创建空间申请后台演示数据返修：前台申请入口暂未实现时，开发/演示环境可通过 `ADMIN_SPACE_APPLICATION_DEMO_SEED` 或 `scripts/seed-admin-space-applications.py` 生成真实待审批空间申请；演示数据走后端申请创建逻辑，审批通过后创建来源为“申请审批”的空间并写入审计，生产环境不自动播种，前端不硬编码 Mock。
- REQ-0017 本轮继续完成空间申请演示数据 seed 目标库返修：手动脚本加载 `.env` 并把 Docker 容器内 SQLite 路径映射到宿主机运行库，输出目标数据库路径和播种数量，避免写入 `data/sqlite/moonbox.db` 导致 Docker 后台申请审批 Tab 无数据。
- REQ-0017 本轮继续完成申请审批 Tab 视觉与信息架构返修：横向大卡片改为后台统一紧凑审批表格，展示空间名称/编码、申请人、负责人、资源申请、有效期、申请时间和操作；资源申请格式化展示成员、存储和 AI Tokens，操作为轻量文字按钮，并补真实分页与 1440px 视觉/computed style 证据。本轮不新增搜索/筛选。
- REQ-0017 本轮继续完成申请审批 Tab 表格细节返修：资源申请列改为成员、存储、AI Tokens 三个独立紧凑资源项，不再使用分隔符伪元素，修复 `Â·` 乱码；AI Tokens 改为 `90万 Tokens`、`150万 Tokens` 等中文短量级格式，并调整列宽避免 1440px 下与有效期列重叠。
- BUG-0001 的 `acceptance.md` 中 AC-001 至 AC-005 全部通过。
- BUG-0002 的 `acceptance.md` 中 AC-001 至 AC-006 全部通过。
- BUG-0003 的 `acceptance.md` 中 AC-001 至 AC-016 全部通过。
- BUG-0004 的 `acceptance.md` 中 AC-001 至 AC-010 全部通过，且前台修改密码弹窗在前台主题中可读可填写，普通前台用户仅有 frontend session token 时可修改密码，后端自助改密不要求后台管理员角色但后台管理接口仍受限，继续编辑密码字段时会清理旧提交级错误。
- BUG-0008 的当前登录管理员自冻结/自删除后端 403、状态和会话不变、当前账号行冻结/删除按钮保留但禁用、无额外“当前账号”文案、其他账号操作保持可用均通过回归测试。
- BUG-0010 的用户编辑异常用户名保存、操作原因空/短值错误提示、校验失败不调用 API、四类操作弹窗操作原因必填红星标识、红星紧跟字段名同一行展示和合法原因成功路径均通过回归测试。
- OpenSpec Change 完成实现、测试、文档同步和归档。
- `/git-check` 成功路径、失败路径、误报豁免和脱敏输出均有验证证据。
- `data/s3/**` 运行时对象存储数据不得继续被 Git 跟踪；本地文件可保留并由 `.gitignore` 覆盖。
- 本机绝对路径片段必须作为隐私数据阻断；历史本机路径命中必须脱敏后通过 `/git-check`。
- REQ/BUG 驱动但触达治理资产的 Change 必须生成或更新 `docs/spec-logs` 治理日志，并同步 `CHANGELOG.md`。
- Docker Web 同源 `/api/v1/admin/auth/login` 曾使用本地管理员账号验证旧后台入口；后续 media-upload 验收不得复用该默认密码假设，必须由脚本准备测试身份。
- 后端容器在需求中心 BFF 启用时必须正常启动；`requirement_center.py` 在容器浅路径下优先使用 `MOONBOX_GOVERNANCE_ROOT`，不得因根路径兜底越界导致登录 API 502。
- 需求中心空间上下文不得返回后端硬编码演示空间；首版应从 `project.yaml`、治理对象负责人和当前登录用户派生真实项目空间。
- 需求中心用户菜单「退出登录」必须清理前台 session 与后台 admin session，调用后台 logout API，并回到 `/login`。
- 前台用户菜单必须显示用户昵称与当前空间，后台用户触发区必须仅显示一行用户昵称；昵称为空时均显示用户名。
- 个人资料修改当前登录用户昵称、用户管理编辑当前登录用户列表项昵称后，当前后台菜单、admin session 与前台需求中心用户菜单必须同步新昵称。

## 验收结果

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:28:17
accepted_by: /sprint-archive sprint-002
evidence:
  - pnpm --dir src/web test -- admin-auth.test.tsx --run
  - pnpm --dir src/web build
  - openspec validate add-admin-user-menu-password-change --strict
  - .tmp-admin-change-password-toggle-1440.png
  - pnpm --dir src/web test -- admin-user-management.test.tsx admin-auth.test.tsx
  - /tmp/moonbox-req0011-profile-avatar-modify-1440.png
  - /tmp/moonbox-req0011-profile-auth-avatar-modify-1440.png
  - /tmp/moonbox-req0011-profile-shared-avatar-modify-1440.png
  - pnpm --dir src/web test -- requirement-center.test.tsx
  - pnpm --dir src/web build
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/visual-1440.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/visual-1440-space-popover.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/visual-1440-space-settings.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/visual-1440-low-modal.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-space-settings.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-low-modal.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapsed.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-shell-alignment.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-user-menu-alignment.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-shell-collapsed-alignment.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-board-prototype-alignment.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-board-bug-filter.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-card-header-prototype.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-card-header-bug-filter.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-structure.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-user-menu-structure.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-structure-collapsed.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-brand-no-overlap.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapse-button-visible.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-admin-parity-brand.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-admin-parity-collapsed.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapse-text-expanded.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapse-text-collapsed.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapse-admin-parity-expanded.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapse-admin-parity-collapsed.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-admin-collapse-24px.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-frontend-admin-collapse-height-parity.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-user-menu-grouped-session.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-space-popover-simplified.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-space-popover-dark-readable.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-admin-return-frontend.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-user-menu-floating-surface.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-admin-user-menu-grouped-surface.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-user-menu-permission-icons.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-admin-user-menu-icons.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-board-scroll-mask.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-space-popover-list-lightweight.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-toolbar-refresh-button.png
  - uv run pytest tests/integration/api/test_requirement_center.py
  - pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx admin-auth.test.tsx --run
  - pnpm --dir src/web build
  - /private/tmp/req-0014-modify-frontend-profile-parity-1440.png
  - /private/tmp/req-0014-modify-admin-profile-close-1440.png
  - /private/tmp/req-0014-modify2-frontend-profile-clean-1440.png
  - /private/tmp/req-0014-modify2-admin-profile-clean-1440.png
  - /private/tmp/req-0014-docker-18102-profile-menu.png
  - /private/tmp/req-0014-modify3-theme-profile-1440.png
  - node -e "<Docker 18102 头像上传/受保护读取/前台菜单回显验收脚本>"
  - node -e "<1440px 主题偏好/昵称输入 computed style 验收脚本>"
  - pnpm --dir src/web test -- requirement-center.test.tsx --run
  - pnpm --dir src/web build
  - pnpm --dir src/web test -- requirement-center.test.tsx admin-auth.test.tsx --run
  - pnpm --dir src/web build
  - /tmp/moonbox-bug0004-change-password-readable-1440.png
  - openspec validate add-requirement-center-real-data-integration --strict
  - python scripts/validate-openspec-language.py --root openspec/changes/add-requirement-center-real-data-integration
  - /private/tmp/req-center-real-1440-second.png
  - uv run pytest tests/integration/api/test_requirement_center.py
  - pnpm --dir src/web test -- requirement-center.test.tsx admin-auth.test.tsx --run
  - pnpm --dir src/web build
  - docker compose config --quiet
  - pnpm --dir src/web test -- homepage.test.tsx admin-auth.test.tsx --run
  - pnpm --dir src/web build
  - pnpm --dir src/web test -- homepage.test.tsx requirement-center.test.tsx admin-auth.test.tsx --run
  - pnpm --dir src/web build
  - pnpm --dir src/web test -- requirement-center.test.tsx homepage.test.tsx admin-auth.test.tsx --run
  - pnpm --dir src/web build
  - uv run pytest tests/unit/test_requirement_center_paths.py tests/integration/api/test_requirement_center.py
  - docker compose up -d --build backend
  - docker compose ps backend
  - pnpm --dir src/web test -- requirement-center.test.tsx admin-auth.test.tsx homepage.test.tsx --run
  - pnpm --dir src/web build
  - pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx admin-auth.test.tsx homepage.test.tsx --run
  - python -m pytest tests/integration/api/test_requirement_center.py
  - pnpm --dir src/web build
  - pnpm --dir src/web test -- admin-user-management.test.tsx requirement-center.test.tsx admin-auth.test.tsx homepage.test.tsx --run
  - python -m pytest tests/integration/api/test_admin_users.py tests/integration/api/test_requirement_center.py
  - pnpm --dir src/web build
  - pnpm --dir src/web test -- admin-user-management.test.tsx requirement-center.test.tsx admin-auth.test.tsx homepage.test.tsx --run
  - pnpm --dir src/web build
  - pnpm --dir src/web test -- homepage.test.tsx admin-auth.test.tsx requirement-center.test.tsx --run
  - pnpm --dir src/web build
  - pnpm --dir src/web test -- requirement-center.test.tsx homepage.test.tsx admin-auth.test.tsx --run
  - pnpm --dir src/web build
  - uv run pytest tests/integration/api/test_requirement_center.py
  - pnpm --dir src/web test -- admin-user-management.test.tsx --run
  - pnpm --dir src/web build
failed_items: []
notes: 2026-08-09 08:18:35 已通过 git rm -r --cached data/s3 将 42 个运行时对象存储文件迁出 Git 索引；本机绝对路径已升级为 error 阻断，历史归档文档和校验脚本中的命中已脱敏或改写；REQ-0012 已补充前后台视觉对齐、9 阶段看板原型对齐、卡片/表头原型对齐、Sidebar 结构性交互、品牌/折叠按钮提示文案细节返修、后台同构品牌区、展开/收起按钮同构、收起态控制柄可点击复验、前后台控制柄高度一致、用户菜单分组/危险色、空间二级浮层轻量化、前台菜单 summary 移除、后台返回前台入口、前后台用户菜单浮层层级、后台用户菜单分组、前台进入后台权限显示、前后台菜单图标语义、看板滚动遮罩层级、空间浮层轻量列表行和工具栏刷新按钮证据；REQ-0013 已接入需求中心真实数据 BFF，覆盖 REQ/BUG/Sprint/OpenSpec 聚合、状态映射、字段白名单、错误脱敏、前端 Mock 替换、加载/错误/空态、权限态和 1440px 首屏截图；验收返修已补齐 `/requirements` 登录保护、真实产品版本 badge、Docker 治理事实源只读挂载、context Bearer 鉴权和缺失事实源脱敏 503；本次继续修复空间列表仍为硬编码演示数据的问题，BFF 改为从 `project.yaml`、治理对象负责人和当前登录用户派生真实项目空间；已补充 spec-logs 治理日志与 CHANGELOG 索引；BUG-0003 已修复官网「开启 MoonBox」进入 `/login` 统一登录页，并补齐 `/login` 调用后台登录 API、`/admin` 未登录回 `/login`、需求中心用户菜单不显示「未登录」且已有后台权限显示「进入后台」的返修；已修复需求中心服务容器内根路径兜底，避免后端启动失败导致登录 API 502；已修复需求中心退出登录无效，退出会清理前台 session 与后台 admin session、调用后台 logout API 并跳转 `/login`；已补齐前后台用户菜单显示规则测试，固定前台显示用户昵称与当前空间、后台显示用户昵称，昵称为空时均显示用户名；已修复昵称保存后当前会话未同步，个人资料和用户管理编辑当前用户两条路径都会同步新昵称到后台菜单、admin session 和前台需求中心上下文；已修复后台用户菜单仍显示两行，后台触发区移除角色第二行，仅保留昵称/用户名一行；本次继续修复前台用户菜单未显示头像，需求中心 BFF 返回 `current_user.avatar_url`，前台菜单通过 admin token 加载受保护头像，头像为空时回退首字，通过前后台回归测试；BUG-0004 已修复前台用户菜单“修改密码”入口点击无效，复用后台修改密码弹窗和既有改密 API，成功后清理前后台会话并跳转 `/login`，失败和确认密码不一致路径均通过测试；验收返修已补齐前台复用后台弹窗时的主题 token 桥接，修改密码弹窗在前台主题中可读可填写，并通过 1440px computed style 与截图验收；本次继续修复普通前台用户仅有 frontend session token 时改密误提示登录失效的问题，改密请求会使用 `Bearer front-token` 并在成功后清理前后台 session；本次继续修复后端自助改密误要求后台管理员权限的问题，普通前台用户可修改自己的密码、旧 session 会失效、新密码可登录，后台用户管理接口仍返回 403；本次继续修复旧接口错误与当前字段校验错误同时展示的问题，用户继续编辑任一密码字段后会清理旧提交级错误，仅保留当前字段级错误。
```

## REQ-0017 回收站返修补充

- 2026-08-14：空间回收站 Tab 已改为独立请求 `status=RECYCLE` 真实分页数据，不再从默认空间列表本地过滤；回收站 total 使用接口返回值，表格补齐删除时间、删除人、删除原因、剩余天数和查看/恢复/彻底删除操作，删除空间后可刷新并在回收站看到。
- 2026-08-14：回收站行内“更多”菜单已复用普通空间列表 body 级 fixed 浮层能力，补齐回收站更多菜单 1440px 展开截图和 computed style 证据，确认菜单不被表格、分页、sticky 操作列或回收站容器遮罩/裁剪。
- 2026-08-14：回收站更多菜单位置已回退到“更多”按钮下方并保持 6px 间隙；真实问题改为无更多收敛操作时不渲染“更多”按钮或空面板，补充菜单项位于最上层可见和无空菜单回归证据。

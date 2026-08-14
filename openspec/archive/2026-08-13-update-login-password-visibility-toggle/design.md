## 概览

本 Change 将 `REQ-0015-login-password-visibility-toggle` 转化为 OpenSpec 实施方案。范围聚焦 Web 登录页密码字段的显示/隐藏切换，不改变登录 API、Token、会话、改密、注册、找回密码或权限策略。

策略选择：沿用 MoonBox 现有登录页设计系统与当前后台密码显隐交互模式，复用 `Eye` / `EyeOff` 或等价图标按钮语义；不做 CSS Port 大搬迁，不新增独立页面。

## 影响范围

```yaml
impact:
  backend: false
  web: true
  miniapp: false
  admin: false
  database: false
  storage: false
  api: false
capabilities:
  new: []
  modified:
    - web-catalog-login-page
change_type: update
source_requirement: REQ-0015-login-password-visibility-toggle
source_sprint: sprint-002
```

## 冲突处理

事实源优先级：

```text
issues/requirements/review/REQ-0015-login-password-visibility-toggle/prototype/web/prototype.html
> issues/requirements/review/REQ-0015-login-password-visibility-toggle/prototype/web/context.md
> issues/requirements/review/REQ-0015-login-password-visibility-toggle/acceptance.md
> rules/ui-design.md
> openspec/specs/web-catalog-login-page/spec.md
```

冲突处理：

- 既有 `web-catalog-login-page` spec 只要求密码默认隐藏；本 Change 在不删除该要求的前提下增加用户主动显示/隐藏。
- `REQ-0002` 旧文档曾描述“当前原型提交不连接后端”，但当前产品已通过后续 Change 将 `/login` 接入登录 API；本 Change 不改变当前登录提交语义，只要求显隐按钮不得触发表单提交或 API 调用。
- `prototype.html` 使用 `Eye` 文本占位表达图标槽位；实现应使用项目图标库中的 `Eye` / `EyeOff` 或等价图标，而不是在产品界面显示文字占位。
- PNG 当前不强制；实现阶段必须用 1440px 截图和关键交互截图补证。

## UI 合同

| 项 | 合同 |
|---|---|
| 页面与入口 | Web 登录页，路由 `/login` 或兼容 `#login` 状态；不新增入口。 |
| 信息架构 | 保持返回首页、登录卡片、Logo、标题、用户名字段、密码字段、记住我、登录按钮、错误反馈顺序。 |
| 组件结构 | 密码字段内部增加稳定容器与图标按钮；按钮属于密码字段，不进入主操作区。 |
| 视觉 token | 继续使用 MoonBox 深色主题、近直角、细线边框、金色主按钮；图标按钮颜色与登录页次级文本一致，hover/focus-visible 清晰。 |
| 尺寸间距 | 密码输入框右侧预留按钮空间，建议 `padding-right >= 44px`；按钮建议宽约 32px、高约 28px、右侧约 6px。 |
| 图标与文案 | 隐藏状态按钮语义为“显示密码”，显示状态按钮语义为“隐藏密码”；图标使用 `Eye` / `EyeOff` 或等价图标。 |
| 交互状态 | 默认隐藏；点击或键盘触发后切换；按钮 `type="button"`；支持 focus-visible、Enter/Space、`aria-pressed`。 |
| Mock/API 边界 | 不新增 Mock，不新增 API；显隐切换不得调用登录接口；登录提交继续走既有流程。 |
| 权限规则 | 登录页未登录可见；不新增角色权限分支。 |
| 一致性参照 | 对齐既有 Web 登录页视觉；交互语义可参考后台修改密码输入显隐控件，但不得引入后台 modal 或改密流程。 |

## UI 骨架

```text
Homepage
  login-page
    login-back
    login-card[aria-label="MoonBox login"]
      login-logo
      login-title
      login-field(username)
        input[name="username"]
      login-field(password)
        login-password-field
          input[name="password"][autocomplete="current-password"]
          button[type="button"][aria-label][aria-pressed]
            Eye | EyeOff
      login-remember
      login-submit
      admin-login-error[aria-live="polite"]
```

可测选择器建议：

- `screen.getByLabelText("密码")` 定位密码输入框。
- `screen.getByRole("button", { name: "显示密码" })` 定位显示按钮。
- `screen.getByRole("button", { name: "隐藏密码" })` 定位隐藏按钮。
- `screen.getByRole("form", { name: "MoonBox login" })` 验证提交回归。

状态容器：

- `isPasswordVisible: boolean` 或等价本地 UI 状态。
- 登录表单字段仍由 DOM FormData 或既有状态处理，不因显隐切换改变字段名和值。

## 1440px 视觉验收

实现阶段必须在 1440px 桌面视口验证：

- 登录卡片整体布局、Logo、标题、字段间距、记住我、登录按钮和错误反馈不回归。
- 密码字段右侧图标按钮与输入框垂直居中，不与 placeholder、输入文本或浏览器自动填充视觉重叠。
- 显示态、隐藏态、hover 和 focus-visible 可辨识。
- 关键 computed style 记录：密码字段容器 `position`，输入框 `padding-right`，按钮 `width`、`height`、`right`、`color`、`border-color`、`outline/focus`。

## 风险

- 图标按钮如果不是 `type="button"`，会误触发表单提交。
- 输入框右侧未预留空间时，密码文本或浏览器自动填充视觉可能与图标重叠。
- 若切换后丢失焦点或光标位置，会打断连续输入。
- 测试输出、调试日志或截图说明不得包含真实密码。

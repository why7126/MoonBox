## 1. UI Skeleton 与合同确认

- [x] 1.1 在登录页实现前确认 `design.md` UI Contract、UI Skeleton 和 Conflict Resolution 覆盖 `REQ-0015` 的 prototype refs、AC-PROTOTYPE 与 Mock/API 边界。
- [x] 1.2 在 `Homepage` 登录页密码字段建立稳定结构：密码字段容器、`input[name="password"]`、显隐按钮和可测语义。

## 2. Web 实现

- [x] 2.1 为 Web 登录页密码字段增加本地显隐状态，默认隐藏密码。
- [x] 2.2 增加显隐按钮，使用 `Eye` / `EyeOff` 或等价图标；按钮必须为 `type="button"`。
- [x] 2.3 切换按钮更新密码输入框 `type`，不改变字段名、输入值、记住我、登录错误、登录提交或会话逻辑。
- [x] 2.4 为按钮补齐 `aria-label`、`aria-pressed`、title 或等价可访问语义，并支持键盘触发。
- [x] 2.5 调整登录页样式，确保密码输入框右侧预留图标空间，hover/focus-visible 清晰，移动端不溢出。

## 3. 测试

- [x] 3.1 更新 `homepage.test.tsx`，覆盖密码默认隐藏、点击显示、再次隐藏、值不丢失和显隐按钮不提交表单。
- [x] 3.2 回归登录成功路径、登录失败路径、必填校验、记住我和返回首页行为。
- [x] 3.3 确认测试输出不包含真实密码、token、会话 ID 或密码哈希。

## 4. UI 验收证据

- [x] 4.1 在 1440px 桌面视口截图验证登录页默认隐藏态布局。
- [x] 4.2 在 1440px 桌面视口截图验证显示密码态和隐藏密码态交互。
- [x] 4.3 记录密码字段关键 computed style：容器 `position`、输入框 `padding-right`、按钮 `width/height/right/color/border/focus`。
- [x] 4.4 验证移动视口下显隐控件不溢出、不遮挡输入内容和登录按钮。

## 5. 文档与追溯

- [x] 5.1 更新 Change `trace.md`，记录 UI Skeleton、1440px 截图、关键交互截图、computed style、Mock/API 边界和最终一致性状态。
- [x] 5.2 根据实现结果同步 `REQ-0015` 的 `acceptance.md` / `trace.md` 验收证据。
- [x] 5.3 运行 OpenSpec 校验和相关前端测试。

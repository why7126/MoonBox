## 验收项

- [x] AC-001：根目录 `.vite/` 被 `.gitignore` 覆盖。
- [x] AC-002：目录结构校验允许忽略 `.vite/` 本地缓存目录。
- [x] AC-003：目录结构规则说明 `.vite/` 不属于正式项目目录，不得承载长期证据、密钥、真实客户数据或运行时数据库。
- [x] AC-004：OpenSpec delta spec 记录 `.vite/` 本地缓存边界。
- [x] AC-005：目录结构、上下文预算、OpenSpec 中文、目标 Change、Sprint scope 和 Workflow Sync 校验通过或记录明确阻塞。

## 验收结果

通过：根目录 `.vite/` 已纳入 Git 忽略和目录结构校验忽略边界；目录结构、脚本语法、上下文预算、当前 Change 中文、OpenSpec validate、Sprint scope 和 Workflow Sync 均通过。AI Usage hook 返回 warning/unavailable，未发现可归因 command-run token 事件，不阻断本治理变更。

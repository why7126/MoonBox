## 验收项

- [x] AC-001：`/req-opsx` 技能明确 OpenSpec CLI template 只作结构参考，proposal、design、tasks 标题落盘前必须中文化。
- [x] AC-002：`/bug-opsx` 技能采用同一中文化映射，避免 BUG 链路继续输出英文脚手架标题。
- [x] AC-003：上下文预算校验脚本检查两个 opsx 技能必须保留中文化契约。
- [x] AC-004：语言规则和 Agent 入口同步说明 OpenSpec CLI 模板标题中文优先边界。
- [x] AC-005：本 Change 当前中文校验、OpenSpec validate、目录结构、Sprint scope 和 Workflow Sync 通过或记录明确阻塞。

## 验收结果

通过：上下文预算校验、当前 Change 中文校验、OpenSpec validate、脚本语法检查、Sprint scope 校验和 Workflow Sync 均已通过。目录结构校验因既有根目录 `.vite` 未登记失败，非本轮新增或修改；AI Usage hook 返回 warning/unavailable，未发现可归因 command-run token 事件，不阻断本治理变更。

## 设计目标

建立“证据先于根因”的项目治理闭环：AI 可以提出假设，但只有在日志、复现、截图、测试失败、代码定位、配置差异或运行时观测能够支撑时，才能把根因标记为 `confirmed`。证据不足时，AI 必须输出可操作的人工补证步骤，等待补证后再定根因。

## 根因状态模型

| 状态 | 含义 | 可进入修复评审 |
|---|---|---|
| `unknown` | 当前证据不足，无法形成有效假设 | 否 |
| `hypothesis` | 有方向性推测，但缺关键证据 | 否 |
| `probable` | 有间接证据，仍需补充验证 | 条件阻断，必须说明例外 |
| `confirmed` | 至少一条证据直接支撑根因，且有验证闭环 | 是 |

## 证据类型

证据链支持以下类型，实际记录时可扩展但必须能定位来源：

- `reproduction`：复现步骤、账号角色、输入、期望/实际。
- `test_failure`：失败测试、命令、失败断言、堆栈关键段。
- `runtime_log`：后端日志、容器日志、trace_id、request_id。
- `browser_console`：浏览器 Console 错误。
- `network_request`：请求 method/path/status、response 摘要、trace_id。
- `screenshot`：截图、录屏、视口、页面状态和标注。
- `computed_style`：选择器、视口、关键 CSS 属性和结论。
- `data_sample`：脱敏数据记录、查询结果、迁移状态。
- `config_diff`：环境、端口、Compose、feature flag 或版本差异。
- `code_path`：代码路径、函数、分支或提交 diff 片段。

## 人工补证契约

当 AI 无法从仓库、测试或可用日志中确认根因时，输出必须包含：

```text
待补证项：
- 证据名称
- 为什么需要
- 操作步骤
- 需要返回的字段
- 脱敏要求
- 返回格式
```

AI 不得只说“请提供日志/截图”。操作步骤必须按场景说明如何打开 DevTools、复制 Network 请求、获取后端日志、记录视口、导出脱敏数据或运行指定命令。

## 门禁接入点

- `/explore`：证据不足时只能输出 `hypothesis` 或 `unknown`，并列人工补证步骤。
- `/bug-explore`：围绕复现、影响面、证据缺口和补证动作展开，不写已确认根因。
- `/bug-complete`：`root-cause.md` 未达到 `confirmed` 且缺少证据链时，不得推进到 `pending_review`。
- `/opsx-apply`：BUG 来源 Change 开发前运行 root-cause evidence 校验；失败则阻断。
- `/opsx-modify`：验收返修或效果不如预期时，先记录偏差证据和补证步骤，再确定修复方向。
- 测试治理：BUG 修复必须有复现测试或明确说明不可自动化时的替代证据。
- UI 验收：视觉不符必须有截图、视口、关键交互状态和 computed style 证据。
- 日志/安全：日志证据必须可关联 trace/request，输出和文档必须脱敏。

## 脚本设计

`scripts/validate-root-cause-evidence.py` 负责结构化检查：

- `--bug BUG-xxxx-slug`：定位 `issues/bugs/{plan,review,archive}/<BUG>/root-cause.md`。
- `--change <change-id>`：从 Change 文档中识别 BUG 来源后校验对应 BUG；纯治理或 REQ Change 输出 `na`。
- `--all-active`：扫描 active BUG 与 active Change。
- 返回码：`0` 表示通过或不适用，`1` 表示阻断，`2` 表示用法错误。

脚本只做结构化门禁，不尝试替代人工判断；它要求 `root-cause.md` 包含“根因状态”和“证据链”，且 `confirmed` 状态至少有一条非空证据项。

## 安全边界

- 不保存原始 prompt、session 日志、完整工具输出、Cookie、Authorization header、真实 `.env`、真实客户数据或未脱敏日志。
- 人工补证内容持久化前必须脱敏。
- 脚本报告只输出路径、状态、缺失项和摘要，不打印原始敏感证据全文。

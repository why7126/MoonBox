---
purpose: 证据化根因分析治理
content: 问题排查、BUG 完善、验收返修和效果不符场景的根因状态、证据链、人工补证和校验门禁
created_at: 2026-08-14 17:00:00
updated_at: 2026-08-14 17:00:00
owner: MoonBox 产品团队
---

# 证据化根因分析治理

## 1. 目标

问题排查、BUG 完善、验收返修、效果不如预期、发布或部署异常时，AI MUST 先建立证据链，再确认根因。根因不能靠猜测；没有日志、复现、截图、测试失败、代码定位、配置差异、数据样本或运行时观测证据时，MUST 保持为待验证假设或未知状态。

## 2. 根因状态

| 状态 | 含义 | 门禁 |
|---|---|---|
| `unknown` | 证据不足，无法形成有效假设 | MUST 输出人工补证步骤；不得进入修复评审 |
| `hypothesis` | 有方向性推测，但缺少关键证据 | MUST 标注为假设；不得写成已确认根因 |
| `probable` | 有间接证据，但仍需补关键验证 | SHOULD 继续补证；除 P0 热修外不得通过 BUG review |
| `confirmed` | 证据链可复核，能解释现象和触发条件 | MAY 进入 BUG review、opsx 和修复实现 |

AI MUST NOT 将 `unknown`、`hypothesis` 或 `probable` 表述为“已确认根因”。如因 P0 热修需要基于 `probable` 先做 workaround，MUST 明确记录热修理由、证据缺口、回滚方案和补证任务。

## 3. 证据链

`confirmed` 根因 MUST 至少包含一条直接证据，并 SHOULD 包含复现或验证闭环。证据记录 SHOULD 使用表格：

```md
| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | test_failure | `uv run pytest ...` | 某断言稳定失败 | 证明 X 输入触发 Y |
```

允许的证据类型：

| type | 说明 |
|---|---|
| `reproduction` | 复现步骤、账号角色、入口、输入、期望/实际 |
| `test_failure` | 测试命令、失败用例、断言、堆栈关键段 |
| `runtime_log` | 后端日志、容器日志、trace_id、request_id、时间段 |
| `browser_console` | Console error/warning、页面路由、触发动作 |
| `network_request` | method、path、status、request/response 摘要、trace_id |
| `screenshot` | 截图/录屏、视口、页面状态、标注结论 |
| `computed_style` | 选择器、视口、关键 CSS 属性、实际值和期望值 |
| `data_sample` | 脱敏记录、查询结果、迁移状态、数据版本 |
| `config_diff` | 环境变量名、Compose、端口、feature flag、版本差异，敏感值脱敏 |
| `code_path` | 文件、函数、分支、异常路径或 diff 摘要 |

证据 MUST 可复核、可定位、已脱敏。MUST NOT 在文档、日志、截图说明或脚本输出中保存真实密码、Token、Cookie、Authorization header、真实 `.env` 原文、真实客户数据、未脱敏日志、本机绝对路径、系统用户名或用户主目录。

## 4. root-cause.md 模板

BUG 的 `root-cause.md` SHOULD 使用以下结构：

```md
# 根因分析

## 根因状态
status: confirmed

## 现象
- ...

## 证据链
| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | ... | ... | ... | ... |

## 已排除假设
| 假设 | 排除证据 |
|---|---|
| ... | ... |

## 已确认根因
...

## 修复方向
...

## 验证闭环
...
```

`status: confirmed` 缺少 `## 证据链` 或缺少有效证据项时视为不通过。若状态为 `unknown`、`hypothesis` 或 `probable`，MUST 在文档中保留证据缺口和人工补证步骤。

## 5. 人工补证契约

AI 判断证据不足时，MUST 输出可执行的补证指引，而不是泛泛要求“提供日志/截图”。补证指引 MUST 包含：

```text
待补证项：
- 证据名称
- 为什么需要
- 操作步骤
- 需要返回的字段
- 脱敏要求
- 返回格式
```

### 5.1 浏览器 Console

操作步骤：

1. 打开出问题页面。
2. 按 F12 或右键检查，进入 Console。
3. 清空 Console。
4. 重复触发问题。
5. 复制红色错误；warning 仅在相关时提供。
6. 将 token、手机号、邮箱、真实用户 ID 替换为 `<REDACTED>`。

返回字段：页面路由、操作步骤、Console 错误文本、出现时间。

### 5.2 Network 请求

操作步骤：

1. 打开 DevTools Network。
2. 勾选 Preserve log。
3. 重复触发问题。
4. 选中失败或异常请求。
5. 复制 method、path、status、request payload 摘要、response body 摘要、trace_id/request_id。
6. 不要提供 Authorization header、Cookie 或完整 Token。

返回字段：请求 method/path/status、响应摘要、trace_id/request_id、触发动作。

### 5.3 后端或容器日志

操作步骤：

1. 确认问题发生时间段。
2. 获取该时间段后端或容器日志。
3. 优先按 trace_id、request_id、用户 ID 占位符或 API path 过滤。
4. 只提供异常堆栈关键段和上下文摘要。
5. 脱敏连接串、密钥、密码、Token、Cookie、真实邮箱、手机号和客户数据。

返回字段：时间段、服务名、相关 path 或 trace_id、错误摘要、关键堆栈片段。

### 5.4 UI 视觉或交互偏差

操作步骤：

1. 记录页面路由、浏览器、视口尺寸。
2. 截取实际页面和期望参照图，标注偏差区域。
3. 对关键元素提供选择器或可定位描述。
4. 如偏差与字号、颜色、间距、层级有关，提供 computed style。
5. 若涉及交互，补充 hover/open/active/disabled 等状态截图。

返回字段：页面、视口、期望/实际截图、偏差描述、选择器、computed style。

### 5.5 数据异常

操作步骤：

1. 明确异常记录 ID 或业务键。
2. 查询相关脱敏字段、状态、更新时间、迁移版本。
3. 提供期望数据和实际数据差异。
4. 不提供真实客户姓名、手机号、邮箱、订单原文或敏感业务内容。

返回字段：记录标识、查询条件、脱敏结果、期望/实际差异、查询时间。

### 5.6 部署或环境异常

操作步骤：

1. 记录部署方式、本地/生产、镜像或提交版本。
2. 提供服务状态、健康检查结果、端口映射和配置差异。
3. 提供启动日志或失败命令摘要。
4. 环境变量只提供变量名和差异说明，不提供真实值。

返回字段：环境、版本、服务状态、健康检查、配置差异、日志摘要。

### 5.7 权限或登录问题

操作步骤：

1. 记录账号角色，不提供密码。
2. 记录入口路径和操作步骤。
3. 提供失败请求状态码、错误码、trace_id。
4. 提供服务端鉴权日志摘要，脱敏凭证。

返回字段：角色、入口、操作、请求状态、错误码、trace_id、日志摘要。

## 6. 工作流门禁

- `/explore` 和 `/bug-explore`：证据不足时 MUST 输出 `unknown/hypothesis/probable` 和人工补证步骤，不得确认根因。
- `/bug-complete`：未达到 `confirmed` 且证据链不足时 MUST 停留在探索或补齐阶段，不得推进 `pending_review`。
- `/bug-review --approve`：SHOULD 先确认 root-cause evidence gate 通过。
- `/bug-opsx`：BUG 未完成证据化根因时不得创建 fix Change。
- `/opsx-apply <BUG-full-id>`：实现前 MUST 运行或等价执行 `python scripts/validate-root-cause-evidence.py --bug <BUG-full-id>`。
- `/opsx-modify`：验收返修和效果不如预期 MUST 先记录偏差证据；证据不足时输出人工补证步骤。

## 7. 测试、日志与 UI 验收

- BUG 修复 MUST 添加复现或回归测试；无法自动化时 MUST 说明原因并提供替代证据。
- 测试通过只是验证结果，MUST NOT 替代根因证据。
- 日志和错误响应 SHOULD 支持 trace_id/request_id 或等价关联字段。
- UI 偏差 MUST 使用截图、视口、关键交互状态和 computed style 或等价证据定位。

## 8. 校验脚本

项目 SHOULD 提供：

```bash
python scripts/validate-root-cause-evidence.py --bug <BUG-full-id>
python scripts/validate-root-cause-evidence.py --change <change-id>
python scripts/validate-root-cause-evidence.py --all-active
```

脚本用于结构化校验，不替代人工判断；脚本失败时，AI MUST 输出缺失项和补证建议。

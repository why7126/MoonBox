# chat-midrun-question-response Specification

## Purpose
TBD - created by archiving change fix-chat-midrun-question-response. Update Purpose after archive.
## Requirements
### Requirement: 结构化问题与双阶段接入

系统 MUST 为支持的交互请求创建稳定问题身份，在RPC等待及事件循环统一接入，并展示选项和补充输入。

#### Scenario: 结构化问题与双阶段接入验证
- **WHEN** 受支持请求到达任一接收阶段
- **THEN** 持久化同一问题且展示可回答卡片，不误拒绝或重复创建

### Requirement: 专用回答与同轮消费

系统 MUST 允许授权用户在活跃轮次回答原问题，保留普通新命令互斥，答案只回传绑定执行实例和原请求。

#### Scenario: 专用回答与同轮消费验证
- **WHEN** 用户回答活跃轮次的问题
- **THEN** 原轮次消费答案并按预期分支续接，普通新命令仍被拒绝

### Requirement: 答案校验与幂等

系统 MUST 校验问题版本、选项、文本限制及幂等键，通过原子状态转换防止重复推进。

#### Scenario: 答案校验与幂等验证
- **WHEN** 重复同键同答案或冲突答案并发到达
- **THEN** 同内容返回一致结果，冲突拒绝，协议投递不被重复触发

### Requirement: 终止竞争与恢复

系统 MUST 在刷新重连时恢复真实问题状态，在取消、超时和进程丢失时拒绝迟到答案；无法确认投递时不得重发或新开写轮次。

#### Scenario: 终止竞争与恢复验证
- **WHEN** 待答期间发生取消、超时或worker重启
- **THEN** 按原子胜出状态处理；句柄不可恢复则标记不可恢复并提供安全续接指引

### Requirement: 权限与能力降级

系统 MUST 校验空间、会话和轮次权限；不支持交互时前置声明限制，不将Markdown选项伪装为可提交请求。

#### Scenario: 权限与能力降级验证
- **WHEN** 跨用户提交、撤权或适配器不支持交互
- **THEN** 越权拒绝且不泄漏问题，不支持时展示真实可执行指引而非无限等待

### Requirement: 交互状态与真实验收

系统 MUST 区分待答、提交中、错误、已回答和过期，保证键盘与窄屏可用；答案接收不等于任务完成。

#### Scenario: 交互状态与真实验收验证
- **WHEN** 在1440px和390px查看各状态并完成真实问答
- **THEN** 视觉及样式证据完整，真实轮次消费与后续效果独立于合成测试证明

### Requirement: 观测与敏感数据保护

系统 MUST 关联问题、请求和轮次，保护业务答案存取与保留策略，不在日志记录自由文本答案、完整Prompt或凭证。

#### Scenario: 观测与敏感数据保护验证
- **WHEN** 通过页面或直接API提交答案
- **THEN** 关联可信请求与任务节点，直接API不伪造行为事件，观测故障不阻断回答


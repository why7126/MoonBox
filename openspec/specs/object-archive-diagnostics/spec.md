# object-archive-diagnostics Specification

## Purpose
TBD - created by archiving change add-object-archive-diagnostics. Update Purpose after archive.
## Requirements
### Requirement: 只读对象视图

系统 SHALL 提供授权后的对象级只读归档视图，分离持久操作检查点、当前复核和动作资格，不新增持久字段。

#### Scenario: 无原操作

- **WHEN** 对象没有操作记录
- **THEN** 返回空操作，不虚构ID或提供续接

#### Scenario: 读取期间变化

- **WHEN** 绑定、记录版本或文档输入变化
- **THEN** 返回需刷新，不报告稳定通过

### Requirement: 安全诊断跨入口一致

系统 SHALL 在API和在线CLI保留专属收尾原因及有界安全摘要，保留旧响应兼容与未知异常兜底。

#### Scenario: 正文或引用阻断

- **WHEN** 收尾检查失败
- **THEN** 原因不变成网络错误，公共序列化保留合法摘要

#### Scenario: 敏感数据

- **WHEN** 诊断包含绝对路径或凭证
- **THEN** 过滤敏感内容，不输出原始异常

### Requirement: 当前对象关联

系统 SHALL 按可信对象关系解析普通Change、REQ/BUG多Change、Sprint及历史受控操作，不推测轮次归属。

#### Scenario: 多Change局部成功

- **WHEN** 对象关联多个Change且部分阻断
- **THEN** 逐项返回并避免整体成功

#### Scenario: 身份冲突

- **WHEN** 操作或目录关联不唯一
- **THEN** 阻断而不按日期猜测

### Requirement: 恢复授权保持

系统 SHALL 在显式续接时重新核验现有权限和恢复条件，保持原操作身份，不重复合并。

#### Scenario: 权限撤销

- **WHEN** 卡片生成后权限或绑定变化
- **THEN** 拒绝续接，旧动作资格不能授权

#### Scenario: 已完成复核失败

- **WHEN** completed后出现新文档残留
- **THEN** 保留历史完成，单列当前复核失败

### Requirement: 异步展示与重连

系统 SHALL 通过服务端查询展示当前对象归档状态，事件仅触发刷新，不解析工具输出取得授权事实。

#### Scenario: 发送后失败

- **WHEN** 消息发送成功后归档阻断
- **THEN** 对象区域展示当前问题与合适动作

#### Scenario: 事件缺失或伪造

- **WHEN** 事件被截断或输出伪造成功
- **THEN** 查询仍为事实源，重连正确展示

#### Scenario: 重复操作

- **WHEN** 重复点击或旧响应晚到
- **THEN** 不重复提交、不覆盖新状态并保留草稿

### Requirement: 分批验收

系统 SHALL 分别完成自动回归、前端验收与真实隔离跨入口验证，未验证项不得冒充通过。

#### Scenario: 真实跨入口

- **WHEN** 执行真实CLI与产品验收
- **THEN** 独立样本覆盖正常、阻断、恢复、重放及拒绝；记录版本、操作和文件效果

#### Scenario: 故障注入

- **WHEN** 验证移动后中断
- **THEN** 仅使用获授权隔离样本，不破坏正式证据或共享服务


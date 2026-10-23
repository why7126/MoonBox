---
title: 治理命令持久化恢复闭环增量规格
---
# 治理命令持久化恢复闭环增量规格

## ADDED Requirements

### Requirement: 操作身份与终态分离
系统 SHALL 持久保存业务操作身份、独立执行尝试和prepare/generation/validation/apply/readback/complete阶段，保持原stopped/failed终态。

#### Scenario: 同键重复或输入冲突
- **WHEN** 相同幂等键被重放
- **THEN** 同输入返回原操作/尝试，异输入冲突；新生成创建关联新操作，不改原turn

### Requirement: 模型前完整性和能力预检
系统 SHALL 在调用模型前验证记录完整性、schema/action及backend/worker/controller兼容交集和心跳；旧记录不伪造历史。

#### Scenario: 缺失记录或不兼容
- **WHEN** 准备记录缺失损坏、能力未知或交集为空
- **THEN** 明确失败且模型调用数为零；不同发行版本但兼容交集有效可继续

### Requirement: 按可信阶段续接
系统 SHALL 复用不可变成果、application和逐文件journal，恢复前重查权限、绑定、源指纹、期限及version，不承诺跨存储原子提交。

#### Scenario: 中断和响应丢失
- **WHEN** 生成完成后重启、部分文件已写或提交响应丢失
- **THEN** 分别从校验续接、前后镜像核验续接原集合、读回原应用；不重复模型或覆盖外部修改

### Requirement: 并发领取与有限自动重试
系统 SHALL 用CAS、对象互斥与fencing保护单次领取；每操作最多3次自动重试，退避2/10/30秒，持久次数及next_retry_at。

#### Scenario: 重启与争锁
- **WHEN** 临时错误后重启或两个控制器并发
- **THEN** 不重置预算，争锁不计次数，旧fence不可提交；未知执行占用阻塞；仅可证明未提交错误自动重试，未知提交先读回

### Requirement: 预算耗尽后的明确授权
系统 SHALL 将预算耗尽或不可重试冲突置为blocked，只读复查无写副作用。

#### Scenario: 用户手动重试
- **WHEN** 阻塞原因已解除且后端重新允许恢复，用户确认
- **THEN** 同请求去重后只领取一次剩余事务尝试并计manual_count，不重置自动预算，不创建自动循环

### Requirement: 主动停止和授权保护
系统 SHALL 撤销未领取自动恢复并保留原停止终态，apply前续接需明确确认。

#### Scenario: 停止发生在提交窗口
- **WHEN** 用户停止且原事务正在提交
- **THEN** 只进行原授权集合最小一致性恢复和读回；权限撤销仍阻塞，确认执行器终结或fence安全才接管，不自动下一命令

### Requirement: 恢复期限与清理保护
系统 SHALL 以可靠终态加7天、既有配置期限及原更早期限取最早截止，不因读或重试延期。

#### Scenario: 过期或缺少保留配置
- **WHEN** 期限到达、成果缺失或配置未知
- **THEN** 拒绝新恢复领取，给出具体原因；活动事务保护清理，半迁移标cleanup_blocked保留最小证据等待授权处置；已提交允许只读核验

### Requirement: 只读查询和受控恢复接口
系统 SHALL 提供权限过滤的操作详情与allowed_actions，恢复请求携带expected_version和idempotency_key并服务端重校验。

#### Scenario: 陈旧页面确认
- **WHEN** 用户在版本改变后确认恢复
- **THEN** 返回冲突并重新读回，不覆盖；GET无写入/模型副作用，重新生成仅填草稿

### Requirement: 可信业务完成
系统 SHALL 仅在校验、原完整文件集合应用、Workflow Sync及事实源读回一致后标业务完成。

#### Scenario: 评审恢复成功
- **WHEN** REQ或BUG成果恢复通过门禁
- **THEN** 全套文档迁入review且approved，registry/index同步，卡片刷新一致；原失败/停止仍保留，页面加载失败不回滚业务

### Requirement: 局部恢复界面与原型门禁
系统 SHALL 将prototype视为设计输入，最终验收同时依赖Change设计、REQ验收、1440px及关键交互视觉证据、computed style、Mock/API边界和REQ最终一致性回填。

#### Scenario: 恢复动作族验收
- **WHEN** 真实面板在1440x900及390x844呈现
- **THEN** Skeleton先确认；确认/提交/成功/阻塞/到期、键盘焦点及长原因无溢出，按钮按能力呈现，无模拟成功；共用展示关联REQ-0046

### Requirement: 可观测性与数据库兼容
系统 SHALL 在SQLite/MySQL保持等价唯一性、预算、CAS与迁移语义，关联operation/attempt/application/request/trace并脱敏。

#### Scenario: 直接API和保留验证
- **WHEN** 恢复由直接API调用或进入清理
- **THEN** 不伪造前端行为、不重复模型计费；诊断摘要90天、usage_events180天、聚合1年，不扩大敏感原文保留

### Requirement: 首期边界与真实验收
系统 SHALL 首期仅开放req-review和bug-review恢复，其他治理动作明确只观察或不支持。

#### Scenario: 部署验证
- **WHEN** 验收正常和中断恢复链路
- **THEN** 核验服务实际版本及原会话，各类最多一个正常一个恢复样本，故障先诊断；重启/刷新后状态一致，合成测试不冒充真实产品观察


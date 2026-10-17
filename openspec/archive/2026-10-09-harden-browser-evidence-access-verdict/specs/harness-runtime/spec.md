---
title: Agent 浏览器取证访问判定规格增量
change_id: harden-browser-evidence-access-verdict
capability: harness-runtime
---

# Agent 浏览器取证访问判定规格增量

## ADDED Requirements

### Requirement: 浏览器取证失败重试与访问结论

Agent 需要产品运行态证据时，SHALL 先检查现有浏览器窗口和目标标签页；清单失败时 SHALL 尝试直接连接浏览器窗口，并在当前入口失败后检查可行替代入口。单次工具超时或终端连接失败 SHALL NOT 单独作为产品无法访问的结论。Agent SHALL 区分旧页面展示、当前服务连通性和仍待验证的跨层事实。全部已有浏览器自主取证技能 SHALL 引用同一失败重试门禁，并接受集中校验。

#### Scenario: 浏览器清单超时但窗口可连接

- **WHEN** 浏览器清单调用超时而浏览器应用仍在运行
- **THEN** Agent 直接连接应用窗口，检查目标标签页并记录脱敏页面证据

#### Scenario: 终端入口连接失败

- **WHEN** 终端 HTTP 探测失败而浏览器可能有独立会话或网络路径
- **THEN** Agent 继续浏览器取证，不以终端结果宣称产品无法访问

#### Scenario: 旧页面仍可见

- **WHEN** 已加载页面显示目标信息但当前服务连通性尚未验证
- **THEN** Agent 仅确认页面展示事实，并在需要最新状态时刷新或观察相关请求

#### Scenario: 自主取证仍受阻

- **WHEN** 可行入口均失败或关键证据仍不足
- **THEN** Agent 逐项说明尝试路径、错误和缺口，再请求具体人工补证

#### Scenario: 技能入口遗漏失败重试门禁

- **WHEN** 任一浏览器自主取证技能未引用统一失败重试门禁
- **THEN** 治理校验失败，阻止将该技能作为已同步的取证入口

---
requirement_id: REQ-0052-stage-spec-reading-center
title: 九阶段流转规范查阅与研发规范中心验收标准
created_at: '2026-10-23 09:38:16'
updated_at: 2026-10-23 09:39:10
acceptance_status: not_started
---

# 九阶段流转规范查阅与研发规范中心验收标准

## 功能验收

- [ ] AC-001 九阶段入口：九阶段各在空列及有卡片时可打开摘要；已完成不出现虚构下一阶段。
- [ ] AC-002 摘要完整性：逐阶段核对条件、产物、角色、命令与异常分支；REQ/BUG 差异和验收返修语义正确。
- [ ] AC-003 同源定位：同一规范从两个入口打开时标识、指纹和正文一致，摘要跳到对应章节；缺锚点给出提示。
- [ ] AC-004 上下文返回：原文返回保留阶段及阅读位置；切换项目后无旧正文、筛选或缓存串读。
- [ ] AC-005 检索：分类与阶段过滤可组合，标题/正文关键词可搜索；无结果、长标题、特殊字符不异常。
- [ ] AC-006 日志：按时间倒序展示来源已有字段；字段缺失标为未记录，不生成历史事实。
- [ ] AC-007 版本：有历史版本时打开对应正文，无历史时明确不可取得；未提交变更标识工作区版本，不能冒充已生效。
- [ ] AC-008 过期：修改来源后刷新检测指纹变化；旧摘要标过期，重载后整体一致；并发变化不混版。
- [ ] AC-009 权限安全：无权、权限撤销、跨项目同路径、直接链接、目录穿越、符号链接越界与危险 Markdown 均不能泄露或执行。
- [ ] AC-010 异常：覆盖加载、空目录、缺映射、缺原文、读取失败和重试；局部失败不影响其他条目。
- [ ] AC-011 只读：完整查阅前后规范及 Issue/Change/Sprint 文件与业务状态不变；无编辑、审批、流转请求。
- [ ] AC-012 观测：行为与读取请求可关联，服务端生成 request_id；无正文/搜索原文/私有路径；采集失败不阻断阅读。

## 验证数据与证据

使用隔离测试项目，准备 REQ/BUG 分支、九阶段映射、两版本规范、一份未提交变更、缺字段日志、失效锚点及无权限身份。权限负例用合成数据，不采集真实客户正文。

命令测试验证版本和零写入；真实浏览器验证入口、返回、检索和权限提示，两类证据分别记录。每条记录环境、输入版本、操作、预期、实际与证据路径，结果全部 pending，不以原型交互代替产品验收。

性能基线：100 份规范、总正文 5 MiB、500 条日志的隔离样本；稳定环境连续 20 次，暖读取及搜索 P95 不超过 2 秒，首次索引不超过 5 秒；记录环境与冷暖条件。超限给加载反馈，不静默挂起。

## 横切 AC（knowledge-base）

管理端列表、表单、弹窗和上传四种标签均不适用：本需求为 Web 只读阅读。无该四类横切 AC。依据 docs/knowledge-base/retrospectives/sprint-011-retrospective.md 补充证据语义要求：

- [ ] AC-XCUT-001 当前来源、生效依据和历史日志分别展示；历史日志不能证明当前准入或生效。
- [ ] AC-XCUT-002 合成权限/零写入回归与真实浏览器观察分开记录，不能以按钮打开证明完整链路通过。

## 原型驱动 UI AC

来源：docs/knowledge-base/best-practices/prototype-driven-ui-gate.md。

- [x] AC-PROTOTYPE-001 原型页面、区域、层级、状态、交互、数据与断点完成拆解，见 prototype/web/context.md。
- [ ] AC-PROTOTYPE-002 Change 先建立 UI Contract、UI Skeleton 和稳定 selector，完成首轮结构确认后实现细节。
- [ ] AC-PROTOTYPE-003 1440px 与窄视口、深浅主题、摘要/原文/日志/空错态取得截图及 computed style 证据。
- [ ] AC-PROTOTYPE-004 归档前 PRD、业务流程、用户故事、验收、trace 与原型保持最终一致。
- [ ] AC-PROTOTYPE-005 抽屉焦点进入和返回、Escape、内部点击不误关与外部点击关闭均可用；外部关闭使用 capture 阶段或等价机制。

## 验收结果回填

```yaml
acceptance_status: not_started
accepted_at: null
accepted_by: null
source_change: null
source_sprint: null
evidence: []
failed_items: []
source_event: req.complete
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

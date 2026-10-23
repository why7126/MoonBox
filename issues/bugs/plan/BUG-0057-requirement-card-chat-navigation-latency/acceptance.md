---
bug_id: BUG-0057-requirement-card-chat-navigation-latency
title: 会话准备导航延迟验收计划
created_at: '2026-10-21 09:22:50'
updated_at: '2026-10-21 09:30:17'
owner: 产品团队
acceptance_status: not_started
---

# 会话准备导航延迟验收计划

## 验收状态

acceptance_status: pending

以下为待实施、待执行计划，不表示测试通过；未创建 Change，无性能修复实现。

| AC | 验收内容 | 证据与通过条件 |
|---|---|---|
| AC-01 | 同请求耗时归因 | 一个 request_id 可关联浏览器与所有准备阶段；解释主要耗时、读取次数及重试；缺失阶段显式报告，不能以独立微基准替代。 |
| AC-02 | 已有会话的写动作性能 | 同部署、同数据规模、同并发条件前后各至少五个样本，比较中位数与最大值；性能阈值在修复方案评审时确定，禁止仅凭主观变快通过。 |
| AC-03 | 新会话与已有会话 | 已有会话保持复用，新会话不重复创建，返回目标与命令草稿一致。 |
| AC-04 | 一致性与并发 | 源/投影不一致、读取中写入、持续更新、版本推进时按契约重试或阻断，禁止复用过期快照。 |
| AC-05 | 权限和流程门禁 | 无权限、错误阶段、执行占用、待审候选仍正确拒绝或引导，不因减少读取绕过检查。 |
| AC-06 | 幂等与失败交互 | 重复点击、网络失败、重试不产生重复会话/动作；准备状态可辨识，失败提示可恢复。 |
| AC-07 | 只读与直接查看入口回归 | 只读动作、“查看执行”不误走写动作门禁；准备导航与历史加载分别测量。 |
| AC-08 | 状态协调与观测 | 如收窄 reconcile，目标与相关对象恢复语义不回退；复用会话的每次请求均可独立归因，日志不包含凭证/业务正文。 |

## 验收结果回填

```yaml
acceptance_status: not_started
accepted_at: null
accepted_by: null
source_change: null
source_sprint: null
evidence: []
failed_items: []
source_event: bug.enrich
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 观测声明

product_data_collection_observability: applicable；affected_layers: Web、API、request_logs、Task Trace。validation: 已有请求级观测和采样，阶段证据待补。DB schema、部署、权限策略、对象存储及客户端生成未变更，暂为 N/A；后续方案若触及须重新评估。

## 诊断证据补充

AC-01 已取得隔离 ASGI 同请求阶段树，尚未取得线上原请求全阶段计时；不得标记修复验收通过。完整数据及夹具差异见 root-cause.md。其他 AC 未执行，未实现性能修复。

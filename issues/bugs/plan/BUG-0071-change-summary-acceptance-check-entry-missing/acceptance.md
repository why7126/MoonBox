---
title: 独立 Change 归档按钮禁用且缺少验收检查入口回归验收清单
created_at: '2026-10-30 09:48:10'
updated_at: 2026-10-30 09:49:12
acceptance_status: not_started
---

# 独立 Change 归档按钮禁用且缺少验收检查入口回归验收清单

## 回归验收

全部未执行，不以文档完善标记产品通过。

- [ ] AC-001 摘要首屏验收卡提供检查入口及待检查说明；初始归档仍禁用。
- [ ] AC-002 检查中防重复，检查调用只读门禁不执行验收计划命令、不发Agent消息、不创建归档任务。
- [ ] AC-003 检查通过且其他授权/执行条件满足才开放归档；真实阻塞展示AC或缺口及处理方向。
- [ ] AC-004 检查失败显示错误并可重试；取消/切项目和迟到响应不会串对象。
- [ ] AC-005 证据变化、版本过期或权限撤销使旧结果失效，归档提交重新校验；历史passed不直接授权。
- [ ] AC-006 无权限、只读、归档、多个卡片、不同项目场景覆盖；优先级和任务7/7不绕过门禁。
- [ ] AC-007 检查行为与请求关联、脱敏，采集失败不阻断；新增接口同步API及客户端。
- [ ] AC-008 回归首屏摘要性能不退回全量重检查，真实产品待检查→检查→结果可操作链与合成测试分开记录。

## UI 证据

1440×900与390×844、深浅主题检查相关卡片状态，记录截图及按钮disabled/文本、字号、间距、颜色、overflow等样式；无需整页复刻用户截图。修复后重新采集，不沿用旧故障截图当通过证据。

## 验证记录

当前仅根因和文档检查；实际实现、产品回归及验收通过均待后续Change。

## 验收结果回填

```yaml
acceptance_status: not_started
accepted_at: null
accepted_by: null
source_change: null
source_sprint: null
evidence: []
failed_items: []
source_event: bug.complete
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

---
created_at: 2026-09-15 00:02:17
updated_at: 2026-09-15 00:02:17
owner: MoonBox 产品团队
source_bug: BUG-0018-standalone-change-acceptance-source-unverified
---

# 测试计划

## 最小相关验证

| 影响面 | 验证 |
|---|---|
| 后端治理聚合 | 运行需求中心 Change 可见性相关 pytest，覆盖验收来源识别。 |
| API 响应语义 | 使用后端测试或合成上下文确认 `disabled_reason` 不再误报；若响应字段无变化，不运行客户端生成。 |
| 前端展示 | 若实现仅改变后端禁用原因，不需要新增前端快照；若前端渲染逻辑调整，补充聚焦前端测试。 |
| 文档与 OpenSpec | 运行当前 Change 中文校验与 OpenSpec validate。 |
| 观测 | 确认不新增 usage_events、DB、Task Trace；请求日志沿用既有脱敏策略。 |

## 建议命令

```bash
pytest src/backend/tests/test_change_visibility.py
python scripts/validate-openspec-language.py --change fix-standalone-change-acceptance-source --residual-report
openspec validate fix-standalone-change-acceptance-source --strict
```

---
created_at: 2026-09-15 00:02:17
updated_at: 2026-09-15 00:02:17
owner: MoonBox 产品团队
source_bug: BUG-0018-standalone-change-acceptance-source-unverified
source_sprint: sprint-006
---

## 背景与动机

BUG-0018 记录了需求中心独立 Change 卡片在验收中阶段误报“验收来源待核实：未找到交付验证记录”的问题。目标 Change 已存在非空 `## 验证摘要` 或 `## Validation Log` 章节，但后端验收来源识别只接受少量固定标题，导致卡片提示与真实交付证据不一致。

该问题影响需求中心对独立 Change 交付完整性的可信展示。修复需要扩展独立 Change trace 交付验证章节识别，同时保持显式 `acceptance_refs` 的安全边界和“证据存在不等于自动验收通过”的语义。

## 变更内容

- 扩展独立 Change trace 验收来源识别，接受非空 `验证摘要`、`Validation Log` 和项目既有等价验证章节。
- 保持 `acceptance_refs` 优先级和安全校验：无效、越界、缺失或空文件必须返回具体原因，不得回退掩盖显式错误。
- 保持既有 `acceptance.md`、`verification.md`、`验证记录`、`验收记录`、`验证结果`、`验收结果` 识别能力。
- 增加回归测试覆盖 `验证摘要`、`Validation Log`、既有来源、显式引用失败和无来源提示。
- 回填 BUG、Sprint 和父需求追溯，使后续 `/opsx-apply BUG-0018-standalone-change-acceptance-source-unverified` 可解析到同一 Sprint 与 Change。

## 能力范围

### 新增能力

- 无。

### 修改能力

- `web-catalog-requirement-center-real-data`: 扩展独立 Change 交付验收来源识别标题范围，并保留安全边界。

## 影响范围

- 后端治理聚合：独立 Change 卡片验收来源判断和禁用原因生成。
- Web 前台：卡片不再展示由后端漏判造成的错误红色待核实提示；前端展示结构不变。
- API：需求中心上下文响应的既有字段语义更准确，不新增字段、不修改路径、不要求客户端生成。
- 测试：补充后端回归测试；如前端仅消费后端禁用原因，无需新增 UI 行为。
- 文档与追溯：更新 BUG trace、父需求关联缺陷、Sprint scope 与 OpenSpec delta spec。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - api
    - request_logs
  reason: 本修复影响需求中心上下文接口中独立 Change 动作禁用原因的服务端计算结果；不新增 API 路径、请求头、响应字段、DB、对象存储、行为事件、Task Trace 或流程节点。
  validation: apply 阶段需通过后端回归测试验证禁用原因修正，并确认请求日志保持既有脱敏摘要；无新增 OpenAPI/Orval 生成要求。
```

## 回滚计划

- 若扩展标题识别造成误判，可回退标题集合到既有四类中文标题，并保留显式 `acceptance_refs` 与文件入口逻辑。
- 回滚后需保留 BUG-0018 的测试样本作为失败证据，避免后续归档误认已闭环。
- 回滚不得删除 BUG 文档包或 Sprint 追溯，只需将 Change 状态和验收结果如实记录为未通过或返修。

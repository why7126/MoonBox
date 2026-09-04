# 提案：建立 UI 参考稿复刻治理流程

## 背景

REQ-0023 的产品工作台现代 Ops 视觉升级在后期出现多轮逐元素返修：列头、空列、卡片、标签、按钮、sticky 边界等问题需要用户反复截图指出。复盘结论是现有原型驱动 UI 门禁能要求截图和 computed style，但没有在 explore、req、opsx 阶段把“参考稿复刻”拆成组件级视觉契约、selector 映射和分批验收门禁。

## 变更内容

- 在 UI 设计规则和原型验收标准中新增“UI 参考稿复刻契约”，明确适用条件、保真模式、反向工程清单、selector 映射、computed style 采样和分批验收。
- 更新 explore、req-complete、req-opsx、opsx-apply、opsx-modify、opsx-archive 技能，使参考稿复刻从只读分析、需求完善、Change 生成、实现、返修到归档连续承接。
- 补充 AGENTS 入口和上下文预算规则，避免 UI 复刻任务靠宽泛视觉形容词或逐元素问答推进。
- 写入治理日志并将纯治理 Change 纳入当前 Sprint。

## 范围

本 Change 只修改治理资产和 OpenSpec 文档，不修改 `src/` 业务实现、API、数据库、部署、客户端生成物或运行时行为。

## 风险

- 规则新增后 UI Change 的前期分析成本会上升，但可减少后期逐元素返修。
- 若参考稿缺少 HTML、截图或关键状态，流程会要求先补证，短期看会更严格。

## 验证

- OpenSpec Change 校验。
- 上下文预算、OpenSpec 中文优先和目录结构校验。
- 聚焦 diff 复核，确认未触碰 `src/` 业务实现。

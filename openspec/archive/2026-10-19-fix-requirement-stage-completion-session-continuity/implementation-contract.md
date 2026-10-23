---
title: 需求中心执行门禁实施契约与证据矩阵
created_at: "2026-10-19 12:09:24"
updated_at: "2026-10-19 12:09:24"
---

# 需求中心执行门禁实施契约与证据矩阵

## 增量视觉契约

fidelity_mode: preserve-existing-layout。参考优先级：当前需求中心卡片结构与设计token，其次父需求prototype-context；历史原型不覆盖已交付卡片宽度/负责人修复。新增状态为执行中、结果待核对、可继续；只读入口和原阶段布局保留，不新增modal。

| 区域 | 骨架selector | 状态/动作 | 实施与证据门禁 |
|---|---|---|---|
| 执行中卡片 | [data-testid=governance-running] | 下一动作禁用，查看原执行 | 1440px首轮确认、状态文案及按钮可访问名称 |
| 待核验卡片 | [data-testid=governance-needs-review] | 保留成果，仅查看 | 失败/停止/unknown分支与权限验证 |
| 已核验卡片 | [data-testid=governance-ready] | 原会话继续 | 验证后迁移，不覆盖草稿 |
| 查看执行 | [data-testid=view-execution] | 直接跳转Chat，无modal | 本人可访问会话才显示；他人占用仅摘要 |
| 文档/进度/验收 | 既有document/task/drawer入口 | 继续只读 | 原drawer/modal保留，执行锁不拦截 |

动作族矩阵：下一治理动作沿用现有动作对话框/Chat准备；busy时不打开新的动作对话框，不填入建议命令；查看执行直接导航；文档、进度和验收沿用既有抽屉。本轮骨架HTML无API调用、无真实身份，三个示例是合成状态，不是产品截图。

采样清单：卡片width/min-height/padding/border、状态line-height/color、按钮disabled/cursor、footer gap、长ID溢出；复用现有token，不用独立HTML样式作为生产token来源。实施分批为契约/骨架、共享状态与动作组件、真实API及草稿、视觉与交互验收。

## 当前门禁

用户已确认骨架；实际1440×900产品视口、关键交互、computed style及父需求一致性已检查。详细AC与逐入口证据见 [逐项签认](evidence/acceptance/signoff.md)，明确标记真实模型、真实HTTP及合成故障注入。正式自动验收结果由 acceptance-plan.json 和机器清单给出，文档存在不替代验收。

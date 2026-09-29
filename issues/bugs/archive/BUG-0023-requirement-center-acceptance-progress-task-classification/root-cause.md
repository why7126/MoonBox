---
bug_id: BUG-0023-requirement-center-acceptance-progress-task-classification
title: 需求中心验收中卡片进度未按 tasks.md 分类统计返修任务
status: confirmed
created_at: 2026-09-15 22:47:41
updated_at: 2026-09-15 22:47:41
owner: 产品团队
---

# 根因分析

## 根因状态

status: confirmed

## 现象

需求中心「验收中」卡片显示研发、测试、人工验收三组进度。用户附件 Image #1 显示两张验收中卡片均呈现满格或完成态：

- Capture 图文候选审阅与确认采集：研发 `33/33`、测试 `3/3`、人工验收 `1/1`。
- 聊天框新增 Agent、模型和推理程序选择：研发 `29/29`、测试 `3/3`、人工验收 `1/1`。

该展示会让用户误以为研发、测试和人工验收都已按当前交付闭环完成。但产品定义要求三类进度都来自 `tasks.md` 的分类 checkbox，并且 `/opsx-modify` 返修任务应进入对应分母。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | screenshot | 用户附件 Image #1 | 验收中卡片展示 `研发 33/33 测试 3/3 人工验收 1/1` 和 `研发 29/29 测试 3/3 人工验收 1/1` | 证明用户可见页面存在满格进度展示，且影响验收中卡片 |
| E2 | code_path | `src/backend/app/services/requirement_center.py` `_build_issue` | Issue 响应字段由 `task_progress`、`test_progress` 和 `manual_acceptance_count=0` 组成 | 证明三类进度不是同一 `tasks.md` 分类模型输出 |
| E3 | code_path | `src/backend/app/services/requirement_center.py` `_change_tasks` | 研发进度的来源会遍历 linked Change `tasks.md` 中所有 checkbox，只累计总数和完成数 | 证明当前 `task_progress` 未区分研发、测试、人工验收任务类别 |
| E4 | code_path | `src/backend/app/services/requirement_center.py` `_test_progress` | 测试进度在验收阶段按 `acceptance.md`、`review.md`、`trace.md` 三个文档存在性返回 `(done, 3)` | 证明 `测试 n/3` 是文档齐备度，不是 `tasks.md` 测试任务完成度 |
| E5 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx` `visibleManualAcceptanceProgress` | 验收中且存在测试进度时，若没有显式人工验收进度且 `manualAcceptanceCount <= 0`，前端显示 `[1, 1]` | 证明 `人工验收 1/1` 可由默认推导产生，不代表真实 sign-off 或 `tasks.md` 人工验收任务完成 |
| E6 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx` 卡片进度渲染 | 卡片直接渲染 `taskProgress`、`testProgress` 和 `manualProgress` 三组值 | 证明 E2-E5 的后端字段与前端推导会直接成为用户看到的三组进度 |
| E7 | code_path | `src/web/src/requirement-center.test.tsx` | 测试 fixture 明确使用 `test_progress: [1, 3]`、`manual_acceptance_count: 1`，并断言 `测试 1/3`、`人工验收 0/1` 只用于打开 `tasks.md` 并定位章节 | 证明现有测试固化了旧口径：进度值不是按 `tasks.md` 分类统计得到 |
| E8 | code_path | `rules/document-governance.md` | 文档治理规定 `tasks.md` 是计划任务、执行勾选和完成门禁入口，`acceptance-fixes.md` 是 `/opsx-modify` 完整返修台账事实源，返修完成后回到验收中 / 待复验 | 证明产品治理链路需要把返修任务作为交付闭环事实处理，而当前卡片进度没有结构化纳入返修任务分类 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| 只是前端样式或文案误导，数据实际已经按分类统计 | E2-E5 显示响应字段本身就不是分类统计模型，前端只是渲染这些字段或默认推导 |
| 测试 `3/3` 来自自动化测试任务通过数量 | E4 显示测试进度来自三个文档存在性，不读取 `tasks.md` 测试任务 |
| 人工验收 `1/1` 代表人工 sign-off 已完成 | E5 显示 `manualAcceptanceCount <= 0` 时会显示 `[1, 1]`，不能证明人工确认事实 |
| `/opsx-modify` 返修任务已经自然进入三类进度 | E3 仅做所有 checkbox 总数统计，E4/E5 不读取返修任务分类；E8 要求返修作为交付闭环事实处理，但当前缺少对应分类口径 |

## 已确认根因

需求中心验收中卡片的三类进度缺少统一的 `tasks.md` 分类统计模型。

当前实现将三类展示拆成三种不同事实源：

1. 研发进度使用 linked Change `tasks.md` 的全部 checkbox 总数。
2. 测试进度使用 `acceptance.md`、`review.md`、`trace.md` 三个文档存在性。
3. 人工验收进度使用前端对 `manual_acceptance_count` 的默认推导。

因此，卡片显示的「研发 / 测试 / 人工验收」并不代表 `tasks.md` 中研发类、测试类、人工验收类任务的完成度，也无法稳定纳入 `/opsx-modify` 返修追加任务。该根因可以解释 Image #1 中测试和人工验收满格、以及用户指出的返修任务未进入进度口径问题。

## 修复方向

- 在后端建立 `tasks.md` 分类解析模型，输出至少三组结构化进度：研发、测试、人工验收。
- 分类优先使用稳定章节或显式标记；长期应同步沉淀 `tasks.md` 三类任务与 `/opsx-modify` 返修任务统计口径，避免靠关键词漂移。
- `/opsx-modify` 追加的可关闭返修任务若以 checkbox 形式存在，应按任务性质进入研发、测试或人工验收分母。
- 保留 `acceptance-fixes.md` 作为完整返修台账事实源，但不要把台账表格正文直接计入卡片进度。
- 更新前端卡片展示、API schema / OpenAPI / 客户端类型和回归测试，确保进度值来自同一分类模型。

## 验证闭环

修复后需要验证：

- 构造含研发、测试、人工验收三类任务的 `tasks.md`，卡片分别展示三类完成度。
- 构造含 `/opsx-modify` 返修任务的 `tasks.md`，返修任务进入对应分类分母。
- 未完成人工复验任务时，人工验收不得默认显示 `1/1`。
- 文档齐备但测试任务未完成时，测试不得显示 `3/3` 或完成态。
- Image #1 类似的验收中卡片在修复后不再由文档存在性和默认推导误报完成。

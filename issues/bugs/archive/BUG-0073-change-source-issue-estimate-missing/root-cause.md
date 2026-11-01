---
title: Change 来源人力估算缺失根因分析
created_at: '2026-10-31 23:16:00'
status: confirmed
bug_id: BUG-0073-change-source-issue-estimate-missing
updated_at: '2026-10-31 23:16:00'
---

# Change 来源人力估算缺失根因分析

## 根因状态
status: confirmed
确认范围：仓库当前代码对真实Sprint估算记录的读取机制；不等于当前部署浏览器已复验或修复有效。

## 现象
来源BUG已有3人天，关联Change卡片显示待估算。

## 证据链
| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | data_sample | iterations/archive/sprint-018/sprint.yaml，scope_estimates | BUG-0070行含change关联及estimated_person_days: 3 | 数据已填写 |
| E2 | code_path | src/backend/app/governance/card_metadata.py，estimate_metadata | Change分支只接受自身id或无id行 | Issue id行被排除 |
| E3 | code_path | src/backend/app/governance/change_index.py，apply_card_metadata | 交付卡以card.id和空changes调用 | 按Change身份取值 |
| E4 | reproduction | 下方复现命令，本轮断言通过 | 相同scope，Issue=3/available，Change=None/missing | 真实输入触发取值缺失 |
| E5 | code_path | src/web/src/pages/catalog/RequirementCenterPage.tsx，rc-estimate-pending | 非available显示待估算 | 解释用户文案 |

## 可复核命令
```bash
PYTHONDONTWRITEBYTECODE=1 bash scripts/project-python.sh - <<'CHECK'
import runpy, yaml
from pathlib import Path
f=runpy.run_path('src/backend/app/governance/card_metadata.py')['estimate_metadata']
s=yaml.safe_load(Path('iterations/archive/sprint-018/sprint.yaml').read_text())['scope_estimates']
c='fix-standalone-change-updated-time'
b='BUG-0070-standalone-change-updated-time-missing'
assert f(s,b,[c]) == {'estimated_person_days':3,'estimate_status':'available'}
assert f(s,c,[]) == {'estimated_person_days':None,'estimate_status':'missing'}
print('读取机制复现通过；非修复通过')
CHECK
```

## 已排除假设
| 假设 | 排除证据 |
|---|---|
| Sprint未填写估算 | E1、E4 |
| 3为非法值或零值 | E4 Issue路径接受3 |
| 仅前端样式隐藏数字 | E4后端直接返回缺失 |

## 已确认根因
估算归属规则过于严格：为防止Issue总量复制给多个Change，排除所有带Issue id的行，未区分明确唯一归属。原REQ-0056禁止多Change重复计量仍有效，不能简单全量继承。

## 修复方向
优先Change自身估算；来源与目标归属唯一且无冲突时允许引用来源估算并标明来源。多个交付或多个来源无法确定归属时保持待核实，不自动求和、均分、复制或改写Sprint容量。

## 验证闭环
本轮真实输入函数断言通过，机制确认；修复未实施。后续按acceptance.md验证独立优先、一对一、多来源、一对多、零值及UI真实刷新。当前部署版本、历史单次请求响应未采集，不声称线上复验。

## 修复验证补充
旧复现命令保留为修复前证据（无授权来源参数仍保守返回missing）。当前完整索引验证BUG-0070已返回3/available及来源ID；本地测试服务重建后真实页面复验通过，详见关联Change verification.md。历史单次请求仍未追溯，不扩大原根因确认范围。

---
bug_id: BUG-0053-deployed-acceptance-input-resolution
title: 部署态验收输入解析不完整导致纯 Change 归档误阻塞根因分析
created_at: '2026-10-20 18:56:49'
updated_at: '2026-10-20 18:56:49'
owner: 产品团队
severity: high
root_cause_status: confirmed
---

# 部署态验收输入解析不完整导致纯 Change 归档误阻塞根因分析

## 根因状态

status: confirmed

确认范围限本会话已取得的样本、代码分支与当时部署版本，不等于修复验收通过。

## 现象

本地 ready、部署 blocked，纯 Change 完成/归档按钮禁用。

## 证据链

| ID | 类型 | 来源 | 观察与支持的判断 |
|---|---|---|---|
| E1 | reproduction | 本会话刷新后的需求中心 `/requirements` 与用户截图，摘要见 capture.md | 同一卡片 6/6、blocked、完成/归档禁用，证明用户可见影响 |
| E2 | data_sample | `scripts/opsx_acceptance.py --change optimize-governance-feedback-loop --readiness` 及 `openspec/changes/optimize-governance-feedback-loop/evidence/acceptance/20261020183342423385-0a32c636/manifest.json` | ready、stale=[]，run_id 与部署态相同，排除读取了不同验收轮次 |
| E3 | code_path | 当时运行容器的 acceptance_evidence.input_bytes；本地对应 `src/backend/app/governance/acceptance_evidence.py` | 部署仅将 src/scripts 路由至可信源码根，四个输入被误判缺失；源码绑定存在且可访问，排除全局未配置源码根 |
| E4 | data_sample | 本会话部署态只读输入诊断与内存指纹对照，摘要见 capture.md | 从既有绑定源码根读取四个文件后，三个 AC 指纹全部匹配 manifest，直接解释解析缺口与 stale 的因果关系 |

以上运行态证据复用本会话前序取证，不表示本次生成命令重新执行了部署验收。原始终端输出未复制入仓库；可按相同仓库绑定、验收轮次和四个相对输入复核。当前本地代码已包含 tests 与目录输入处理，但根级文件来源仍未覆盖；本地工作区与部署版本不可混同。


## 已排除假设

| 假设 | 排除依据 |
|---|---|
| 验收运行轮次不同 | 本地与部署读取相同 run_id：20261020183342423385-0a32c636 |
| 源码绑定完全缺失或不可达 | 当时部署绑定已配置且可访问；四个文件可从绑定源码根读取 |
| 三个 AC 的实际输入已经变化 | 只读内存对照读取正确输入后，三个指纹均匹配原 manifest |

## 已确认根因

根因状态：confirmed（针对本轮已取证样本及当时部署版本）。部署态输入读取按顶层目录限定源码来源，未覆盖验收计划引用的测试文件和根级文件；存在的输入被当作缺失参与指纹计算，导致有效证据被标为 stale，归档准入随之阻断。


## 修复方向

分别验证读取来源、指纹一致性及真实部署页面恢复；增加缺失、改动、目录和越界输入的负向覆盖。源码根只读且可信这一安全边界保持不变。当前没有实施或验证修复，修复效果尚未测量。


## 验证闭环

复用 capture.md、bug.md 的已取得证据完成现象—代码分支—原因对应；逐项修复验收见 acceptance.md，目前均未执行。没有额外人工补证阻塞，其他样本影响面在修复回归时核实。

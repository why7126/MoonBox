---
bug_id: BUG-0028-requirement-center-card-owner-raw-user-id
title: 需求中心 Capture 卡片负责人标识根因分析
status: confirmed
created_at: 2026-10-08 17:53:55
updated_at: 2026-10-09 23:13:15
owner: 产品团队
---

# 需求中心 Capture 卡片负责人标识根因分析

## 根因状态

status: confirmed

确认范围：当前本机 MoonBox 需求中心中，REQ-0038 的负责人标签直接显示并截断 `user_` 内部标识。刷新后的页面、同条目治理 owner、后端映射函数及前端渲染路径形成可复核闭环；BUG 卡片、其他来源、详情与筛选的影响范围仍待修复阶段验证。

## 现象

capture.md 曾记录 REQ-0038 卡片显示并截断内部用户标识。2026-10-09 在 Firefox 访问本机 `http://localhost:39002/requirements`，刷新后以 `REQ-0038` 筛选，页面重新加载完成，卡片负责人标签仍显示截断的 `user_` 内部标识；可访问性树保留同一标签的完整标识。会话截图仅用于当轮视觉核对，文档不保存原始标识或未脱敏图像。

## 证据链

| id | type | source | 摘要 | 支持的判断与边界 |
|---|---|---|---|---|
| E1 | reproduction | capture.md；bug.md 既有反馈 | 用户反馈新建 Capture 后卡片显示 user_ 前缀标识 | 二手复现记录；原图与环境待补 |
| E2 | code_path | src/backend/app/api/v1/capture_drafts.py:37；src/backend/app/governance/capture_confirmations.py:72 | reader.actor 进入确认流程，入队 owner 取 actor | 当前代码可传递内部身份；未确认线上 actor 值 |
| E3 | code_path | src/backend/app/governance/capture.py:55、67、112 | 批量候选、主文档和追溯记录传递 payload.owner | 写入路径未在此处解析名称 |
| E4 | code_path | src/backend/app/services/requirement_center.py:1406 | _owner_name 只映射固定别名，其他非空字符串原样返回 | 内部 ID 无自动可读名称转换 |
| E5 | code_path | src/web/src/pages/catalog/RequirementCenterPage.tsx:3214 | .rc-owner-tag 文本及 title 均取 issue.owner | 卡片直接展示传入值；需实际响应关联 |
| E6 | reproduction | bug.md 历史隔离函数记录 | 合成标识与 product 两项断言通过 | 历史合成证据，不是页面复现 |
| E7 | reproduction | 本轮 Python AST 隔离调用 _owner_name | user_synthetic_bug0028 原样返回；product 返回产品团队；None 返回未分配；3/3 通过 | 可按下述步骤复核函数行为，未连接服务或数据库 |
| E8 | reproduction | Firefox，`/requirements`，2026-10-09 23:12（Asia/Shanghai），刷新后筛选 `REQ-0038` | 页面完成同步，单条卡片标签显示并截断 `user_` 内部标识；可访问性树呈现该标签完整值；截图视觉核对一致 | 直接复现报告现象；原始身份值未落盘，当前本机页面可按相同步骤复核 |
| E9 | data_sample | `issues/requirements/_registry.yaml` 的 `REQ-0038-capture-md` 条目 | owner 是 `user_` 前缀内部标识；记录来源为 capture | 与 E8 为同一 REQ，确认治理事实源已有内部身份键；值已脱敏 |
| E10 | reproduction | 同条目隔离断言与代码路径：`requirement_center.py:210,1406`；`RequirementCenterPage.tsx:3214` | E9 的实际 owner 传入 `_owner_name` 原样返回，前端 `.rc-owner-tag` 的文本与 title 均取 `issue.owner`；三项断言通过 | 从同条目治理值到页面显示的当前代码链路可复核；不声称抓取了 Network 响应 |

E7 复核：只解析 requirement_center.py 的 AST，提取 _owner_name 函数，以 typing.Any 补齐注解后独立执行，分别断言上述三个输入及返回值。不导入应用，不产生业务写入。

## 已排除假设

| 假设 | 处置与证据 |
|---|---|
| 仅增加标签宽度即可解决负责人辨识 | 对当前代码路径不成立：E4、E5、E7 表明完整文本仍为标识；不据此排除实际环境其他样式因素 |
| 当前映射函数已统一解析任意 user_ 标识 | E4、E7 排除这一函数级假设 |
| 部署版本不同导致本机页面无法复现 | E8 刷新后仍复现，排除当前本机环境下的这一解释；其他部署环境不在本次确认范围 |
| 上游数据为可读名称、仅样式截断名称 | E8、E9、E10 表明同一条目的治理 owner 和显示内容均为内部标识；扩大标签宽度只会露出完整标识 |

## 已确认根因

Capture 来源条目的稳定内部身份键被写入治理 owner；需求中心读取时 `_owner_name` 对未知 `user_` 值原样返回，前端负责人标签又直接使用 `issue.owner`。因此卡片展示内部标识，标签宽度不足时将其截断。E8 为刷新后的直接页面复现，E9–E10 将同一条目与当前代码链路关联。尚未抓取 Network 响应，故确认的是当前本机页面和治理事实源解释的缺陷，不扩大断言到所有部署或来源。

## 修复方向

评审后考虑区分稳定身份字段与展示名称，在合适读取层解析可读名称并定义缺失回退。昵称、用户名优先级和回退文案尚待评审；不得直接把 owner 身份替换为昵称而破坏权限、归属及筛选键。同步核查 REQ/BUG、详情和筛选，不预先承诺 API 或数据库变更方案。

## 自主补证与阻碍

前一轮浏览器清单首次超时、终端 HTTP 探测失败后曾误判“产品不可访问”；这只反映当时两个工具入口失败。随后直接连接已运行的 Firefox，找到需求中心页面；本轮再次刷新并筛选同一条目完成 E8，误判已撤回。终端与浏览器可能有不同连接路径，不能用终端失败否定浏览器观察。本轮未创建业务样本、读取凭证或保存原始身份值。

尚未取得 Network 响应和原始反馈截图；它们可用于扩大部署范围或检查 API 契约，但不再阻止确认当前本机页面的缺陷根因。BUG 卡片、详情、筛选及其他来源仍是修复验收范围，而非本次已确认事实。

## 后续范围验证

| 项目 | 原因 | 操作步骤 | 返回字段与格式 |
|---|---|---|---|
| 部署范围 | 核查其他部署是否同样受影响 | 在目标环境刷新已有问题卡片，记录版本与路由 | 脱敏表格：版本、路由、时间、浏览器、视口、角色与标签结果 |
| API 契约 | 决定修复层及字段命名 | 在授权测试环境检查同条目列表请求，仅摘录身份及名称字段 | method、path、status、owner 类型、名称字段是否存在；可用时附 request_id/trace_id |
| 影响边界 | 验证共用链路 | 优先只读检查已有 REQ/BUG、详情与筛选；修复验收使用授权测试样本 | 条目类型、来源、标签及筛选结果 |

真实 ID、姓名、邮箱以一致合成别名替换，保留字段之间的关系。不提供 Cookie、Authorization、密码、Token、完整响应或客户业务内容。

## 验证闭环

当前：同一 REQ 的刷新后页面、治理 owner、映射函数与标签渲染已关联，根因 confirmed。运行 `validate-root-cause-evidence.py` 和完成态 Workflow Sync 校验；修复后的功能、权限与视觉验收仍待执行，验收方案见 acceptance.md。

## 隔离验证复核方法

以下命令仅解析函数并使用合成数据，不导入服务或访问业务数据库：

```bash
python - <<'PYTHON'
import ast
from pathlib import Path
from typing import Any
source = Path("src/backend/app/services/requirement_center.py").read_text()
function = next(node for node in ast.parse(source).body
                if isinstance(node, ast.FunctionDef) and node.name == "_owner_name")
namespace = {"Any": Any}
exec(compile(ast.Module(body=[function], type_ignores=[]), "isolated-owner", "exec"), namespace)
for value, expected in [("user_synthetic_bug0028", "user_synthetic_bug0028"),
                        ("product", "产品团队"), (None, "未分配")]:
    assert namespace["_owner_name"](value) == expected
print("3/3 isolated assertions passed")
PYTHON
```

历史复核时间：2026-10-08 22:57:52（Asia/Shanghai）。该次仅完成 3/3 隔离断言，未观察真实页面；2026-10-09 的 E8–E10 已补齐当前本机运行态与同条目事实源关联。

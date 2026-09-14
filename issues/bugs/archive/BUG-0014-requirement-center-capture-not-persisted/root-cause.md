---
bug_id: BUG-0014-requirement-center-capture-not-persisted
created_at: 2026-09-11 19:02:39
updated_at: 2026-09-12 21:33:52
root_cause_status: confirmed
---

# 根因分析

## 根因状态

status: confirmed

确认范围为当前工作区的 Capture 提交代码路径；不是生产环境故障定界或修复验收结论。

## 现象

REQ/BUG 新建 Capture 提示成功，仅插入前端内存卡片，未提交持久化请求。目录、capture、trace、注册表与索引没有通过该动作创建；描述字段在重置表单时丢弃。

## 证据链

| ID | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx` 的 `submitCapture` | 计算客户端编号、构造 IssueCard、setContext 后提示成功，无后端调用 | 提交路径没有持久化步骤，是直接原因 |
| E2 | reproduction | 本文“验证闭环”的实际函数提取命令 | bug-complete 再次执行 REQ/BUG 两种输入：memory_card=1、network_calls=0、description_saved=false、success_toast=true | 合成执行与代码判断一致 |
| E3 | code_path | `src/backend/app/services/requirement_center.py` 的 `_load_issues`；前端 `loadContext` | 后端读取注册表，前端初始加载替换上下文 | 内存新增条目不会由注册表加载恢复 |
| E4 | code_path | `src/web/src/requirement-center.test.tsx` 的 `creates a capture card from the reference-style modal` | 仅验证卡片与提示，未断言持久化、描述保留或刷新恢复 | 当前测试覆盖缺口允许假成功逻辑通过 |
| E5 | code_path | `issues/requirements/archive/REQ-0012-frontend-requirement-center/requirement.md` 的阶段模型 | Capture 创建后要求存在 capture.md、trace.md | 现有行为不满足父需求规定 |

## 已排除假设

| 假设 | 排除证据与边界 |
|---|---|
| 当前路径因接口报错才未落盘 | E1/E2：提交函数没有发出创建请求，不存在该次创建请求的失败响应 |
| 只有 Bug 类型遗漏 | E2：两种类型均复现 |
| 仅索引刷新遗漏而文档已创建 | E1：函数没有任何服务端持久化入口，不能通过此动作创建文档 |
| 当前未提交修改新引入 | 上一阶段已比对 HEAD 的同名函数，存在相同逻辑；不据此推断首次引入日期 |

## 已确认根因

新建 Capture 仍采用前端模拟：编号按客户端已加载卡片计算，文档只写入展示元数据，通过 setContext 插入卡片后直接显示成功。未将表单交给授权项目的服务端写入流程，因此无法完成真实编号分配、目录和文档写入以及注册表/索引同步。描述字段也没有进入新卡片对象，随表单重置丢弃。

该原因解释当前代码的 REQ/BUG 共同失败。并发编号冲突、实际部署刷新表现和受影响记录数量仍属于待验证影响，不能作为已观察结果。

## 修复方向

1. 在授权项目范围内提供 Capture 持久化操作；校验类型、内容与写权限，由服务端分配完整唯一 ID。
2. 将目录、capture、trace、注册表与索引的一致性纳入同一成功条件；并发、重试与部分失败的处理方式由 Change 设计明确。
3. 前端使用服务端结果更新卡片，仅在持久化完成后提示成功；失败保留输入，避免本地编号或虚构可用文档。
4. 同步 API/OpenAPI、客户端调用与生成物、错误反馈和请求观测；测试覆盖真实文件结果与刷新加载。

## 验证闭环

在仓库根目录执行以下只读合成验证。它提取实际函数，不复制实现；需要已有 Node 与前端 TypeScript 依赖。断言描述的是修复前缺陷特征，修复后应由 acceptance.md 中的正向回归替代。

```bash
node <<'JS'
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const ts=require('./src/web/node_modules/typescript');
const src=fs.readFileSync('src/web/src/pages/catalog/RequirementCenterPage.tsx','utf8');
const start=src.indexOf('  const submitCapture =');
const end=src.indexOf('  const handleCaptureKeyDown',start);
assert(start>=0 && end>start);
const body=src.slice(start,end);
for(const type of ['requirement','bug']) {
  let state={issues:[]},calls=0,toast='';
  const scope={issues:[],captureForm:{type,title:'synthetic-capture',
    description:'synthetic-description',priority:'P1',owner:'未分配',source:'explore'},
    setContext:f=>state=f(state),setCaptureForm:()=>{},setCaptureError:()=>{},
    setCaptureOpen:()=>{},setToast:v=>toast=v,
    fetch:()=>{calls++;},governanceRequest:()=>{calls++;}};
  vm.runInNewContext(ts.transpile(body+'\nsubmitCapture({preventDefault(){}});',
    {target:ts.ScriptTarget.ES2022}),scope);
  assert.equal(calls,0);assert.equal(state.issues.length,1);
  assert.equal(state.issues[0].description,undefined);assert(toast.includes('已创建'));
  console.log(type+': memory_card=1 network_calls=0 description_saved=false success_toast=true');
}
JS
```

本次上述两类合成输入断言均通过；业务代码未修改。真实浏览器、后端鉴权、并发和部署验证未执行。修复后按 acceptance.md 回填真实结果，不将本次缺陷复现记为修复通过。


## 目标部署返修证据（confirmed）

期望当前环境可创建Capture；实际返回“治理成果存储尚未配置”。只读docker inspect发现backend未设置MOONBOX_GOVERNANCE_STATE_ROOT，启动集合仅基础/Chat配置且没有governance-controller；store.py root分支精确对应2605/503。此证据补充部署接入缺口，不推翻原本地假成功根因。原限时maintenance门禁只适合受控成果应用，Capture持续使用改为显式常驻配置和心跳就绪；其余授权/恢复边界不变。

## 分级返修补充证据

confirmed：Capture表单共用priority，schema未提供severity，capture.py在BUG capture/trace/registry/index使用固定medium或severity_hint。与document-governance第243行的类型分级契约不一致。本轮改为REQ priority、BUG severity，沿用原持久化目标。

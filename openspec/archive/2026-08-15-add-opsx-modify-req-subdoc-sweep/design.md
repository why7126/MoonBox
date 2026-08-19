---
purpose: OpenSpec Change Design
content: opsx-modify REQ 子文档一致性扫尾检查设计
created_at: 2026-08-15 13:02:00
updated_at: 2026-08-15 13:02:00
owner: MoonBox 产品团队
---

# Design: add-opsx-modify-req-subdoc-sweep

## Approach

在 `/opsx-modify` 的文档更新阶段之后、Validate 阶段之前增加一个明确门禁。该门禁只对 REQ 来源 Change 强制执行；BUG 来源 Change 和纯治理 Change 记录“不适用”即可。

## Sweep Checklist

REQ 来源返修完成前，Agent MUST 定位 linked REQ 目录，并按“存在即检查”的原则扫尾：

| 子文档/资产 | 检查重点 |
|---|---|
| `requirement.md` | PRD 目标、范围、非目标、最终行为、用户可见文案是否与返修后实现一致 |
| 业务流程文档 | 入口、主流程、异常流、状态流转、权限/角色路径是否仍准确 |
| 用户故事文档 | 角色、目标、收益、场景、验收故事是否被返修改变 |
| `acceptance.md` | 验收项、通过标准、证据要求和状态是否与二次验证一致 |
| `trace.md` | Change、Sprint、验证摘要和状态是否可追溯；Workflow Sync marker 块仍由脚本维护 |
| `prototype/**` | `prototype.html`、`context.md`、截图或原型说明是否与最终 UI/交互意图一致 |

若返修改变上述任一事实源，必须同步更新；若未改变，必须在 Change `tasks.md` 的验收返修记录或 `trace.md` 中写明“REQ 子文档一致性扫尾检查：无需更新 <items>，原因：...”。若发现原型或用户故事已超出当前 Change 边界，应阻断 `/opsx-modify` 并引导新建 REQ/BUG 或新 Change。

## Validation Strategy

- OpenSpec 变更运行 `openspec validate add-opsx-modify-req-subdoc-sweep --strict`。
- Markdown 变更运行 `git diff --check` 聚焦 touched docs。
- 运行上下文预算、OpenSpec 中文优先和目录结构校验。

---
bug_id: BUG-0012-requirement-registry-changelog-req0017-archive-drift
status: done
created_at: 2026-08-15 10:32:44
updated_at: 2026-08-15 11:49:25
severity_hint: medium
environment: governance
related_requirement: REQ-0017-admin-space-management
related_bug:
captured_via: capture
classification_rationale: 已有需求治理索引与真实归档目录不一致，属于已交付治理资产的状态/路径偏差，按 BUG 记录。
---

# 现象

`issues/requirements/_registry.yaml` 与 `issues/requirements/CHANGELOG.md` 仍指向 `REQ-0017-admin-space-management` 的 `review/` 路径和开发中状态，但该 REQ 的真实目录已经位于 `issues/requirements/archive/REQ-0017-admin-space-management/`。

# 复现步骤

1. 检查 `issues/requirements/_registry.yaml` 中 `REQ-0017-admin-space-management` 的 `lifecycle_stage` 与 `path`。
2. 检查 `issues/requirements/CHANGELOG.md` 中 `REQ-0017-admin-space-management` 的阶段、下一步和事实源路径。
3. 检查文件系统中 `REQ-0017-admin-space-management` 的真实目录位置。

# 期望 vs 实际

期望：REQ 当前态索引与 registry 应指向真实 `archive/` 目录，并体现已归档闭环后的状态、阶段、下一步和事实源路径。

实际：registry 与 CHANGELOG 仍保留 `review/` 路径或开发中下一步，和真实目录 `archive/` 不一致。

# 初步证据

- 用户报告：发现一个非阻塞治理漂移，`issues/requirements/_registry.yaml` 和 `CHANGELOG.md` 仍指向 `REQ-0017` 的 `review` 路径，但真实目录在 `archive`。
- 本次 capture 定位：`issues/requirements/_registry.yaml` 中 `REQ-0017-admin-space-management` 的 `path` 为 `issues/requirements/review/REQ-0017-admin-space-management/`。
- 本次 capture 定位：`issues/requirements/CHANGELOG.md` 中 `REQ-0017-admin-space-management` 的事实源仍为 `issues/requirements/review/REQ-0017-admin-space-management/trace.md`。
- 本次 capture 定位：真实目录存在于 `issues/requirements/archive/REQ-0017-admin-space-management/`。

# 附件

无

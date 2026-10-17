---
bug_id: BUG-0034-chat-standalone-archive-scope-tool-path
title: 产品内纯治理 Change 归档失败临时规避方案
created_at: 2026-10-09 10:52:00
updated_at: 2026-10-09 10:52:00
owner: 产品团队
---

# 产品内纯治理 Change 归档失败临时规避方案

已在宿主受信任环境按归档门禁执行标准脚本，将本次 `prevent-issue-iteration-tool-dirs` 完成归档；无须重复归档该 Change。其他纯治理 Change 在产品修复前，先确认任务、规格、证据和目标路径，再由具备完整工具链与写权限的受信任环境运行标准归档脚本。不得通过放宽普通治理 profile 或在执行容器中挂载 Docker socket 规避。

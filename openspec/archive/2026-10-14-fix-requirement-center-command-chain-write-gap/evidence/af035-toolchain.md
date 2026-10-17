---
title: AF-035 执行镜像工具链验证
created_at: 2026-10-06 10:01:30
updated_at: 2026-10-06 10:01:30
---

# AF-035 执行镜像工具链验证

## 直接证据

旧镜像 command-v 检查缺 node/npm/pnpm/openspec/curl；新镜像非 root 构建探针通过。固定工具版本 Node 22.22.0、OpenSpec 1.3.1、pnpm 11.2.2、uv 0.8.15，npm 依赖树有 lockfile/integrity。原 Python/Git/Bash/rg 保留，补充 curl/jq/patch/zip/unzip。

实际沙箱首次 pnpm 探针失败；工具 HOME/XDG 缓存迁入每容器 /tmp 后通过，凭证目录依旧禁止读取。不是通过关闭沙箱解决。

## 可复跑验证

- `uv run --project src/backend --with pytest --with httpx python -m pytest -q src/backend/tests/test_chat_toolchain.py src/backend/tests/test_chat_preparation_failure.py src/backend/tests/test_chat_platform.py`：32 passed。覆盖工具清单、版本与构建输入一致、完整 run_claim 缺工具后 failed/零用量/会话释放/原文件保留、平台权限回归。
- `CHAT_CONTAINER_PROBE=1 uv run --project src/backend --with pytest --with httpx python -m pytest -q src/backend/tests/test_chat_container_worker.py -k 'preflight_two or governance_openspec'`：2 passed。使用实际产品工厂、非 root、只读根、独立凭证和嵌套沙箱；OpenSpec new/status/instructions/validate/list 全部离线通过，临时 Change 文件存在。
- Web `chat-preparation-failure.test.tsx`：6 passed，缺工具展示执行前阻断及部署建议，无等待结果提示。
- 标准 `docker-down.sh self-storage-sqlite` 随后 `docker-up.sh self-storage-sqlite`：均退出 0。部署前无 queued/connecting/running/stopping；两条旧 unknown 无执行容器，保持原状未恢复/删除。
- 部署后 `check_toolchain.py`：ready=true、unavailable=[]；Web HTTP 200，实际 bundle `/assets/index-5XuRY61A.js` 包含 container_toolchain_unavailable 与中文提示。backend/chat-worker/governance-controller healthy，Web running。

## 镜像摘要

| 角色 | SHA-256 |
|---|---|
| executor | 1f4f71c38fd5de9ef962f6b2f8e3fc5fb16edabf2e93cad37b79599bc5e8f997 |
| backend / governance-controller | 4a28179dd458411b388030cd7d6fa93fe29233825aafa6dcdc2e45ec269ebcdf |
| chat-worker | 01ced7ac780a825f27a7d1de6781b48c89e1f5aa92c19b373303dee5f076e712 |
| web | ec0734799fcc81189ab2d9a0bad0b1d2d16b64d61166c58a698845cfeb3565dd |

## 验证边界

Workflow Sync opsx.modify 退出 0，errors=0、blockers=0、acceptance=pending；两项 warning 为既有 root-cause.status=confirmed、workaround.status=active 的独立语义，保留原值，不将其改成 Issue 生命周期状态。AI Usage hook 为 unavailable/no-command-runs，未猜测用量。

真实容器命令使用临时项目和无效合成认证，不调用模型，不写项目事实源；它证明执行器命令工具可用，不代表真实业务审批或状态已推进。浏览器控制入口超时，未取得新浏览器截图；运行态 bundle 为直接 HTTP 读取，DOM 为组件测试，不冒充浏览器观察。未改变 API/DB schema、模型网络和文件写入权限，无客户端生成需求。Python 测试提示既有 Starlette/httpx 弃用警告，Web 构建有既有 chunk 大小警告，均未阻断。

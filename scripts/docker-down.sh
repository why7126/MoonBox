#!/usr/bin/env bash
# 停止同一环境的Chat验证实例和常规服务；不删除常规数据库或对象存储卷。
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/docker-common.sh" "$@"
if [[ "$CHECK_ONLY" = true ]]; then
  "${COMPOSE[@]}" config --quiet
  echo '停止配置校验通过；未停止服务或删除数据。'; exit 0
fi
if command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  chat_control stop
elif [[ "$CHAT_TEST" = true ]]; then
  echo '停止Chat需要启动时使用的Python；请设置PYTHON_BIN。' >&2; exit 2
fi
"${COMPOSE[@]}" down
echo "服务已停止：${MODE}；常规数据库与对象存储数据保留。"

#!/usr/bin/env bash
# 按模式启动常规服务；--chat-test显式增加独立Chat验证环境。
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/docker-common.sh" "$@"
validate_database_mode
if [[ "$CHAT_PLATFORM" = true ]]; then
  PYTHONPATH=src/backend "$PYTHON_BIN" -m app.chat.platform_deployment check
  PYTHONPATH=src/backend "$PYTHON_BIN" -m app.governance.deployment check
fi
RESOLVED_HOST_PORT_WEB="$(config_value HOST_PORT_WEB 18102)"
RESOLVED_HOST_PORT_BACKEND="$(config_value HOST_PORT_BACKEND 18101)"
RESOLVED_HOST_PORT_MINIO_CONSOLE="$(config_value HOST_PORT_MINIO_CONSOLE 18104)"
if [[ "$CHECK_ONLY" = true ]]; then
  "${COMPOSE[@]}" config --quiet
  if [[ "$CHAT_TEST" = true ]]; then
    export HOST_PORT_CHAT_TEST="$(config_value HOST_PORT_CHAT_TEST 18121)"
    chat_control check
  fi
  echo '部署校验通过；未构建、启动或停止服务。'; exit 0
fi
if [[ "$CHAT_PLATFORM" = true ]]; then
  PYTHONPATH=src/backend "$PYTHON_BIN" -m app.chat.platform_deployment prepare
  PYTHONPATH=src/backend "$PYTHON_BIN" -m app.governance.deployment prepare
  "${COMPOSE[@]}" build backend web
  docker build -f src/backend/Dockerfile.chat-executor -t moonbox-chat-executor:0.153.4-test src/backend
  "${COMPOSE[@]}" build chat-worker
  "${COMPOSE[@]}" up -d --wait --wait-timeout 180 "${SERVICES[@]}"
elif [[ "$CHAT_TEST" = true ]]; then
  export HOST_PORT_CHAT_TEST="$(config_value HOST_PORT_CHAT_TEST 18121)"
  chat_control check
  "${COMPOSE[@]}" build backend web
  docker build -f src/backend/Dockerfile.chat-executor -t moonbox-chat-executor:0.153.4-test src/backend
  "${COMPOSE[@]}" up -d --wait --wait-timeout 90 "${SERVICES[@]}"
  chat_control start --web-image "$(config_value WEB_IMAGE moonbox-web:local)"
else
  "${COMPOSE[@]}" up -d --build "${SERVICES[@]}"
fi
echo "服务已按模式启动：$MODE"
echo "- Web: http://localhost:${RESOLVED_HOST_PORT_WEB}"
echo "- Backend API: http://localhost:${RESOLVED_HOST_PORT_BACKEND}/docs"
if [[ "$MODE" == self-storage-* ]]; then echo "- MinIO Console: http://localhost:${RESOLVED_HOST_PORT_MINIO_CONSOLE}"; fi

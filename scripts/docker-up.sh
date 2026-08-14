#!/usr/bin/env bash
# 文档用途：启动Docker Compose开发环境
# 文档内容：按部署模式构建并启动后端、Web、MinIO、MySQL
# 内容来源：AI自动生成，项目团队确认
# 更新方式：compose服务变化时更新
# 备注：执行前请确保已安装Docker和Docker Compose

set -euo pipefail

MODE="${1:-self-storage-sqlite}"
ENV_FILE="${ENV_FILE:-.env}"

env_file_value() {
  local key="$1"
  if [[ ! -f "$ENV_FILE" ]]; then
    return 1
  fi
  awk -F= -v key="$key" '
    $0 !~ /^[[:space:]]*#/ && $1 == key {
      value = substr($0, index($0, "=") + 1)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
      gsub(/^"|"$/, "", value)
      gsub(/^'\''|'\''$/, "", value)
      print value
      found = 1
      exit
    }
    END { if (!found) exit 1 }
  ' "$ENV_FILE"
}

config_value() {
  local key="$1"
  local default_value="$2"
  local current_value="${!key-}"
  if [[ -n "$current_value" ]]; then
    printf '%s\n' "$current_value"
    return 0
  fi
  env_file_value "$key" || printf '%s\n' "$default_value"
}

RESOLVED_HOST_PORT_WEB="$(config_value HOST_PORT_WEB 18102)"
RESOLVED_HOST_PORT_BACKEND="$(config_value HOST_PORT_BACKEND 18101)"
RESOLVED_HOST_PORT_MINIO_CONSOLE="$(config_value HOST_PORT_MINIO_CONSOLE 18104)"

case "$MODE" in
  self-storage-sqlite)
    docker compose up -d --build backend web minio
    ;;
  external-storage-sqlite)
    OBJECT_STORAGE_DEPLOYMENT_MODE=external-minio docker compose up -d --build backend web
    ;;
  self-storage-self-mysql)
    DATABASE_DEPLOYMENT_MODE=self-hosted-mysql DATABASE_TYPE=mysql DATABASE_URL="${DATABASE_URL:-mysql+pymysql://moonbox:change-me@mysql:3306/moonbox}" docker compose --profile mysql up -d --build backend web minio mysql
    ;;
  self-storage-external-mysql)
    DATABASE_DEPLOYMENT_MODE=external-mysql DATABASE_TYPE=mysql docker compose up -d --build backend web minio
    ;;
  external-storage-self-mysql)
    OBJECT_STORAGE_DEPLOYMENT_MODE=external-minio DATABASE_DEPLOYMENT_MODE=self-hosted-mysql DATABASE_TYPE=mysql DATABASE_URL="${DATABASE_URL:-mysql+pymysql://moonbox:change-me@mysql:3306/moonbox}" docker compose --profile mysql up -d --build backend web mysql
    ;;
  external-storage-external-mysql)
    OBJECT_STORAGE_DEPLOYMENT_MODE=external-minio DATABASE_DEPLOYMENT_MODE=external-mysql DATABASE_TYPE=mysql docker compose up -d --build backend web
    ;;
  *)
    echo "未知部署模式: $MODE" >&2
    echo "可选模式:" >&2
    echo "  self-storage-sqlite" >&2
    echo "  external-storage-sqlite" >&2
    echo "  self-storage-self-mysql" >&2
    echo "  self-storage-external-mysql" >&2
    echo "  external-storage-self-mysql" >&2
    echo "  external-storage-external-mysql" >&2
    exit 2
    ;;
esac

echo "服务已按模式启动：$MODE"
echo "- Web: http://localhost:${RESOLVED_HOST_PORT_WEB}"
echo "- Backend API: http://localhost:${RESOLVED_HOST_PORT_BACKEND}/docs"
if [[ "$MODE" == self-storage-* ]]; then
  echo "- MinIO Console: http://localhost:${RESOLVED_HOST_PORT_MINIO_CONSOLE}"
fi

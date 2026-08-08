#!/usr/bin/env bash
# 文档用途：按部署域停止 Docker Compose
# 文档内容：停止 local/prod 部署域并输出数据保留说明
# 更新方式：新增部署域或 Compose 文件时同步更新

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DOMAIN="${1:-local}"

case "${DOMAIN}" in
  local)
    COMPOSE_FILE="${ROOT_DIR}/deploy/local/compose.yml"
    docker compose --project-name moonbox --profile self-hosted-storage --profile self-hosted-db --profile docs-site -f "${COMPOSE_FILE}" down --remove-orphans
    echo "本地域服务已停止。SQLite、MySQL、MinIO 和临时数据保留在 data/ 或命名卷中。"
    ;;
  prod)
    COMPOSE_FILE="${ROOT_DIR}/deploy/prod/compose.s3-mysql.yml"
    docker compose --project-name moonbox --profile docs-site -f "${COMPOSE_FILE}" down --remove-orphans
    echo "生产域服务已停止。外部 MySQL 与对象存储数据由运维系统保留。"
    ;;
  *)
    echo "未知部署域：${DOMAIN}" >&2
    echo "可用部署域：local, prod" >&2
    exit 2
    ;;
esac


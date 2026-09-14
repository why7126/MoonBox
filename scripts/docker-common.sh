#!/usr/bin/env bash
# 共用部署参数；不执行env文件内容，不打印配置凭证。
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -n "${ENV_FILE:-}" ]]; then
  [[ "$ENV_FILE" = /* ]] || ENV_FILE="$PWD/$ENV_FILE"
  [[ -f "$ENV_FILE" ]] || { echo '指定的ENV_FILE不存在。' >&2; exit 2; }
else
  ENV_FILE="$ROOT_DIR/.env"
fi
cd "$ROOT_DIR"
MODE=self-storage-sqlite
CHAT_TEST=false
CHAT_PLATFORM=false
CHECK_ONLY=false
MODE_SET=false
for arg in "$@"; do
  case "$arg" in
    --chat-test) CHAT_TEST=true ;;
    --chat-platform) CHAT_PLATFORM=true ;;
    --check) CHECK_ONLY=true ;;
    --help|-h) echo '用法：bash scripts/docker-up.sh [部署模式] [--chat-test|--chat-platform] [--check]；docker-down.sh参数相同。'; exit 0 ;;
    --*) echo "未知选项：$arg" >&2; exit 2 ;;
    *) [[ "$MODE_SET" = false ]] || { echo '只能指定一个部署模式。' >&2; exit 2; }; MODE="$arg"; MODE_SET=true ;;
  esac
done
SERVICES=(backend web)
PROFILES=()
case "$MODE" in
  self-storage-sqlite) SERVICES+=(minio) ;;
  external-storage-sqlite) export OBJECT_STORAGE_DEPLOYMENT_MODE=external-minio ;;
  self-storage-self-mysql) SERVICES+=(minio mysql); PROFILES=(--profile mysql); export DATABASE_DEPLOYMENT_MODE=self-hosted-mysql DATABASE_TYPE=mysql ;;
  self-storage-external-mysql) SERVICES+=(minio); export DATABASE_DEPLOYMENT_MODE=external-mysql DATABASE_TYPE=mysql ;;
  external-storage-self-mysql) SERVICES+=(mysql); PROFILES=(--profile mysql); export OBJECT_STORAGE_DEPLOYMENT_MODE=external-minio DATABASE_DEPLOYMENT_MODE=self-hosted-mysql DATABASE_TYPE=mysql ;;
  external-storage-external-mysql) export OBJECT_STORAGE_DEPLOYMENT_MODE=external-minio DATABASE_DEPLOYMENT_MODE=external-mysql DATABASE_TYPE=mysql ;;
  *) echo "未知部署模式：$MODE" >&2; exit 2 ;;
esac
if [[ "$CHAT_TEST" = true && "$MODE" != self-storage-sqlite ]]; then
  echo '--chat-test当前仅支持self-storage-sqlite；不会对其他数据库启用测试执行。' >&2; exit 2
fi
if [[ "$CHAT_PLATFORM" = true && ( "$MODE" != self-storage-sqlite || "$CHAT_TEST" = true ) ]]; then
  echo '--chat-platform仅支持self-storage-sqlite，且不能与--chat-test同时使用。' >&2; exit 2
fi
config_value() {
  local key="$1" default_value="$2" value
  if [[ -n "${!key-}" ]]; then printf '%s\n' "${!key}"; return; fi
  if [[ -f "$ENV_FILE" ]]; then
    value="$(awk -F= -v key="$key" '$0 !~ /^[[:space:]]*#/ && $1 == key {v=substr($0,index($0,"=")+1);gsub(/^[[:space:]]+|[[:space:]]+$/, "",v);gsub(/^"|"$/, "",v);gsub(/^'\''|'\''$/, "",v);print v;exit}' "$ENV_FILE")"
    if [[ -n "$value" ]]; then printf '%s\n' "$value"; return; fi
  fi
  printf '%s\n' "$default_value"
}
validate_database_mode() {
case "$MODE" in
  *-sqlite)
    [[ "$(config_value DATABASE_TYPE sqlite)" = sqlite && "$(config_value DATABASE_URL sqlite:///default)" = sqlite:* ]] || {
      echo 'SQLite部署模式与数据库配置不一致，请检查所选ENV_FILE。' >&2; exit 2;
    } ;;
  *-self-mysql)
    export DATABASE_URL="$(config_value DATABASE_URL 'mysql+pymysql://moonbox:change-me@mysql:3306/moonbox')" ;;
  *-external-mysql)
    [[ "$(config_value DATABASE_URL '')" = mysql* ]] || { echo '外部MySQL模式需要显式MySQL连接配置。' >&2; exit 2; } ;;
esac
if [[ "$MODE" = *-mysql && "$(config_value DATABASE_URL '')" != mysql* ]]; then
  echo 'MySQL部署模式与数据库连接配置不一致。' >&2; exit 2
fi
}
if [[ "$CHAT_TEST" = false && "$(config_value MOONBOX_CHAT_EXECUTION_MODE disabled)" = local-codex ]]; then
  CHAT_PLATFORM=true
fi
if [[ "$CHAT_PLATFORM" = true && "$MODE" != self-storage-sqlite ]]; then
  echo '已配置常驻Chat，必须使用self-storage-sqlite模式。' >&2; exit 2
fi
COMPOSE=(docker compose --project-directory "$ROOT_DIR" -f "$ROOT_DIR/docker-compose.yml")
if [[ -f "$ENV_FILE" ]]; then
  COMPOSE+=(--env-file "$ENV_FILE")
  export MOONBOX_ENV_FILE="$ENV_FILE"
fi
if [[ ${#PROFILES[@]} -gt 0 ]]; then COMPOSE+=("${PROFILES[@]}"); fi
PYTHON_BIN="${PYTHON_BIN:-python}"
chat_control() {
  PYTHONPATH="$ROOT_DIR/src/backend${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" -m app.chat.deployment --scope "$ENV_FILE" "$@"
}
if [[ "$CHAT_PLATFORM" = true ]]; then
  export MOONBOX_CHAT_HOST_ROOT="$(config_value MOONBOX_CHAT_HOST_ROOT "$ROOT_DIR/data/runtime/chat-platform")"
  export MOONBOX_CHAT_SOURCE_ROOT="$(config_value MOONBOX_CHAT_SOURCE_ROOT '')"
  export MOONBOX_CHAT_SPACE_ID="$(config_value MOONBOX_CHAT_SPACE_ID '')"
  export MOONBOX_CHAT_REPOSITORY_ID="$(config_value MOONBOX_CHAT_REPOSITORY_ID '')"
  export MOONBOX_CHAT_AUTH_SOURCE="$(config_value MOONBOX_CHAT_AUTH_SOURCE "$HOME/.codex/auth.json")"
  export MOONBOX_CHAT_WORKER_UID="$(id -u)" MOONBOX_CHAT_WORKER_GID="$(id -g)"
  export MOONBOX_CHAT_DOCKER_GID="$(config_value MOONBOX_CHAT_DOCKER_GID 0)"
  # JSON由Python编码，路径和标识从不当作shell代码执行。
  MOONBOX_CHAT_REPOSITORIES="$(PYTHONPATH=src/backend "$PYTHON_BIN" -m app.chat.platform_deployment catalog)"; export MOONBOX_CHAT_REPOSITORIES
  MOONBOX_CHAT_REPOSITORY_BINDINGS="$(PYTHONPATH=src/backend "$PYTHON_BIN" -m app.chat.platform_deployment bindings)"; export MOONBOX_CHAT_REPOSITORY_BINDINGS
  export MOONBOX_CHAT_LIMITS="$(config_value MOONBOX_CHAT_LIMITS '{"user_concurrency":"unlimited","space_concurrency":"unlimited","user_monthly_tokens":"unlimited","space_monthly_tokens":"unlimited","user_storage_bytes":"unlimited","space_storage_bytes":"unlimited","turn_reserved_tokens":"unlimited","turn_reserved_bytes":16777216}')"
  export MOONBOX_CHAT_RETENTION="$(config_value MOONBOX_CHAT_RETENTION '{"executor_delete_seconds":"unlimited","backup_expiry_seconds":"unlimited"}')"
  COMPOSE+=(-f "$ROOT_DIR/deploy/docker-compose.chat-platform.yml")
  SERVICES+=(chat-worker)
fi

# 常驻Chat项目复用既有治理controller；Capture模式可显式关闭。
if [[ "$CHAT_PLATFORM" = true ]]; then
  export MOONBOX_GOVERNANCE_CAPTURE_MODE="$(config_value MOONBOX_GOVERNANCE_CAPTURE_MODE continuous)"
  export MOONBOX_GOVERNANCE_HOST_STATE_ROOT="$(config_value MOONBOX_GOVERNANCE_HOST_STATE_ROOT "$ROOT_DIR/data/runtime/governance")"
  COMPOSE+=(-f "$ROOT_DIR/deploy/docker-compose.governance.yml")
  SERVICES+=(governance-controller)
fi

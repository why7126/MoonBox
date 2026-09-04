#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEB_DIR="${ROOT_DIR}/src/web"
OPENAPI_JSON="${WEB_DIR}/openapi.json"
ORVAL_CONFIG="${WEB_DIR}/orval.config.ts"
LOCAL_ORVAL="${WEB_DIR}/node_modules/.bin/orval"
PACKAGE_JSON="${WEB_DIR}/package.json"

print_client_generation_help() {
  local reason="$1"

  cat >&2 <<EOF
OpenAPI contract exported to: ${OPENAPI_JSON}
OpenAPI client generation skipped: ${reason}

How to fix:
  1. Ensure pnpm is available:
     corepack enable
  2. Ensure pnpm matches src/web/package.json packageManager:
     corepack prepare pnpm@11.2.2 --activate
  3. Install frontend dependencies:
     pnpm --dir src/web install
  4. If Orval is not declared in src/web/package.json, add it explicitly:
     pnpm --dir src/web add -D orval
  5. Ensure the Orval config exists:
     src/web/orval.config.ts

This script does not implicitly download Orval or rewrite the lockfile. Re-run:
  ./scripts/generate-openapi-client.sh
EOF
}

has_orval_dependency() {
  [[ -f "${PACKAGE_JSON}" ]] && grep -q '"orval"' "${PACKAGE_JSON}"
}

check_pnpm_version() {
  local output_file
  output_file="$(mktemp)"
  if ! pnpm --dir "${WEB_DIR}" --version >"${output_file}" 2>&1; then
    local output
    output="$(tr '\n' ' ' <"${output_file}")"
    rm -f "${output_file}"
    print_client_generation_help "pnpm version check failed for src/web packageManager (${output})"
    exit 2
  fi
  rm -f "${output_file}"
}

generate_openapi_contract() {
  (cd "${ROOT_DIR}/src/backend" && uv run python -c "import json; from app.main import app; print(json.dumps(app.openapi(), ensure_ascii=False, indent=2))") \
    > "${OPENAPI_JSON}"
}

generate_openapi_contract

if command -v pnpm >/dev/null 2>&1; then
  check_pnpm_version
fi

if [[ ! -f "${ORVAL_CONFIG}" ]]; then
  print_client_generation_help "missing Orval config (${ORVAL_CONFIG})"
  exit 2
fi

if [[ -x "${LOCAL_ORVAL}" ]]; then
  (cd "${WEB_DIR}" && "${LOCAL_ORVAL}" --config orval.config.ts)
  exit 0
fi

if ! command -v pnpm >/dev/null 2>&1; then
  print_client_generation_help "pnpm is not available and local Orval was not found (${LOCAL_ORVAL})"
  exit 2
fi

if ! has_orval_dependency; then
  print_client_generation_help "Orval is not declared in src/web/package.json"
  exit 2
fi

print_client_generation_help "local Orval binary is missing (${LOCAL_ORVAL})"
exit 2

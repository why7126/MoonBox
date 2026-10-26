#!/usr/bin/env bash
# Governance Python entry; no installation or implicit system fallback.
set -euo pipefail
ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ${1:-} == --help ]]; then
  echo 'Usage: bash scripts/project-python.sh --check | SCRIPT [ARGS...]'
  echo 'PYTHON_BIN overrides src/backend/.venv/bin/python. Requires Python >=3.12 and PyYAML.'
  exit 0
fi
if [[ ${PYTHON_BIN+x} ]]; then
  selected="$PYTHON_BIN"
else
  selected="$ROOT_DIR/src/backend/.venv/bin/python"
fi
if [[ -z "$selected" ]] || ! selected="$(command -v -- "$selected")"; then
  echo 'Python environment unavailable. Prepare the project venv or set PYTHON_BIN to an installed project interpreter.' >&2
  exit 2
fi
if [[ "$selected" != /* ]]; then selected="$PWD/$selected"; fi
export PYTHON_BIN="$selected"
export PYTHONDONTWRITEBYTECODE=1
"$PYTHON_BIN" "$ROOT_DIR/scripts/project_python_preflight.py" || exit 2
if [[ ${1:-} == --check ]]; then exit 0; fi
if [[ $# == 0 ]]; then echo 'Missing governance script; use --help.' >&2; exit 2; fi
script="$1"; shift
if [[ "$script" != /* ]]; then script="$ROOT_DIR/$script"; fi
exec "$PYTHON_BIN" "$script" "$@"

#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/validate-openspec.sh [--change <change-id>] [--include-archive] [--residual-report]

默认运行 OpenSpec 相关全局校验；传入 --change 时只聚焦目标 Change 的中文优先校验和 openspec 结构校验。
EOF
}

changes=()
include_archive=()
residual_report=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --change)
      if [[ $# -lt 2 || "$2" == --* ]]; then
        echo "缺少 --change 参数值" >&2
        usage >&2
        exit 2
      fi
      changes+=("$2")
      shift 2
      ;;
    --include-archive)
      include_archive=("--include-archive")
      shift
      ;;
    --residual-report)
      residual_report=("--residual-report")
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "未知参数：$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ${#residual_report[@]} -gt 0 && ${#changes[@]} -eq 0 ]]; then
  echo "--residual-report 需要与 --change 配合使用" >&2
  usage >&2
  exit 2
fi

echo "Validate OpenSpec documents"

if [[ ${#changes[@]} -gt 0 ]]; then
  language_args=()
  if [[ ${#include_archive[@]} -gt 0 ]]; then
    language_args+=("${include_archive[@]}")
  fi
  for change in "${changes[@]}"; do
    language_args+=("--change" "$change")
  done
  if [[ ${#residual_report[@]} -gt 0 ]]; then
    language_args+=("${residual_report[@]}")
  fi

  echo "校验当前 Change 中文优先..."
  python scripts/validate-openspec-language.py "${language_args[@]}"

  echo "校验当前 Change OpenSpec 结构..."
  for change in "${changes[@]}"; do
    if [[ -d "openspec/changes/$change" ]]; then
      openspec validate "$change"
    elif [[ ${#include_archive[@]} -gt 0 ]] && compgen -G "openspec/archive/*-$change" > /dev/null; then
      echo "归档 Change 已合并到正式规格，校验正式规格结构：$change"
      openspec validate --specs
    else
      echo "未找到 active Change：$change" >&2
      exit 2
    fi
  done
else
  echo "校验目录结构..."
  python scripts/validate-directory-structure.py

  echo "校验 OpenSpec 中文优先..."
  python scripts/validate-openspec-language.py
fi

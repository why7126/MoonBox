#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: scripts/archive-change.sh <change-id> [YYYY-MM-DD] [--finalize]" >&2
}

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

safe_move() {
  python - "$1" "$2" <<'PY'
import pathlib
import shutil
import sys
source, target = map(pathlib.Path, sys.argv[1:])
if target.exists() or target.is_symlink():
    raise SystemExit('ERROR: archive destination already exists')
shutil.move(str(source), str(target))
PY
}

run_language_gate() {
  if [[ -f "scripts/validate-openspec-language.py" ]]; then
    python scripts/validate-openspec-language.py
  fi
}

emit_unknown_archive_output() {
  local output_file="$1"
  local stream="$2"
  local line
  local has_unknown=0
  local in_known_proposal_warning=0

  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ Proposal\ warnings\ in\ proposal\.md ]]; then
      in_known_proposal_warning=1
      continue
    fi
    if [[ "$line" =~ proposal\.md ]] && [[ "$line" =~ (Why|What\ Changes) ]]; then
      in_known_proposal_warning=1
      continue
    fi
    if (( in_known_proposal_warning )); then
      if [[ -z "$line" ]]; then
        in_known_proposal_warning=0
        continue
      fi
      if [[ "$line" =~ ^[[:space:]] ]] || [[ "$line" =~ ^[-*][[:space:]] ]] || [[ "$line" =~ Missing\ required\ sections ]] || [[ "$line" =~ (Why|What\ Changes|Implementation|Validation|Root\ Cause) ]]; then
        continue
      fi
      in_known_proposal_warning=0
    fi
    if [[ -z "$line" ]]; then
      continue
    fi
    if [[ "$stream" == "stderr" ]]; then
      printf '%s\n' "$line" >&2
    else
      printf '%s\n' "$line"
    fi
    has_unknown=1
  done <"$output_file"

  return "$has_unknown"
}

run_openspec_archive() {
  local change="$1"
  local recovery_mode="$2"
  local stdout_file
  local stderr_file
  stdout_file="$(mktemp)"
  stderr_file="$(mktemp)"

  local archive_args=(archive "$change" -y)
  if [[ "$recovery_mode" == "move-only" ]]; then
    archive_args+=(--skip-specs)
  fi
  if ! openspec "${archive_args[@]}" >"$stdout_file" 2>"$stderr_file"; then
    cat "$stdout_file"
    cat "$stderr_file" >&2
    rm -f "$stdout_file" "$stderr_file"
    fail "openspec archive failed for $change"
  fi

  emit_unknown_archive_output "$stdout_file" stdout || true
  emit_unknown_archive_output "$stderr_file" stderr || true

  rm -f "$stdout_file" "$stderr_file"
}

relocate_legacy_archives() {
  local canonical_root="$1"
  local legacy_root="$2"

  if [[ ! -e "$legacy_root" ]]; then
    return 0
  fi
  if [[ ! -d "$legacy_root" ]]; then
    fail "$legacy_root exists but is not a directory"
  fi

  mkdir -p "$canonical_root"
  shopt -s nullglob dotglob

  local child
  for child in "$legacy_root"/*; do
    local target="$canonical_root/$(basename "$child")"
    if [[ -e "$target" ]]; then
      shopt -u nullglob dotglob
      fail "cannot migrate $child because $target already exists"
    fi
    safe_move "$child" "$target"
    echo "Migrated legacy archive: $child -> $target"
  done
  shopt -u nullglob dotglob

  rmdir "$legacy_root"
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

change_id="${1:-}"
archive_date="$(date +%Y-%m-%d)"
finalize=0
for argument in "${@:2}"; do
  if [[ "$argument" == "--finalize" ]]; then
    finalize=1
  else
    archive_date="$argument"
  fi
done

if [[ -z "$change_id" ]]; then
  usage
  exit 2
fi
[[ "$change_id" =~ ^[a-z0-9][a-z0-9-]{0,100}$ ]] || fail "invalid change id"

if [[ ! "$archive_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  fail "archive date must use YYYY-MM-DD: $archive_date"
fi

project_root="$(pwd)"
if [[ -e "$project_root/openspec/archive/.controlled-successors" ]]; then
  fail "受控归档项目须通过在线共同提交入口执行；使用 scripts/controlled-archive.py，保留原对象与操作身份。离线脚本不能领取授权。"
fi
canonical_root="$project_root/openspec/archive"
legacy_root="$project_root/openspec/changes/archive"
active_dir="$project_root/openspec/changes/$change_id"
target_dir="$canonical_root/$archive_date-$change_id"
legacy_target_dir="$legacy_root/$archive_date-$change_id"

python scripts/validate-issue-acceptance-ready.py "$change_id" || fail "Issue acceptance gate blocked archive for $change_id"
python scripts/validate-change-delivery-evidence.py --change "$change_id" || fail "Change delivery evidence gate blocked archive for $change_id"

if [[ -f "$active_dir/acceptance-plan.json" ]]; then
  python scripts/opsx_acceptance.py --change "$change_id" --readiness || fail "automated acceptance evidence is missing or stale for $change_id"
fi

python scripts/validate-change-identity.py
run_language_gate
relocate_legacy_archives "$canonical_root" "$legacy_root"

mkdir -p "$canonical_root"
if [[ -d "$active_dir" ]]; then
  [[ ! -e "$target_dir" ]] || fail "archive target already exists"
  python scripts/validate-directory-structure.py
  recovery_mode="$(python scripts/archive-recovery-guard.py "$change_id" "$archive_date")" || fail "archive recovery guard blocked $change_id"
  run_openspec_archive "$change_id" "$recovery_mode"
else
  python scripts/archive-recovery-guard.py "$change_id" "$archive_date" >/dev/null || fail "archive recovery guard blocked $change_id"
  shopt -s nullglob
  matches=("$canonical_root"/????-??-??-"$change_id")
  shopt -u nullglob
  [[ "${#matches[@]}" == 1 && -d "${matches[0]}" ]] || fail "expected exactly one archived change for recovery"
  target_dir="${matches[0]}"
  echo "Resuming archived change without re-merging specs: $change_id"
fi

if [[ -d "$legacy_target_dir" && ! -e "$target_dir" ]]; then
  safe_move "$legacy_target_dir" "$target_dir"
  echo "Relocated OpenSpec CLI legacy output to canonical archive: openspec/archive/$archive_date-$change_id"
fi

relocate_legacy_archives "$canonical_root" "$legacy_root"

# OpenSpec chooses its actual migration day; resolve the single identity rather
# than assuming a preparation date or a caller-supplied day is the destination.
shopt -s nullglob
matches=("$canonical_root"/????-??-??-"$change_id")
shopt -u nullglob
[[ "${#matches[@]}" == 1 && -d "${matches[0]}" ]] || fail "expected exactly one archived change"
target_dir="${matches[0]}"
archive_date="$(basename "$target_dir")"
archive_date="${archive_date:0:10}"

[[ -d "$target_dir" ]] || fail "canonical archive target missing after archive: openspec/archive/$archive_date-$change_id"
[[ ! -e "$active_dir" ]] || fail "active change still exists after archive: openspec/changes/$change_id"
python scripts/archive-recovery-guard.py "$change_id" "$archive_date" >/dev/null || fail "archive recovery guard blocked $change_id"

python scripts/validate-directory-structure.py
python scripts/validate-env-ignore-policy.py
python scripts/validate-archive-evidence.py --change "$change_id" --archive-path "$target_dir"

if (( finalize )); then
  python scripts/sync-workflow-status.py --event opsx.archive --change "$change_id" --sprint auto
  python scripts/promote-issues-for-archive.py --change "$change_id" --reason "/opsx-archive $change_id"
  resolved_sprint="$(python - "$change_id" <<'PYTHON'
import sys
sys.path.insert(0, 'scripts')
from workflow_sync.collect import resolve_sprint_id
sprint, _ = resolve_sprint_id('auto', event='opsx.archive', change_id=sys.argv[1])
print(sprint or '')
PYTHON
)"
  usage_arguments=(--post-command-hook --workflow-event opsx.archive --change "$change_id")
  if [[ -n "$resolved_sprint" ]]; then usage_arguments+=(--sprint "$resolved_sprint"); fi
  python scripts/extract-ai-usage.py "${usage_arguments[@]}" --json | python -c '
import json, sys
data = json.load(sys.stdin)
keys = ("status", "usage_mode", "command_run_count", "sprint_snapshot", "warning_count", "warnings", "recommended_action")
print(json.dumps({key: data[key] for key in keys if key in data}, ensure_ascii=False))
'
fi

echo "Archived OpenSpec change to ${target_dir#"$project_root/"}/"

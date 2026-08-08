#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: scripts/archive-change.sh <change-id> [YYYY-MM-DD]" >&2
}

fail() {
  echo "ERROR: $*" >&2
  exit 1
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
  local stdout_file
  local stderr_file
  stdout_file="$(mktemp)"
  stderr_file="$(mktemp)"

  if ! openspec archive "$change" -y >"$stdout_file" 2>"$stderr_file"; then
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
    mv "$child" "$target"
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
archive_date="${2:-$(date +%Y-%m-%d)}"

if [[ -z "$change_id" ]]; then
  usage
  exit 2
fi

if [[ ! "$archive_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  fail "archive date must use YYYY-MM-DD: $archive_date"
fi

project_root="$(pwd)"
canonical_root="$project_root/openspec/archive"
legacy_root="$project_root/openspec/changes/archive"
active_dir="$project_root/openspec/changes/$change_id"
target_dir="$canonical_root/$archive_date-$change_id"
legacy_target_dir="$legacy_root/$archive_date-$change_id"

[[ -d "$active_dir" ]] || fail "active change not found: openspec/changes/$change_id"
[[ ! -e "$target_dir" ]] || fail "archive target already exists: openspec/archive/$archive_date-$change_id"

run_language_gate
relocate_legacy_archives "$canonical_root" "$legacy_root"

mkdir -p "$canonical_root"
run_openspec_archive "$change_id"

if [[ -d "$legacy_target_dir" && ! -e "$target_dir" ]]; then
  mv "$legacy_target_dir" "$target_dir"
  echo "Relocated OpenSpec CLI legacy output to canonical archive: openspec/archive/$archive_date-$change_id"
fi

relocate_legacy_archives "$canonical_root" "$legacy_root"

[[ -d "$target_dir" ]] || fail "canonical archive target missing after archive: openspec/archive/$archive_date-$change_id"
[[ ! -e "$active_dir" ]] || fail "active change still exists after archive: openspec/changes/$change_id"

python scripts/validate-directory-structure.py
python scripts/validate-env-ignore-policy.py
python scripts/validate-archive-evidence.py --change "$change_id" --archive-path "$target_dir"

echo "Archived OpenSpec change to openspec/archive/$archive_date-$change_id/"

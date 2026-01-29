#!/usr/bin/env bash
set -euo pipefail

# shell-guard: Detect and snapshot dirty git state before critical operations.
# Version: 1.0.0
# License: MIT

usage() {
  cat <<'EOF'
shell-guard - prevent accidental commits in dirty states.

Usage:
  shell-guard [--check] [--snapshot] [--status]

Options:
  --check     Exit 0 if clean, 2 if dirty (default).
  --snapshot  Write patch and untracked list to .guardian/snapshots/.
  --status    Print short git status.
EOF
}

mode_check=true
mode_snapshot=false
mode_status=false

for arg in "$@"; do
  case "$arg" in
    --check) mode_check=true ;;
    --snapshot) mode_snapshot=true ;;
    --status) mode_status=true ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Unknown option: $arg" >&2
      usage
      exit 1
      ;;
  esac
done

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$repo_root" ]]; then
  echo "Not inside a git repository." >&2
  exit 1
fi

cd "$repo_root"

if $mode_status; then
  git status -sb
fi

dirty_count="$(git status --porcelain | wc -l | tr -d ' ')"
if [[ "$dirty_count" -gt 0 ]]; then
  if $mode_snapshot; then
    snapshot_dir=".guardian/snapshots"
    mkdir -p "$snapshot_dir"
    ts="$(date +"%Y%m%d_%H%M%S")"
    patch_path="$snapshot_dir/dirty_${ts}.patch"
    git diff > "$patch_path"
    echo "Snapshot written: $patch_path"
  fi
  if $mode_check; then
    echo "Repository is dirty. Fix or stash changes before proceeding."
    exit 2
  fi
else
  if $mode_check; then
    exit 0
  fi
fi

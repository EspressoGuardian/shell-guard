#!/usr/bin/env python3
## FILE: repo_guard.py
## VERSION: v1.0.0
## LAST_TOUCHED: 2026-01-29
## OWNER: Hubsays-Studio
## STATUS: ACTIVE

import argparse
import fnmatch
import json
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath


def git(cmd, cwd):
    try:
        return subprocess.check_output(cmd, cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:
        return ""


def repo_root() -> Path:
    root = git(["git", "rev-parse", "--show-toplevel"], os.getcwd())
    if not root:
        return Path.cwd()
    return Path(root).resolve()


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_patterns(items):
    if not items:
        return []
    if isinstance(items, list):
        return [str(x) for x in items]
    return [str(items)]


def match_any(path: str, patterns) -> bool:
    posix_path = str(PurePosixPath(path))
    for pattern in patterns:
        try:
            if fnmatch.fnmatch(posix_path, pattern):
                return True
        except Exception:
            continue
    return False


def match_any_remote(urls, patterns) -> bool:
    for url in urls:
        for pattern in patterns:
            if fnmatch.fnmatch(url, pattern):
                return True
    return False


def get_repo_config(config: dict, root: Path) -> dict:
    repos = config.get("repos", [])
    for repo in repos:
        if Path(repo.get("root", "")).resolve() == root:
            return repo
    return {}


def parse_remotes(root: Path):
    raw = git(["git", "remote", "-v"], root)
    urls = []
    for line in raw.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            urls.append(parts[1])
    return sorted(set(urls))

def redact_remote(url: str) -> str:
    if "://" in url and "@" in url:
        scheme, rest = url.split("://", 1)
        if "@" in rest:
            _, host = rest.split("@", 1)
            return f"{scheme}://***@{host}"
    return url

def remote_has_credentials(url: str) -> bool:
    if "://" in url and "@" in url:
        scheme, rest = url.split("://", 1)
        if "@" in rest and not rest.startswith("@"):
            return True
    return False


def staged_files(root: Path):
    raw = git(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"], root)
    return [line.strip() for line in raw.splitlines() if line.strip()]


def detect_visibility(urls, repo_cfg, defaults):
    expected = repo_cfg.get("expected_visibility")
    public_patterns = normalize_patterns(repo_cfg.get("public_remotes"))
    private_patterns = normalize_patterns(repo_cfg.get("private_remotes"))

    matched_public = match_any_remote(urls, public_patterns) if public_patterns else False
    matched_private = match_any_remote(urls, private_patterns) if private_patterns else False

    if matched_public and matched_private:
        return "conflict", "remote", "Remote URLs match both public and private patterns."

    if matched_public:
        return "public", "remote", "Matched public remote pattern."

    if matched_private:
        return "private", "remote", "Matched private remote pattern."

    if expected:
        return expected, "expected", "Using expected visibility from config."

    if defaults.get("unknown_remotes_assume_public", True):
        return "public", "default", "Unknown remote; defaulting to public for safety."

    return "unknown", "default", "Unknown remote visibility."


def main() -> int:
    ap = argparse.ArgumentParser(description="Repo visibility + path guard")
    ap.add_argument("--config", default="tools/ci/repo_visibility.json")
    ap.add_argument("--staged", action="store_true", help="Check staged files (default)")
    args = ap.parse_args()

    root = repo_root()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = (root / config_path).resolve()

    if not config_path.exists():
        print(f"[repo-guard] Missing config: {config_path}", file=sys.stderr)
        return 1

    config = load_config(config_path)
    defaults = config.get("defaults", {})
    repo_cfg = get_repo_config(config, root)
    if not repo_cfg:
        print(f"[repo-guard] No repo entry for root: {root}", file=sys.stderr)
        return 1

    urls = parse_remotes(root)
    visibility, vis_source, vis_note = detect_visibility(urls, repo_cfg, defaults)

    errors = []
    warns = []

    expected = repo_cfg.get("expected_visibility")
    if visibility == "conflict":
        errors.append("Remote visibility patterns conflict; fix repo_visibility.json.")
    elif expected and visibility in ("public", "private") and expected != visibility and vis_source == "remote":
        errors.append(
            f"Remote visibility mismatch: expected {expected}, detected {visibility}."
        )

    files = staged_files(root)
    if not files:
        print("[repo-guard] No staged files; skipping.")
        return 0

    allowed = normalize_patterns(repo_cfg.get("allowed_paths", []))
    default_allowed = normalize_patterns(defaults.get("allowed_paths", []))
    allowed = allowed + default_allowed

    if not allowed:
        errors.append("No allowed_paths configured for repo.")

    forbidden = normalize_patterns(defaults.get("always_forbidden_paths", []))
    forbidden += normalize_patterns(repo_cfg.get("always_forbidden_paths", []))

    public_block = normalize_patterns(defaults.get("public_block_paths", []))
    public_block += normalize_patterns(repo_cfg.get("public_block_paths", []))

    for path in files:
        if path.startswith("/"):
            errors.append(f"Invalid staged path (absolute): {path}")
            continue
        parts = PurePosixPath(path).parts
        if ".." in parts:
            errors.append(f"Invalid staged path (parent traversal): {path}")
            continue

        if forbidden and match_any(path, forbidden):
            errors.append(f"Forbidden path staged: {path}")
            continue

        if visibility == "public" and public_block and match_any(path, public_block):
            errors.append(f"Public repo block: {path}")
            continue

        if allowed and not match_any(path, allowed):
            errors.append(f"Path outside allowlist: {path}")

    if visibility == "unknown":
        warns.append("Repo visibility unknown; verify in GitHub UI.")
    else:
        warns.append(f"Repo visibility: {visibility} (source: {vis_source}).")
        warns.append(vis_note)

    if urls:
        redacted = [redact_remote(u) for u in urls]
        warns.append("Remotes: " + ", ".join(redacted))
        if any(remote_has_credentials(u) for u in urls):
            warns.append("Remote URL contains embedded credentials; prefer credential helpers.")

    if errors:
        print("\n[repo-guard] FAIL")
        for err in errors:
            print(f" - {err}")
        if warns:
            print("\n[repo-guard] Notes")
            for w in warns:
                print(f" - {w}")
        return 1

    print("[repo-guard] OK")
    for w in warns:
        print(f"[repo-guard] NOTE: {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
